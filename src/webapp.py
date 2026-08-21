"""
Interfaz web local (Flask): la misma búsqueda que la versión de terminal,
pero mostrada como una página prolija en el navegador.

Corre 100% en tu computadora — nadie más que vos puede acceder, porque el
servidor solo escucha en tu propia máquina (127.0.0.1).
"""
from flask import Flask, jsonify, render_template, request

from .config import Config
from .agent import gather_producer_data, datos_a_dict

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/buscar")
def api_buscar():
    nombre = request.args.get("nombre", "").strip()
    if not nombre:
        return jsonify({"error": "Escribí el nombre de un productor."}), 400
    try:
        Config.validate()
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    try:
        datos = gather_producer_data(nombre, verbose=False)
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error buscando información: {e}"}), 500

    return jsonify(datos_a_dict(datos))


def main():
    print("=" * 60)
    print(" Agente de Productores — abriendo en el navegador")
    print(" http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
