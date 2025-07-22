"""
Test script to verify database schema and multi-user setup
"""

import sqlite3
import os

def test_database():
    """Test the database schema"""
    
    db_path = 'business_web.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    print("🔍 Testing database schema...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users table: {user_count} users")
        
        # Test admin user
        cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin:
            print(f"✅ Admin user found: {admin[0]} (role: {admin[1]})")
        else:
            print("❌ Admin user not found!")
        
        # Test tables with user_id columns
        tables_to_test = ['parties', 'items', 'purchases', 'sales', 'cashbook', 'bankbook', 'company']
        
        for table in tables_to_test:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' in columns:
                print(f"✅ {table} table: user_id column exists")
                
                # Count records
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   📊 {table}: {count} records")
            else:
                print(f"❌ {table} table: user_id column missing!")
        
        # Test foreign key relationships
        print("\n🔗 Testing foreign key relationships...")
        
        # Test admin user ID
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_id = cursor.fetchone()[0]
        print(f"✅ Admin user ID: {admin_id}")
        
        # Test company for admin
        cursor.execute("SELECT name FROM company WHERE user_id = ?", (admin_id,))
        company = cursor.fetchone()
        if company:
            print(f"✅ Company for admin: {company[0]}")
        else:
            print("❌ No company found for admin")
        
        conn.close()
        print("\n🎉 Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🧪 Database Test Tool")
    print("=" * 30)
    test_database() 
 
 
 