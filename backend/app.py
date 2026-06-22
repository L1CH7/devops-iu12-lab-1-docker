import os
from typing import Any, Dict, List
from flask import Flask, jsonify, request, Response
import psycopg2
from psycopg2.extras import RealDictCursor

app: Flask = Flask(__name__)

def get_db() -> psycopg2.extensions.connection:
    """Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: The database connection object.
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        database=os.environ.get("POSTGRES_DB", "taskdb"),
        user=os.environ.get("POSTGRES_USER", "appuser"),
        password=os.environ.get("POSTGRES_PASSWORD", "changeme")
    )

def init_db() -> None:
    """Initializes the database by creating the tasks table if it does not exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/api/health", methods=["GET"])
def health() -> Response:
    """Returns the health status of the application.

    Returns:
        Response: A JSON response containing status: ok.
    """
    return jsonify({"status": "ok"})

@app.route("/api/tasks", methods=["GET"])
def get_tasks() -> Response:
    """Retrieves all tasks from the database sorted by creation time.

    Returns:
        Response: A JSON response containing the list of tasks.
    """
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(tasks)

@app.route("/api/tasks", methods=["POST"])
def create_task() -> tuple[Response, int]:
    """Creates a new task in the database.

    Returns:
        tuple[Response, int]: A JSON response with the created task and status code 201.
    """
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING *", (data["title"],))
    task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(task), 201

@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def toggle_task(task_id: int) -> Response:
    """Toggles the done status of a specific task.

    Args:
        task_id (int): The ID of the task to toggle.

    Returns:
        Response: A JSON response containing the updated task.
    """
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s RETURNING *", (task_id,))
    task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if task is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(task)

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int) -> Response:
    """Deletes a specific task from the database.

    Args:
        task_id (int): The ID of the task to delete.

    Returns:
        Response: A JSON response confirming deletion.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"deleted": task_id})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
