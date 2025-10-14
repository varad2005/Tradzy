"""
⚠️ DEVELOPMENT HELPER SCRIPT ⚠️

Add sample products to database for e-commerce platform.
This replaces hardcoded HTML products with real database records.

NOTE: This script is useful for:
- Initial setup and testing
- Demonstrating the platform
- Development and staging environments

In PRODUCTION, products should be added through:
- The admin dashboard/panel
- Retailer product upload interface
- API endpoints with proper authentication
"""
import sqlite3
import os

# Connect to database using absolute path
db_path = os.path.join(os.path.dirname(__file__), 'tradzy.db')
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row
cursor = db.cursor()

# Sample products to add (real data, not dummy)
sample_products = [
    {
        'name': 'Premium Cotton T-Shirts',
        'description': 'High-quality 100% cotton t-shirts in various sizes and colors. Perfect for retail stores and promotional events. Available in S, M, L, XL sizes.',
        'price': 350.00,
        'stock': 5000,
        'category': 'Fashion',
        'min_order': 50,
        'retailer_id': 2,  # Retailer user
        'image_url': None
    },
    {
        'name': 'Smartphone Accessories Kit',
        'description': 'Complete smartphone accessory bundle including cases, screen protectors, and charging cables. Universal compatibility with most smartphone models.',
        'price': 799.00,
        'stock': 3000,
        'category': 'Electronics',
        'min_order': 25,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'Stainless Steel Kitchen Set',
        'description': 'Premium 15-piece stainless steel kitchen cookware set. Includes pots, pans, and utensils. Dishwasher safe and durable construction.',
        'price': 2499.00,
        'stock': 500,
        'category': 'Home & Kitchen',
        'min_order': 10,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'Industrial Safety Equipment',
        'description': 'Complete safety gear set including helmets, gloves, safety glasses, and reflective vests. Meets international safety standards.',
        'price': 1299.00,
        'stock': 1000,
        'category': 'Industrial',
        'min_order': 20,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'Yoga & Fitness Mat Set',
        'description': 'Eco-friendly non-slip yoga mats with carrying bag. 6mm thickness, perfect for yoga, pilates, and general fitness exercises.',
        'price': 499.00,
        'stock': 2000,
        'category': 'Sports & Fitness',
        'min_order': 30,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'LED Desk Lamps',
        'description': 'Energy-efficient LED desk lamps with adjustable brightness and color temperature. USB charging port included. Modern minimalist design.',
        'price': 899.00,
        'stock': 1500,
        'category': 'Electronics',
        'min_order': 20,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'Organic Cotton Bed Sheets',
        'description': '100% organic cotton bed sheet sets. Available in Queen and King sizes. Hypoallergenic and breathable fabric. Multiple color options.',
        'price': 1599.00,
        'stock': 800,
        'category': 'Home & Living',
        'min_order': 15,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'Bluetooth Wireless Speakers',
        'description': 'Portable wireless Bluetooth speakers with 12-hour battery life. Water-resistant design, perfect for outdoor use. High-quality sound output.',
        'price': 1299.00,
        'stock': 1200,
        'category': 'Electronics',
        'min_order': 25,
        'retailer_id': 2,
        'image_url': None
    },
    {
        'name': 'Professional Hair Care Set',
        'description': 'Complete salon-quality hair care set including shampoo, conditioner, and treatment products. Suitable for all hair types.',
        'price': 699.00,
        'stock': 2500,
        'category': 'Beauty & Personal Care',
        'min_order': 40,
        'retailer_id': 2,
        'image_url': None
    }
]

print("\n" + "="*70)
print("ADDING REAL PRODUCTS TO DATABASE")
print("="*70)

# Check if products table has the necessary columns
cursor.execute("PRAGMA table_info(products)")
columns = [col[1] for col in cursor.fetchall()]
print(f"\n✓ Products table columns: {', '.join(columns)}")

# Clear existing products (optional - comment out if you want to keep existing)
# cursor.execute("DELETE FROM products")
# print("\n✓ Cleared existing products")

added_count = 0
skipped_count = 0

for product in sample_products:
    try:
        # Check if product already exists
        cursor.execute("SELECT id FROM products WHERE name = ?", (product['name'],))
        existing = cursor.fetchone()
        
        if existing:
            print(f"\n⊝ Skipped: '{product['name']}' (already exists)")
            skipped_count += 1
            continue
        
        # Insert product
        cursor.execute('''
            INSERT INTO products (name, description, price, stock, retailer_id, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            product['name'],
            product['description'],
            product['price'],
            product['stock'],
            product['retailer_id'],
            product['image_url']
        ))
        
        print(f"\n✓ Added: '{product['name']}'")
        print(f"  Category: {product['category']}")
        print(f"  Price: ₹{product['price']:.2f}")
        print(f"  Stock: {product['stock']} units")
        print(f"  Min Order: {product['min_order']} pcs")
        
        added_count += 1
        
    except Exception as e:
        print(f"\n✗ Error adding '{product['name']}': {e}")

# Commit changes
db.commit()

# Verify products were added
cursor.execute("SELECT COUNT(*) as count FROM products")
total_products = cursor.fetchone()['count']

print("\n" + "="*70)
print(f"SUMMARY:")
print(f"  • Products added: {added_count}")
print(f"  • Products skipped: {skipped_count}")
print(f"  • Total products in database: {total_products}")
print("="*70)

db.close()

print("\n✅ Real product data is now ready!")
print("   Frontend can now fetch products from: GET /api/products\n")
