from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *

roles_bp = Blueprint("roles", __name__)

# aca las rutas


@roles_bp.route("/")
def get_roles():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        return jsonify(roles)
    except Exception as ex:
        return devolver_error(ruta="roles", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@roles_bp.route("/<int:id>")
def get_rol(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM roles WHERE ID_rol = %s", (id,))
        rol = cursor.fetchone()
        if rol:
            return jsonify(rol)
        else:
            return jsonify({"error": "Rol no encontrado"}), 404
    except Exception as ex:
        return devolver_error(ruta=f"roles/{id}", ex=ex)
    finally:
        cursor.close()
        conn.close()


@roles_bp.route("/", methods=["POST"])
def post_rol():
    body = request.get_json()

    required = {"tipo_rol": str}

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ID_rol FROM roles WHERE tipo_rol = %s", (body["tipo_rol"],)
        )
        if cursor.fetchone():
            return jsonify({"error": "El rol ya existe"}), 409

        cursor.execute(
            """
            INSERT INTO roles (tipo_rol)
            VALUES (%s)
            """,
            (body["tipo_rol"],),
        )

        new_id = cursor.lastrowid
        conn.commit()

        return jsonify({"success": True, "id": new_id}), 201

    except Exception as ex:
        return devolver_error(ruta="roles", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



