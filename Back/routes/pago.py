from flask import Blueprint, jsonify, request, session
from db.db import get_connection
from util.log import devolver_error
from util.util import *

pago_bp = Blueprint("pago", __name__)

@pago_bp.route("/", methods=["POST"])
def procesar_pago():
    data = request.get_json()

    required = ["numero", "fecha", "cvv", "titular", "productos", "user_id"]
    if not all(k in data for k in required):
        return jsonify({"error": "Datos incompletos"}), 400

    productos = data["productos"]
    user_id = data["user_id"]

    if not productos:
        return jsonify({"error": "No se enviaron productos"}), 400
    if not user_id:
        return jsonify({"error": "No se envio el userId"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stock_invalido = []
        # Primero verificar que todos los productos estan en stock.
        # ya se, double loop, que se le va a hacer, sql es asi
        for item in productos:
            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad", 1)

            cursor.execute("SELECT Nombre,Cantidad from productos WHERE ID_Producto = %s LIMIT 1", (producto_id,))
            datos = cursor.fetchone()
            stock_producto = datos[1]
            if cantidad > stock_producto:
                stock_invalido.append(datos[0])

        if len(stock_invalido) > 0:
            return jsonify({
                "error": f"Los siguientes productos no tienen el suficiente stock: {", ".join(stock_invalido)}"
            }), 400
        fecha_actual = date.today()
        for item in productos:
            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad", 1)
            total = item.get("subtotal")

            if not producto_id:
                continue  # Producto inválido
            cursor.execute(
                """
                INSERT INTO compras (ID_Usuario, ID_Producto, FechaCompra, Total, Cantidad)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, producto_id, fecha_actual, total, cantidad),
            )
            nueva_cantidad = stock_producto - cantidad
            cursor.execute(
                """
                UPDATE productos SET Cantidad = %s WHERE ID_Producto = %s
                """, (nueva_cantidad, producto_id))

        conn.commit()

        return (
            jsonify(
                { "mensaje": "Pago procesado correctamente" }
            ),
            200,
        )

    except Exception as e:
        print(f"Error al procesar compra: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        cursor.close()
        conn.close()