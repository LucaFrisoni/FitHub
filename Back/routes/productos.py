from flask import Blueprint, jsonifym request
from db import get_connection

productos_bp = Blueprint("productos",__name__)

//aca las rutas

@productos_bp.route("/")
def get_productos():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Productos")
    productos= cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(productos)