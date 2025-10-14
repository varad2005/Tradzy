"""Check users in database"""
import sqlite3

db = sqlite3.connect('tradzy.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

users = cursor.execute('SELECT id, username, email, role FROM users').fetchall()

print(f"\nFound {len(users)} users in database:")
print("-" * 70)

for user in users:
    print(f"ID: {user['id']:<3} | Username: {user['username']:<15} | Email: {user['email']:<30} | Role: {user['role']}")

print("-" * 70)
db.close()
