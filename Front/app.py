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


@app.route("/planes")
def planes():
    planes = [
        {
            "id": "bodybuilding",
            "nombre": "Body-Building",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/bodybuilding.png"),
            "precio_dias": {3: 46900, 5: 63000},
        },
        {
            "id": "spinning",
            "nombre": "Spinning",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/spinning.png"),
            "precio_dias": {3: 29500, 5: 42000},
        },
        {
            "id": "sport",
            "nombre": "Sport-Focused Training",
            "dias_elegidos": 3,
            "imagen": url_for("static", filename="images/sport.png"),
            "precio_dias": {3: 49500, 5: 65000},
            "deportes": ["futbol sala", "boxeo", "rugby"],
        },
    ]
    return render_template("planes.html", planes=planes, user=current_user)


@app.route("/reservas")
# @login_required
def reservas():
    return render_template("reservas.html", user=current_user)


@app.route("/tienda", methods=["GET"])
def tienda():
    try:
        response = requests.get(f"{API_HOST}/api/productos/")
        if response.status_code == 200:
            productos_api = response.json()
            productos = []
            for p in productos_api:
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
        # si existe la session login, la devuelve y luego la borra, sino usa False
        toast_exitoso = session.pop("toast_exitoso", False)

        return render_template(
            "user.html",
            user=current_user,
            toast_exitoso=toast_exitoso,
        )

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

    except Exception:
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
def subir_imagen_producto():
    try:
        # Verificar que se envió un archivo
        if "foto" not in request.files:
            return (
                jsonify({"success": False, "error": "No se seleccionó ningún archivo"}),
                400,
            )

        foto = request.files["foto"]

        if foto.filename == "":
            return (
                jsonify(
                    {"success": False, "error": "El nombre del archivo está vacío"}
                ),
                400,
            )

        # Verificar extensión del archivo
        if "." not in foto.filename:
            return (
                jsonify({"success": False, "error": "Archivo sin extensión válida"}),
                400,
            )

        extension = foto.filename.rsplit(".", 1)[1].lower()

        # Definir extensiones permitidas si no están definidas
        EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png"}

        if extension not in EXTENSIONES_PERMITIDAS:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Formato no permitido. Formatos aceptados: {', '.join(EXTENSIONES_PERMITIDAS)}",
                    }
                ),
                400,
            )

        # Generar nombre único para el archivo
        filename = f"producto_{uuid.uuid4().hex}.{extension}"

        # Asegurarse de que el directorio existe
        upload_dir = os.path.join(app.static_folder, "images/uploads/productos")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)

        # Guardar la imagen
        foto.save(filepath)

        # Retornar respuesta exitosa
        return jsonify(
            {
                "success": True,
                "filename": filename,
                "url": url_for(
                    "static", filename=f"images/uploads/productos/{filename}"
                ),
            }
        )

    except Exception as e:
        app.logger.error(f"Error al subir imagen de producto: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Error interno del servidor al guardar la imagen",
                }
            ),
            500,
        )


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    try:
        # Obtener productos desde la API
        response = requests.get(f"{API_HOST}/api/productos/")
        if response.status_code == 200:
            productos = response.json()
        else:
            productos = []
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        productos = []

    producto_editado = session.pop("producto_editado", False)
    producto_creado = session.pop("producto_creado", False)
    producto_eliminado = session.pop("producto_eliminado", False)

    return render_template(
        "admin/admin_panel.html",
        productos=productos,
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
def subir_imagen_plan():
    try:
        # Verificar que se envió un archivo
        if "foto" not in request.files:
            return (
                jsonify({"success": False, "error": "No se seleccionó ningún archivo"}),
                400,
            )

        foto = request.files["foto"]

        if foto.filename == "":
            return (
                jsonify(
                    {"success": False, "error": "El nombre del archivo está vacío"}
                ),
                400,
            )

        # Verificar extensión del archivo
        if "." not in foto.filename:
            return (
                jsonify({"success": False, "error": "Archivo sin extensión válida"}),
                400,
            )

        extension = foto.filename.rsplit(".", 1)[1].lower()

        # Definir extensiones permitidas si no están definidas
        EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png"}

        if extension not in EXTENSIONES_PERMITIDAS:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Formato no permitido. Formatos aceptados: {', '.join(EXTENSIONES_PERMITIDAS)}",
                    }
                ),
                400,
            )

        # Generar nombre único para el archivo
        filename = f"plan_{uuid.uuid4().hex}.{extension}"

        # Asegurarse de que el directorio existe
        upload_dir = os.path.join(app.static_folder, "images/uploads/planes")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)

        # Guardar la imagen
        foto.save(filepath)

        # Retornar respuesta exitosa
        return jsonify(
            {
                "success": True,
                "filename": filename,
                "url": url_for("static", filename=f"images/uploads/planes/{filename}"),
            }
        )

    except Exception as e:
        app.logger.error(f"Error al subir imagen de plan: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Error interno del servidor al guardar la imagen",
                }
            ),
            500,
        )


@app.route("/admin/planes")
@login_required
@admin_required
def admin_planes():
    try:
        # Obtener planes desde la API
        response = requests.get(f"{API_HOST}/api/planes/")
        if response.status_code == 200:
            planes = response.json()
            for plan in planes:
                if plan.get("Imagen"):
                    plan["imagen_url"] = url_for(
                        "static", filename=f'images/uploads/planes/{plan["Imagen"]}'
                    )
                else:
                    plan["imagen_url"] = url_for(
                        "static", filename="images/default_plan.png"
                    )
        else:
            planes = []
    except Exception as e:
        print(f"Error al obtener planes: {e}")
        planes = []

    plan_editado = session.pop("plan_editado", False)
    plan_creado = session.pop("plan_creado", False)
    plan_eliminado = session.pop("plan_eliminado", False)

    return render_template(
        "admin/admin_planes.html",
        planes=planes,
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

    # Obtener datos del formulario
    descripcion = request.form.get("descripcion")
    duracion = request.form.get("duracion")
    precio = request.form.get("precio")
    imagen = request.form.get("imagen")

    # Validaciones básicas
    if not all([descripcion, duracion, precio]):
        return render_template(
            "admin/nuevo_plan.html",
            error="Todos los campos son obligatorios.",
            user=current_user,
        )

    try:
        payload = {
            "Descripcion": descripcion,
            "DuracionPlan": duracion,
            "Precio": int(precio),
            "Imagen": imagen,
        }

        response = requests.post(f"{API_HOST}/api/planes/", json=payload)

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

    # POST - Actualizar plan
    descripcion = request.form.get("descripcion")
    duracion = request.form.get("duracion")
    precio = request.form.get("precio")
    imagen = request.form.get("imagen")

    if not all([descripcion, duracion, precio]):
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
            "Descripcion": descripcion,
            "DuracionPlan": duracion,
            "Precio": int(precio),
            "Imagen": imagen,
        }

        response = requests.put(f"{API_HOST}/api/planes/{id}", json=payload)

        if response.status_code == 200:
            session["plan_editado"] = True
            return redirect("/admin/planes")
        else:
            error_msg = response.json().get("error", "Error al actualizar plan")
            # Obtener plan actual para mostrar en caso de error
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


@app.route("/admin/reservas")
@login_required
@admin_required
def admin_reservas():
    try:
        # Obtener reservas desde la API
        response = requests.get(f"{API_HOST}/api/alquileres/")
        reservas = response.json() if response.status_code == 200 else []

        # Obtener usuarios y planes para mostrar nombres
        usuarios_response = requests.get(f"{API_HOST}/api/usuarios/")
        usuarios = (
            {u["ID_usuario"]: u for u in usuarios_response.json()}
            if usuarios_response.status_code == 200
            else {}
        )

        planes_response = requests.get(f"{API_HOST}/api/planes/")
        planes = (
            {p["ID_Plan"]: p for p in planes_response.json()}
            if planes_response.status_code == 200
            else {}
        )

    except Exception as e:
        print(f"Error al obtener reservas: {e}")
        reservas = []
        usuarios = {}
        planes = {}

    reserva_editada = session.pop("reserva_editada", False)
    reserva_creada = session.pop("reserva_creada", False)
    reserva_eliminada = session.pop("reserva_eliminada", False)

    return render_template(
        "admin/admin_reservas.html",
        reservas=reservas,
        usuarios=usuarios,
        planes=planes,
        user=current_user,
        reserva_editada=reserva_editada,
        reserva_creada=reserva_creada,
        reserva_eliminada=reserva_eliminada,
    )


@app.route("/admin/reserva/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def nueva_reserva():
    try:
        # Obtener usuarios y planes para los selects
        usuarios_response = requests.get(f"{API_HOST}/api/usuarios/")
        usuarios = (
            usuarios_response.json() if usuarios_response.status_code == 200 else []
        )

        planes_response = requests.get(f"{API_HOST}/api/planes/")
        planes = planes_response.json() if planes_response.status_code == 200 else []

        if request.method == "GET":
            return render_template(
                "admin/nueva_reserva.html",
                usuarios=usuarios,
                planes=planes,
                user=current_user,
            )

        # POST - Crear nueva reserva
        usuario_id = request.form.get("usuario")
        plan_id = request.form.get("plan")
        nota = request.form.get("nota", "")

        if not usuario_id or not plan_id:
            return render_template(
                "admin/nueva_reserva.html",
                usuarios=usuarios,
                planes=planes,
                error="Usuario y Plan son obligatorios",
                user=current_user,
            )

        payload = {"ID_Usuario": int(usuario_id), "ID_Plan": int(plan_id), "Nota": nota}

        response = requests.post(f"{API_HOST}/api/alquileres/", json=payload)

        if response.status_code == 201:
            session["reserva_creada"] = True
            return redirect("/admin/reservas")
        else:
            error_msg = response.json().get("error", "Error al crear reserva")
            return render_template(
                "admin/nueva_reserva.html",
                usuarios=usuarios,
                planes=planes,
                error=error_msg,
                user=current_user,
            )

    except Exception as e:
        print(f"Error: {e}")
        return render_template(
            "admin/nueva_reserva.html",
            usuarios=usuarios,
            planes=planes,
            error="Error en el servidor",
            user=current_user,
        )


@app.route("/admin/reserva/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_reserva(id):
    try:
        # Obtener reserva actual
        response = requests.get(f"{API_HOST}/api/alquileres/{id}")
        if response.status_code != 200:
            return "Reserva no encontrada", 404
        reserva = response.json()

        # Obtener usuarios y planes para los selects
        usuarios_response = requests.get(f"{API_HOST}/api/usuarios/")
        usuarios = (
            usuarios_response.json() if usuarios_response.status_code == 200 else []
        )

        planes_response = requests.get(f"{API_HOST}/api/planes/")
        planes = planes_response.json() if planes_response.status_code == 200 else []

        if request.method == "GET":
            return render_template(
                "admin/editar_reserva.html",
                reserva=reserva,
                usuarios=usuarios,
                planes=planes,
                user=current_user,
            )

        # POST - Actualizar reserva
        usuario_id = request.form.get("usuario")
        plan_id = request.form.get("plan")
        nota = request.form.get("nota", "")

        if not usuario_id or not plan_id:
            return render_template(
                "admin/editar_reserva.html",
                reserva=reserva,
                usuarios=usuarios,
                planes=planes,
                error="Usuario y Plan son obligatorios",
                user=current_user,
            )

        payload = {"ID_Usuario": int(usuario_id), "ID_Plan": int(plan_id), "Nota": nota}

        response = requests.put(f"{API_HOST}/api/alquileres/{id}", json=payload)

        if response.status_code == 200:
            session["reserva_editada"] = True
            return redirect("/admin/reservas")
        else:
            error_msg = response.json().get("error", "Error al actualizar reserva")
            return render_template(
                "admin/editar_reserva.html",
                reserva=reserva,
                usuarios=usuarios,
                planes=planes,
                error=error_msg,
                user=current_user,
            )

    except Exception as e:
        print(f"Error: {e}")
        return render_template(
            "admin/editar_reserva.html",
            reserva=reserva,
            usuarios=usuarios,
            planes=planes,
            error="Error en el servidor",
            user=current_user,
        )


@app.route("/admin/reserva/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_reserva(id):
    try:
        response = requests.delete(f"{API_HOST}/api/alquileres/{id}")

        if response.status_code == 200:
            session["reserva_eliminada"] = True

        return redirect("/admin/reservas")
    except Exception as e:
        return redirect("/admin/reservas")


@app.route("/agregar_carrito/<int:producto_id>", methods=["POST"])
def agregar_carrito(producto_id):
    try:
        response = requests.get(
            f"{API_HOST}/api/productos/", params={"id": producto_id}
        )
        if response.status_code == 404:
            flash("Producto no encontrado")
            return redirect(url_for("tienda"))

        producto = response.json()[0]
        # Obtener carrito de la sesión
        carrito = session.get("carrito", [])

        # Verificar si el producto ya está en el carrito
        for item in carrito:
            if item["id"] == producto_id:
                item["cantidad"] += 1
                break
        else:

            # Agregar nuevo producto al carrito
            carrito.append(
                {
                    "id": producto["ID_Producto"] if "ID_Producto" in producto else "",
                    "nombre": producto["Nombre"] if "Nombre" in producto else "",
                    "precio": float(producto["Precio"] if "Precio" in producto else 0),
                    "cantidad": 1,
                    "imagen": producto["Imagen"] if "Imagen" in producto else "",
                }
            )

        # Guardar carrito en sesión
        session["carrito"] = carrito
        flash("Producto agregado al carrito")

        # CAMBIO: Usar request.referrer para redirigir inteligentemente
        return redirect(request.referrer or url_for("tienda"))

    except Exception as ex:
        print(f"error al agregar producot al carrito: {ex}")
        flash("Error al agregar producto al carrito", category="error")
        return redirect(request.referrer or url_for("tienda"))


@app.route("/ver_carrito")
def ver_carrito():
    carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    return render_template(
        "carrito.html", carrito=carrito, total=total, user=current_user
    )


@app.route("/eliminar_producto_carrito/<int:producto_id>", methods=["POST"])
def eliminar_producto_carrito(producto_id):
    carrito = session.get("carrito", [])
    carrito = [item for item in carrito if item["id"] != producto_id]
    session["carrito"] = carrito
    flash("Producto eliminado del carrito")
    return redirect(url_for("ver_carrito"))


@app.route("/pasarela")
@login_required
def pasarela():
    carrito = session.get("carrito", [])
    
    # Si el carrito está vacío, redirigir a la tienda
    if not carrito:
        flash("Tu carrito está vacío")
        return redirect(url_for("tienda"))
    
    # Calcular total
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    
    return render_template(
        "pasarela.html", 
        carrito=carrito, 
        total=total, 
        user=current_user,
        API_HOST=API_HOST  
    )

@app.route("/limpiar-carrito-frontend", methods=["POST"])
def limpiar_carrito_frontend():
    """Limpiar carrito en la sesión del frontend"""
    try:
        if 'carrito' in session:
            productos_eliminados = len(session['carrito'])
            session['carrito'] = []
            session.modified = True
            print(f"Carrito limpiado en frontend: {productos_eliminados} productos eliminados")
            return jsonify({
                "mensaje": "Carrito limpiado en frontend",
                "productos_eliminados": productos_eliminados
            }), 200
        else:
            return jsonify({"mensaje": "No hay carrito para limpiar"}), 200
    except Exception as e:
        print(f"Error al limpiar carrito en frontend: {e}")
        return jsonify({"error": "Error al limpiar carrito"}), 500
@app.route("/estado-carrito", methods=["GET"])
def estado_carrito():
    try:
        carrito = session.get('carrito', [])
        total_productos = len(carrito)
        return jsonify({
            "carrito": carrito,
            "total_productos": total_productos,
            "tiene_productos": total_productos > 0
        }), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener estado del carrito"}), 500

if __name__ == "__main__":
    app.run("localhost", port=3000, debug=True, threaded=True)
