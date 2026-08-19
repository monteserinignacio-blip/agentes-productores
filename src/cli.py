"""Chat simple en la terminal: escribís el nombre del productor y te trae el resumen."""
import sys

from .config import Config
from .agent import build_producer_summary


def main():
    # En algunas consolas de Windows, la salida no soporta emojis/tildes por
    # defecto (usan un códec viejo, cp1252) y el programa se cae al imprimir.
    # Forzamos UTF-8 para que siempre funcione, sin importar la consola.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("=" * 60)
    print(" Agente de Productores — ficha para reunión")
    print(" (Excel local + CRM en Firebase + noticias)")
    print("=" * 60)

    try:
        Config.validate()
    except RuntimeError as e:
        print(f"\n⚠️  {e}\n")
        return

    print("\nEscribí el nombre de un productor (o 'salir' para terminar).\n")

    while True:
        nombre = input("Productor > ").strip()
        if not nombre:
            continue
        if nombre.lower() in ("salir", "exit", "quit"):
            break

        try:
            resumen = build_producer_summary(nombre)
        except Exception as e:
            print(f"\n⚠️  Ocurrió un error buscando información: {e}\n")
            continue

        print("\n" + "-" * 60)
        print(resumen)
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
