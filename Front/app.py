# -*- coding: utf-8 -*-
import os
import uuid
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash,
    jsonify,
)
from functools import wraps
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from models.user import User
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Definimos en el .env el host de la api
API_HOST = os.getenv("API_HOST")

# ------------------Upload Foto------------------
UPLOAD_FOLDER_PROFILE = "static/images/uploads/perfil"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER_PROFILE
UPLOAD_FOLDER_PRODUCTOS = "static/images/uploads/productos"
app.config["UPLOAD_FOLDER_PRODUCTOS"] = UPLOAD_FOLDER_PRODUCTOS
UPLOAD_FOLDER_PLANES = "static/images/uploads/planes"
app.config["UPLOAD_FOLDER_PLANES"] = UPLOAD_FOLDER_PLANES
# ------------------Init auth------------------
login_manager = LoginManager()
login_manager.init_app(app)  # Conectás Flask-Login con tu app
login_manager.login_view = (
    "login"  # la ruta donde te lleva si no esta logeado en una ruta proteguida
)


@login_manager.user_loader
def load_user(user_id):
    try:
        response = requests.get(f"{API_HOST}/api/usuarios/{user_id}")
        if response.status_code == 200:
            data = response.json()
            usuario = data.get("usuario")
            return User(
                usuario["ID_usuario"],
                usuario["Nombre"],
                usuario["Apellido"],
                usuario["Email"],
                usuario["Telefono"],
                usuario["FechaNacimiento"],
                usuario["Usuario"],
                usuario.get("Imagen"),
                usuario["ID_rol"],
            )
    except Exception as e:
        print(f"Error cargando usuario desde API: {e}")
    return None


# -------------------------------------Rutas-----------------------------------
@app.route("/")
def home():
    # si existe la session toast_exitoso, la devuelve y luego la borra, sino usa False
    toast_exitoso = session.pop("toast_exitoso", False)
    return render_template("home.html", toast_exitoso=toast_exitoso, user=current_user)


@app.errorhandler(404)
def pagina_error(error):
    return render_template("404.html", user=current_user), 404


@app.route("/planes", methods=["GET"])
def planes():
    try:
        respuesta = requests.get(f"{API_HOST}/api/planes/")
        if respuesta.status_code == 200:
            planes = respuesta.json()
            for plan in planes:
                if plan.get("imagen") is None:
                    plan["imagen"] = "default_plan.jpg"
        else:
            planes = []
    except Exception as e:
        print(f"error al conectar con el back: {e}")
        planes = []
    return render_template("planes.html", planes=planes, user=current_user)


@app.route("/procesar_reserva", methods=["POST"])
@login_required
def procesar_reserva():
    data = request.get_json()
    dias = data.get("dias", [])
    tipo_entrenamiento = data.get("tipo_entrenamiento")
    hora_inicio = data.get("hora_inicio")
    hora_fin = data.get("hora_fin")

    if not dias:
        return jsonify({"error": "Debe seleccionar al menos un día"}), 400
    if not tipo_entrenamiento:
        return jsonify({"error": "Debe seleccionar un tipo de entrenamiento"}), 400

    try:
        tipo_entrenamiento = int(tipo_entrenamiento)
    except ValueError:
        return jsonify({"error": "Tipo de entrenamiento inválido"}), 400

    try:
        url_alquileres = f"{API_HOST}/api/alquileres/verificacion_reserva"
        payload = {"user_id": current_user.id, "tipoEntrenamiento": tipo_entrenamiento}
        response_alquileres = requests.post(url_alquileres, json=payload)

        if response_alquileres.status_code != 200:
            error_msg = response_alquileres.json().get(
                "error", "Error en la verificación"
            )
            return jsonify({"error": error_msg}), 400

        horario_completo = f"{hora_inicio} - {hora_fin}"
        url_horarios = f"{API_HOST}/api/horariosentrenamiento/"

        reservas_creadas = []
        for dia in dias:
            payload_horario = {
                "Dias": dia,
                "Horario": horario_completo,
                "ID_Plan": tipo_entrenamiento,
                "ID_Usuario": current_user.id,
            }

            response_horario = requests.post(url_horarios, json=payload_horario)

            if response_horario.status_code == 201:
                reserva_id = response_horario.json().get("id")
                reservas_creadas.append({"dia": dia, "id": reserva_id})
            else:
                for reserva in reservas_creadas:
                    try:
                        requests.delete(f"{url_horarios}{reserva['id']}")
                    except:
                        pass

                error_msg = response_horario.json().get(
                    "error", "Error al crear el horario"
                )
                return (
                    jsonify(
                        {"error": f"Error al crear reserva para {dia}: {error_msg}"}
                    ),
                    400,
                )

        return (
            jsonify(
                {
                    "message": "Reservas realizadas con éxito",
                    "reservas": reservas_creadas,
                }
            ),
            200,
        )

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error de conexión con el servidor"}), 500
    except Exception as ex:
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/reservas")
@login_required
def reservas():
    toast_exitoso = session.pop("toast_exitoso", False)
    toast_error = session.pop("toast_error", False)
    planes = []
    contador_dias = {
        "lunes": 0,
        "martes": 0,
        "miercoles": 0,
        "jueves": 0,
        "viernes": 0,
        "sabado": 0,
        "domingo": 0,
    }

    # Diccionario para controlar límites por día
    dias_disponibles = {
        "lunes": True,
        "martes": True,
        "miercoles": True,
        "jueves": True,
        "viernes": True,
        "sabado": True,
        "domingo": True,
    }

    try:
        url_planes = f"{API_HOST}/api/planes/"
        response_planes = requests.get(url_planes)

        if response_planes.status_code == 200:
            planes_data = response_planes.json()
            planes = [
                {"id": plan["id"], "nombre": plan["nombre"]} for plan in planes_data
            ]
        else:
            print(f"Error al obtener planes: {response_planes.status_code}")

        url_horarios = f"{API_HOST}/api/horariosentrenamiento/"
        response_horarios = requests.get(url_horarios)

        if response_horarios.status_code == 200:
            horarios_data = response_horarios.json()

            for horario in horarios_data:
                dias_reserva = horario.get("Dias", "").lower()

                if "," in dias_reserva:
                    dias_lista = [dia.strip() for dia in dias_reserva.split(",")]
                    for dia in dias_lista:
                        if dia in contador_dias:
                            contador_dias[dia] += 1
                            # Verificar límite de 20
                            if contador_dias[dia] >= 20:
                                dias_disponibles[dia] = False
                else:
                    if dias_reserva in contador_dias:
                        contador_dias[dias_reserva] += 1
                        # Verificar límite de 20
                        if contador_dias[dias_reserva] >= 20:
                            dias_disponibles[dias_reserva] = False
        else:
            print(f"Error al obtener horarios: {response_horarios.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
    except Exception as ex:
        print(f"Error general: {ex}")

    return render_template(
        "reservas.html",
        user=current_user,
        toast_exitoso=toast_exitoso,
        error=toast_error,
        planes=planes,
        contador_dias=contador_dias,
        dias_disponibles=dias_disponibles,
    )


@app.route("/tienda", methods=["GET"])
def tienda():
    categorias_filtro = request.args.getlist("categorias")

    try:
        response = requests.get(f"{API_HOST}/api/productos/")
        if response.status_code == 200:
            productos_api = response.json()
            productos = []
            for p in productos_api:
                categoria = p.get("Categoria", "")
                if not categorias_filtro or categoria in categorias_filtro:
                    productos.append(
                        {
                            "id": p.get("ID_Producto"),
                            "imagen": p.get("Imagen", "default.png"),
                            "nombre": p.get("Nombre"),
                            "descripcion": p.get("Descripcion"),
                            "precio": p.get("Precio"),
                        }
                    )
        else:
            productos = []
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        productos = []

    return render_template("tienda.html", productos=productos, user=current_user)


@app.route("/producto/<int:id>")
def producto(id):
    try:
        response = requests.get(f"{API_HOST}/api/productos/{id}")
        if response.status_code == 200:
            producto = response.json()
            return render_template(
                "producto.html", producto=producto, user=current_user
            )
        else:
            return "Producto no encontrado", 404
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return "Error del servidor", 500


@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    if request.method == "GET":
        toast_exitoso = session.pop("toast_exitoso", False)
        compras = []  # <-- definila acá para que siempre exista

        try:
            # Cargamos las compras del user
            response = requests.get(f"{API_HOST}/api/compras/usuario/{current_user.id}")
            if response.status_code == 200:
                compras = response.json()
            # Cargamos las reservas del user
            response2 = requests.get(
                f"{API_HOST}/api/horariosentrenamiento/usuario/{current_user.id}"
            )
            if response2.status_code == 200:
                reservas = response2.json()
        except Exception as ex:
            # Podrías loguear el error acá si querés
            return render_template(
                "user.html", error="Error en el servidor. Intentalo más tarde."
            )
        finally:
            return render_template(
                "user.html",
                user=current_user,
                toast_exitoso=toast_exitoso,
                compras=compras,
                reservas=reservas,
            )

    # POST
    payload = {
        "Email": current_user.email,  # fijo, para identificar al usuario
        "Nombre": request.form.get("nombre"),
        "Apellido": request.form.get("apellido"),
        "Usuario": request.form.get("usuario"),
        "Telefono": request.form.get("telefono"),
        "FechaNacimiento": request.form.get("nacimiento"),
    }

    try:
        response = requests.put(f"{API_HOST}/api/usuarios/editar-usuario", json=payload)
        if response.status_code == 200:
            data = response.json()
            usuario = data["usuario"]

            nuevo_usuario = User(
                usuario["ID_usuario"],
                usuario["Nombre"],
                usuario["Apellido"],
                usuario["Email"],
                usuario["Telefono"],
                usuario["FechaNacimiento"],
                usuario["Usuario"],
                usuario.get("Imagen") or None,
                usuario["ID_rol"],
            )
            # Guardar en session si querés mostrar algo en el User
            session["toast_exitoso"] = "Usuario editado"
            login_user(nuevo_usuario)
            return redirect("/user")
        else:
            error_msg = response.json().get("error", "Error inesperado")
            return render_template("user.html", user=current_user, error=error_msg)
    except Exception as ex:
        return render_template(
            "user.html", error="Error en el servidor. Intentalo más tarde."
        )


@app.route("/subir-foto-perfil", methods=["POST"])
@login_required
def subir_foto_perfil():

    foto = request.files["foto"]
    if not foto:
        return render_template(
            "user.html", user=current_user, error="Falta adjuntar una imagen."
        )

    try:
        # Enviamos datos como form-data
        files = {"foto": (foto.filename, foto, foto.content_type)}
        data = {
            "Id": current_user.id,
            "Email": current_user.email,
        }

        response = requests.put(
            f"{API_HOST}/api/usuarios/editar-foto", data=data, files=files
        )

        if response.status_code == 200:
            data = response.json()
            usuario = data["usuario"]

            nuevo_usuario = User(
                usuario["ID_usuario"],
                usuario["Nombre"],
                usuario["Apellido"],
                usuario["Email"],
                usuario["Telefono"],
                usuario["FechaNacimiento"],
                usuario["Usuario"],
                usuario.get("Imagen"),
                usuario["ID_rol"],
            )

            login_user(nuevo_usuario)
            session["toast_exitoso"] = "Imagen de Perfil cambiada"
            return redirect("/user")
        else:
            error_msg = response.json().get("error", "Error inesperado")
            return render_template("user.html", user=current_user, error=error_msg)

    except Exception as ex:
        return render_template(
            "user.html", error="Error en el servidor. Intentalo más tarde."
        )


# ----------------------Rutas||Auth----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    toast_exitoso = session.pop("toast_exitoso", False)

    if request.method == "GET":
        return render_template("auth/login.html", toast_exitoso=toast_exitoso)

    email = request.form.get("email")
    contraseña = request.form.get("contraseña")

    try:
        # Llamada a la API
        payload = {"Email": email, "Contraseña": contraseña}
        response = requests.post(f"{API_HOST}/api/usuarios/login", json=payload)

        if response.status_code == 200:
            data = response.json()
            user = data["usuario"]

            usuario = User(
                user["ID_usuario"],
                user["Nombre"],
                user["Apellido"],
                user["Email"],
                user["Telefono"],
                user["FechaNacimiento"],
                user["Usuario"],
                user.get("Imagen") or None,
                user["ID_rol"],
            )

            login_user(usuario)
            session["toast_exitoso"] = "Login exitoso"
            return redirect("/")

        else:
            error = response.json().get("error", "Error desconocido")
            return render_template("auth/login.html", error=error)

    except Exception:
        return render_template(
            "auth/login.html", error="Error del servidor. Intentalo más tarde."
        )


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("auth/registro.html")

    # Obtener datos del formulario
    email = request.form.get("email")
    contraseña = request.form.get("contraseña")
    nombre_usuario = request.form.get("nombre_usuario")
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    nacimiento = request.form.get("nacimiento")
    telefono = request.form.get("telefono")

    try:
        payload = {
            "Email": email,
            "Contrasenia": contraseña,
            "Usuario": nombre_usuario,
            "Nombre": nombre,
            "Apellido": apellido,
            "FechaNacimiento": nacimiento,
            "Telefono": telefono,
        }

        response = requests.post(f"{API_HOST}/api/usuarios/registro", json=payload)

        if response.status_code == 201:
            # Guardar en session si querés mostrar algo en el login
            session["toast_exitoso"] = "Usuario creado"
            return redirect("/login")
        elif response.status_code == 409:
            return render_template("auth/registro.html", error="Email ya registrado.")
        else:
            error = response.json().get("error", "Error desconocido")
            return render_template("auth/registro.html", error=error)

    except Exception as ex:
        print("ERROR EN EL GET:", ex)
        return render_template(
            "auth/registro.html", error="Error en el servidor. Intentalo más tarde."
        )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/cambiarcontra", methods=["GET", "POST"])
def cambiarcontra():
    if request.method == "GET":
        return render_template("auth/cambiar_contra.html")

    # Obtener datos
    email = request.form.get("email")
    nueva_contraseña = request.form.get("nueva_contraseña")
    nueva_contraseña2 = request.form.get("nueva_contraseña2")

    try:
        payload = {
            "Email": email,
            "Contraseña": nueva_contraseña,
            "Contraseña2": nueva_contraseña2,
        }

        response = requests.post(
            f"{API_HOST}/api/usuarios/cambiar-contra", json=payload
        )

        if response.status_code == 200:
            session["toast_exitoso"] = "Contraseña cambiada"
            return redirect("/login")
        else:
            try:
                error_msg = response.json().get("error", "Error desconocido")
            except:
                error_msg = "Error en el servidor. Intentalo más tarde."
            return render_template("auth/cambiar_contra.html", error=error_msg)

    except Exception as e:
        return render_template(
            "auth/cambiar_contra.html",
            error="Error en el servidor. Intentalo más tarde.",
        )


# ----------------------Rutas||Admin----------------------
# Decorator para verificar si el usuario es admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id_rol != 1:
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/subir-imagen-producto", methods=["POST"])
@login_required  # Si querés que esté protegido
def subir_imagen_producto():
    try:
        # Verificar que se envió un archivo
        if "foto" not in request.files:
            return (
                jsonify({"success": False, "error": "No se seleccionó ningún archivo"}),
                400,
            )

        foto = request.files["foto"]

        if not foto or foto.filename == "":
            return (
                jsonify({"success": False, "error": "No se seleccionó ninguna imagen"}),
                400,
            )

        # Preparar los archivos para enviar a la API
        files = {"foto": (foto.filename, foto, foto.content_type)}

        # Hacer la petición a tu API
        response = requests.post(f"{API_HOST}/api/productos/subir-imagen", files=files)

        # Procesar la respuesta de la API
        if response.status_code == 200:
            data = response.json()

            # Si la API retornó éxito, también generar la URL completa para el frontend
            if data.get("success"):
                filename = data.get("filename")
                data["url"] = url_for(
                    "static", filename=f"images/uploads/productos/{filename}"
                )

            return jsonify(data), 200
        else:
            # Si hubo error en la API, retornar el error
            error_data = (
                response.json()
                if response.content
                else {"success": False, "error": "Error desconocido"}
            )
            return jsonify(error_data), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": "Error de conexión con la API"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    try:
        response = requests.get(f"{API_HOST}/api/productos/")
        if response.status_code == 200:
            productos = response.json()
            total_stock = sum(p.get("Cantidad", 0) for p in productos)
            total_valor = sum(
                float(p.get("Precio", 0)) * p.get("Cantidad", 0) for p in productos
            )
        else:
            productos = []
            total_stock = 0
            total_valor = 0
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        productos = []
        total_stock = 0
        total_valor = 0

    producto_editado = session.pop("producto_editado", False)
    producto_creado = session.pop("producto_creado", False)
    producto_eliminado = session.pop("producto_eliminado", False)

    return render_template(
        "admin/admin_panel.html",
        productos=productos,
        total_stock=total_stock,
        total_valor=total_valor,
        user=current_user,
        producto_editado=producto_editado,
        producto_creado=producto_creado,
        producto_eliminado=producto_eliminado,
    )


@app.route("/admin/producto/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def nuevo_producto():
    if request.method == "GET":
        return render_template("admin/nuevo_producto.html", user=current_user)

    # Obtener datos del formulario
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    codigo = request.form.get("codigo")
    cantidad = request.form.get("cantidad")
    precio = request.form.get("precio")
    categoria = request.form.get("categoria")
    imagen = request.form.get("imagen")

    # Validaciones básicas
    if not all(
        [nombre, descripcion, codigo, cantidad, precio, categoria, imagen]
    ):  # ← INCLUIR categoria
        return render_template(
            "admin/nuevo_producto.html",
            error="Todos los campos son obligatorios.",
            user=current_user,
        )

    try:
        payload = {
            "Nombre": nombre,
            "Descripcion": descripcion,
            "Codigo": codigo,
            "Cantidad": int(cantidad),
            "Precio": int(precio),
            "Categoria": categoria,
            "Imagen": imagen,
        }

        response = requests.post(f"{API_HOST}/api/productos/", json=payload)

        if response.status_code == 201:
            session["producto_creado"] = True
            return redirect("/admin")
        else:
            error_msg = response.json().get("error", "Error al crear producto")
            return render_template(
                "admin/nuevo_producto.html", error=error_msg, user=current_user
            )
    except Exception as e:
        return render_template(
            "admin/nuevo_producto.html",
            error="Error en el servidor. Inténtalo más tarde.",
            user=current_user,
        )


@app.route("/admin/producto/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_producto(id):
    if request.method == "GET":
        try:
            response = requests.get(f"{API_HOST}/api/productos/{id}")
            if response.status_code == 200:
                producto = response.json()
                return render_template(
                    "admin/editar_producto.html", producto=producto, user=current_user
                )
            else:
                return "Producto no encontrado", 404
        except Exception as e:
            return "Error del servidor", 500

    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    codigo = request.form.get("codigo")
    cantidad = request.form.get("cantidad")
    precio = request.form.get("precio")
    categoria = request.form.get("categoria")
    imagen = request.form.get("imagen")

    if not all([nombre, descripcion, codigo, cantidad, precio, categoria, imagen]):
        try:
            response = requests.get(f"{API_HOST}/api/productos/{id}")
            producto = response.json() if response.status_code == 200 else {}
            return render_template(
                "admin/editar_producto.html",
                producto=producto,
                error="Todos los campos son obligatorios.",
                user=current_user,
            )
        except:
            return "Error del servidor", 500

    try:
        payload = {
            "Nombre": nombre,
            "Descripcion": descripcion,
            "Codigo": codigo,
            "Cantidad": int(cantidad),
            "Precio": int(precio),
            "Categoria": categoria,
            "Imagen": imagen,
        }

        response = requests.put(f"{API_HOST}/api/productos/{id}", json=payload)

        if response.status_code == 200:
            session["producto_editado"] = True
            return redirect("/admin")
        else:
            error_msg = response.json().get("error", "Error al actualizar producto")
            # Obtener producto actual para mostrar en caso de error
            prod_response = requests.get(f"{API_HOST}/api/productos/{id}")
            producto = prod_response.json() if prod_response.status_code == 200 else {}
            return render_template(
                "admin/editar_producto.html",
                producto=producto,
                error=error_msg,
                user=current_user,
            )
    except Exception as e:
        return render_template(
            "admin/editar_producto.html",
            error="Error en el servidor. Inténtalo más tarde.",
            user=current_user,
        )


@app.route("/admin/producto/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_producto(id):
    try:
        response = requests.delete(f"{API_HOST}/api/productos/{id}")

        if response.status_code == 200:
            session["producto_eliminado"] = True

        return redirect("/admin")
    except Exception as e:
        return redirect("/admin")


@app.route("/subir-imagen-plan", methods=["POST"])
@login_required
def subir_imagen_plan():
    try:
        if "foto" not in request.files:
            return (
                jsonify({"success": False, "error": "No se seleccionó ningún archivo"}),
                400,
            )

        foto = request.files["foto"]

        if not foto or foto.filename == "":
            return (
                jsonify({"success": False, "error": "No se seleccionó ninguna imagen"}),
                400,
            )

        files = {"foto": (foto.filename, foto, foto.content_type)}

        response = requests.post(f"{API_HOST}/api/planes/subir-imagen", files=files)

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                filename = data.get("filename")
                data["url"] = url_for(
                    "static", filename=f"images/uploads/planes/{filename}"
                )

            return jsonify(data), 200
        else:
            error_data = (
                response.json()
                if response.content
                else {"success": False, "error": "Error desconocido"}
            )
            return jsonify(error_data), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": "Error de conexión con la API"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@app.route("/admin/planes")
@login_required
@admin_required
def admin_planes():
    try:
        response = requests.get(f"{API_HOST}/api/planes/")
        if response.status_code == 200:
            planes_api = response.json()
            planes = []

            for plan_api in planes_api:
                precio_dias = plan_api.get("precio_dias", {})

                plan = {
                    "ID_Plan": plan_api.get("id"),
                    "Nombre": plan_api.get("nombre"),
                    "Precio_3_dias": precio_dias.get("3", 0),
                    "Precio_5_dias": precio_dias.get("5", 0),
                    "Deportes_disponibles": ", ".join(plan_api.get("deportes", [])),
                    "Imagen": plan_api.get("imagen"),
                }

                if plan.get("Imagen"):
                    plan["imagen_url"] = url_for(
                        "static", filename=f'images/uploads/planes/{plan["Imagen"]}'
                    )
                else:
                    plan["imagen_url"] = url_for(
                        "static", filename="images/default_plan.jpg"
                    )

                planes.append(plan)

            promedio_3_dias = 0
            promedio_5_dias = 0
            if planes:
                total_3 = sum(plan["Precio_3_dias"] for plan in planes)
                total_5 = sum(plan["Precio_5_dias"] for plan in planes)
                promedio_3_dias = round(total_3 / len(planes), 2)
                promedio_5_dias = round(total_5 / len(planes), 2)

        else:
            print(f"Error al obtener planes de la API: {response.status_code}")
            planes = []
            promedio_3_dias = 0
            promedio_5_dias = 0
    except Exception as e:
        print(f"Error al obtener planes: {e}")
        planes = []
        promedio_3_dias = 0
        promedio_5_dias = 0

    plan_editado = session.pop("plan_editado", False)
    plan_creado = session.pop("plan_creado", False)
    plan_eliminado = session.pop("plan_eliminado", False)

    return render_template(
        "admin/admin_planes.html",
        planes=planes,
        promedio_3_dias=promedio_3_dias,
        promedio_5_dias=promedio_5_dias,
        user=current_user,
        plan_editado=plan_editado,
        plan_creado=plan_creado,
        plan_eliminado=plan_eliminado,
    )


@app.route("/admin/plan/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def nuevo_plan():
    if request.method == "GET":
        return render_template("admin/nuevo_plan.html", user=current_user)

    nombre = request.form.get("nombre")
    precio_3_dias = request.form.get("precio_3_dias")
    precio_5_dias = request.form.get("precio_5_dias")
    deportes_disponibles = request.form.get("deportes_disponibles")
    imagen = request.form.get("imagen")

    # Validaciones básicas
    if not all([nombre, precio_3_dias, precio_5_dias]):
        return render_template(
            "admin/nuevo_plan.html",
            error="Todos los campos son obligatorios.",
            user=current_user,
        )

    try:
        payload = {
            "nombre": nombre,
            "precio_3_dias": int(precio_3_dias),
            "precio_5_dias": int(precio_5_dias),
            "deportes_disponibles": deportes_disponibles,
            "imagen": imagen,
        }

        response = requests.post(f"{API_HOST}/api/planes/", json=payload)

        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 201:
            session["plan_creado"] = True
            return redirect("/admin/planes")
        else:
            error_msg = response.json().get("error", "Error al crear plan")
            return render_template(
                "admin/nuevo_plan.html", error=error_msg, user=current_user
            )
    except Exception as e:
        return render_template(
            "admin/nuevo_plan.html",
            error="Error en el servidor. Inténtalo más tarde.",
            user=current_user,
        )


@app.route("/admin/plan/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_plan(id):
    if request.method == "GET":
        try:
            response = requests.get(f"{API_HOST}/api/planes/{id}")
            if response.status_code == 200:
                plan = response.json()
                return render_template(
                    "admin/editar_plan.html", plan=plan, user=current_user
                )
            else:
                return "Plan no encontrado", 404
        except Exception as e:
            return "Error del servidor", 500

    nombre = request.form.get("nombre")
    precio_3_dias = request.form.get("precio_3_dias")
    precio_5_dias = request.form.get("precio_5_dias")
    deportes_disponibles = request.form.get("deportes_disponibles")
    imagen = request.form.get("imagen")

    if not all([nombre, precio_3_dias, precio_5_dias, deportes_disponibles]):
        try:
            response = requests.get(f"{API_HOST}/api/planes/{id}")
            plan = response.json() if response.status_code == 200 else {}
            return render_template(
                "admin/editar_plan.html",
                plan=plan,
                error="Todos los campos son obligatorios.",
                user=current_user,
            )
        except:
            return "Error del servidor", 500

    try:
        payload = {
            "nombre": nombre,
            "precio_3_dias": int(precio_3_dias),
            "precio_5_dias": int(precio_5_dias),
            "deportes_disponibles": deportes_disponibles,
            "imagen": imagen,
        }

        response = requests.put(f"{API_HOST}/api/planes/{id}", json=payload)

        if response.status_code == 200:
            session["plan_editado"] = True
            return redirect("/admin/planes")
        else:
            error_msg = response.json().get("error", "Error al actualizar plan")
            plan_response = requests.get(f"{API_HOST}/api/planes/{id}")
            plan = plan_response.json() if plan_response.status_code == 200 else {}
            return render_template(
                "admin/editar_plan.html", plan=plan, error=error_msg, user=current_user
            )
    except Exception as e:
        return render_template(
            "admin/editar_plan.html",
            error="Error en el servidor. Inténtalo más tarde.",
            user=current_user,
        )


@app.route("/admin/plan/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_plan(id):
    try:
        response = requests.delete(f"{API_HOST}/api/planes/{id}")

        if response.status_code == 200:
            session["plan_eliminado"] = True

        return redirect("/admin/planes")
    except Exception as e:
        return redirect("/admin/planes")


# ----------------------Rutas||Tienda----------------------
@app.route("/agregar_plan_carrito/<path:plan_nombre>", methods=["POST"])
@login_required
def agregar_plan_carrito(plan_nombre):
    try:
        dias = request.form.get("dias", 3, type=int)
        deporte = request.form.get("deporte", "")

        response = requests.get(f"{API_HOST}/api/planes/")
        if response.status_code != 200:
            flash("Error al obtener información de los planes")
            return redirect(url_for("planes"))

        planes = response.json()
        plan = next((p for p in planes if p["nombre"] == plan_nombre), None)

        if not plan:
            flash("Plan no encontrado")
            return redirect(url_for("planes"))

        # Obtener el precio correcto del plan según los días
        dias_str = str(dias)
        if dias_str in plan.get("precio_dias", {}):
            precio = plan["precio_dias"][dias_str]
        else:
            flash("Configuración de días no válida para este plan")
            return redirect(url_for("planes"))

        carrito = session.get("carrito", [])
        plan_key = f"{plan['nombre']}_{dias}_{deporte}"
        nombre_completo = f"{plan['nombre']} - {deporte}" if deporte else plan["nombre"]
        nombre_completo += f" ({dias} días/semana)"

        # Verificar si el plan ya está en el carrito
        for item in carrito:
            if item.get("tipo") == "plan" and item.get("plan_key") == plan_key:
                flash("Este plan ya está en el carrito")
                return redirect(url_for("ver_carrito"))

        reemplazado = False
        for i, item in enumerate(carrito):
            if (
                item.get("tipo") == "plan"
                and item.get("plan_original") == plan["nombre"]
            ):
                carrito[i] = {
                    "id": plan["id"],
                    "plan_key": plan_key,
                    "nombre": nombre_completo,
                    "precio": float(precio),
                    "cantidad": 1,
                    "imagen": plan.get("imagen", ""),
                    "tipo": "plan",
                    "dias": dias,
                    "deporte": deporte,
                    "plan_original": plan["nombre"],
                }
                reemplazado = True
                flash(f"Se actualizó el plan '{plan['nombre']}' en el carrito")
                break

        if not reemplazado:
            carrito.append(
                {
                    "id": plan["id"],
                    "plan_key": plan_key,
                    "nombre": nombre_completo,
                    "precio": float(precio),
                    "cantidad": 1,
                    "imagen": plan.get("imagen", ""),
                    "tipo": "plan",
                    "dias": dias,
                    "deporte": deporte,
                    "plan_original": plan["nombre"],
                }
            )
            flash(f"Plan '{nombre_completo}' agregado al carrito")

        session["carrito"] = carrito
        session.modified = True
        return redirect(url_for("ver_carrito"))

    except Exception as ex:
        flash("Error al agregar plan al carrito")
        print(f"Error en agregar_plan_carrito: {ex}")
        return redirect(url_for("planes"))


@app.route("/agregar_carrito/<int:producto_id>", methods=["POST"])
@login_required
def agregar_carrito(producto_id):
    try:
        # Capturamos la cantidad enviada desde el formulario
        cantidad = int(request.form.get("cantidad", 1))
        if cantidad < 1:
            cantidad = 1

        response = requests.get(
            f"{API_HOST}/api/productos/", params={"id": producto_id}
        )
        if response.status_code != 200 or not response.json():
            flash("Producto no encontrado", "error")
            return redirect(url_for("tienda"))

        producto = response.json()[0]
        carrito = session.get("carrito", [])

        cantidad_total = cantidad + sum(
            map(lambda itm: itm["cantidad"] if itm["id"] == producto_id else 0, carrito)
        )

        if producto.get("Cantidad", 0) < cantidad_total:
            flash("No hay suficiente stock del producto!", "error")
            return redirect(url_for("tienda"))

        for item in carrito:
            if item.get("id") == producto_id and item.get("tipo") == "producto":
                item["cantidad"] += cantidad
                break
        else:
            carrito.append(
                {
                    "id": producto.get("ID_Producto", producto_id),
                    "nombre": producto.get("Nombre", ""),
                    "precio": float(producto.get("Precio", 0)),
                    "cantidad": cantidad,
                    "imagen": producto.get("Imagen", ""),
                    "tipo": "producto",
                }
            )

        session["carrito"] = carrito
        session.modified = True
        flash("Producto agregado al carrito")
        return redirect(request.referrer or url_for("tienda"))
    except Exception as ex:
        print(f"Error al agregar producto al carrito: {ex}")
        flash("Error al agregar producto al carrito")
        return redirect(request.referrer or url_for("tienda"))


@app.route("/ver_carrito")
@login_required
def ver_carrito():
    carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    return render_template(
        "carrito.html", carrito=carrito, total=total, user=current_user
    )


@app.route("/eliminar_producto_carrito/<item_id>", methods=["POST"])
@login_required
def eliminar_producto_carrito(item_id):
    carrito = session.get("carrito", [])
    carrito_original_len = len(carrito)
    try:
        if item_id.startswith("plan_"):
            plan_key = item_id.replace("plan_", "")
            carrito = [
                item
                for item in carrito
                if not (item.get("tipo") == "plan" and item.get("plan_key") == plan_key)
            ]
        else:
            producto_id = int(item_id)
            carrito = [
                item
                for item in carrito
                if not (
                    item.get("id") == producto_id and item.get("tipo") == "producto"
                )
            ]
        session["carrito"] = carrito
        session.modified = True
        if len(carrito) < carrito_original_len:
            flash("Item eliminado del carrito")
        else:
            flash("No se pudo eliminar el item")
    except Exception as e:
        print(f"Error al eliminar item: {e}")
        flash("Error al eliminar el item del carrito")
    return redirect(url_for("ver_carrito"))


@app.route("/finalizar_compra", methods=["POST"])
@login_required
def finalizar_compra():
    session.pop("carrito", None)
    session.modified = True
    flash("Compra finalizada exitosamente")
    return redirect(url_for("ver_carrito"))


@app.route("/pasarela")
@login_required
def pasarela():
    carrito = session.get("carrito", [])
    if not carrito:
        flash("Tu carrito está vacío")
        return redirect(url_for("tienda"))
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    return render_template(
        "pasarela.html", carrito=carrito, total=total, user=current_user
    )


@app.route("/limpiar-carrito-frontend", methods=["POST"])
def limpiar_carrito_frontend():
    try:
        productos_eliminados = len(session.get("carrito", []))
        session["carrito"] = []
        session.modified = True
        return (
            jsonify(
                {
                    "mensaje": "Carrito limpiado en frontend",
                    "productos_eliminados": productos_eliminados,
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Error al limpiar carrito en frontend: {e}")
        return jsonify({"error": "Error al limpiar carrito"}), 500


@app.route("/estado-carrito", methods=["GET"])
def estado_carrito():
    try:
        carrito = session.get("carrito", [])
        total_productos = len(carrito)
        return (
            jsonify(
                {
                    "carrito": carrito,
                    "total_productos": total_productos,
                    "tiene_productos": total_productos > 0,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "Error al obtener estado del carrito"}), 500


@app.route("/pago", methods=["POST"])
def pagar():
    """
    Ruta definida para hacer un middleware entre el back y la request de la pag
    porque si no no se porque toma mal el Content-Type si lo haces desde el fetch()
    """
    respuesta = requests.post(f"{API_HOST}/api/pago", json=request.get_json())
    return respuesta.json(), respuesta.status_code


if __name__ == "__main__":
    app.run("localhost", port=3000, debug=True, threaded=True)
