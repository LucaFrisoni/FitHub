from flask import Flask
from flask_cors import CORS
from routes.planes import planes_bp
from routes.productos import productos_bp
from routes.reservas import reservas_bp
from routes.usuarios import usuarios_bp
from routes.roles import roles_bp
from routes.docs import init_docs

app = Flask(__name__)

init_docs(app)
app.register_blueprint(planes_bp, url_prefix="/planes")
app.register_blueprint(productos_bp, url_prefix="/productos")
app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(roles_bp, url_prefix="/roles")

if __name__ == "__main__":
    app.run(debug=True)

