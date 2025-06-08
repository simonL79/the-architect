from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from dotenv import load_dotenv
import openai
import os
import re
import io
import zipfile
import json
from datetime import datetime

# Setup
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

project_dir = "projects/current"
chat_history = []

# --- User model ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=4)])
    submit = SubmitField("Register")

# --- Login management ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            return "User already exists."
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        return "Invalid credentials"
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=current_user.username, role=current_user.role)

@app.route("/build", methods=["POST"])
@login_required
def build():
    data = request.get_json()
    instruction = data.get("instruction", "").strip()
    if not instruction:
        return jsonify({"error": "Missing instruction"}), 400

    chat_history.append({"role": "user", "content": instruction})

    def generate():
        yield "data: "
        client = openai.OpenAI()
        try:
            stream = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are The Architect."}
                ] + chat_history,
                temperature=0.7,
                stream=True,
            )

            full = ""
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                full += token
                yield f"data: {token}\n\n"

            chat_history.append({"role": "assistant", "content": full})
            save_files_if_code(full)

        except Exception as e:
            yield f"data: ❌ Error: {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route("/files/save", methods=["POST"])
@login_required
def save_file():
    data = request.get_json()
    filename = data.get("filename")
    content = data.get("content")
    os.makedirs(project_dir, exist_ok=True)
    filepath = os.path.join(project_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return jsonify({"status": "saved", "filename": filename})

@app.route("/files/load", methods=["POST"])
@login_required
def load_file():
    filename = request.get_json().get("filename")
    path = os.path.join(project_dir, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    with open(path, "r", encoding="utf-8") as f:
        return jsonify({"filename": filename, "content": f.read()})

@app.route("/files", methods=["GET"])
@login_required
def list_files():
    files = []
    for f in os.listdir(project_dir):
        if f.endswith(".py") or f.endswith(".html"):
            files.append(f)
    return jsonify(files)

@app.route("/files/version", methods=["POST"])
@login_required
def save_version():
    data = request.get_json()
    filename = data.get("filename")
    content = data.get("content")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_dir = os.path.join("projects", "versions")
    os.makedirs(version_dir, exist_ok=True)
    path = os.path.join(version_dir, f"{filename}_{ts}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return jsonify({"status": "version saved", "path": path})

@app.route("/ai/review", methods=["POST"])
@login_required
def review_code():
    data = request.get_json()
    code = data.get("code", "")
    instruction = data.get("instruction", "Review or refactor this code.")
    client = openai.OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are The Architect. Improve or explain this code."},
                {"role": "user", "content": f"{instruction}\n\n```python\n{code}\n```"}
            ],
            temperature=0.7
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download")
@login_required
def download():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for root, _, files in os.walk(project_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_dir)
                zipf.write(full_path, rel_path)
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="project.zip")

def save_files_if_code(text):
    os.makedirs(project_dir, exist_ok=True)
    if "<html" in text:
        match = re.findall(r"<html[\s\S]*?</html>", text, re.IGNORECASE)
        if match:
            with open(os.path.join(project_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(match[0])
    py = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    if py:
        with open(os.path.join(project_dir, "app.py"), "w", encoding="utf-8") as f:
            f.write(py[0])

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
