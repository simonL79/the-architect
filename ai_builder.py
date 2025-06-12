from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from openai import OpenAI
import os
import psutil

# === Flask App Setup ===
app = Flask(__name__)
app.secret_key = 'super_secret_key'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'users.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

client = OpenAI()  # openai>=1.0 interface

# === User Model ===
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === Routes ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "❌ Invalid credentials.", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = User.query.filter_by(username=request.form['username']).first()
        if existing_user:
            return "⚠️ User already exists. Please log in.", 409
        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/system')
@login_required
def system_status():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    return {
        "cpu": cpu,
        "memory": memory
    }

@app.route('/ask', methods=['POST'])
@login_required
def ask():
    prompt = request.json.get('prompt', '')
    if not prompt:
        return {'response': '❌ No prompt received.'}, 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        return {'response': reply}
    except Exception as e:
        return {'response': f'❌ GPT error: {str(e)}'}, 500

# === Main Entry ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

