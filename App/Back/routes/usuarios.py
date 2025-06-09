from flask import Blueprint, jsonify, request
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
# Contrasenia VARCHAR(100),
# ID_rol INT,
# FOREIGN KEY (ID_rol) REFERENCES roles(ID_rol)
# ─────────────────────────────────────────────────────────────────────────────


@usuarios_bp.route("/", methods=["POST"])
def post_usuario():
    body = request.get_json()
    required = {
        "Nombre": str,
        "Apellido": str,
        "Email": str,
        "FechaNacimiento": str,
        "Usuario": str,
        "Contrasena": str,
        "Telefono": int,
    }
    missing = [r for r in required if r not in body]
    if len(missing) > 0:
        return jsonify({"error": "bad request", "missing": missing}), 400
    badtype = [r for r in required if not isinstance(body.get(r), required[r])]
    if len(badtype) > 0:
        return jsonify({"error": "bad request", "type error": badtype})
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (Nombre,Apellido,Email,FechaNacimiento,Usuario,Contrasenia,ID_rol,Telefono)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                body.get("Nombre"),
                body.get("Apellido"),
                body.get("Email"),
                obtener_fecha(body.get("FechaNacimiento")),
                body.get("Usuario"),
                encryptar_pwd(body.get("Contrasena")),
                2,
                body.get("Telefono"),
            ),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as ex:
        return devolver_error(ruta="usuarios", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
