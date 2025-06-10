from flask import Blueprint, jsonify, request
from Back.db.db import get_connection
from Back.util.log import devolver_error
from Back.util.util import *

detallecompras_bp = Blueprint("detalle-compra", __name__)

@detallecompras_bp.route("/", methods=["GET"])
def get_detallecompra():
    conn = None
    cursor = None

    # OBSERVACION: Realmente podriamos abstraer esta forma de hacerlo y reemplazarlo en 
    # todos los endpoints y agregarle dos parametros: tabla y possible_queries a la funcion 
    # pero obviamente no hay tiempo para hacerlo

    args = request.args
    possible_queries = {
        'id': { 'rename': 'ID_Detalle', 'type': int } ,
        'producto': { 'rename': 'ID_Producto', 'type': int } ,
        'compra': { 'rename': 'ID_Compra', 'type': int },
        'cantidad': { 'type': int },
        'subtotal': { 'type': int }     
    }

    try: 
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        values = []
        query = "SELECT * FROM detallecompras"
        if len(args) > 0:
            invalid_names = []
            invalid_types = []
            conditions = []

            for req_query in args: 
                if req_query not in possible_queries:
                    invalid_names.append(req_query)
                    continue

                requirements = possible_queries[req_query]
                value = convert_value(args.get(req_query), requirements['type'])

                if value is None:
                    invalid_types.append(req_query)
                    continue
                actual_name = req_query
                if 'rename' in requirements: 
                    actual_name = requirements['rename']

                conditions.append(f"{actual_name} = %s")
                values.append(value)
            
            if len(invalid_names) > 0 or len(invalid_types) > 0:
                return jsonify({'error': 'datos mal ingresados', 'nombres_invalidos': invalid_names, 'valores_invalidos': invalid_types}), 400

            query += f" WHERE {" AND ".join(conditions)}"
        cursor.execute(query, values)
        return jsonify(cursor.fetchall())
    except Exception as e:
        return devolver_error(ruta="detallecompras", ex=e)
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()


@detallecompras_bp.route("/", methods=["POST"])
def post_detalle():
    body = request.get_json()
    required = {
        'ID_Producto': int,
        'ID_Compra': int,
        'Cantidad': int,
        'SubTotal': int
    }

    missing = [r for r in body if r not in required]
    if len(missing) > 0:
        return jsonify({'error': 'faltan datos', 'missing': missing}), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM productos WHERE ID_Producto = %s", (body['ID_Producto'],))
        if not cursor.fetchone():
            return jsonify({'error': 'No existe ningun producto con esa ID'}), 404

        cursor.execute("SELECT 1 FROM compras WHERE ID_Compra = %s", ( body['ID_Compra'], ))
        if not cursor.fetchone():
            return jsonify({'error': 'No existe ningun compra con esa ID'}), 404

        cursor.execute("INSERT INTO detallecompras(ID_Producto,ID_Compra,Cantidad,SubTotal) VALUES (%s,%s,%s,%s)", (
            body['ID_Producto'],
            body['ID_Compra'],
            body['Cantidad'],
            body['SubTotal']
        ))

        new_id = cursor.lastrowid
        conn.commit()

        return jsonify({'success': True, 'new_id': new_id}),201
    except Exception as e:
        return devolver_error("compras", "POST", e)
    finally:
        if conn:
            conn.close()
        if cursor: 
            cursor.close()