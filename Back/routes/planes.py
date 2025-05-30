from flask import Blueprint, jsonify, request
from db.db import get_connection

planes_bp = Blueprint("planes",__name__)

#aca las rutas

@planes_bp.route("/")
def get_planes():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Planes")
    planes= cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(planes)