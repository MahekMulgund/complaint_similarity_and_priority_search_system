"""
Main Application Entry Point
Complaint Similarity Search and Priority Search System
"""
import sys
from app import create_app, seed_initial_data
from app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            # Create all MySQL tables if they do not exist
            db.create_all()
            # Seed default departments and categories
            seed_initial_data()
            print("==================================================")
            print(" MySQL Database connection established.")
            print(" All tables verified and seed data initialized.")
            print("==================================================")
        except Exception as e:
            print("==================================================")
            print(" WARNING: Could not connect to MySQL database.")
            print(f" Error: {e}")
            print(" Please check your .env credentials and ensure MySQL is running.")
            print("==================================================")

    print(" Starting development server at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
