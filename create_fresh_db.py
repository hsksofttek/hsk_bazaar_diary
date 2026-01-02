#!/usr/bin/env python3
"""
Create Fresh Database Script
Forces Flask to create a new database with correct multi-user schema
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

# Import models
from models import db, User, Company, Party, Item, Purchase, Sale, Cashbook, Bankbook

def create_fresh_database():
    """Create a fresh database with correct schema"""
    
    print("🔧 Creating fresh database...")
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business_web.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Drop all tables and recreate
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        print("🏗️  Creating new tables...")
        db.create_all()
        
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
        
        # Create default company for admin
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
        
        print("✅ Database created successfully!")
        print(f"👤 Admin user created: admin / admin123")
        print(f"🏢 Default company created for admin")
        
        # Verify tables
        print("\n🔍 Verifying database schema...")
        tables = ['users', 'company', 'parties', 'items', 'purchases', 'sales', 'cashbook', 'bankbook']
        
        for table in tables:
            try:
                result = db.session.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in result]
                if 'user_id' in columns:
                    print(f"✅ {table}: user_id column exists")
                else:
                    print(f"❌ {table}: user_id column missing")
            except Exception as e:
                print(f"❌ {table}: Error checking table - {e}")
        
        print("\n🎉 Fresh database ready! You can now start the application.")

if __name__ == "__main__":
    create_fresh_database() 
 
 
 