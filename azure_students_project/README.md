# Gestor de Tareas en Azure con Flask

Este proyecto implementa una aplicación web simple para gestionar tareas, diseñada para ser desplegada en Azure App Service con conexión a una base de datos SQL de Azure.

## 💻 Requisitos

- Python 3.8 o superior
- Cuenta de Azure for Students
- Azure SQL Database creada y accesible
- Variables de entorno configuradas en App Service:
  - SQL_SERVER
  - SQL_DATABASE
  - SQL_USERNAME
  - SQL_PASSWORD

## 🚀 Cómo ejecutar localmente

1. Clona el repositorio.
2. Crea un entorno virtual (opcional): `python -m venv venv`
3. Actívalo y luego instala dependencias: `pip install -r requirements.txt`
4. Configura tus variables de entorno en tu máquina.
5. Ejecuta: `python app.py`
6. Accede a `http://127.0.0.1:5000`

## 📦 Despliegue en Azure

Sigue las instrucciones del curso para desplegar en Azure App Service y enlazar la base de datos.

## 🧠 Créditos
Desarrollado como plantilla de proyecto para el curso de Cloud Computing – Prof. Javier A. Dastas
