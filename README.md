# FitHub
Aplicacion para conseguir planes de entrenamiento y suplementos.

## Instalacion
Para clonar el repositorio con HTTPS, en la consola 
```bash
git clone https://github.com/LucaFrisoni/FitHub.git
```

Una vez clonado, entramos al directorio y corremos el script para instalar todas las dependencias
> El script instala las dependencias tanto del front, como del back. Crea el entorno virtual y abre Visual Studio Code al finalizar.
```bash
cd FitHub/ && ./init.sh
```

Una vez finalizado, el proyecto ya esta listo para correr.

## Backend
>Para poder correr el backend, se necesita una base de datos MySQL, los datos de la misma estan ubicados en el .env, y la estructura es la siguiente:
```text
MYSQL_ADDR=127.0.0.1
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWD=passwd
```
Es necesario correr el script ubicado en Back/db/script.sql en la base de datos para generar todas las tablas necesarias para el correcto funcionamiento.

Finalmente, para correr el backend:
```bash
cd Back
flask run
```

## Frontend
*WIP*

Para correr el frontend, correr en la terminal
```bash
npm run dev
```