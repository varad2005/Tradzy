import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import secrets

def setup_database():
    # Generate a secure secret key
    secret_key = secrets.token_hex(24)
    
    try:
        # First connect without database to create it
        conn = mysql.connector.connect(
            host="localhost",
            user=input("Enter MySQL username: "),
            password=input("Enter MySQL password: ")
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS tradzy")
            print("Database 'tradzy' created successfully!")
            
            # Switch to our database
            cursor.execute("USE tradzy")
            
            # Read and execute schema file
            with open('schema.sql', 'r') as file:
                # Split into individual commands
                commands = file.read().split(';')
                for command in commands:
                    if command.strip():
                        cursor.execute(command)
                        conn.commit()
            
            print("Database tables created successfully!")
            
            # Create .env file with credentials
            env_content = f"""DB_HOST=localhost
DB_USER={conn.user}
DB_PASSWORD={conn.password}
DB_NAME=tradzy
SECRET_KEY={secret_key}"""
            
            with open('.env', 'w') as env_file:
                env_file.write(env_content)
            
            print(".env file created successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    setup_database()
    print("\nSetup completed! You can now run the Flask application.")