import calendar
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

    # Validación de fecha de tarjeta
    try:
        fecha_actual = date.today()
        mes_str, año_str = data["fecha"].split("/")
        mes = int(mes_str)
        año = int("20" + año_str) if len(año_str) == 2 else int(año_str)
        ultimo_dia = calendar.monthrange(año, mes)[1]
        fecha_expiracion = date(año, mes, ultimo_dia)

        if fecha_expiracion < fecha_actual:
            return jsonify({"error": "La tarjeta está vencida"}), 400
    except:
        return jsonify({"error": "Formato de fecha inválido (usar MM/AA)"}), 400

    productos = data["productos"]
    user_id = data["user_id"]

    if not productos:
        return jsonify({"error": "No se enviaron productos"}), 400
    if not user_id:
        return jsonify({"error": "No se envió el user_id"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        stock_invalido = []

        for item in productos:
            # Si es un producto
            if item.get("producto_id"):
                producto_id = item.get("producto_id")
                cantidad = item.get("cantidad", 1)
                total = item.get("subtotal")

                cursor.execute(
                    "SELECT Nombre, Cantidad FROM productos WHERE ID_Producto = %s LIMIT 1",
                    (producto_id,),
                )
                datos = cursor.fetchone()
                if not datos:
                    stock_invalido.append(f"ID {producto_id} (no existe)")
                    continue

                nombre, stock_producto = datos
                if cantidad > stock_producto:
                    stock_invalido.append(nombre)
                    continue

                cursor.execute(
                    """
                    INSERT INTO compras (ID_Usuario, ID_Producto, FechaCompra, Total, Cantidad)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, producto_id, fecha_actual, total, cantidad),
                )

                cursor.execute(
                    """
                    UPDATE productos SET Cantidad = %s WHERE ID_Producto = %s
                    """,
                    (stock_producto - cantidad, producto_id),
                )
            elif item.get("plan_id"):
                plan_id = item.get("plan_id")
                cursor.execute(
                    """
                    INSERT INTO alquileresplan (ID_Plan, ID_Usuario, Nota)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        plan_id,
                        user_id,
                        f"Compra online del {fecha_actual.strftime('%d/%m/%Y')}",
                    ),
                )

        if stock_invalido:
            return (
                jsonify(
                    {
                        "error": f"Los siguientes productos no tienen el suficiente stock o no existen: {', '.join(stock_invalido)}"
                    }
                ),
                400,
            )

        conn.commit()
        return jsonify({"mensaje": "Pago procesado correctamente"}), 200

    except Exception as e:
        print(f"Error al procesar compra: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass
