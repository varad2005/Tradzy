"""
⚠️ DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION ⚠️

Script to create test users for authentication testing.
This creates one admin and one retailer user with known credentials.

This script is for DEVELOPMENT and TESTING purposes only.
In production, users should register through the application
and use strong, unique passwords.
"""
import sqlite3
from werkzeug.security import generate_password_hash

# Database connection
db = sqlite3.connect('tradzy.db')
cursor = db.cursor()

# Test users with credentials
test_users = [
    {
        'username': 'admin',
        'email': 'admin@tradzy.com',
        'password': 'admin123',  # Plain text password - will be hashed
        'role': 'admin'
    },
    {
        'username': 'retailer',
        'email': 'retailer@tradzy.com',
        'password': 'retailer123',  # Plain text password - will be hashed
        'role': 'retailer'
    },
    {
        'username': 'deadpool',
        'email': 'deadpool.ops106@gmail.com',
        'password': 'deadpool123',  # Plain text password - will be hashed
        'role': 'admin'
    }
]

print("Creating test users...")
print("-" * 50)

for user in test_users:
    try:
        # Check if user already exists
        existing = cursor.execute(
            'SELECT id FROM users WHERE email = ?', 
            (user['email'],)
        ).fetchone()
        
        if existing:
            print(f"❌ User {user['email']} already exists. Skipping.")
            continue
        
        # Hash the password
        password_hash = generate_password_hash(user['password'])
        
        # Insert the user
        cursor.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            (user['username'], password_hash, user['email'], user['role'])
        )
        
        print(f"✅ Created {user['role']} user:")
        print(f"   Email: {user['email']}")
        print(f"   Password: {user['password']}")
        print()
        
    except Exception as e:
        print(f"❌ Error creating user {user['email']}: {e}")

# Commit the changes
db.commit()
db.close()

print("-" * 50)
print("✅ Test users creation complete!")
print("\nYou can now login with these credentials:")
print("1. Admin: admin@tradzy.com / admin123")
print("2. Retailer: retailer@tradzy.com / retailer123")
print("3. Admin (Deadpool): deadpool.ops106@gmail.com / deadpool123")
