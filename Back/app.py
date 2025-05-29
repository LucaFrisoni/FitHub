from flask import Flask
from flask_cors impor CORS
from routes.planes import planes_bp
from routes.productos import productos_bp
from routes.reservas import reservas_bp
from routes.usuarios import usuarios_bp

app = Flask(__name__)

app.register_blueprint(planes_bp, url_prefix="/planes")
app.register_blueprint(productos_bp, url_prefix="/productos")
app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")

if __name__ == "__main__":
    app.run(debug=true)