CREATE DATABASE IF NOT EXISTS fithub_db;
USE fithub_db;

-- Tabla de roles
-- CREATE TABLE roles (
--     ID_rol INT PRIMARY KEY AUTO_INCREMENT,
--     Tipo_rol VARCHAR(50)
-- );

-- Tabla de usuarios
CREATE TABLE usuarios (
    ID_usuario INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(50),
    Apellido VARCHAR(50),
    Email VARCHAR(100),
    Telefono VARCHAR(30),
    FechaNacimiento DATE,
    Usuario VARCHAR(50),
    Imagen VARCHAR(255) DEFAULT NULL,
    Contrasenia VARCHAR(100),
    -- ID_rol INT DEFAULT 1,
    -- FOREIGN KEY (ID_rol) REFERENCES roles(ID_rol)
);

-- Tabla de planes
CREATE TABLE planes (
    ID_Plan INT PRIMARY KEY AUTO_INCREMENT,
    Precio INT,
    Descripcion VARCHAR(255),
    DuracionPlan VARCHAR(50)
);

-- Tabla de Alquileres de Plan
CREATE TABLE alquileresplan (
    ID_AlquilerPlan INT PRIMARY KEY AUTO_INCREMENT,
    ID_Plan INT,
    ID_Usuario INT,
    Nota VARCHAR(255),
    FOREIGN KEY (ID_Plan) REFERENCES planes(ID_Plan),
    FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_usuario)
);

-- Tabla de Horarios de Entrenamiento
CREATE TABLE horariosentrenamiento (
    ID_HorarioEntrenamiento INT PRIMARY KEY AUTO_INCREMENT,
    Dias VARCHAR(50),
    Horario VARCHAR(50),
    ID_Plan INT,
    ID_Usuario INT,
    FOREIGN KEY (ID_Plan) REFERENCES planes(ID_Plan),
    FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_usuario)
);

-- Tabla de productos
CREATE TABLE productos (
    ID_Producto INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    Descripcion VARCHAR(255),
    Codigo VARCHAR(50),
    Cantidad INT,
    Precio INT
);

-- Tabla de compras
CREATE TABLE compras (
    ID_Compra INT PRIMARY KEY AUTO_INCREMENT,
    NroCompra INT,
    ID_Usuario INT,
    FechaCompra DATE,
    Total INT,
    FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_usuario)
);

-- Tabla de detalle de compras
CREATE TABLE detallecompras (
    ID_Detalle INT PRIMARY KEY AUTO_INCREMENT,
    ID_Producto INT,
    ID_Compra INT,
    Cantidad INT,
    SubTotal INT,
    FOREIGN KEY (ID_Producto) REFERENCES productos(ID_Producto),
    FOREIGN KEY (ID_Compra) REFERENCES compras(ID_Compra)
);

-- Insert de roles
INSERT INTO roles (Tipo_rol) VALUES ('admin'); 
INSERT INTO roles (Tipo_rol) VALUES ('user');  

-- Insert de administrador
INSERT INTO usuarios (Nombre, Apellido, Email, Telefono, FechaNacimiento, Usuario, Contrasenia, ID_rol)
VALUES ('aa', 'aa', 'admin@ejemplo.com', 123456789, '2000-01-01', 'admin', '$2b$12$7TppS8uD4mYf92MN7MFMvOITn3HkMXEyTln0hQUN/05aNLF8tGEiS', 1);