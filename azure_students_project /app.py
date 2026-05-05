from flask import Flask, render_template, request, redirect
import pyodbc
import os

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")
driver = "{ODBC Driver 17 for SQL Server}"

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Crear tabla si no existe (una sola vez)
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
    CREATE TABLE tasks (
        id INT PRIMARY KEY IDENTITY(1,1),
        title NVARCHAR(100),
        done BIT
    )
""")
conn.commit()

@app.route("/")
def index():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    if title:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
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
