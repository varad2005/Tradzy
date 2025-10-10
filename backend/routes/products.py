from flask import Blueprint, request, jsonify, session
from app import get_db_connection
from functools import wraps

products_bp = Blueprint('products', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT p.*, u.username as retailer_name 
            FROM products p 
            LEFT JOIN users u ON p.retailer_id = u.id
        ''')
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/api/products', methods=['POST'])
@login_required
def add_product():
    try:
        if session['role'] != 'retailer':
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            INSERT INTO products (name, description, price, stock, retailer_id, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            data['name'],
            data['description'],
            data['price'],
            data['stock'],
            session['user_id'],
            data.get('image_url')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if the user owns the product or is an admin
        cursor.execute('SELECT retailer_id FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        
        if not product or (session['role'] != 'admin' and product['retailer_id'] != session['user_id']):
            return jsonify({'error': 'Unauthorized'}), 403
            
        cursor.execute('''
            UPDATE products 
            SET name = %s, description = %s, price = %s, stock = %s, image_url = %s
            WHERE id = %s
        ''', (
            data['name'],
            data['description'],
            data['price'],
            data['stock'],
            data.get('image_url'),
            product_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Product updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if the user owns the product or is an admin
        cursor.execute('SELECT retailer_id FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        
        if not product or (session['role'] != 'admin' and product['retailer_id'] != session['user_id']):
            return jsonify({'error': 'Unauthorized'}), 403
            
        cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400