import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "supersecretportfolio_key"

def get_db_connection():
    if not os.path.exists("database"):
        os.makedirs("database")
    conn = sqlite3.connect("database/portfolio.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subtitle TEXT,
            description TEXT,
            tech TEXT,
            github TEXT,
            demo TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/skills")
def skills():
    skills_data = {
        "Programming": ["Python", "Java", "HTML", "CSS", "JavaScript"],
        "Framework": ["Flask"],
        "Database": ["MySQL", "SQLite"],
        "Tools": ["Git", "GitHub", "VS Code"]
    }
    return render_template("skills.html", skills=skills_data)

@app.route("/projects")
def projects():
    conn = get_db_connection()
    project_list = conn.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return render_template("projects.html", projects=project_list)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

# --- ADMIN AUTH & CRUD ---
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "12345":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials!", "error")
    return render_template("login.html")

@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    proj_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    conn.close()
    return render_template("admin/dashboard.html", msg_count=msg_count, proj_count=proj_count)

@app.route("/admin/projects", methods=["GET", "POST"])
def admin_projects():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    if request.method == "POST":
        title = request.form.get("title")
        subtitle = request.form.get("subtitle")
        description = request.form.get("description")
        tech = request.form.get("tech")
        github = request.form.get("github")
        demo = request.form.get("demo")

        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (title, subtitle, description, tech, github, demo) VALUES (?, ?, ?, ?, ?, ?)",
                       (title, subtitle, description, tech, github, demo))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_projects"))

    projects = conn.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return render_template("admin/projects.html", projects=projects)

@app.route("/admin/projects/delete/<int:id>")
def delete_project(id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    conn.execute("DELETE FROM projects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_projects"))

@app.route("/admin/messages")
def admin_messages():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin/messages.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)