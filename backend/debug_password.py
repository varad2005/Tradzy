"""Debug password verification"""
import sqlite3
from werkzeug.security import check_password_hash

db = sqlite3.connect('tradzy.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

# Get the deadpool user
user = cursor.execute(
    'SELECT * FROM users WHERE email = ?',
    ('deadpool.ops106@gmail.com',)
).fetchone()

if user:
    print(f"\n✅ User found: {user['email']}")
    print(f"Username: {user['username']}")
    print(f"Role: {user['role']}")
    print(f"Password Hash: {user['password'][:50]}...")
    
    # Test password verification
    test_password = 'deadpool123'
    print(f"\n🔐 Testing password: '{test_password}'")
    
    result = check_password_hash(user['password'], test_password)
    print(f"Password verification result: {result}")
    
    if result:
        print("✅ Password verification successful!")
    else:
        print("❌ Password verification failed!")
        
else:
    print("❌ User not found!")

db.close()
