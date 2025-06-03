from flask import Blueprint, jsonify, request
from db.db import get_connection
from util.log import devolver_error
from util.util import *

usuarios_bp = Blueprint("usuarios",__name__)


@usuarios_bp.route("/")
def get_usuarios():
    conn = None
    cursor = None
    params = request.args

    try:
        conn= get_connection()
        cursor= conn.cursor(dictionary=True)
        
        if len(params) == 0:
            cursor.execute("SELECT * FROM usuarios")
            usuarios= cursor.fetchall()
            return jsonify(usuarios)
        
        clauses = []
        values = []
        for key in params: 
            clauses.append(f"{key} = %s")
            values.append(params[key])
        
        cursor.execute(f"SELECT * FROM usuarios WHERE {' AND '.join(clauses)}", tuple(values))
        usuarios = cursor.fetchmany()
        if len(usuarios) == 1: 
            return jsonify(usuarios[0])
        return jsonify(usuarios)
    except Exception as ex:  
        return devolver_error(ruta='usuarios', ex=ex)
    finally:
        if cursor:
            cursor.close()
        if conn: 
            conn.close()



@usuarios_bp.route("/<int:id>")
def get_usuario(id):
    try: 
        conn= get_connection()
        cursor= conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario= cursor.fetchone()
        if usuario:
            return jsonify(usuario)
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as ex: 
        return devolver_error(ruta=f"usuarios/{id}", ex=ex)
    finally:
        cursor.close()
        conn.close()
# ─────────────────────────────────────────────────────────────────────────────
# Tabla: USUARIOS
# ─────────────────────────────────────────────────────────────────────────────
# ID_usuario INT PRIMARY KEY AUTO_INCREMENT,
# Nombre VARCHAR(50),
# Apellido VARCHAR(50),
# Email VARCHAR(100),
# Telefono INT,
# FechaNacimiento DATE,
# Usuario VARCHAR(50),
# Contrasenia VARCHAR(100),
# ID_rol INT,
# FOREIGN KEY (ID_rol) REFERENCES roles(ID_rol)
# ─────────────────────────────────────────────────────────────────────────────
KEYS = {'Nombre': str, 'Apellido': str, 'Email': str, 'FechaNacimiento': str, 'Usuario': str, 'Contrasenia': str, 'ID_rol': int, 'Telefono': int}
@usuarios_bp.route("/", methods=["POST"])
def post_usuario():
    body = request.get_json()
    missing = [r for r in KEYS if r not in body]
    if len(missing) > 0:
        return jsonify({'error': 'bad request', 'missing': missing}), 400
    badtype = [r for r in KEYS if not isinstance(body.get(r), KEYS[r])]
    if len(badtype) > 0:
        return jsonify({'error': 'bad request', 'type error': badtype})
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE Email = %s", (body.get('Email'),))
        if cursor.fetchone():
            return jsonify({
                'error': 'El email ya esta registrado'
            }), 409

        cursor.execute(
            """
            INSERT INTO usuarios (Nombre,Apellido,Email,FechaNacimiento,Usuario,Contrasenia,ID_rol,Telefono)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                body.get('Nombre'),
                body.get('Apellido'),
                body.get('Email'),
                obtener_fecha(body.get('FechaNacimiento')),
                body.get('Usuario'),
                encryptar_pwd(body.get('Contrasenia')),
                body.get('ID_rol'),
                body.get('Telefono')
                )
        )
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({
            'success': True,
            'id': new_id  
        }), 201
    except Exception as ex:
        return devolver_error(ruta="usuarios", metodo="POST", ex=ex)
    finally: 
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route('/<int:id>', methods=["PUT"])
def actualizar_usuario(id: int):
    body = request.get_json()
    