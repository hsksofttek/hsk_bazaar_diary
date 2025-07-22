#!/usr/bin/env python3
"""
PostgreSQL Setup Script - Best Practice Implementation
Automatically sets up PostgreSQL for the multi-user business application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_postgresql_installation():
    """Check if PostgreSQL is installed"""
    print("🔍 Checking PostgreSQL installation...")
    
    try:
        # Try to connect to PostgreSQL
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password='postgres',
            database='postgres'
        )
        conn.close()
        print("✅ PostgreSQL is running and accessible!")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL not accessible: {e}")
        return False

def install_postgresql_windows():
    """Install PostgreSQL on Windows"""
    print("🔄 Installing PostgreSQL on Windows...")
    
    # Check if PostgreSQL is already installed
    pg_path = Path("C:/Program Files/PostgreSQL")
    if pg_path.exists():
        print("✅ PostgreSQL appears to be already installed!")
        return True
    
    print("📥 Please download and install PostgreSQL from:")
    print("   https://www.postgresql.org/download/windows/")
    print("   Use default settings:")
    print("   - Port: 5432")
    print("   - Username: postgres")
    print("   - Password: postgres")
    print("   - Database: postgres")
    
    input("Press Enter after installing PostgreSQL...")
    return check_postgresql_installation()

def setup_environment():
    """Set up environment variables"""
    print("⚙️ Setting up environment variables...")
    
    # Create .env file
    env_content = """# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=business_web
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with PostgreSQL configuration")
    else:
        print("✅ .env file already exists")

def create_database():
    """Create the business database"""
    print("🗄️ Creating business database...")
    
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password='postgres',
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'business_web'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE business_web")
            print("✅ Database 'business_web' created successfully!")
        else:
            print("✅ Database 'business_web' already exists!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_application():
    """Set up the Flask application with PostgreSQL"""
    print("🚀 Setting up Flask application...")
    
    try:
        # Import and run the PostgreSQL database creation script
        from create_postgresql_db import create_postgresql_database
        success = create_postgresql_database()
        
        if success:
            print("✅ Application setup complete!")
            return True
        else:
            print("❌ Application setup failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up application: {e}")
        return False

def main():
    """Main setup function"""
    print("🐘 PostgreSQL Setup for Multi-User Business Application")
    print("=" * 60)
    
    # Step 1: Check PostgreSQL installation
    if not check_postgresql_installation():
        system = platform.system()
        if system == "Windows":
            if not install_postgresql_windows():
                print("❌ PostgreSQL installation failed!")
                return False
        else:
            print(f"❌ Please install PostgreSQL on {system}")
            return False
    
    # Step 2: Set up environment
    setup_environment()
    
    # Step 3: Create database
    if not create_database():
        print("❌ Database creation failed!")
        return False
    
    # Step 4: Set up application
    if not setup_application():
        print("❌ Application setup failed!")
        return False
    
    print("\n🎉 PostgreSQL Setup Complete!")
    print("=" * 60)
    print("✅ PostgreSQL is installed and running")
    print("✅ Database 'business_web' is created")
    print("✅ Admin user: admin / admin123")
    print("✅ Environment variables are configured")
    print("\n🚀 Ready to start the application!")
    print("Run: python run.py")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1) 
 
 
 