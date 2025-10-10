import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import secrets

def test_database_connection():
    print("Testing database connection...")
    try:
        # Create connection without database first
        connection = mysql.connector.connect(
            host="localhost",
            user=input("Enter MySQL username: "),
            password=input("Enter MySQL password: ")
        )
        
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            
            # Create database and tables
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS tradzy")
            print("Database 'tradzy' created successfully")
            
            # Switch to our database
            cursor.execute("USE tradzy")
            
            # Create tables
            tables = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    role ENUM('admin', 'retailer', 'customer') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    stock INT NOT NULL DEFAULT 0,
                    retailer_id INT,
                    image_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (retailer_id) REFERENCES users(id)
                )
                """
            ]
            
            for table_query in tables:
                cursor.execute(table_query)
                print("Table created successfully")
            
            connection.commit()
            
            # Create .env file
            env_content = f"""DB_HOST=localhost
DB_USER={connection.user}
DB_PASSWORD={connection.password}
DB_NAME=tradzy
SECRET_KEY={secrets.token_hex(24)}"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            print(".env file created successfully")
            
            cursor.close()
            connection.close()
            print("Database setup completed successfully!")
            return True
            
    except Error as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()