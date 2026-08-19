"""Lectura y búsqueda sobre Excel guardados en una carpeta local de tu PC."""
import pandas as pd


def search_excel(query: str, paths: list[str]) -> dict[str, pd.DataFrame]:
    """
    Abre cada Excel en `paths` (rutas locales, ej. "C:\\...\\Productores.xlsx")
    y devuelve, por archivo, las filas donde alguna celda contiene `query`
    (case-insensitive, búsqueda simple de texto).

    Devuelve: { "Productores.xlsx": DataFrame_con_filas_matcheadas, ... }
    """
    query_lower = query.lower()
    resultados: dict[str, pd.DataFrame] = {}

    for path in paths:
        nombre_archivo = path.replace("\\", "/").rsplit("/", 1)[-1]
        try:
            hojas = pd.read_excel(path, sheet_name=None, dtype=str)
        except FileNotFoundError:
            print(f"  ! No se encontró el archivo: {path}")
            continue
        except Exception as e:
            print(f"  ! No se pudo leer {path}: {e}")
            continue

        filas_matcheadas = []
        for nombre_hoja, df in hojas.items():
            df = df.fillna("")
            mask = df.apply(
                lambda fila: fila.astype(str).str.lower().str.contains(query_lower).any(),
                axis=1,
            )
            matches = df[mask].copy()
            if not matches.empty:
                matches.insert(0, "_hoja", nombre_hoja)
                filas_matcheadas.append(matches)

        if filas_matcheadas:
            resultados[nombre_archivo] = pd.concat(filas_matcheadas, ignore_index=True)

    return resultados
