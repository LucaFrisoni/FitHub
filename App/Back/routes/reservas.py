from flask import Blueprint, jsonify, request
from Back.db.db import get_connection

reservas_bp = Blueprint("reservas", __name__)

# aca las rutas


@reservas_bp.route("/")
def get_reservas():
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Reservas")
        reservas = cursor.fetchall()
        return jsonify(reservas)
    except Exception as ex:
        return devolver_error(ruta="reservas", ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
