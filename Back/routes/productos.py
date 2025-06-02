from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *
import uuid
productos_bp = Blueprint("productos",__name__)

#aca las rutas

@productos_bp.route("/")
def get_productos():
    conn = None
    cursor = None

    try:
        conn= get_connection()
        cursor= conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos= cursor.fetchall()
        return jsonify(productos)
    except Exception as ex:  
        return devolver_error(ruta='productos', ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn: 
            conn.close()

@productos_bp.route("/<int:id>")
def get_producto(id):
    try: 
        conn= get_connection()
        cursor= conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        producto= cursor.fetchone()
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
    
    required = {'Nombre': str, 'Descripcion': str, 'Codigo': str, 'Cantidad': int, 'Precio': int}

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({'error': 'Campos faltantes', 'missing': missing}), 400
    
    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({'error': 'Tipos incorrectos', 'campos': badtype}), 400
    
    if body['Cantidad'] < 0 or body['Precio'] < 0:
        return jsonify({'error': 'Cantidad y Precio deben ser positivos'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM productos WHERE Codigo = %s", (body['Codigo'],))
        if cursor.fetchone():
            return jsonify({'error': 'El código ya existe'}), 409
        
        cursor.execute(
            """
            INSERT INTO productos (Nombre, Descripcion, Codigo, Cantidad, Precio)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id  # Obtener el ID generado
            """, (
                body['Nombre'],
                body['Descripcion'],
                body['Codigo'],
                body['Cantidad'],
                body['Precio']
            )
        )
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'success': True,
            'id': new_id  
        }), 201
        
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
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400

    required = {'Nombre': str,'Descripcion': str,'Codigo': str,'Cantidad': int,'Precio': int}

    missing = [r for r in required if r not in body]
    if missing:
        return jsonify({'error': 'Campos faltantes', 'missing': missing}), 400

    badtype = [r for r in required if not isinstance(body[r], required[r])]
    if badtype:
        return jsonify({'error': 'Tipos incorrectos', 'campos': badtype}), 400

    if body['Cantidad'] < 0:
        return jsonify({'error': 'Cantidad debe ser positiva'}), 400
    if body['Precio'] < 0:
        return jsonify({'error': 'Precio debe ser positivo'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM productos WHERE ID_producto = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        cursor.execute(
            "SELECT 1 FROM productos WHERE Codigo = %s AND ID_producto != %s",
            (body['Codigo'], id)
        )
        if cursor.fetchone():
            return jsonify({'error': 'El código ya existe en otro producto'}), 409
        
        set_clauses = []
        params = []
        for field in required:
            set_clauses.append(f"{field} = %s")
            params.append(body[field])
        params.append(id) 
        
        query = f"""
            UPDATE productos
            SET {', '.join(set_clauses)}
            WHERE ID_producto = %s
        """
        
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'success': True, 'message': 'No se realizaron cambios'}), 200
        
        return jsonify({'success': True}), 200
        
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
        
        cursor.execute("SELECT 1 FROM productos WHERE ID_producto = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        cursor.execute("DELETE FROM productos WHERE ID_producto = %s", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'No se pudo eliminar el producto'}), 500
        
        return jsonify({'success': True}), 200
        
    except Exception as ex:
        return devolver_error(ruta="productos", metodo="DELETE", ex=ex)
    finally: 
        if cursor:
            cursor.close()
        if conn:
            conn.close()