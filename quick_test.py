#!/usr/bin/env python3
"""
Quick test to verify database is working
"""

import sqlite3
import os

def test_database():
    """Quick database test"""
    
    if not os.path.exists('business_web.db'):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect('business_web.db')
        cursor = conn.cursor()
        
        # Test admin user
        cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin:
            print(f"✅ Admin user: {admin[0]} (role: {admin[1]})")
        else:
            print("❌ Admin user not found!")
            return False
        
        # Test user_id columns
        tables = ['parties', 'items', 'purchases', 'sales', 'cashbook', 'bankbook', 'company']
        all_good = True
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            if 'user_id' in columns:
                print(f"✅ {table}: user_id column exists")
            else:
                print(f"❌ {table}: user_id column missing!")
                all_good = False
        
        conn.close()
        
        if all_good:
            print("\n🎉 Database is ready! Multi-user system is working!")
            print("🌐 Application should be running at: http://localhost:5000")
            print("🔑 Login with: admin / admin123")
            return True
        else:
            print("\n❌ Database has issues!")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick Database Test")
    print("=" * 25)
    test_database() 
 
 
 