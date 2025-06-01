CREATE DATABASE IF NOT EXISTS fithub_db;
USE fithub_db;

-- Tabla de roles
CREATE TABLE ROLES (
    ID_rol INT PRIMARY KEY,
    Tipo_rol VARCHAR(50)
);

-- Tabla de usuarios
CREATE TABLE USUARIOS (
    ID_usuario VARCHAR(50) PRIMARY KEY,
    Nombre VARCHAR(50),
    Apellido VARCHAR(50),
    Email VARCHAR(100),
    Telefono INT,
    FechaNacimiento DATE,
    Usuario VARCHAR(50),
    Contrasenia VARCHAR(100),
    ID_rol INT,
    FOREIGN KEY (ID_rol) REFERENCES ROLES(ID_rol)
);

-- Tabla de planes
CREATE TABLE Planes (
    ID_Plan INT PRIMARY KEY,
    Precio INT,
    Descripcion VARCHAR(255),
    DuracionPlan VARCHAR(50)
);

-- Tabla de Alquileres de Plan
CREATE TABLE AlquileresPlan (
    ID_AlquilerPlan INT PRIMARY KEY,
    ID_Plan INT,
    ID_Usuario VARCHAR(50),
    Nota VARCHAR(255),
    FOREIGN KEY (ID_Plan) REFERENCES Planes(ID_Plan),
    FOREIGN KEY (ID_Usuario) REFERENCES USUARIOS(ID_usuario)
);

-- Tabla de Horarios de Entrenamiento
CREATE TABLE HorariosEntrenamiento (
    ID_HorarioEntrenamiento INT PRIMARY KEY,
    Dias VARCHAR(50),
    Horario VARCHAR(50),
    ID_Plan INT,
    ID_Usuario VARCHAR(50),
    FOREIGN KEY (ID_Plan) REFERENCES Planes(ID_Plan),
    FOREIGN KEY (ID_Usuario) REFERENCES USUARIOS(ID_usuario)
);

-- Tabla de productos
CREATE TABLE PRODUCTOS (
    ID_Producto INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Descripcion VARCHAR(255),
    Codigo VARCHAR(50),
    Cantidad INT,
    Precio INT
);

-- Tabla de compras
CREATE TABLE COMPRAS (
    ID_Compra INT PRIMARY KEY,
    NroCompra INT,
    ID_Usuario VARCHAR(50),
    FechaCompra DATE,
    Total INT,
    FOREIGN KEY (ID_Usuario) REFERENCES USUARIOS(ID_usuario)
);

-- Tabla de detalle de compras
CREATE TABLE DETALLECOMPRAS (
    ID_Detalle INT PRIMARY KEY,
    ID_Producto INT,
    ID_Compra INT,
    Cantidad INT,
    SubTotal INT,
    FOREIGN KEY (ID_Producto) REFERENCES PRODUCTOS(ID_Producto),
    FOREIGN KEY (ID_Compra) REFERENCES COMPRAS(ID_Compra)
);
