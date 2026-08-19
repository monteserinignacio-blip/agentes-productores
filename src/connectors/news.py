"""
Búsqueda de noticias recientes sobre un productor, usando el buscador de
noticias de Google (RSS público, no requiere clave ni cuenta).
"""
import xml.etree.ElementTree as ET

import requests

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


def search_news(query: str, idioma: str = "es-419", pais: str = "AR", top: int = 5) -> list[dict]:
    """
    Busca noticias que mencionen `query` (ej. el nombre del productor).

    Devuelve una lista de dicts con: title, source, date, link.
    Si no encuentra nada, o si falla la conexión, devuelve lista vacía
    (nunca corta la ejecución del resto del programa).
    """
    params = {
        "q": query,
        "hl": idioma,
        "gl": pais,
        "ceid": f"{pais}:{idioma}",
    }
    try:
        resp = requests.get(GOOGLE_NEWS_RSS, params=params, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as e:
        print(f"  ! No se pudo buscar noticias: {e}")
        return []

    resultados = []
    for item in root.findall(".//item")[:top]:
        titulo = item.findtext("title", "")
        fuente_el = item.find("source")
        fuente = fuente_el.text if fuente_el is not None else ""
        resultados.append({
            "title": titulo,
            "source": fuente,
            "date": item.findtext("pubDate", ""),
            "link": item.findtext("link", ""),
        })
    return resultados
