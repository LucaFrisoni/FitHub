from flask import Blueprint, jsonify, request
from Back.db.db import get_connection
from Back.util.log import devolver_error
from Back.util.util import *

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
            queries = []
            conditions = ""
            
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

                queries.append(f"{actual_name} = %s")
                values.append(args.get(req_query))

            if len(type_invalid) > 0 or len(nombre_invalid) > 0:
                return jsonify({'error': 'datos mal ingresados', 'nombres_invalidos': nombre_invalid, 'valor_erroneo': type_invalid}),400
            
            conditions += " AND ".join(queries)
            query += f" WHERE {conditions}"

        cursor.execute(query, values)
        productos = cursor.fetchall()

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
            INSERT INTO productos (Nombre, Descripcion, Codigo, Cantidad, Precio)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                body["Nombre"],
                body["Descripcion"],
                body["Codigo"],
                body["Cantidad"],
                body["Precio"],
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

        cursor.execute("SELECT 1 FROM productos WHERE ID_producto = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Producto no encontrado"}), 404

        cursor.execute("DELETE FROM productos WHERE ID_producto = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "No se pudo eliminar el producto"}), 500

        return jsonify({"success": True}), 200

    except Exception as ex:
        return devolver_error(ruta="productos", metodo="DELETE", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
