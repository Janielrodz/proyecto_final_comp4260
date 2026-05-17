from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import pyodbc
import os
import uuid
from datetime import datetime, timezone, timedelta

load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")
driver = "{ODBC Driver 18 for SQL Server}"

# Configuración de Azure Storage
storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "task-files"

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Crear tabla si no existe (una sola vez)
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
    CREATE TABLE tasks (
        id INT PRIMARY KEY IDENTITY(1,1),
        title NVARCHAR(100),
        done BIT,
        file_url NVARCHAR(500)
    )
""")
conn.commit()

def generate_sas_url(blob_name):
    blob_service = BlobServiceClient.from_connection_string(storage_connection_string)
    account_name = blob_service.account_name
    account_key = blob_service.credential.account_key

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

@app.route("/")
def index():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    tasks_with_sas = []
    for task in tasks:
        file_sas_url = generate_sas_url(task.file_url.split("/")[-1]) if task.file_url else None
        tasks_with_sas.append({
            "id": task.id,
            "title": task.title,
            "done": task.done,
            "file_url": file_sas_url
        })
    return render_template("index.html", tasks=tasks_with_sas)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    file = request.files.get("file")
    file_url = None

    if file and file.filename != "":
        blob_service = BlobServiceClient.from_connection_string(storage_connection_string)
        blob_name = f"{uuid.uuid4()}_{file.filename}"
        blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(file)
        file_url = blob_client.url

    if title:
        cursor.execute("INSERT INTO tasks (title, done, file_url) VALUES (?, ?, ?)", (title, 0, file_url))
        conn.commit()
    return redirect("/")

@app.route("/done/<int:task_id>")
def mark_done(task_id):
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)