# Agente de Productores — ficha para reunión

Trabajo coordinando un equipo comercial que maneja la relación con **Agentes
Productores** para un grupo de empresas financieras. Antes de cada reunión
con un productor necesito juntar su información de tres lugares distintos
(un Excel, un CRM propio, y a veces alguna noticia pública sobre esa
persona/empresa) — y eso me lleva tiempo cada vez.

Este es un agente de línea de comandos que hace ese trabajo por mí: le
escribo el nombre de un productor y busca en las tres fuentes a la vez,
después me arma una "ficha" ordenada y legible, lista para llevar a la
reunión.

## Qué hace, concretamente

```
Productor > Pedro Carafi

Buscando en los Excel locales...
Buscando en el CRM (Firebase)...
Buscando noticias sobre 'PEDRO CARAFI' en internet...

------------------------------------------------------------
FICHA DEL PRODUCTOR: Pedro Carafi

DATOS EN EXCEL
--------------
Fila 1 (BASE Clientes Copia.xlsx):
  • Cuenta: 2459
  • Cliente: PEDRO CARAFI
  • Cartera propia: NO
  • Esquema: A
  ...

DATOS EN EL CRM
---------------
Datos del productor:
  • Activo: True
  • Fecha ultimo contacto: 2026-07-28
  • Provincia: CABA

NOTICIAS PÚBLICAS
------------------
  • RODRIGO CARAFI: "Ha sido un año difícil" - Agencia Comunas
    (Agencia Comunas, Fri, 20 Dec 2024)
    https://news.google.com/...
------------------------------------------------------------
```

Tres fuentes, un solo lugar:

1. **Excel local** — lee un archivo `.xlsx` en tu computadora y busca todas
   las filas donde aparezca el nombre buscado, mostrando solo los campos
   que tienen datos (nada de columnas vacías o técnicas).
2. **CRM propio (Firebase / Firestore)** — busca en varias colecciones a la
   vez (por defecto: `agentesProductores`, `aperturas`, `companies`,
   `reminders`) los documentos relacionados al productor.
3. **Noticias públicas (Google News)** — busca si hay noticias recientes
   sobre el productor y avisa arriba de todo si encontró algo, para que no
   se te pase por alto antes de la reunión.

## Cómo está armado (y por qué)

- **100% local**: es un script de Python que corre en tu computadora, no un
  servicio en la nube. Vos controlás tus propias credenciales.
- **Gratis por defecto**: no necesita ninguna clave paga. El "resumen" se
  arma ordenando y filtrando los datos en Python (ver
  [`src/agent.py`](src/agent.py), función `build_producer_summary`), no
  redactándolo con un modelo de lenguaje. Si en algún momento se quiere una
  versión narrada en prosa, alcanza con cargar una clave de la API de
  Anthropic en el `.env` (`ANTHROPIC_API_KEY`) — el mismo código detecta si
  está configurada y cambia de modo automáticamente.
- **Cada fuente es un "conector" independiente**
  (`src/connectors/local_excel.py`, `firebase_crm.py`, `news.py`), y
  `src/agent.py` es el orquestador: le pide a cada conector sus resultados,
  los combina, y arma la ficha final. Separar así permite agregar o sacar
  fuentes sin tocar el resto (por ejemplo, agregar Outlook en el futuro).

## Qué NO hace (todavía)

- No escribe nada de vuelta en el CRM ni en el Excel — es solo lectura.
- No busca en el correo (Outlook) — se evaluó al principio, pero requería
  registrar una aplicación en Azure AD a través del área de sistemas de la
  empresa, y se decidió dejarlo afuera de esta v1.0 para no depender de
  ese trámite. El código está pensado para poder sumarlo después como un
  conector más.
- No corre solo ni manda alertas automáticas — hay que abrirlo y escribir
  el nombre del productor cada vez.
- Cuando el Excel tiene al mismo productor cargado en varias filas (algo
  común en la base real que usé), las muestra todas por separado en vez de
  combinarlas en una sola ficha.
- La búsqueda de noticias es por nombre y apellido; con nombres muy
  comunes puede seguir trayendo resultados de otra persona.

## Instalación

Necesitás Python 3.10 o superior.

```bash
cd agente-productores
pip install -r requirements.txt
cp .env.example .env
```

Completá el `.env` con:

- **`EXCEL_PATHS`**: ruta completa del Excel en tu computadora (podés poner
  varias separadas por coma).
- **`FIREBASE_CREDENTIALS_PATH`** y **`FIREBASE_COLLECTIONS`**: credenciales
  y colecciones de tu CRM en Firebase. Para generar la credencial: Firebase
  Console → tu proyecto → ⚙️ Configuración del proyecto → **Service
  accounts** → **Generate new private key**. Guardá ese archivo como
  `firebase-service-account.json` en esta carpeta (nunca lo compartas ni lo
  subas a un repo — por eso está en `.gitignore`).
- **`FIREBASE_DATABASE_ID`**: dejalo vacío salvo que tu proyecto use una
  base de Firestore con nombre propio en vez de la "(default)" (se ve en
  Firebase → Firestore, arriba de todo, al lado de "Base de datos").
- **`ANTHROPIC_API_KEY`**: opcional, dejala vacía si no la vas a usar.

## Uso

```bash
python run.py
```

Escribís el nombre de un productor y Enter. Para terminar, escribís `salir`.

## Seguridad

Corre localmente con tus propias credenciales. `.env`,
`firebase-service-account.json` y cualquier caché de tokens están excluidos
en `.gitignore` — nunca se suben al repositorio.

## Reflexión: qué entendí y qué falta

**Sobre la lógica del agente:** entendí que "agente" acá no significa una
sola caja mágica, sino un **orquestador** que le pide datos a distintas
fuentes independientes (Excel, CRM, noticias) y después decide cómo
combinarlos. Cada fuente es intercambiable — pude sacar Outlook sin romper
nada, y puedo agregar una fuente nueva el día de mañana sin tocar las
demás. También entendí que "usar IA" era opcional: la parte inteligente de
verdad (buscar, cruzar, filtrar información dispersa) la resuelve código
normal; un modelo de lenguaje solo hacía falta para la redacción final, y
eso lo pude reemplazar por reglas simples cuando decidí no pagarlo.

**Qué falta para que sea realmente usable por mi equipo:**
- Que combine las filas repetidas del mismo productor en el Excel en vez
  de mostrarlas todas por separado.
- Sumar el correo (Outlook), que quedó afuera por la traba de Azure AD.
- Una interfaz más simple que la terminal (una página web local, por
  ejemplo) para que lo use alguien no técnico del equipo.
- Poder decirle "dame la ficha de estos 5 productores" de una sola vez,
  para preparar una reunión con varios en la agenda.
- Guardar un historial de qué se buscó y cuándo, para no repetir consultas.

**Qué aprendí del proceso en sí:** que documentar bien el proceso importa
tanto como el resultado — más de una vez el "error" fue mío (una sintaxis
de PowerShell mal escrita) y no del programa, y separar esas dos cosas fue
tan importante como arreglar los bugs reales.

## Proceso de construcción

Este proyecto se armó 100% conversando con un agente de IA (Claude), sin
escribir código a mano. El detalle completo de cómo se pidió, qué se
iteró, qué se rompió y cómo se arregló está documentado en
[`PROCESO.md`](PROCESO.md).
