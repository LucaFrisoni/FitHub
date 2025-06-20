from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
import os

from db.db import get_connection
from routes.planes import planes_bp
from routes.productos import productos_bp
from routes.horariosentrenamiento import horarios_bp
from routes.usuarios import usuarios_bp
from routes.roles import roles_bp
from routes.alquileresplan import alquileres_plan_bp
from routes.compras import compras_bp
from routes.pago import pago_bp
from routes.docs import init_docs

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[os.getenv("FRONT_HOST")])
init_docs(app)
app.register_blueprint(planes_bp, url_prefix="/api/planes")
app.register_blueprint(productos_bp, url_prefix="/api/productos")
app.register_blueprint(alquileres_plan_bp, url_prefix="/api/alquileres")
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(roles_bp, url_prefix="/api/roles")
app.register_blueprint(compras_bp, url_prefix="/api/compras")
app.register_blueprint(pago_bp, url_prefix="/api/pago")
app.register_blueprint(horarios_bp, url_prefix="/api/horariosentrenamiento")


# ------------------Check-conexion-bd------------------
try:
    conn = get_connection()
    conn.close()
    print("\033[92m------Conectado a la base de datos exitosamente.\033[0m")
except Exception as e:
    print("\033[91mError al conectar con la base de datos:", e, "\033[0m")


@app.route("/debug")
def debug_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(f"{rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
    return "<br>".join(output)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
