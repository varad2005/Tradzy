from flask import Blueprint, request, jsonify, session
from app import get_db_connection
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT id, username, email, role, created_at FROM users')
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total users by role
        cursor.execute('''
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role
        ''')
        user_stats = cursor.fetchall()
        
        # Get total products
        cursor.execute('SELECT COUNT(*) as total_products FROM products')
        product_stats = cursor.fetchone()
        
        # Get total orders
        cursor.execute('SELECT COUNT(*) as total_orders FROM orders')
        order_stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'users': user_stats,
            'products': product_stats,
            'orders': order_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400