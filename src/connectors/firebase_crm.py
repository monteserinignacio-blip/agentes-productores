"""Búsqueda de productores en tu CRM propio (Firebase / Firestore)."""
import firebase_admin
from firebase_admin import credentials, firestore

from ..config import Config

_app = None


def _get_client():
    global _app
    if _app is None:
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
        _app = firebase_admin.initialize_app(cred)
    # Tu proyecto usa una base de Firestore con nombre propio (no la
    # "(default)"), así que hay que indicárselo explícitamente.
    if Config.FIREBASE_DATABASE_ID:
        return firestore.client(app=_app, database_id=Config.FIREBASE_DATABASE_ID)
    return firestore.client(app=_app)


def search_crm(query: str) -> dict[str, list[dict]]:
    """
    Busca en TODAS las colecciones configuradas (ej. agentesProductores,
    aperturas, companies, reminders) los documentos que contengan `query`
    en alguno de sus campos de texto.

    NOTA: Firestore no tiene búsqueda de texto libre nativa. Como punto de
    partida traemos cada colección entera y filtramos en Python — anda bien
    para carteras de hasta unos pocos miles de registros. Si alguna colección
    es mucho más grande, conviene reemplazar esto por una query indexada
    sobre un campo específico (ej. "nombre") o por Algolia/Typesense.

    Devuelve: { "agentesProductores": [...], "aperturas": [...], ... }
    (solo incluye colecciones donde hubo al menos un resultado).
    """
    db = _get_client()
    query_lower = query.lower()

    resultados: dict[str, list[dict]] = {}
    for nombre_coleccion in Config.FIREBASE_COLLECTIONS:
        coleccion = db.collection(nombre_coleccion)
        matches = []
        for doc in coleccion.stream():
            data = doc.to_dict()
            data["_id"] = doc.id
            texto_completo = " ".join(str(v) for v in data.values()).lower()
            if query_lower in texto_completo:
                matches.append(data)
        if matches:
            resultados[nombre_coleccion] = matches
    return resultados
