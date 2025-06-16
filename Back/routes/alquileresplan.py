from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *

alquileres_plan_bp = Blueprint("alquileres_plan", __name__)

@alquileres_plan_bp.route("/")
def get_alquileres_plan():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ap.ID_AlquilerPlan, ap.ID_Plan, ap.ID_Usuario, ap.Nota,
                   u.Nombre AS Usuario_Nombre, u.Apellido AS Usuario_Apellido
            FROM alquileresplan ap
            JOIN planes p ON ap.ID_Plan = p.ID_Plan
            JOIN usuarios u ON ap.ID_Usuario = u.ID_Usuario
        """)
        alquileres = cursor.fetchall()
        return jsonify(alquileres)
    except Exception as ex:
        return devolver_error(ruta='alquileres_plan', ex=ex)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@alquileres_plan_bp.route("/<int:id>")
def get_alquiler_plan(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ap.ID_AlquilerPlan, ap.ID_Plan, ap.ID_Usuario, ap.Nota,
                   p.Descripcion AS Plan_Descripcion, p.Precio, p.DuracionPlan,
                   u.Nombre AS Usuario_Nombre, u.Apellido AS Usuario_Apellido
            FROM alquileresplan ap
            JOIN planes p ON ap.ID_Plan = p.ID_Plan
            JOIN usuarios u ON ap.ID_Usuario = u.ID_Usuario
            WHERE ap.ID_AlquilerPlan = %s
        """, (id,))
        alquiler = cursor.fetchone()
        if alquiler:
            return jsonify(alquiler)
        else:
            return jsonify({"error": "Alquiler no encontrado"}), 404
    except Exception as ex:
        return devolver_error(ruta=f'alquileres_plan/{id}', ex=ex)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@alquileres_plan_bp.route("/usuario/<int:id_usuario>")
def get_alquileres_por_usuario(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT 1 FROM usuarios WHERE ID_usuario = %s", (id_usuario,))
        if not cursor.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        cursor.execute("""
            SELECT ap.ID_AlquilerPlan, ap.ID_Plan, ap.ID_Usuario, ap.Nota,
                   p.Descripcion AS Plan_Descripcion, p.Precio, p.DuracionPlan,
                   u.Nombre AS Usuario_Nombre, u.Apellido AS Usuario_Apellido
            FROM alquileresplan ap
            JOIN planes p ON ap.ID_Plan = p.ID_Plan
            JOIN usuarios u ON ap.ID_Usuario = u.ID_Usuario
            WHERE ap.ID_Usuario = %s
        """, (id_usuario,))
        
        alquileres = cursor.fetchall()
        if alquileres:
            return jsonify(alquileres)
        else:
            return jsonify({"message": "El usuario no tiene alquileres registrados"}), 200
    except Exception as ex:
        return devolver_error(ruta=f'alquileres_plan/usuario/{id_usuario}', ex=ex)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@alquileres_plan_bp.route("/", methods=["POST"])
def post_alquiler_plan():
    body = request.get_json()
    
    required = {'ID_Plan': int, 'ID_Usuario': int}
    optional = {'Nota': str}
    
    missing = [field for field in required if field not in body]
    if missing:
        return jsonify({'error': 'Campos faltantes', 'missing': missing}), 400

    bad_types = []
    for field, t in required.items():
        if not isinstance(body.get(field), t):
            bad_types.append(field)
    for field, t in optional.items():
        if field in body and not isinstance(body.get(field), t):
            bad_types.append(field)
    
    if bad_types:
        return jsonify({'error': 'Tipos incorrectos', 'campos': bad_types}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (body['ID_Plan'],))
        if not cursor.fetchone():
            return jsonify({'error': 'Plan no encontrado'}), 404

        cursor.execute("SELECT 1 FROM usuarios WHERE ID_Usuario = %s", (body['ID_Usuario'],))
        if not cursor.fetchone():
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        cursor.execute("""
            INSERT INTO alquileresplan (ID_Plan, ID_Usuario, Nota)
            VALUES (%s, %s, %s)
        """, (
            body['ID_Plan'],
            body['ID_Usuario'],
            body.get('Nota', None)
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        return jsonify({'success': True, 'id': new_id}), 201
        
    except Exception as ex:
        return devolver_error(ruta="alquileres_plan", metodo="POST", ex=ex)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@alquileres_plan_bp.route("/<int:id>", methods=["PUT"])
def put_alquiler_plan(id):
    body = request.get_json()
    
    if not body:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    allowed_fields = {'ID_Plan': int, 'ID_Usuario': int, 'Nota': str}
    update_fields = {k: v for k, v in body.items() if k in allowed_fields}
    
    if not update_fields:
        return jsonify({'error': 'Ningún campo válido para actualizar'}), 400

    bad_types = []
    for field, value in update_fields.items():
        if not isinstance(value, allowed_fields[field]):
            bad_types.append(field)
    if bad_types:
        return jsonify({'error': 'Tipos incorrectos', 'campos': bad_types}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM alquileresplan WHERE ID_AlquilerPlan = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Alquiler no encontrado'}), 404

        if 'ID_Plan' in update_fields:
            cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (update_fields['ID_Plan'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Plan no encontrado'}), 404

        if 'ID_Usuario' in update_fields:
            cursor.execute("SELECT 1 FROM usuarios WHERE ID_Usuario = %s", (update_fields['ID_Usuario'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Usuario no encontrado'}), 404
        
        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        values = list(update_fields.values())
        values.append(id)
        
        query = f"""
            UPDATE alquileresplan
            SET {set_clause}
            WHERE ID_AlquilerPlan = %s
        """
        
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'success': True}), 200
        
    except Exception as ex:
        return devolver_error(ruta="alquileres_plan", metodo="PUT", ex=ex)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@alquileres_plan_bp.route("/<int:id>", methods=["DELETE"])
def delete_alquiler_plan(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM alquileresplan WHERE ID_AlquilerPlan = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Registro no encontrado'}), 404
        
        cursor.execute("DELETE FROM alquileresplan WHERE ID_AlquilerPlan = %s", (id,))
        conn.commit()
        return jsonify({'success': True}), 200
        
    except Exception as ex:
        return devolver_error(ruta="alquileres_plan", metodo="DELETE", ex=ex)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()