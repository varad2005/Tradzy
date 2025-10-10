from flask import Flask, jsonify, send_from_directory, request, session, g, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import secrets

# Create the Flask application
app = Flask(__name__, 
           static_url_path='/static',
           static_folder='../frontend/static',
           template_folder='../frontend/templates')

# Configure CORS to allow credentials
CORS(app, supports_credentials=True)

# Configure session
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Database setup
DATABASE = 'tradzy.db'

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Routes for serving pages
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/login')
def serve_login():
    return render_template('login.html')

@app.route('/admin')
def serve_admin():
    # Check if user is logged in and is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        return render_template('login.html')
    return render_template('admin.html')

@app.route('/retailer')
def serve_retailer():
    # Check if user is logged in and is a retailer
    if 'user_id' not in session or session.get('role') != 'retailer':
        return render_template('login.html')
    return render_template('retailer.html')

# Import auth blueprint and decorators
from routes.auth import auth_bp, login_required, role_required

# Test protected routes
@app.route('/api/test/user')
@login_required
def test_auth():
    return jsonify({'message': 'You are authenticated!'})

@app.route('/api/test/admin')
@role_required(['admin'])
def test_admin():
    return jsonify({'message': 'You have admin access!'})

@app.route('/api/test/retailer')
@role_required(['retailer'])
def test_retailer():
    return jsonify({'message': 'You have retailer access!'})

# Serve static files (CSS)
@app.route('/<path:filename>')
def serve_static(filename):
    if filename.endswith('.css'):
        return send_from_directory('.', filename)
    return render_template(filename)

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        hashed_password = generate_password_hash(data['password'])
        cursor.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            (data['username'], hashed_password, data['email'], data['role'])
        )
        db.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (data['username'],))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], data['password']):
            session['user_id'] = user['id']
            session['role'] = user['role']
            return jsonify({
                'user': dict(user)
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        return jsonify([dict(p) for p in products])
    
    if request.method == 'POST':
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.json
        cursor.execute(
            'INSERT INTO products (name, description, price, stock, retailer_id, image_url) VALUES (?, ?, ?, ?, ?, ?)',
            (data['name'], data['description'], data['price'], data['stock'], session['user_id'], data.get('image_url'))
        )
        db.commit()
        return jsonify({'message': 'Product added successfully'}), 201

@app.route('/api/products/<int:id>', methods=['PUT', 'DELETE'])
def product(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute(
            'UPDATE products SET name=?, description=?, price=?, stock=?, image_url=? WHERE id=? AND retailer_id=?',
            (data['name'], data['description'], data['price'], data['stock'], data.get('image_url'), id, session['user_id'])
        )
        db.commit()
        return jsonify({'message': 'Product updated successfully'})
    
    if request.method == 'DELETE':
        cursor.execute('DELETE FROM products WHERE id=? AND retailer_id=?', (id, session['user_id']))
        db.commit()
        return jsonify({'message': 'Product deleted successfully'})

# Initialize database on startup
with app.app_context():
    init_db()

# Register blueprints
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)