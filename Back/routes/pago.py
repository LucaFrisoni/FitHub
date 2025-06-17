from flask import Blueprint, jsonify, request, session
from db.db import get_connection
from util.log import devolver_error
from util.util import *

pago_bp = Blueprint("pago", __name__)


@pago_bp.route("/pago", methods=["POST"])
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

        conn.commit()

        # Vaciar carrito
        if "carrito" in session:
            session["carrito"] = []
            session.modified = True

        return (
            jsonify(
                {"mensaje": "Pago procesado correctamente", "carrito_limpio": True}
            ),
            200,
        )

    except Exception as e:
        print(f"Error al procesar compra: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        cursor.close()
        conn.close()


@pago_bp.route("/limpiar-carrito", methods=["POST"])
def limpiar_carrito():
    """Endpoint adicional para limpiar carrito si es necesario"""
    try:
        if "carrito" in session:
            session["carrito"] = []
            session.modified = True
        return jsonify({"mensaje": "Carrito limpiado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al limpiar carrito"}), 500
