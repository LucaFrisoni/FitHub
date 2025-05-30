from flask import Blueprint, jsonify, request
from db.db import get_connection

usuarios_bp = Blueprint("usuarios",__name__)

#aca las rutas

@usuarios_bp.route("/")
def get_usuarios():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuarios")
    usuarios= cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(usuarios)