from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from Back.routes.planes import planes_bp
from Back.routes.productos import productos_bp
from Back.routes.reservas import reservas_bp
from Back.routes.usuarios import usuarios_bp
from Back.routes.roles import roles_bp
from Back.routes.docs import init_docs
from Back.db.db import get_connection

# import requests

# --------------------------------------------Rutas||Back--------------------------------------------
app = Flask(__name__)
CORS(app, supports_credentials=True)
init_docs(app)
app.register_blueprint(planes_bp, url_prefix="/api/planes")
app.register_blueprint(productos_bp, url_prefix="/api/productos")
app.register_blueprint(reservas_bp, url_prefix="/api/reservas")
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(roles_bp, url_prefix="/api/roles")

try:
    conn = get_connection()
    conn.close()
    print("\033[92m------Conectado a la base de datos exitosamente.\033[0m")
except Exception as e:
    print("\033[91mError al conectar con la base de datos:", e, "\033[0m")

# --------------------------------------------Rutas||Front--------------------------------------------


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/planes")
def planes():
    planes = [
        {
            "id": "bodybuilding",
            "nombre": "Body-Building",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/bodybuilding.png"),
            "precio_dias": {
                3: 46900,
                5: 63000
            }
        },
        {
            "id": "spinning",
            "nombre": "Spinning",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/spinning.png"), 
            "precio_dias": {
                3: 29500,
                5: 42000
            }
        },
        {
            "id": "sport",
            "nombre": "Sport-Focused Training",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/sport.png"),
            "precio_dias": {
                3: 49500,
                5: 65000
            },
            "deportes": ["futbol sala", "boxeo", "rugby"]
        }
    ]
    return render_template("planes.html", planes=planes)


@app.route("/reservas")
def reservas():
    return render_template("reservas.html")


@app.route('/tienda', methods=['GET'])
def tienda():
    productos = [
        {
            'nombre': 'Bomba de Proteína',
            'descripcion': 'Milkshake sabor chocolate alto en proteína',
            'precio': 4500,
            'imagen': 'milkshake.png'
        },
        {
            'nombre': 'Proteína en Polvo',
            'descripcion': 'Suplemento concentrado de suero',
            'precio': 8500,
            'imagen': 'proteina.png'
        },
        {
            'nombre': 'Mancuernas 5kg',
            'descripcion': 'Accesorio esencial para entrenamiento',
            'precio': 6200,
            'imagen': 'mancuernas.png'
        }
    ]
    return render_template('tienda.html', productos=productos)


@app.route("/user")
def user():
    return render_template("user.html")


# ----------------------Auth----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    # if request.method == "POST":
    #     mail = request.form.get("email")
    #     contraseña = request.form.get("contraseña")
    #     if not mail or not contraseña:
    #         return render_template(
    #             "auth/login.html", error="No se completaron todos los campos"
    #         )
    #     try:
    #         # Mandar los datos al backend
    #         response = requests.post(
    #             "http://localhost:3001/usuarios/login",
    #             json={"email": mail, "password": contraseña},
    #             timeout=5,  # evita que cuelgue si el back no responde
    #         )

    #         if response.status_code == 200:
    #             return redirect(url_for("home"))
    #         else:
    #             mensaje = response.json().get("error", "Error al iniciar sesión")
    #             return render_template("auth/login.html", error=mensaje)

    #     except requests.exceptions.RequestException:
    #         return render_template(
    #             "auth/login.html", error="Error de conexión con el servidor"
    #         )


@app.route("/registro")
def registro():
    return render_template("auth/registro.html")


@app.route("/cambiarcontra")
def cambiarcontra():
    return render_template("auth/cambiar_contra.html")


if __name__ == "__main__":
    app.run("localhost", port=3000, debug=True)
