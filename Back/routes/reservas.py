from flask import Blueprint, jsonifym request
from db import get_connection

reservas_bp = Blueprint("reservas",__name__)

//aca las rutas

@reservas_bp.route("/")
def get_reservas():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reservas")
    reservas= cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(reservas)