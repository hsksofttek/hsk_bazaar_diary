"""
Database Migration Script for Multi-User System
Adds user_id columns to all business tables
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the database to add user_id columns"""
    
    # Database file path
    db_path = 'business_web.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    print("🔄 Starting database migration for multi-user system...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current user (admin) ID
        cursor.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ Admin user not found! Creating admin user first...")
            # Create admin user if not exists
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@example.com', 
                  'pbkdf2:sha256:600000$your_hash_here', 'admin', True, datetime.utcnow()))
            conn.commit()
            
            cursor.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
            admin_user = cursor.fetchone()
        
        admin_id = admin_user[0]
        print(f"✅ Using admin user ID: {admin_id}")
        
        # List of tables to migrate
        tables_to_migrate = [
            'parties',
            'items', 
            'purchases',
            'sales',
            'cashbook',
            'bankbook',
            'company'
        ]
        
        for table in tables_to_migrate:
            print(f"🔄 Migrating table: {table}")
            
            # Check if user_id column already exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                # Add user_id column
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")
                print(f"  ✅ Added user_id column to {table}")
                
                # Update existing records with admin user_id
                cursor.execute(f"UPDATE {table} SET user_id = ? WHERE user_id IS NULL", (admin_id,))
                updated_count = cursor.rowcount
                print(f"  ✅ Updated {updated_count} records in {table}")
            else:
                print(f"  ⏭️  user_id column already exists in {table}")
        
        # Commit all changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        for table in tables_to_migrate:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = ?", (admin_id,))
            count = cursor.fetchone()[0]
            print(f"  📊 {table}: {count} records assigned to admin user")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def create_admin_user():
    """Create admin user if not exists"""
    from werkzeug.security import generate_password_hash
    
    db_path = 'business_web.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            # Create admin user
            password_hash = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@example.com', password_hash, 'admin', True, datetime.utcnow()))
            
            conn.commit()
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
        else:
            print("✅ Admin user already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Database Migration Tool for Multi-User System")
    print("=" * 50)
    
    # First create admin user
    if create_admin_user():
        # Then migrate database
        if migrate_database():
            print("\n🎉 Migration completed successfully!")
            print("You can now run the application with multi-user support.")
        else:
            print("\n❌ Migration failed!")
    else:
        print("\n❌ Failed to create admin user!") 
 
 
 