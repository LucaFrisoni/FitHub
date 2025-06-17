from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *
import os
import uuid


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
                "nombre": plan_db['Nombre'],
                "dias_elegidos": 3,  
                "imagen": plan_db['Imagen'],
                "precio_dias": {
                    3: plan_db['Precio_3_dias'], 
                    5: plan_db['Precio_5_dias']
                }
            }
            
            if plan_db['Deportes_disponibles']:
                deportes_list = plan_db['Deportes_disponibles'].split(',')
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
                "nombre": plan_db['Nombre'],
                "dias_elegidos": 3,  
                "imagen": plan_db['Imagen'],
                "precio_dias": {
                    3: plan_db['Precio_3_dias'], 
                    5: plan_db['Precio_5_dias']
                }
            }
            
            if plan_db['Deportes_disponibles']:
                deportes_list = plan_db['Deportes_disponibles'].split(',')
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
    # Detectar si es JSON o formulario
    if request.is_json:
        # Manejo de JSON (para API)
        body = request.get_json()
        
        # Campos obligatorios
        required = {
            "nombre": str, 
            "precio_3_dias": int, 
            "precio_5_dias": int
        }

        # Campos opcionales
        optional = {
            "imagen": str,
            "deportes_disponibles": str
        }

        # Validar campos obligatorios
        missing = [r for r in required if r not in body]
        if missing:
            return jsonify({"error": "Campos obligatorios faltantes", "missing": missing}), 400

        # Validar tipos de campos obligatorios
        badtype = [r for r in required if not isinstance(body[r], required[r])]
        if badtype:
            return jsonify({"error": "Tipos incorrectos en campos obligatorios", "campos": badtype}), 400

        # Validar tipos de campos opcionales (solo si están presentes)
        for field, expected_type in optional.items():
            if field in body and body[field] is not None and not isinstance(body[field], expected_type):
                return jsonify({"error": f"Tipo incorrecto para campo opcional '{field}'"}), 400

        if body["precio_3_dias"] < 0 or body["precio_5_dias"] < 0:
            return jsonify({"error": "Los precios deben ser positivos"}), 400

        # Obtener valores con defaults para campos opcionales
        imagen = body.get("imagen", None)
        deportes_disponibles = body.get("deportes_disponibles", None)
        nombre = body["nombre"]
        precio_3_dias = body["precio_3_dias"]
        precio_5_dias = body["precio_5_dias"]
        
    else:
        # Manejo de formulario HTML
        nombre = request.form.get("nombre", "").strip()
        precio_3_dias_str = request.form.get("precio_3_dias", "").strip()
        precio_5_dias_str = request.form.get("precio_5_dias", "").strip()
        imagen = request.form.get("imagen", "").strip()
        deportes_disponibles = request.form.get("deportes_disponibles", "").strip()
        
        # Validaciones básicas
        if not nombre:
            return jsonify({"error": "El nombre es requerido"}), 400
            
        if not precio_3_dias_str or not precio_5_dias_str:
            return jsonify({"error": "Los precios son requeridos"}), 400
        
        # Convertir precios a enteros
        try:
            precio_3_dias = int(precio_3_dias_str)
            precio_5_dias = int(precio_5_dias_str)
        except ValueError:
            return jsonify({"error": "Los precios deben ser números válidos"}), 400
        
        if precio_3_dias < 0 or precio_5_dias < 0:
            return jsonify({"error": "Los precios deben ser positivos"}), 400
        
        # Manejar campos opcionales
        if not imagen:
            imagen = None
        if not deportes_disponibles:
            deportes_disponibles = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID_Plan FROM planes WHERE Nombre = %s", (nombre,)
        )
        if cursor.fetchone():
            return jsonify({"error": "El nombre del plan ya existe"}), 409

        cursor.execute(
            """
            INSERT INTO planes (Nombre, Imagen, Precio_3_dias, Precio_5_dias, Deportes_disponibles)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nombre, imagen, precio_3_dias, precio_5_dias, deportes_disponibles),
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
    
    # Campos obligatorios
    required = {
        "Nombre": str,  # Usando nombres de columnas SQL como en el payload
        "Precio_3_dias": int, 
        "Precio_5_dias": int
    }

    # Campos opcionales
    optional = {
        "Imagen": str,
        "Deportes_disponibles": str
    }

    # Validar campos obligatorios
    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos obligatorios faltantes", "missing": missing}), 400

    # Validar tipos de campos obligatorios
    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos en campos obligatorios", "campos": badtype}), 400

    # Validar tipos de campos opcionales (solo si están presentes)
    for field, expected_type in optional.items():
        if field in body and body[field] is not None and not isinstance(body[field], expected_type):
            return jsonify({"error": f"Tipo incorrecto para campo opcional '{field}'"}), 400

    if body["Precio_3_dias"] < 0 or body["Precio_5_dias"] < 0:
        return jsonify({"error": "Los precios deben ser positivos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM planes WHERE ID_Plan = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Plan no encontrado"}), 404
            
        cursor.execute(
            "SELECT 1 FROM planes WHERE Nombre = %s AND ID_Plan != %s",
            (body["Nombre"], id),
        )
        if cursor.fetchone():
            return jsonify({"error": "El nombre del plan ya existe en otro plan"}), 409

        # Construir query dinámicamente solo con campos presentes
        set_clauses = []
        params = []
        
        # Mapear los campos disponibles
        all_fields = {**required, **optional}
        
        for field in all_fields:
            if field in body:
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

        cursor.execute("SELECT Imagen FROM planes WHERE ID_Plan = %s", (id,))
        plan = cursor.fetchone()
        
        if not plan:
            return jsonify({"error": "Plan no encontrado"}), 404

        # Obtener el nombre de la imagen (si existe)
        imagen_filename = plan[0] if plan[0] else None

        cursor.execute("DELETE FROM planes WHERE ID_Plan = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "No se pudo eliminar el plan"}), 500

        if imagen_filename:
            try:
                upload_dir = "../Front/static/images/uploads/planes"
                imagen_path = os.path.join(upload_dir, imagen_filename)
                
                if os.path.exists(imagen_path):
                    os.remove(imagen_path)
                    print(f"Imagen de plan eliminada: {imagen_path}")
                else:
                    print(f"La imagen del plan no existe en el path: {imagen_path}")
                    
            except Exception as img_ex:
                print(f"Error al eliminar imagen del plan: {str(img_ex)}")

        return jsonify({"success": True, "message": "Plan eliminado correctamente"}), 200

    except Exception as ex:
        return devolver_error(ruta=f"planes/{id}", metodo="DELETE", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg"}

@planes_bp.route("/subir-imagen", methods=["POST"])
def subir_imagen_plan():
    """
    Endpoint para subir imágenes de planes
    """
    try:
        # Verificar que se envió un archivo
        if "foto" not in request.files:
            return jsonify({"success": False, "error": "No se seleccionó ningún archivo"}), 400

        foto = request.files["foto"]

        if foto.filename == "":
            return jsonify({"success": False, "error": "El nombre del archivo está vacío"}), 400

        # Verificar extensión del archivo
        if "." not in foto.filename:
            return jsonify({"success": False, "error": "Archivo sin extensión válida"}), 400

        extension = foto.filename.rsplit(".", 1)[1].lower()

        if extension not in EXTENSIONES_PERMITIDAS:
            return jsonify({
                "success": False, 
                "error": f"Formato no permitido. Formatos aceptados: {', '.join(EXTENSIONES_PERMITIDAS)}"
            }), 400

        # Generar nombre único para el archivo
        filename = f"plan_{uuid.uuid4().hex}.{extension}"
        
        # Crear directorio si no existe - RUTA DEL FRONTEND
        upload_dir = "../Front/static/images/uploads/planes"  # Ruta relativa al backend
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)

        # Guardar la imagen
        foto.save(filepath)

        # Retornar respuesta exitosa con el nombre del archivo
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "Imagen de plan subida exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error del servidor al subir imagen: {str(e)}"
        }), 500