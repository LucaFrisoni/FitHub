from flask import Blueprint, jsonify, request, session
from db.db import get_connection
from util.log import devolver_error
from util.util import *

pago_bp = Blueprint("pago", __name__)

@pago_bp.route("/pago", methods=["POST"])
def procesar_pago():
    data = request.get_json()
    
    required = ["numero", "fecha", "cvv", "titular"]
    if not all(k in data for k in required):
        return jsonify({"error": "Datos incompletos"}), 400
    
    try:
        # Simulación de validación exitosa
        # Limpiar el carrito después del pago exitoso
        if 'carrito' in session:
            session['carrito'] = []
            session.modified = True
        
        return jsonify({
            "mensaje": "Pago procesado correctamente",
            "carrito_limpio": True
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500

@pago_bp.route("/limpiar-carrito", methods=["POST"])
def limpiar_carrito():
    """Endpoint adicional para limpiar carrito si es necesario"""
    try:
        if 'carrito' in session:
            session['carrito'] = []
            session.modified = True
        return jsonify({"mensaje": "Carrito limpiado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al limpiar carrito"}), 500