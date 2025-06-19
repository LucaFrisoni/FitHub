from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *

horarios_bp = Blueprint("horariosentrenamiento", __name__)


@horarios_bp.route("/")
def get_horarios():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM horariosentrenamiento")
        horarios = cursor.fetchall()
        return jsonify(horarios)
    except Exception as ex:
        return devolver_error(ruta="horarios", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@horarios_bp.route("/usuario/<int:id_usuario>")
def get_horarios_usuario(id_usuario):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT 1 FROM usuarios WHERE ID_usuario = %s", (id_usuario,))
        if not cursor.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404

        cursor.execute(
            """
            SELECT horariosentrenamiento.*, planes.Nombre AS Nombre_plan
            FROM horariosentrenamiento
            INNER JOIN planes ON horariosentrenamiento.ID_Plan = planes.ID_Plan
            WHERE horariosentrenamiento.ID_Usuario = %s
            ORDER BY horariosentrenamiento.ID_HorarioEntrenamiento DESC
            """,
            (id_usuario,),
        )
        horarios = cursor.fetchall()
        # Formatear FechaReserva a dd/mm/aaaa
        # for compra in compras:
        #     if "FechaCompra" in compra and compra["FechaCompra"]:
        #         compra["FechaCompra"] = formatear_fecha_ddmmaaaa(compra["FechaCompra"])
        return jsonify(horarios), 200
    except Exception as ex:
        return devolver_error(ruta=f"horarios/usuario/{id_usuario}", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@horarios_bp.route("/", methods=["POST"])
def post_horario():
    body = request.get_json()
    required = {"Dias": str, "Horario": str, "ID_Plan": int, "ID_Usuario": int}

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (body["ID_Plan"],))
        if not cursor.fetchone():
            return jsonify({"error": "Plan no encontrado"}), 404

        cursor.execute(
            "SELECT 1 FROM usuarios WHERE ID_usuario = %s", (body["ID_Usuario"],)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404

        cursor.execute(
            """
            INSERT INTO horariosentrenamiento 
            (Dias, Horario, ID_Plan, ID_Usuario)
            VALUES (%s, %s, %s, %s)
            """,
            (body["Dias"], body["Horario"], body["ID_Plan"], body["ID_Usuario"]),
        )
        new_id = cursor.lastrowid
        conn.commit()
        return jsonify({"success": True, "id": new_id}), 201

    except Exception as ex:
        return devolver_error(ruta="horarios", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@horarios_bp.route("/<int:id_horario>", methods=["PUT"])
def put_horario(id_horario):
    body = request.get_json()
    if not body:
        return jsonify({"error": "Sin datos para actualizar"}), 400

    allowed_fields = {"Dias": str, "Horario": str, "ID_Plan": int}
    updates = {}

    for field, field_type in allowed_fields.items():
        if field in body:
            if not isinstance(body[field], field_type):
                return jsonify({"error": f"Tipo incorrecto para {field}"}), 400
            updates[field] = body[field]

    if not updates:
        return jsonify({"error": "No hay campos válidos para actualizar"}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM horariosentrenamiento WHERE ID_HorarioEntrenamiento = %s",
            (id_horario,),
        )
        if not cursor.fetchone():
            return jsonify({"error": "Horario no encontrado"}), 404

        if "ID_Plan" in updates:
            cursor.execute(
                "SELECT 1 FROM planes WHERE ID_Plan = %s", (updates["ID_Plan"],)
            )
            if not cursor.fetchone():
                return jsonify({"error": "Plan no encontrado"}), 404

        set_clause = ", ".join([f"{field} = %s" for field in updates.keys()])
        values = list(updates.values())
        values.append(id_horario)

        query = f"""
            UPDATE horariosentrenamiento
            SET {set_clause}
            WHERE ID_HorarioEntrenamiento = %s
        """

        cursor.execute(query, values)
        conn.commit()

        return jsonify({"success": True}), 200

    except Exception as ex:
        return devolver_error(ruta=f"horarios/{id_horario}", metodo="PUT", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@horarios_bp.route("/<int:id_horario>", methods=["DELETE"])
def delete_horario(id_horario):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM horariosentrenamiento WHERE ID_HorarioEntrenamiento = %s",
            (id_horario,),
        )
        if not cursor.fetchone():
            return jsonify({"error": "Horario no encontrado"}), 404

        cursor.execute(
            "DELETE FROM horariosentrenamiento WHERE ID_HorarioEntrenamiento = %s",
            (id_horario,),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "No se pudo eliminar el horario"}), 500

        return jsonify({"success": True}), 200

    except Exception as ex:
        return devolver_error(ruta=f"horarios/{id_horario}", metodo="DELETE", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

