#!/bin/bash
# Render deployment initialization script

echo "Starting Tradzy Backend Deployment..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
cd backend
python -c "from db import init_db; init_db()"
cd ..

echo "Deployment preparation complete!"
