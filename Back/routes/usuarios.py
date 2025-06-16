import os
import re
from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *
from werkzeug.utils import secure_filename

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/")
def get_usuarios():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        return jsonify(usuarios)
    except Exception as ex:
        return devolver_error(ruta="usuarios", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@usuarios_bp.route("/<int:id>")
def get_usuario(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE ID_Usuario = %s", (id,))
        usuario = cursor.fetchone()

        if usuario:
            if "FechaNacimiento" in usuario:
                usuario["FechaNacimiento"] = formatear_fecha_ddmmaaaa(
                    usuario["FechaNacimiento"]
                )
            return jsonify({"usuario": usuario})
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as ex:
        return devolver_error(ruta=f"usuarios/{id}", ex=ex)
    finally:
        cursor.close()
        conn.close()


@usuarios_bp.route("/editar-usuario", methods=["PUT"])
def editar_usuario():
    data = request.get_json()

    email = data.get("Email")
    if not email:
        return jsonify({"error": "Email requerido para identificar al usuario"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar si el usuario existe
        cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 400

        # Construir campos a actualizar dinámicamente
        campos_validos = [
            "Nombre",
            "Apellido",
            "Usuario",
            "Telefono",
            "FechaNacimiento",
        ]
        updates = []
        valores = []

        for campo in campos_validos:
            if campo in data and data[campo] != usuario.get(campo):
                updates.append(f"{campo} = %s")
                valores.append(data[campo])

        valores.append(email)  # para el WHERE

        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE Email = %s"
        cursor.execute(query, valores)
        conn.commit()
        # Traer el usuario actualizado
        cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
        usuario_actualizado = cursor.fetchone()

        return (
            jsonify(
                {
                    "message": "Usuario actualizado exitosamente",
                    "usuario": usuario_actualizado,
                }
            ),
            200,
        )

    except Exception as ex:
        return jsonify({"error": f"Error al actualizar usuario: {str(ex)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg"}


@usuarios_bp.route("/editar-foto", methods=["PUT"])
def editar_foto():
    user_id = request.form.get("Id")
    email = request.form.get("Email")
    nueva_imagen = request.files.get("foto")

    if not user_id:
        return jsonify({"error": "Falta el id del usuario"}), 400
    if not email:
        return jsonify({"error": "Falta el email"}), 400
    if not nueva_imagen:
        return jsonify({"error": "No se adjuntó ninguna imagen"}), 400
    if nueva_imagen.filename == "":
        return jsonify({"error": "No seleccionaste ninguna imagen."}), 400

    extension = nueva_imagen.filename.rsplit(".", 1)[1].lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        return jsonify({"error": "Formato no permitido."}), 400

    filename = secure_filename(f"user_{user_id}.{extension}")
    filepath = os.path.join("static/images/uploads/perfil", filename)
    nueva_imagen.save(filepath)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Actualizar imagen
        query = "UPDATE usuarios SET Imagen = %s WHERE Email = %s"
        cursor.execute(query, (filename, email))
        conn.commit()
        # Obtener usuario actualizado
        cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"usuario": usuario}), 200

    except Exception as ex:
        print("Excepcion")
        return jsonify(
            {"error": f"Error del servidor al cambiar la foto usuario: {str(ex)}"}
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Tabla: USUARIOS
# ─────────────────────────────────────────────────────────────────────────────
# ID_usuario INT PRIMARY KEY AUTO_INCREMENT,
# Nombre VARCHAR(50),
# Apellido VARCHAR(50),
# Email VARCHAR(100),
# Telefono INT,
# FechaNacimiento DATE,
# Usuario VARCHAR(50),
# imagen VARCHAR(100),
# Contrasenia VARCHAR(100),
# ID_rol INT,
# FOREIGN KEY (ID_rol) REFERENCES roles(ID_rol)
# ─────────────────────────────────────────────────────────────────────────────


# --------------------------------------------Auth--------------------------------------------


@usuarios_bp.route("/login", methods=["POST"])
def verificacion_login():
    body = request.get_json()

    email = body.get("Email")
    contraseña = body.get("Contraseña")

    if not email:
        return jsonify({"error": "Falta el email"}), 400
    if not email or not contraseña:
        return jsonify({"error": "Falta la contraseña"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if not check_pwd(contraseña, user["Contrasenia"]):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        return jsonify({"usuario": user}), 200

    except Exception as ex:
        return devolver_error(ruta="usuarios/login", metodo="POST", ex=ex)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@usuarios_bp.route("/registro", methods=["POST"])
def post_usuario():
    body = request.get_json()
    required = {
        "Email": str,
        "Usuario": str,
        "Nombre": str,
        "Apellido": str,
        "FechaNacimiento": str,
        "Contrasenia": str,
        "Telefono": str,
    }

    missing = [r for r in required if r not in body]
    if missing:
        return (
            jsonify(
                {
                    "error": f"El campo '{missing}' es obligatorio.",
                }
            ),
            400,
        )

    badtype = [r for r in required if not isinstance(body.get(r), required[r])]
    if badtype:
        return jsonify({"error": f"El campo '{badtype}' tiene un error de tipo."}), 400

    # Validar contraseña
    if not re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", body.get("Contrasenia")):
        return (
            jsonify(
                {
                    "error": "La contraseña debe tener al menos 8 caracteres, una mayúscula y un número."
                }
            ),
            400,
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verifica si el email ya está registrado
        cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (body["Email"],))
        if cursor.fetchone():
            return jsonify({"error": "Email ya registrado"}), 409

        cursor.execute(
            """
            INSERT INTO usuarios (Nombre, Apellido, Email, FechaNacimiento, Usuario, Contrasenia, ID_rol, Telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                body.get("Nombre"),
                body.get("Apellido"),
                body.get("Email"),
                obtener_fecha(body.get("FechaNacimiento")),
                body.get("Usuario"),
                encryptar_pwd(body.get("Contrasenia")),
                2,
                body.get("Telefono"),
            ),
        )
        conn.commit()
        return jsonify({"success": True}), 201

    except Exception as ex:
        return devolver_error(ruta="usuarios", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@usuarios_bp.route("/cambiar-contra", methods=["POST"])
def change_password():
    body = request.get_json()

    email = body.get("Email")
    nueva_contra = body.get("Contraseña")
    nueva_contra2 = body.get("Contraseña2")

    if not email:
        return jsonify({"error": "Email no proporcionado"}), 400
    if not nueva_contra:
        return jsonify({"error": "Contraseña no proporcionada"}), 400

    if nueva_contra != nueva_contra2:
        return jsonify({"error": "Las contraseñas no coinciden"}), 400

    if not re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", nueva_contra):
        return (
            jsonify(
                {
                    "error": "La contraseña debe tener al menos 8 caracteres, una mayúscula y un número."
                }
            ),
            400,
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el email existe
        cursor.execute("SELECT 1 FROM usuarios WHERE Email = %s", (email,))
        if cursor.fetchone() is None:
            return jsonify({"error": "El email no existe"}), 404

        # Actualizar la contraseña
        cursor.execute(
            "UPDATE usuarios SET Contrasenia = %s WHERE Email = %s",
            (encryptar_pwd(nueva_contra), email),
        )
        conn.commit()

        return jsonify({"success": True, "message": "Contraseña actualizada"}), 200

    except Exception as ex:
        return devolver_error(ruta="usuario/cambiar-contra", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
