"""Carga de configuración desde variables de entorno (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()

# Carpeta raíz del proyecto (un nivel arriba de "src"). La usamos para que
# las rutas relativas del .env funcionen sin importar desde qué carpeta se
# ejecute el programa (ej. si abrís PowerShell en otro lugar).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ruta_absoluta(path: str) -> str:
    if not path or os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


class Config:
    # Firebase: una o más colecciones separadas por coma, ej.
    # "agentesProductores,aperturas,companies,reminders"
    FIREBASE_CREDENTIALS_PATH = _ruta_absoluta(
        os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-service-account.json")
    )
    FIREBASE_COLLECTIONS = [
        c.strip() for c in os.getenv("FIREBASE_COLLECTIONS", "agentesProductores").split(",") if c.strip()
    ]
    # Nombre de la base de Firestore, si no es la "(default)" (ver README)
    FIREBASE_DATABASE_ID = os.getenv("FIREBASE_DATABASE_ID", "")

    # Excel local: uno o más paths separados por coma, ej.
    # "C:\Users\vos\Desktop\Productores.xlsx"
    EXCEL_PATHS = [
        p.strip() for p in os.getenv("EXCEL_PATHS", "").split(",") if p.strip()
    ]

    # Anthropic (OPCIONAL: si no la completás, el resumen se arma sin IA,
    # solo ordenando los datos encontrados)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    @classmethod
    def validate(cls):
        faltantes = []
        if not cls.EXCEL_PATHS:
            faltantes.append("EXCEL_PATHS")
        if faltantes:
            raise RuntimeError(
                "Faltan variables en tu .env: " + ", ".join(faltantes) +
                "\nRevisá el README para completar cada una."
            )
