from flask import Blueprint, jsonify, request
from Back.db.db import get_connection
from Back.util.log import devolver_error
from Back.util.util import *

planes_bp = Blueprint("planes", __name__)

@planes_bp.route("/")
def get_planes():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM planes")
        planes_db = cursor.fetchall()
        
        planes = []
        for plan_db in planes_db:
            plan = {
                "id": plan_db['ID_Plan'],
                "nombre": plan_db['nombre'],
                "dias_elegidos": 3,  
                "imagen": plan_db['imagen'],
                "precio_dias": {
                    3: plan_db['precio_3_dias'], 
                    5: plan_db['precio_5_dias']
                }
            }
            
            if plan_db['deportes_disponibles']:
                deportes_list = plan_db['deportes_disponibles'].split(',')
                deportes_list = [deporte.strip() for deporte in deportes_list]  
                plan["deportes"] = deportes_list
            else:
                plan["deportes"] = []
            
            planes.append(plan)
        
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
        plan_db = cursor.fetchone()
        
        if plan_db:
            plan = {
                "id": plan_db['ID_Plan'],
                "nombre": plan_db['nombre'],
                "dias_elegidos": 3,  
                "imagen": plan_db['imagen'],
                "precio_dias": {
                    3: plan_db['precio_3_dias'], 
                    5: plan_db['precio_5_dias']
                }
            }
            
            if plan_db['deportes_disponibles']:
                deportes_list = plan_db['deportes_disponibles'].split(',')
                deportes_list = [deporte.strip() for deporte in deportes_list]  
                plan["deportes"] = deportes_list
            else:
                plan["deportes"] = []
                
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

    required = {
        "nombre": str, 
        "imagen": str, 
        "precio_3_dias": int, 
        "precio_5_dias": int, 
        "deportes_disponibles": str
    }

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    if body["precio_3_dias"] < 0 or body["precio_5_dias"] < 0:
        return jsonify({"error": "Los precios deben ser positivos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID_Plan FROM planes WHERE nombre = %s", (body["nombre"],)
        )
        if cursor.fetchone():
            return jsonify({"error": "El nombre del plan ya existe"}), 409

        cursor.execute(
            """
            INSERT INTO planes (nombre, imagen, precio_3_dias, precio_5_dias, deportes_disponibles)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (body["nombre"], body["imagen"], 
             body["precio_3_dias"], body["precio_5_dias"], body["deportes_disponibles"]),
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
    
    required = {
        "nombre": str, 
        "imagen": str, 
        "precio_3_dias": int, 
        "precio_5_dias": int, 
        "deportes_disponibles": str
    }

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    if body["precio_3_dias"] < 0 or body["precio_5_dias"] < 0:
        return jsonify({"error": "Los precios deben ser positivos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Plan no encontrado"}), 404
            
        cursor.execute(
            "SELECT 1 FROM planes WHERE nombre = %s AND ID_Plan != %s",
            (body["nombre"], id),
        )
        if cursor.fetchone():
            return jsonify({"error": "El nombre del plan ya existe en otro plan"}), 409

        set_clauses = []
        params = []
        for field in required:
            set_clauses.append(f"{field} = %s")
            params.append(body[field])
        params.append(id)
        
        query = f"UPDATE planes SET {', '.join(set_clauses)} WHERE ID_Plan = %s"
        cursor.execute(query, params)
        conn.commit()

        return jsonify({"success": True, "message": "Plan actualizado correctamente"})

    except Exception as ex:
        return devolver_error(ruta=f"planes/{id}", metodo="PUT", ex=ex)
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

        return jsonify({"success": True, "message": "Plan eliminado correctamente"})

    except Exception as ex:
        return devolver_error(ruta=f"planes/{id}", metodo="DELETE", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()