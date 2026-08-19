"""
Orquestador: junta lo que encuentra en el Excel local y el CRM propio
(Firebase), y arma un resumen de productor.

(Outlook queda deshabilitado por ahora en esta v1.0 — se puede sumar más
adelante si hace falta.)

Por defecto arma el resumen ordenando los datos en Python (gratis, sin
depender de ningún servicio pago), en un formato prolijo pensado para leer
antes de una reunión. Si en el .env cargás ANTHROPIC_API_KEY, en cambio le
pide a Claude que redacte el resumen en prosa a partir de los mismos datos.
"""
import re

import pandas as pd

from .config import Config
from .connectors import local_excel, firebase_crm, news

# Nombres más amigables para las colecciones del CRM
NOMBRES_COLECCIONES = {
    "agentesProductores": "Datos del productor",
    "aperturas": "Aperturas",
    "companies": "Empresas / Compañías",
    "reminders": "Recordatorios",
}

SYSTEM_PROMPT = """\
Sos un asistente de un coordinador comercial que maneja la relación con \
Agentes Productores para un grupo de empresas financieras. Te paso datos \
crudos sacados de tres fuentes (filas de Excel del CRM/planillas, \
registros del CRM propio, y noticias públicas encontradas en internet) \
sobre UN productor puntual.

Tu tarea es armar un resumen breve y accionable, en español, con esta \
estructura:

1. **Estado general**: 2-3 líneas sobre cómo viene la relación con este \
productor (activo, en alta, inactivo, con problemas, etc.), basado en lo \
que ves en los datos.
2. **Documentación / carpeta**: qué se pidió, qué llegó y qué falta, si \
hay información al respecto en los datos. Si no hay info clara, decilo.
3. **Volumen de negocio**: cifras u operaciones mencionadas, con fecha si \
la tenés.
4. **Noticias públicas**: si hay noticias recientes sobre el productor, \
resumilas y marcá si ameritan atención (ej. problemas legales, cambios \
societarios) o si son neutras/positivas. Si no hay ninguna, decilo.
5. **Puntos de atención antes de la reunión**: cualquier cosa que llame \
la atención — algo pendiente hace mucho, una alerta, una oportunidad.

Reglas importantes:
- No inventes datos que no estén en el contexto. Si algo no aparece, \
decilo explícitamente ("no encontré información sobre X").
- Sé concreto y priorizá lo accionable por sobre lo descriptivo.
- Si el contexto está vacío o casi vacío, decilo claramente en vez de \
rellenar con generalidades.
"""


def _campo_vacio(valor) -> bool:
    if valor is None:
        return True
    texto = str(valor).strip()
    return texto == "" or texto.lower() == "nan"


def _humanizar_campo(campo: str) -> str:
    """Convierte nombres técnicos en algo legible: separa camelCase
    ("fechaUltimoContacto" -> "Fecha ultimo contacto") pero deja intactas
    las columnas que ya vienen en MAYÚSCULAS (ej. "CUENTA" -> "Cuenta")."""
    campo = campo.replace("_", " ")
    # Solo separa en transiciones minúscula->MAYÚSCULA (camelCase real),
    # así no rompe encabezados que ya están todo en mayúsculas.
    campo = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", campo)
    campo = re.sub(r"\s+", " ", campo)
    return campo.strip().capitalize()


def _bullets_de_dict(datos: dict, excluir: tuple[str, ...] = ()) -> list[str]:
    """Arma una lista de líneas "• Campo: Valor", salteando campos vacíos,
    técnicos (columnas "Unnamed..." de Excel) o explícitamente excluidos."""
    bullets = []
    for campo, valor in datos.items():
        if campo in excluir or campo.startswith("Unnamed") or campo == "_hoja":
            continue
        if _campo_vacio(valor):
            continue
        bullets.append(f"  • {_humanizar_campo(campo)}: {valor}")
    return bullets


def _df_to_text(nombre_archivo: str, df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    bloques = []
    for i, (_, fila) in enumerate(df.iterrows(), start=1):
        bullets = _bullets_de_dict(fila.to_dict())
        if bullets:
            bloques.append(f"Fila {i} ({nombre_archivo}):\n" + "\n".join(bullets))
    return "\n\n".join(bloques)


def _crm_to_text(por_coleccion: dict[str, list[dict]]) -> str:
    if not por_coleccion:
        return "No se encontraron registros en el CRM."
    partes = []
    for nombre_coleccion, registros in por_coleccion.items():
        titulo = NOMBRES_COLECCIONES.get(nombre_coleccion, nombre_coleccion)
        for r in registros:
            bullets = _bullets_de_dict(r, excluir=("_id",))
            if bullets:
                partes.append(f"{titulo}:\n" + "\n".join(bullets))
    return "\n\n".join(partes) if partes else "No se encontraron registros en el CRM."


def _noticias_to_text(noticias: list[dict]) -> str:
    if not noticias:
        return "No se encontraron noticias recientes."
    partes = []
    for n in noticias:
        partes.append(f"  • {n['title']}\n    ({n['source']}, {n['date']})\n    {n['link']}")
    return "\n".join(partes)


def _nombre_completo_mas_confiable(nombre_buscado: str, crm_registros: dict[str, list[dict]]) -> str:
    """
    El texto que escribe el usuario puede ser solo un apellido (ej. "Carafi"),
    lo cual trae noticias de otras personas con el mismo apellido. Si el CRM
    tiene un campo "nombre" más completo para este productor, lo usamos en su
    lugar para buscar noticias más precisas.
    """
    for registros in crm_registros.values():
        for r in registros:
            nombre = r.get("nombre")
            if nombre and len(nombre) > len(nombre_buscado):
                return nombre
    return nombre_buscado


def build_producer_summary(nombre_productor: str, verbose: bool = True) -> str:
    """Junta las fuentes disponibles y arma el resumen del productor."""

    if verbose:
        print(f"Buscando en los Excel locales...")
    hojas = local_excel.search_excel(nombre_productor, Config.EXCEL_PATHS)

    if verbose:
        print(f"Buscando en el CRM (Firebase)...")
    crm_registros = firebase_crm.search_crm(nombre_productor)

    nombre_para_noticias = _nombre_completo_mas_confiable(nombre_productor, crm_registros)

    if verbose:
        print(f"Buscando noticias sobre '{nombre_para_noticias}' en internet...")
    noticias = news.search_news(nombre_para_noticias)

    bloques_excel = [_df_to_text(nombre, df) for nombre, df in hojas.items()]
    contexto_excel = "\n\n".join(b for b in bloques_excel if b) or "No se encontraron datos en el Excel."

    alerta_noticias = ""
    if noticias:
        alerta_noticias = f"\n⚠️  ATENCIÓN: se encontraron {len(noticias)} noticia(s) sobre '{nombre_para_noticias}' — revisar la sección de Noticias más abajo.\n"

    contexto = f"""\
FICHA DEL PRODUCTOR: {nombre_productor}
{alerta_noticias}
DATOS EN EXCEL
--------------
{contexto_excel}

DATOS EN EL CRM
---------------
{_crm_to_text(crm_registros)}

NOTICIAS PÚBLICAS
------------------
{_noticias_to_text(noticias)}
"""

    if not Config.ANTHROPIC_API_KEY:
        if verbose:
            print("Armando el resumen (sin IA, solo ordenando los datos)...\n")
        return contexto

    if verbose:
        print("Armando el resumen con Claude...\n")

    from anthropic import Anthropic

    client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    respuesta = client.messages.create(
        model=Config.ANTHROPIC_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": contexto}],
    )
    return respuesta.content[0].text
