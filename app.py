from flask import Flask, jsonify, render_template, request, Response, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from partScraper import runScraper
from flask_cors import CORS
from functools import wraps
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexbitpythontasks'  # It's better to use an environment variable for this
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session timeout to 30 minutes
CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be an admin to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/proxy', methods=['POST'])
@login_required
def proxy():
    api_url = 'https://importglasscorp.com/ajax.php'
    data = request.get_data()
    headers = {
        'Content-Type': request.headers.get('Content-Type')
    }
    try:
        response = requests.post(api_url, data=data, headers=headers)
        response.raise_for_status()
        return Response(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vehicle-lookup', methods=['GET'])
@login_required
def vehicleLookup():
    return render_template('vehicle-lookup.html')

@app.route('/part-search/<partNumber>', methods=['GET'])
@login_required
def partSearch(partNumber):
    return render_template('products.html', data=partNumber)

@app.route('/products/<partNumber>', methods=['GET'])
@login_required
def products(partNumber):
    data = runScraper(partNumber)
    return jsonify(data)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists')
            return redirect(url_for('add_user'))
        
        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('New user added successfully.')
        return redirect(url_for('index'))
    return render_template('add_user.html')

def init_db():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('adminpassword')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5001, debug=True)