from flask import Blueprint, jsonify, request
from Back.models.user import User
from Back.db.db import get_connection
from Back.util.log import devolver_error
from Back.util.util import *


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
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        if usuario:
            return jsonify(usuario)
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


@usuarios_bp.route("/registro", methods=["POST"])
def post_usuario():
    body = request.get_json()
    print("Body recibido:", body)
    required = {
        "Email": str,
        "Contrasena": str,
        "Usuario": str,
        "Nombre": str,
        "Apellido": str,
        "FechaNacimiento": str,
        "Usuario": str,
        "Contrasenia": str,
        "Telefono": str,
    }

    missing = [r for r in required if r not in body]
    if missing:
        print("Campos faltantes:", missing)
        return jsonify({"error": "bad request", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body.get(r), required[r])]
    if badtype:
        return jsonify({"error": "bad request", "type error": badtype}), 400

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

    if not email:
        return jsonify({"error": "Email no proporcionado"}), 400
    if not nueva_contra:
        return jsonify({"error": "Contraseña no proporcionada"}), 400

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
