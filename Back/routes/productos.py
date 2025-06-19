import os
import uuid
from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *
from werkzeug.utils import secure_filename

productos_bp = Blueprint("productos", __name__)

# aca las rutas


# Un diccionario para facilitar las keys de las queries
@productos_bp.route("/")
def get_productos():
    conn = None
    cursor = None
    args = request.args

    possible_queries = {
        'id': { 'rename': 'ID_Producto', 'type': int },
        'nombre': { 'type': str },
        'descripcion': { 'type': str },
        'codigo': { 'type': str },
        'cantidad': { 'type': int },
        'precio': { 'type': int },
        'categoria': { 'type': str }
    }

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM productos"
        values = []

        if len(args) > 0: 
            nombre_invalid = []
            type_invalid = []
            conditions = []
            
            for req_query in args:

                if req_query == 'orderBy':
                    continue
                if req_query not in possible_queries:
                    nombre_invalid.append(req_query)
                    continue

                requirements = possible_queries[req_query]
                actual_name = req_query
                if 'rename' in requirements:
                    actual_name = requirements['rename']

                conditions.append(f"{actual_name} = %s")
                values.append(args.get(req_query))

            if len(type_invalid) > 0 or len(nombre_invalid) > 0:
                return jsonify({'error': 'datos mal ingresados', 'nombres_invalidos': nombre_invalid, 'valor_erroneo': type_invalid}),400
            
            query += f" WHERE {" AND ".join(conditions)}"

        print(f"args: {len(args)} query: {query}")

        cursor.execute(query, values)
        productos = cursor.fetchall()
        productos =[ producto for producto in productos if producto['Oculto'] == 0 ]

        return jsonify(productos)
    except Exception as ex:
        return devolver_error(ruta="productos", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@productos_bp.route("/<int:id>")
def get_producto(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE ID_Producto = %s", (id,))
        producto = cursor.fetchone()
        if producto:
            return jsonify(producto)
        else:
            return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as ex:
        return devolver_error(ruta=f"productos/{id}", ex=ex)
    finally:
        cursor.close()
        conn.close()


@productos_bp.route("/", methods=["POST"])
def post_producto():
    body = request.get_json()

    required = {
        "Nombre": str,
        "Descripcion": str,
        "Codigo": str,
        "Cantidad": int,
        "Precio": int,
        "Categoria": str,
        "Imagen": str  
    }

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    if body["Cantidad"] < 0 or body["Precio"] < 0:
        return jsonify({"error": "Cantidad y Precio deben ser positivos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ID_Producto FROM productos WHERE Codigo = %s", (body["Codigo"],)
        )
        if cursor.fetchone():
            return jsonify({"error": "El código ya existe"}), 409

        cursor.execute(
            """
            INSERT INTO productos (Nombre, Categoria, Descripcion, Codigo, Imagen, Cantidad, Precio)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                body["Nombre"],
                body["Categoria"],
                body["Descripcion"],
                body["Codigo"],
                body["Imagen"],
                body["Cantidad"],
                body["Precio"]
            ),
        )

        new_id = cursor.lastrowid
        conn.commit()

        return jsonify({"success": True, "id": new_id}), 201

    except Exception as ex:
        return devolver_error(ruta="productos", metodo="POST", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@productos_bp.route("/<int:id>", methods=["PUT"])
def put_producto(id):
    body = request.get_json()

    if not body:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

    required = {
        "Nombre": str,
        "Descripcion": str,
        "Codigo": str,
        "Cantidad": int,
        "Precio": int,
        "Categoria": str,
        "Imagen": str
    }

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({"error": "Campos faltantes", "missing": missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({"error": "Tipos incorrectos", "campos": badtype}), 400

    if body["Cantidad"] < 0:
        return jsonify({"error": "Cantidad debe ser positiva"}), 400
    if body["Precio"] < 0:
        return jsonify({"error": "Precio debe ser positivo"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM productos WHERE ID_producto = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Producto no encontrado"}), 404

        cursor.execute(
            "SELECT 1 FROM productos WHERE Codigo = %s AND ID_producto != %s",
            (body["Codigo"], id),
        )
        if cursor.fetchone():
            return jsonify({"error": "El código ya existe en otro producto"}), 409

        cursor.execute(
            """
            UPDATE productos
            SET Nombre = %s, Categoria = %s, Descripcion = %s, Codigo = %s, 
                Imagen = %s, Cantidad = %s, Precio = %s
            WHERE ID_producto = %s
            """,
            (
                body["Nombre"],
                body["Categoria"],
                body["Descripcion"],
                body["Codigo"],
                body["Imagen"],
                body["Cantidad"],
                body["Precio"],
                id
            )
        )
        
        conn.commit()

        if cursor.rowcount == 0:
            return (
                jsonify({"success": True, "message": "No se realizaron cambios"}),
                200,
            )

        return jsonify({"success": True}), 200

    except Exception as ex:
        return devolver_error(ruta="productos", metodo="PUT", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@productos_bp.route("/<int:id>", methods=["DELETE"])
def delete_producto(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Imagen FROM productos WHERE ID_Producto = %s", (id,))
        producto = cursor.fetchone()
        
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        
        cursor.execute("UPDATE productos SET Oculto = 1 WHERE ID_Producto = %s", (id,))
        conn.commit()
        
        return jsonify({"success": True, "message": "Producto eliminado exitosamente"}), 200

        # imagen_filename = producto[0] if producto[0] else None

        # cursor.execute("DELETE FROM productos WHERE ID_Producto = %s", (id,))
        # conn.commit()

        # if cursor.rowcount == 0:
        #     return jsonify({"error": "No se pudo eliminar el producto"}), 500

        # if imagen_filename:
        #     try:
        #         upload_dir = "../Front/static/images/uploads/productos"
        #         imagen_path = os.path.join(upload_dir, imagen_filename)
                
        #         if os.path.exists(imagen_path):
        #             os.remove(imagen_path)
        #             print(f"Imagen eliminada: {imagen_path}")
        #         else:
        #             print(f"La imagen no existe en el path: {imagen_path}")
                    
        #     except Exception as img_ex:
        #         print(f"Error al eliminar imagen: {str(img_ex)}")

        # return jsonify({"success": True, "message": "Producto eliminado exitosamente"}), 200

    except Exception as ex:
        return devolver_error(ruta="productos", metodo="DELETE", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg"}

@productos_bp.route("/subir-imagen", methods=["POST"])
def subir_imagen_producto():
    """
    Endpoint para subir imágenes de productos
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
        filename = f"producto_{uuid.uuid4().hex}.{extension}"
        
        # Crear directorio si no existe - RUTA DEL FRONTEND
        upload_dir = "../Front/static/images/uploads/productos"  # Ruta relativa al backend
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)

        # Guardar la imagen
        foto.save(filepath)

        # Retornar respuesta exitosa con el nombre del archivo
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "Imagen subida exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error del servidor al subir imagen: {str(e)}"
        }), 500