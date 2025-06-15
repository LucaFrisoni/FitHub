from flask import Response, jsonify

def logear_error(ruta: str, metodo: str = "GET", ex: Exception = None):
    print(f"""
        -------------------------------------------
        ERROR: Ruta /{ruta} [Metodo: {metodo}]
        -------------------------------------------
        {str(ex)}
        -------------------------------------------
        """
    )

def devolver_error(ruta: str, metodo: str = "GET", ex: Exception = None) -> Response: 
    logear_error(ruta=ruta,metodo=metodo,ex=ex)
    return jsonify({'error': 'internal error'}), 500