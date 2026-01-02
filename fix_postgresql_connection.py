#!/usr/bin/env python3
"""
PostgreSQL Connection Troubleshooter
Helps fix connection issues with PostgreSQL
"""

import os
import sys
import subprocess
import psycopg2
from pathlib import Path

def check_postgresql_service():
    """Check if PostgreSQL service is running"""
    print("🔍 Checking PostgreSQL service status...")
    
    try:
        # Check if PostgreSQL service is running
        result = subprocess.run(['sc', 'query', 'postgresql'], 
                              capture_output=True, text=True, shell=True)
        
        if 'RUNNING' in result.stdout:
            print("✅ PostgreSQL service is running!")
            return True
        else:
            print("❌ PostgreSQL service is not running!")
            print("   Status:", result.stdout.strip())
            return False
            
    except Exception as e:
        print(f"❌ Error checking service: {e}")
        return False

def test_common_passwords():
    """Test common PostgreSQL passwords"""
    print("\n🔐 Testing common PostgreSQL passwords...")
    
    common_passwords = [
        'postgres',
        'password',
        'admin',
        '123456',
        'postgresql',
        '',  # empty password
        'root',
        'user'
    ]
    
    for password in common_passwords:
        try:
            print(f"   Testing password: '{password}'...")
            conn = psycopg2.connect(
                host='localhost',
                port='5432',
                user='postgres',
                password=password,
                database='postgres'
            )
            conn.close()
            print(f"✅ SUCCESS! Password is: '{password}'")
            return password
            
        except psycopg2.OperationalError as e:
            if 'password authentication failed' in str(e):
                print(f"   ❌ Wrong password")
            else:
                print(f"   ❌ Connection error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("❌ None of the common passwords worked!")
    return None

def create_database_with_password(password):
    """Create database with the correct password"""
    print(f"\n🗄️ Creating database with password: '{password}'...")
    
    try:
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=password,
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
        
        # Update .env file with correct password
        update_env_file(password)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def update_env_file(password):
    """Update .env file with correct password"""
    print(f"\n⚙️ Updating .env file with correct password...")
    
    env_content = f"""# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD={password}
DB_NAME=business_web
"""
    
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file updated with correct password!")

def setup_application_with_postgresql():
    """Set up the application with PostgreSQL"""
    print("\n🚀 Setting up application with PostgreSQL...")
    
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
    """Main troubleshooting function"""
    print("🐘 PostgreSQL Connection Troubleshooter")
    print("=" * 50)
    
    # Step 1: Check if service is running
    if not check_postgresql_service():
        print("\n💡 To start PostgreSQL service:")
        print("   1. Open Services (services.msc)")
        print("   2. Find 'postgresql' service")
        print("   3. Right-click and select 'Start'")
        print("   4. Or run: net start postgresql")
        return False
    
    # Step 2: Test passwords
    password = test_common_passwords()
    if not password:
        print("\n❌ Could not find correct password!")
        print("💡 Please check your PostgreSQL installation:")
        print("   1. What password did you set during installation?")
        print("   2. Try connecting with pgAdmin or psql")
        print("   3. Or reset the postgres user password")
        return False
    
    # Step 3: Create database
    if not create_database_with_password(password):
        print("❌ Database creation failed!")
        return False
    
    # Step 4: Set up application
    if not setup_application_with_postgresql():
        print("❌ Application setup failed!")
        return False
    
    print("\n🎉 PostgreSQL Setup Complete!")
    print("=" * 50)
    print("✅ PostgreSQL is connected and working")
    print("✅ Database 'business_web' is created")
    print("✅ Admin user: admin / admin123")
    print("✅ Environment variables are configured")
    print(f"✅ Password found: '{password}'")
    print("\n🚀 Ready to start the application!")
    print("Run: python run.py")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1) 
 
 
 