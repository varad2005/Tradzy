"""
Test database auto-initialization functionality.
This script verifies that the database tables are created automatically.
"""
import sqlite3
import os
from pathlib import Path

def test_database_exists():
    """Test if database file and tables exist."""
    db_path = Path("backend/tradzy.db")
    
    print("🔍 Testing Database Auto-Initialization")
    print("=" * 60)
    
    # Check if database file exists
    if db_path.exists():
        print(f"✅ Database file exists: {db_path}")
    else:
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Connect and check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of all tables
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Found {len(tables)} tables:")
    for table in tables:
        print(f"   ✅ {table}")
    
    # Check for required tables
    required_tables = [
        'users', 'products', 'orders', 'order_items',
        'carts', 'cart_items', 'wishlists', 'wishlist_items',
        'contact_messages'
    ]
    
    print(f"\n🔎 Checking required tables:")
    all_present = True
    for table in required_tables:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} - MISSING!")
            all_present = False
    
    # Check users table structure
    print(f"\n👤 Users table structure:")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, name, col_type, notnull, default, pk = col
        print(f"   - {name} ({col_type}){' PRIMARY KEY' if pk else ''}{' NOT NULL' if notnull else ''}")
    
    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\n👥 Total users in database: {user_count}")
    
    if user_count > 0:
        cursor.execute("SELECT username, email, role FROM users LIMIT 5")
        users = cursor.fetchall()
        print("   Sample users:")
        for username, email, role in users:
            print(f"   - {username} ({role}) - {email}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    if all_present:
        print("✅ All required tables exist - Database is properly initialized!")
        return True
    else:
        print("❌ Some tables are missing - Database initialization incomplete!")
        return False

if __name__ == "__main__":
    success = test_database_exists()
    exit(0 if success else 1)