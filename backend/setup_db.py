import sqlite3
import os
import secrets

def setup_database():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('tradzy.db')
    
    try:
        # Read and execute the schema.sql file
        with open('schema.sql', 'r') as schema_file:
            conn.executescript(schema_file.read())
        
        # Make sure changes are committed
        conn.commit()
        
        # Generate a random secret key for Flask
        secret_key = secrets.token_hex(16)
        
        # Create .env file with the secret key
        env_content = f"SECRET_KEY={secret_key}"
        with open('.env', 'w') as env_file:
            env_file.write(env_content)
        
        print("SQLite database setup completed successfully!")
        print("Database file: tradzy.db")
        print(".env file created with new secret key")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()