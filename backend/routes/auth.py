from flask import Blueprint, request, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools
import sqlite3

# Create blueprint with URL prefix
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('tradzy.db')
        g.db.row_factory = sqlite3.Row
    return g.db

# Decorators for route protection
def login_required(view):
    """Decorator to require login for a route"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return view(**kwargs)
    return wrapped_view

def role_required(allowed_roles):
    """Decorator to require specific role(s) for a route"""
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            db = get_db()
            user = db.execute(
                'SELECT role FROM users WHERE id = ?', (session['user_id'],)
            ).fetchone()
            
            if not user or user['role'] not in allowed_roles:
                return jsonify({'error': 'Permission denied'}), 403
            
            return view(**kwargs)
        return wrapped_view
    return decorator



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password', 'email', 'role')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    if data['role'] not in ['admin', 'retailer', 'customer']:
        return jsonify({'error': 'Invalid role'}), 400
    
    try:
        db = get_db()
        
        # Check if username already exists
        if db.execute('SELECT id FROM users WHERE username = ?', 
                     (data['username'],)).fetchone() is not None:
            return jsonify({'error': 'Username already registered'}), 400
            
        # Check if email already exists
        if db.execute('SELECT id FROM users WHERE email = ?', 
                     (data['email'],)).fetchone() is not None:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash the password
        password_hash = generate_password_hash(data['password'])
        
        # Insert the new user
        db.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            (data['username'], password_hash, data['email'], data['role'])
        )
        db.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
        
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing username or password'}), 400
    
    try:
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (data['username'],)
        ).fetchone()
        
        if user is None:
            return jsonify({'error': 'Invalid username or password'}), 401
            
        if not check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Clear any existing session
        session.clear()
        # Store user info in session
        session['user_id'] = user['id']
        session['role'] = user['role']
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        })
        
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/check-auth')
def check_auth():
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 401
        
    try:
        db = get_db()
        user = db.execute(
            'SELECT id, username, email, role FROM users WHERE id = ?',
            (session['user_id'],)
        ).fetchone()
        
        if user is None:
            session.clear()
            return jsonify({'authenticated': False}), 401
            
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        })
        
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 400

