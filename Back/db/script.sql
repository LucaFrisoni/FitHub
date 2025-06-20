CREATE DATABASE IF NOT EXISTS fithub_db;
USE fithub_db;

-- Tabla de roles
CREATE TABLE roles (
     ID_rol INT PRIMARY KEY AUTO_INCREMENT,
     Tipo_rol VARCHAR(50)
 );


INSERT INTO roles (ID_rol, Tipo_rol) VALUES (1, 'Admin');
INSERT INTO roles (ID_rol, Tipo_rol) VALUES (2, 'Usuario');

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
    ID_rol INT DEFAULT 2,
    FOREIGN KEY (ID_rol) REFERENCES roles(ID_rol)
);

-- Tabla de planes
CREATE TABLE planes (
    ID_Plan INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),  
    Imagen VARCHAR(255),
    Precio_3_dias INT,
    Precio_5_dias INT,
    Deportes_disponibles VARCHAR(255),
    Oculto BIT DEFAULT 0
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
    Categoria VARCHAR(100),
    Descripcion VARCHAR(255),
    Codigo VARCHAR(50),
    Imagen VARCHAR(255) DEFAULT NULL,
    Cantidad INT,
    Precio INT,
    Oculto BIT DEFAULT 0
);

-- Tabla de compras
CREATE TABLE compras( 
    ID_Compra INT PRIMARY KEY AUTO_INCREMENT,
    ID_Usuario INT NOT NULL,
    ID_Producto INT NOT NULL,
    FechaCompra DATE,
    Total INT,
    Cantidad INT DEFAULT 1,
    FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_usuario),
    FOREIGN KEY (ID_Producto) REFERENCES productos(ID_Producto)
);



