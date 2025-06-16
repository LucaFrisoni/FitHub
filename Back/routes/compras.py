from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *

compras_bp = Blueprint("compras", __name__)


@compras_bp.route("/", methods=["GET"])
def get_compras():
    conn = None
    cursor = None

    args = request.args
    possible_queries = {
        "id": {"rename": "ID_Compra", "type": int},
        "nrocompra": {"rename": "NroCompra", "type": int},
        "usuario": {"rename": "Id_Usuario", "type": int},
        "fecha": {"rename": "FechaCompra", "type": datetime},
        "total": {"type": int},
    }

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        values = []

        query = "SELECT * FROM compras"
        if len(args) > 0:
            invalid_names = []
            invalid_types = []
            conditions = []

            for req_query in args:
                if req_query not in possible_queries:
                    invalid_names.append(req_query)
                    continue

                requirements = possible_queries[req_query]
                value = convert_value(args.get(req_query), requirements["type"])

                if value is None:
                    invalid_types.append(req_query)
                    continue
                actual_name = req_query
                if "rename" in requirements:
                    actual_name = requirements["rename"]

                conditions.append(f"{actual_name} = %s")
                values.append(value)

            if len(invalid_names) > 0 or len(invalid_types) > 0:
                return (
                    jsonify(
                        {
                            "error": "datos mal ingresados",
                            "nombres_invalidos": invalid_names,
                            "valores_invalidos": invalid_types,
                        }
                    ),
                    400,
                )

            query += f" WHERE {" AND ".join(conditions)}"
        cursor.execute(query, values)
        return jsonify(cursor.fetchall())
    except Exception as e:
        return devolver_error(ruta="compras", ex=e)
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()


@compras_bp.route("/<int:id>", methods=["GET"])
def get_by_id(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM compras WHERE ID_Compra = %s", (id,))
        compras = cursor.fetchall()

        if len(compras) == 0:
            return jsonify({"error": "Compra no encontrada"}), 404

        return jsonify(compras[0])
    except Exception as e:
        return devolver_error(ruta=f"compras/{id}", ex=e)
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()


@compras_bp.route("/usuario/<int:id>", methods=["GET"])
def get_by_usuario(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT 
                c.ID_Compra,
                c.FechaCompra,
                c.Total,
                c.Cantidad,
                c.ID_Producto,
                p.Nombre AS NombreProducto,
                p.Imagen AS ImagenProducto,
                c.ID_Usuario
            FROM compras c
            JOIN productos p ON c.ID_Producto = p.ID_Producto
            WHERE c.ID_Usuario = %s
        """,
            (id,),
        )

        compras = cursor.fetchall()
        # Formatear FechaCompra a dd/mm/aaaa
        for compra in compras:
            if "FechaCompra" in compra and compra["FechaCompra"]:
                compra["FechaCompra"] = formatear_fecha_ddmmaaaa(compra["FechaCompra"])

        return jsonify(compras), 200

    except Exception as e:
        return devolver_error(ruta=f"compras/usuario/{id}", ex=e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@compras_bp.route("/", methods=["POST"])
def post_compra():
    body = request.get_json()
    required = {"ID_Usuario": int, "FechaCompra": str, "Total": int}

    missing = [r for r in body if r not in required]
    if len(missing) > 0:
        return jsonify({"error": "faltan datos", "missing": missing}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM usuarios WHERE ID_Usuario = %s", (body["ID_Usuario"],)
        )
        if not cursor.fetchone():
            return jsonify({"error": "No existe ningun usuario con esa ID"}), 404

        cursor.execute(
            "INSERT INTO compras(ID_Usuario,FechaCompra,Total) VALUES (%s,%s,%s)",
            (body["ID_Usuario"], body["FechaCompra"], body["Total"]),
        )

        new_id = cursor.lastrowid
        conn.commit()

        return jsonify({"success": True, "new_id": new_id}), 201
    except Exception as e:
        return devolver_error("compras", "POST", e)
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()


@compras_bp.route("/<int:id>", methods=["DELETE"])
def delete_compra(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT 1 FROM compras WHERE ID_Compra = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Compra no encontrada"}), 404

        cursor.execute("DELETE FROM compras WHERE ID_Compra = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "No se pudo eliminar la compra"}), 500

        conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        return devolver_error(ruta=f"compras/{id}", metodo="DELETE", ex=e)
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()
