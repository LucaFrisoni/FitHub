# FitHub
Aplicacion para conseguir planes de entrenamiento y suplementos.

## Instalacion
Para clonar el repositorio con HTTPS, en la consola 
```bash
git clone https://github.com/LucaFrisoni/FitHub.git
```

Una vez clonado, tenemos que preparar el entorno virtual y las dependencias del npm, para el entorno virtual usamos [PipEnv](https://pipenv.pypa.io/en/latest/)
```bash
cd FitHub/ 
pipenv install
cd Front/ && npm i
cd ..
pipenv shell
```

Una vez finalizado, el proyecto ya esta listo para correr.

## Backend
Para poder correr el backend, se necesita una base de datos MySQL, los datos de la misma estan ubicados en el .env, y la estructura es la siguiente:
> La variable FRONT_HOST debe ser la ip del frontend.
```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWD=root
FRONT_HOST=http://127.0.0.1:3000
```
Es necesario correr el script ubicado en Back/db/script.sql en la base de datos para generar todas las tablas necesarias para el correcto funcionamiento.

Finalmente, lo iniciamos: 
```bash
cd Back
flask run --port 5000
```

## Frontend
El frontend tambien contiene un .env el cual es necesario para su funcionamiento. La estructura es la siguiente:
> La variable API_HOST debe ser la ip del backend. Y la variable APP_SECRET_KEY es una clave secreta
```text
API_HOST=http://127.0.0.1:5000
APP_SECRET_KEY=VERY_STRONG_KEY
```

Para correr el frontend, correr en la terminal
```bash
cd Front/
npm run dev
```