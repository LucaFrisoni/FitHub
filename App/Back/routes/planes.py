from flask import Blueprint, jsonify, request
from Back.db.db import get_connection
from Back.util.log import devolver_error
from Back.util.util import *

planes_bp = Blueprint("planes", __name__)

# aca las rutas


@planes_bp.route("/")
def get_planes():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM planes")
        planes = cursor.fetchall()
        return jsonify(planes)
    except Exception as ex:
        return devolver_error(ruta="planes", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@planes_bp.route("/<int:id>")
def get_plan(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM planes WHERE ID_Plan = %s", (id,))
        plan = cursor.fetchone()
        if plan:
            return jsonify(plan)
        else:
            return jsonify({"error": "Plan no encontrado"}), 404
    except Exception as ex:
        return devolver_error(ruta=f"planes/{id}", ex=ex)
    finally:
        cursor.close()
        conn.close()


@planes_bp.route("/", methods=["POST"])
def post_plan():
    body = request.get_json()

    required = {"Precio": int, "Descripcion": str, "DuracionPlan": str}

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    if body["Precio"] < 0:
        return jsonify({"error": "Precio debe ser positivo"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ID_Plan FROM planes WHERE Descripcion = %s", (body["Descripcion"],)
        )
        if cursor.fetchone():
            return jsonify({"error": "La descripcion ya existe"}), 409

        cursor.execute(
            """
            INSERT INTO planes (Precio, Descripcion, DuracionPlan)
            VALUES (%s, %s, %s)
            """,
            (body["Precio"], body["Descripcion"], body["DuracionPlan"]),
        )

        new_id = cursor.lastrowid
        conn.commit()

        return jsonify({"success": True, "id": new_id}), 201

    except Exception as ex:
        return devolver_error(ruta="planes", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@planes_bp.route("/<int:id>", methods=["PUT"])
def put_plan(id):
    body = request.get_json()

    if not body:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

    required = {"Precio": int, "Descripcion": str, "DuracionPlan": str}

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    if body["Precio"] < 0:
        return jsonify({"error": "Precio debe ser positivo"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Plan no encontrado"}), 404

        cursor.execute(
            "SELECT 1 FROM planes WHERE Descripcion = %s AND ID_Plan != %s",
            (body["Descripcion"], id),
        )
        if cursor.fetchone():
            return jsonify({"error": "La descripcion ya existe en otro plan"}), 409

        set_clauses = []
        params = []
        for field in required:
            set_clauses.append(f"{field} = %s")
            params.append(body[field])
        params.append(id)

        query = f"""
            UPDATE planes
            SET {', '.join(set_clauses)}
            WHERE ID_Plan = %s
        """

        cursor.execute(query, params)
        conn.commit()

        if cursor.rowcount == 0:
            return (
                jsonify({"success": True, "message": "No se realizaron cambios"}),
                200,
            )

        return jsonify({"success": True}), 200

    except Exception as ex:
        return devolver_error(ruta="planes", metodo="PUT", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@planes_bp.route("/<int:id>", methods=["DELETE"])
def delete_plan(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Plan no encontrado"}), 404

        cursor.execute("DELETE FROM planes WHERE ID_Plan = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "No se pudo eliminar el plan"}), 500

        return jsonify({"success": True}), 200

    except Exception as ex:
        return devolver_error(ruta="planes", metodo="DELETE", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
