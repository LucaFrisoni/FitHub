from flask_login import UserMixin


class User(UserMixin):
    def __init__(
        self,
        ID_usuario,
        Nombre,
        Apellido,
        Email,
        Telefono,
        FechaNacimiento,
        Usuario,
        Imagen,
        ID_rol,
    ):
        self.id = ID_usuario
        self.nombre = Nombre
        self.apellido = Apellido
        self.email = Email
        self.telefono = Telefono
        self.fecha_nacimiento = FechaNacimiento
        self.usuario = Usuario
        self.imagen = Imagen
        self.id_rol = ID_rol

    def get_id(self):
        return str(self.id)  # Necesario para Flask-Login
