#!/usr/bin/env python3
"""
Create PostgreSQL Database with Multi-User Schema
Sets up PostgreSQL database with all tables and user_id columns
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Import models
from models import db, User, Company, Party, Item, Purchase, Sale, Cashbook, Bankbook

def create_postgresql_database():
    """Create PostgreSQL database and tables"""
    
    print("🐘 Setting up PostgreSQL Database...")
    
    # PostgreSQL connection details
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    DB_NAME = os.environ.get('DB_NAME', 'business_web')
    
    # Connect to PostgreSQL server (not specific database)
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📦 Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' created successfully!")
        else:
            print(f"✅ Database '{DB_NAME}' already exists!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("Please make sure PostgreSQL is running and credentials are correct.")
        return False
    
    # Create Flask app with PostgreSQL
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            print("🏗️ Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Create admin user
                print("👤 Creating admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    is_active=True,
                    created_date=datetime.now()
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created: admin / admin123")
            else:
                print("✅ Admin user already exists")
            
            # Create default company for admin
            company = Company.query.filter_by(user_id=admin_user.id).first()
            if not company:
                print("🏢 Creating default company...")
                default_company = Company(
                    name='Default Company',
                    address1='Default Address',
                    phone='1234567890',
                    user_id=admin_user.id,
                    created_date=datetime.now()
                )
                db.session.add(default_company)
                db.session.commit()
                print("✅ Default company created for admin")
            else:
                print("✅ Default company already exists")
            
            print("\n🎉 PostgreSQL Database Setup Complete!")
            print(f"📊 Database: {DB_NAME}")
            print(f"👤 Admin User: admin / admin123")
            print(f"🔗 Connection: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

if __name__ == '__main__':
    success = create_postgresql_database()
    if success:
        print("\n✅ Ready to start the application!")
        print("Run: python run.py")
    else:
        print("\n❌ Setup failed. Please check PostgreSQL configuration.") 
 
 
 