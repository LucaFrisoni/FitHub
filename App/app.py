# -*- coding: utf-8 -*-
import os
import re
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_cors import CORS
from Back.util.util import check_pwd
from Back.models.user import User
from Back.routes.planes import planes_bp
from Back.routes.productos import productos_bp
from Back.routes.reservas import reservas_bp
from Back.routes.usuarios import usuarios_bp
from Back.routes.roles import roles_bp
from Back.routes.docs import init_docs
from Back.db.db import get_connection
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
import requests


# --------------------------------------------Rutas||Back--------------------------------------------
app = Flask(__name__)

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
app.secret_key = 'APP_SECRET_KEY'

init_docs(app)


app.register_blueprint(planes_bp, url_prefix="/api/planes")
app.register_blueprint(productos_bp, url_prefix="/api/productos")
app.register_blueprint(reservas_bp, url_prefix="/api/reservas")
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(roles_bp, url_prefix="/api/roles")

# ------------------Check-conexion-bd------------------
try:
    conn = get_connection()
    conn.close()
    print("\033[92m------Conectado a la base de datos exitosamente.\033[0m")
except Exception as e:
    print("\033[91mError al conectar con la base de datos:", e, "\033[0m")

# ------------------InitAuth------------------
login_manager = LoginManager()
login_manager.init_app(app)  # Conectás Flask-Login con tu app
login_manager.login_view = (
    "login"  # la ruta donde te lleva si no esta logeado en una ruta proteguida
)


@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE ID_usuario = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(
            user["ID_usuario"],
            user["Nombre"],
            user["Apellido"],
            user["Email"],
            user["Telefono"],
            user["FechaNacimiento"],
            user["Usuario"],
            user.get("Imagen") or None,
            # user["ID_rol"],
        )
    return None


# --------------------------------------------Rutas||Front--------------------------------------------


@app.route("/")
def home():
    # si existe la session login, la devuelve y luego la borra, sino usa False
    login = session.pop("login", False)
    return render_template("home.html", login=login, user=current_user)


@app.route("/planes")
def planes():
    planes = [
        {
            "id": "bodybuilding",
            "nombre": "Body-Building",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/bodybuilding.png"),
            "precio_dias": {3: 46900, 5: 63000},
        },
        {
            "id": "spinning",
            "nombre": "Spinning",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/spinning.png"),
            "precio_dias": {3: 29500, 5: 42000},
        },
        {
            "id": "sport",
            "nombre": "Sport-Focused Training",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/sport.png"),
            "precio_dias": {3: 49500, 5: 65000},
            "deportes": ["futbol sala", "boxeo", "rugby"],
        },
    ]
    return render_template("planes.html", planes=planes, user=current_user)


@app.route("/reservas")
# @login_required
def reservas():
    return render_template("reservas.html", user=current_user)


@app.route("/tienda", methods=["GET"])
def tienda():
    productos = [
        {
            "id": 1,
            "nombre": "Bomba de Proteína",
            "descripcion": "Milkshake sabor chocolate alto en proteína",
            "precio": 4500,
            "imagen": "milkshake.png",
        },
        {
            "id": 2,
            "nombre": "Proteína en Polvo",
            "descripcion": "Suplemento concentrado de suero",
            "precio": 8500,
            "imagen": "proteina.png",
        },
        {
            "id": 3,
            "nombre": "Mancuernas 5kg",
            "descripcion": "Accesorio esencial para entrenamiento",
            "precio": 6200,
            "imagen": "mancuernas.jpg",
        },
    ]
    return render_template("tienda.html", productos=productos, user=current_user)


@app.route("/producto/<int:id>")
def producto(id):
    productos = [
        {
            "id": 1,
            "nombre": "Bomba de Proteína",
            "descripcion": "Milkshake sabor chocolate alto en proteína",
            "precio": 4500,
            "imagen": "images/milkshake.png",
        },
        {
            "id": 2,
            "nombre": "Proteína en Polvo",
            "descripcion": "Suplemento concentrado de suero",
            "precio": 8500,
            "imagen": "images/proteina.png",
        },
        {
            "id": 3,
            "nombre": "Mancuernas 5kg",
            "descripcion": "Accesorio esencial para entrenamiento",
            "precio": 6200,
            "imagen": "images/mancuernas.jpg",
        },
    ]
    producto = next((p for p in productos if p["id"] == id), None)
    if producto is None:
        return "Producto no encontrado", 404
    return render_template("producto.html", producto=producto, user=current_user)


@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    if request.method == "GET":
        # si existe la session login, la devuelve y luego la borra, sino usa False
        usuario_editado = session.pop("usuario_editado", False)
        return render_template(
            "user.html", user=current_user, usuario_editado=usuario_editado
        )

    payload = {
        "Email": current_user.email,  # fijo, para identificar al usuario
        "Nombre": request.form.get("nombre"),
        "Apellido": request.form.get("apellido"),
        "Usuario": request.form.get("usuario"),
        "Telefono": request.form.get("telefono"),
        "FechaNacimiento": request.form.get("nacimiento"),
    }

    try:
        response = requests.put(
            "http://localhost:3000/api/usuarios/editar-usuario", json=payload
        )
        if response.status_code == 200:
            data = response.json()
            usuario = data["usuario"]

            nuevo_usuario = User(
                usuario["ID_usuario"],
                usuario["Nombre"],
                usuario["Apellido"],
                usuario["Email"],
                usuario["Telefono"],
                usuario["FechaNacimiento"],
                usuario["Usuario"],
                usuario.get("Imagen") or None,
            )
            # Guardar en session si querés mostrar algo en el User
            session["usuario_editado"] = True
            login_user(nuevo_usuario)
            return redirect("/user")
        else:
            error_msg = response.json().get("error", "Error inesperado")
            return render_template("user.html", user=current_user, error=error_msg)
    except Exception as ex:
        return render_template(
            "user.html", error="Error en el servidor. Intentalo más tarde."
        )


# ----------------------Rutas||Auth----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    # si existe la session login, la devuelve y luego la borra, sino usa False
    usuario_creado = session.pop("usuario_creado", False)
    contraseña_cambiada = session.pop("contraseña_cambiada", False)
    if request.method == "GET":
        return render_template(
            "auth/login.html",
            usuario_creado=usuario_creado,
            contraseña_cambiada=contraseña_cambiada,
        )

    # Obtener datos del formulario
    email = request.form.get("email")
    contraseña = request.form.get("contraseña")
    # Validaciones básicas
    if not email or not contraseña:
        return render_template(
            "auth/login.html", error="Email y contraseña son obligatorios."
        )

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar usuario
        cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template("auth/login.html", error="Usuario no encontrado.")

        if not check_pwd(contraseña, user["Contrasenia"]):
            return render_template("auth/login.html", error="Contraseña incorrecta.")

        # Crear objeto User y loguear
        usuario = User(
            user["ID_usuario"],
            user["Nombre"],
            user["Apellido"],
            user["Email"],
            user["Telefono"],
            user["FechaNacimiento"],
            user["Usuario"],
            user.get("Imagen") or None,
            # user["ID_rol"],
        )
        login_user(usuario)

        # Guardar en session si querés mostrar algo en el home
        session["login"] = True

        return redirect("/")
    except Exception as ex:
        return render_template(
            "auth/login.html", error="Error en el servidor. Intentalo más tarde."
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("auth/registro.html")

    # Obtener datos del formulario
    email = request.form.get("email")
    contraseña = request.form.get("contraseña")
    nombre_usuario = request.form.get("nombre_usuario")
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    nacimiento = request.form.get("nacimiento")
    telefono = request.form.get("telefono")

    # Validar campos
    campos = [email, contraseña, nombre_usuario, nombre, apellido, nacimiento, telefono]
    nombres_campos = [
        "email",
        "contraseña",
        "nombre de usuario",
        "nombre",
        "apellido",
        "nacimiento",
        "teléfono",
    ]
    for valor, nombre_campo in zip(campos, nombres_campos):
        if not valor:
            return render_template(
                "auth/registro.html", error=f"El campo '{nombre_campo}' es obligatorio."
            )

    # Validar contraseña
    if not re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", contraseña):
        return render_template(
            "auth/registro.html",
            error="La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.",
        )

    try:
        payload = {
            "Email": email,
            "Contraseña": contraseña,
            "Usuario": nombre_usuario,
            "Nombre": nombre,
            "Apellido": apellido,
            "FechaNacimiento": nacimiento,
            "Telefono": telefono,
        }

        response = requests.post(
            "http://localhost:3000/api/usuarios/registro", json=payload
        )

        if response.status_code == 201:
            # Guardar en session si querés mostrar algo en el login
            session["usuario_creado"] = True
            return redirect("/login")
        elif response.status_code == 409:
            return render_template("auth/registro.html", error="Email ya registrado.")
        else:
            return render_template(
                "auth/registro.html", error="Registro fallido. Verificá los datos."
            )

    except Exception:
        return render_template(
            "auth/registro.html", error="Error en el servidor. Intentalo más tarde."
        )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/cambiarcontra", methods=["GET", "POST"])
def cambiarcontra():
    if request.method == "GET":
        return render_template("auth/cambiar_contra.html")

    # Obtener datos
    email = request.form.get("email")
    nueva_contraseña = request.form.get("nueva_contraseña")
    nueva_contraseña2 = request.form.get("nueva_contraseña2")

    # Validaciones
    if not email or not nueva_contraseña or not nueva_contraseña2:
        return render_template(
            "auth/cambiar_contra.html", error="Todos los campos son obligatorios."
        )

    if nueva_contraseña != nueva_contraseña2:
        return render_template(
            "auth/cambiar_contra.html", error="Las contraseñas no coinciden."
        )

    if not re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", nueva_contraseña):
        return render_template(
            "auth/cambiar_contra.html",
            error="La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.",
        )

    try:
        payload = {
            "Email": email,
            "Contraseña": nueva_contraseña,
        }

        response = requests.post(
            "http://localhost:3000/api/usuarios/cambiar-contra", json=payload
        )

        if response.status_code == 200:
            session["contraseña_cambiada"] = True
            return redirect("/login")
        else:
            try:
                error_msg = response.json().get("error", "Error desconocido")
            except:
                error_msg = "Error en el servidor. Intentalo más tarde."
            return render_template("auth/cambiar_contra.html", error=error_msg)

    except Exception as e:
        return render_template(
            "auth/cambiar_contra.html",
            error="Error en el servidor. Intentalo más tarde.",
        )


if __name__ == "__main__":
    app.run("localhost", port=3000, debug=True)
