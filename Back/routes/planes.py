from flask import Blueprint, jsonifym request
from db import get_connection

planes_bp = Blueprint("planes",__name__)

//aca las rutas

@planes_bp.route("/")
def get_planes():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Planes")
    planes= cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(planes)