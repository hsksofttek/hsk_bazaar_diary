"""
Database Reset Script for Multi-User System
Recreates the database with new schema including user_id columns
"""

import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def reset_database():
    """Reset and recreate the database with multi-user schema"""
    
    db_path = 'business_web.db'
    
    # Remove existing database
    if os.path.exists(db_path):
        print(f"🗑️  Removing existing database: {db_path}")
        os.remove(db_path)
    
    print("🔄 Creating new database with multi-user schema...")
    
    try:
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        """)
        print("✅ Created users table")
        
        # Create company table with user_id
        cursor.execute("""
            CREATE TABLE company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name VARCHAR(200) NOT NULL,
                address1 VARCHAR(200),
                address2 VARCHAR(200),
                city VARCHAR(100),
                phone VARCHAR(20),
                from_date DATE,
                to_date DATE,
                password VARCHAR(100),
                directory VARCHAR(200),
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✅ Created company table")
        
        # Create parties table with user_id
        cursor.execute("""
            CREATE TABLE parties (
                party_cd VARCHAR(20) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                party_nm VARCHAR(200) NOT NULL,
                party_nm_hindi VARCHAR(200),
                place VARCHAR(100),
                phone VARCHAR(20),
                bal_cd VARCHAR(1) DEFAULT 'D',
                ly_baln FLOAT DEFAULT 0,
                ytd_dr FLOAT DEFAULT 0,
                ytd_cr FLOAT DEFAULT 0,
                address1 VARCHAR(200),
                address2 VARCHAR(200),
                address3 VARCHAR(200),
                po VARCHAR(50),
                dist VARCHAR(50),
                contact VARCHAR(100),
                state VARCHAR(50),
                pin VARCHAR(10),
                phone1 VARCHAR(20),
                phone2 VARCHAR(20),
                phone3 VARCHAR(20),
                cst_no VARCHAR(50),
                cst_dt DATE,
                trate FLOAT DEFAULT 0,
                agent_cd VARCHAR(20),
                cat VARCHAR(50),
                lpperc FLOAT DEFAULT 0,
                "limit" FLOAT DEFAULT 0,
                ledgtyp VARCHAR(20),
                dis FLOAT DEFAULT 0,
                trans_cd VARCHAR(20),
                pgno INTEGER,
                agent_nm VARCHAR(100),
                p_bal FLOAT DEFAULT 0,
                phone4 VARCHAR(20),
                phone5 VARCHAR(20),
                phone6 VARCHAR(20),
                phone7 VARCHAR(20),
                phone8 VARCHAR(20),
                bst_no VARCHAR(50),
                bst_dt DATE,
                vat_no VARCHAR(50),
                acode VARCHAR(20),
                area VARCHAR(50),
                ly_cd VARCHAR(20),
                cr_dr VARCHAR(1),
                amount FLOAT DEFAULT 0,
                page_no INTEGER,
                group_cd VARCHAR(20),
                group_nm VARCHAR(100),
                gstin VARCHAR(20),
                pan VARCHAR(20),
                email VARCHAR(100),
                fax VARCHAR(20),
                mobile VARCHAR(20),
                opening_bal FLOAT DEFAULT 0,
                closing_bal FLOAT DEFAULT 0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✅ Created parties table")
        
        # Create items table with user_id
        cursor.execute("""
            CREATE TABLE items (
                it_cd VARCHAR(20) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                it_nm VARCHAR(200) NOT NULL,
                unit VARCHAR(10) DEFAULT 'KG',
                rate FLOAT DEFAULT 0,
                category VARCHAR(100),
                it_size VARCHAR(50),
                colo_cd VARCHAR(20),
                pkgs VARCHAR(50),
                mrp FLOAT DEFAULT 0,
                sprc FLOAT DEFAULT 0,
                pkt FLOAT DEFAULT 0,
                cat_cd VARCHAR(20),
                maxrt FLOAT DEFAULT 0,
                minrt FLOAT DEFAULT 0,
                taxpr FLOAT DEFAULT 0,
                hamrt FLOAT DEFAULT 0,
                itwt FLOAT DEFAULT 0,
                ccess INTEGER DEFAULT 0,
                hsn VARCHAR(20),
                gst FLOAT DEFAULT 0,
                cess FLOAT DEFAULT 0,
                batch VARCHAR(50),
                exp_date DATE,
                barcode VARCHAR(50),
                rack VARCHAR(50),
                shelf VARCHAR(50),
                reorder_level FLOAT DEFAULT 0,
                opening_stock FLOAT DEFAULT 0,
                closing_stock FLOAT DEFAULT 0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✅ Created items table")
        
        # Create purchases table with user_id
        cursor.execute("""
            CREATE TABLE purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bill_no INTEGER NOT NULL,
                bill_date DATE NOT NULL,
                party_cd VARCHAR(20) NOT NULL,
                it_cd VARCHAR(20) NOT NULL,
                qty FLOAT NOT NULL DEFAULT 0,
                katta FLOAT DEFAULT 0,
                tot_smt FLOAT DEFAULT 0,
                rate FLOAT NOT NULL DEFAULT 0,
                sal_amt FLOAT NOT NULL DEFAULT 0,
                order_no VARCHAR(50),
                order_dt DATE,
                it_size VARCHAR(50),
                colo_cd VARCHAR(20),
                pack FLOAT DEFAULT 0,
                smt FLOAT DEFAULT 0,
                f_smt FLOAT DEFAULT 0,
                b_code INTEGER,
                st FLOAT DEFAULT 0,
                stcd VARCHAR(20),
                discount FLOAT DEFAULT 0,
                tot_amt FLOAT DEFAULT 0,
                trans VARCHAR(50),
                lrno VARCHAR(50),
                lr_dt DATE,
                agent_cd VARCHAR(20),
                remark TEXT,
                gdn_cd VARCHAR(20),
                name VARCHAR(100),
                lo INTEGER DEFAULT 0,
                bc INTEGER DEFAULT 0,
                pkgs VARCHAR(50),
                scheme VARCHAR(100),
                less FLOAT DEFAULT 0,
                otexp FLOAT DEFAULT 0,
                expdt DATE,
                sp FLOAT DEFAULT 0,
                cd FLOAT DEFAULT 0,
                comm FLOAT DEFAULT 0,
                nara TEXT,
                short FLOAT DEFAULT 0,
                truck_no VARCHAR(20),
                exp1 FLOAT DEFAULT 0,
                exp2 FLOAT DEFAULT 0,
                exp3 FLOAT DEFAULT 0,
                exp4 FLOAT DEFAULT 0,
                exp5 FLOAT DEFAULT 0,
                taxamt FLOAT DEFAULT 0,
                cash_date DATE,
                lr_no VARCHAR(50),
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                FOREIGN KEY (it_cd) REFERENCES items (it_cd)
            )
        """)
        print("✅ Created purchases table")
        
        # Create sales table with user_id
        cursor.execute("""
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bill_no INTEGER NOT NULL,
                bill_date DATE NOT NULL,
                party_cd VARCHAR(20) NOT NULL,
                it_cd VARCHAR(20) NOT NULL,
                qty FLOAT NOT NULL DEFAULT 0,
                katta FLOAT DEFAULT 0,
                tot_smt FLOAT DEFAULT 0,
                rate FLOAT NOT NULL DEFAULT 0,
                sal_amt FLOAT NOT NULL DEFAULT 0,
                order_no VARCHAR(50),
                order_dt DATE,
                it_size VARCHAR(50),
                colo_cd VARCHAR(20),
                pack FLOAT DEFAULT 0,
                smt FLOAT DEFAULT 0,
                f_smt FLOAT DEFAULT 0,
                b_code INTEGER,
                st FLOAT DEFAULT 0,
                stcd VARCHAR(20),
                discount FLOAT DEFAULT 0,
                tot_amt FLOAT DEFAULT 0,
                trans VARCHAR(50),
                lrno VARCHAR(50),
                lr_dt DATE,
                agent_cd VARCHAR(20),
                remark TEXT,
                gdn_cd VARCHAR(20),
                name VARCHAR(100),
                lo INTEGER DEFAULT 0,
                bc INTEGER DEFAULT 0,
                pkgs VARCHAR(50),
                scheme VARCHAR(100),
                less FLOAT DEFAULT 0,
                otexp FLOAT DEFAULT 0,
                expdt DATE,
                sp FLOAT DEFAULT 0,
                cd FLOAT DEFAULT 0,
                comm FLOAT DEFAULT 0,
                nara TEXT,
                short FLOAT DEFAULT 0,
                truck_no VARCHAR(20),
                exp1 FLOAT DEFAULT 0,
                exp2 FLOAT DEFAULT 0,
                exp3 FLOAT DEFAULT 0,
                exp4 FLOAT DEFAULT 0,
                exp5 FLOAT DEFAULT 0,
                taxamt FLOAT DEFAULT 0,
                cash_date DATE,
                lr_no VARCHAR(50),
                purchase_id INTEGER,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                FOREIGN KEY (it_cd) REFERENCES items (it_cd),
                FOREIGN KEY (purchase_id) REFERENCES purchases (id)
            )
        """)
        print("✅ Created sales table")
        
        # Create cashbook table with user_id
        cursor.execute("""
            CREATE TABLE cashbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                narration TEXT,
                dr_amt FLOAT DEFAULT 0,
                cr_amt FLOAT DEFAULT 0,
                balance FLOAT DEFAULT 0,
                party_cd VARCHAR(20),
                voucher_type VARCHAR(20),
                voucher_no VARCHAR(20),
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
            )
        """)
        print("✅ Created cashbook table")
        
        # Create bankbook table with user_id
        cursor.execute("""
            CREATE TABLE bankbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                narration TEXT,
                dr_amt FLOAT DEFAULT 0,
                cr_amt FLOAT DEFAULT 0,
                balance FLOAT DEFAULT 0,
                party_cd VARCHAR(20),
                voucher_type VARCHAR(20),
                voucher_no VARCHAR(20),
                bank_name VARCHAR(100),
                account_no VARCHAR(50),
                cheque_no VARCHAR(20),
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
            )
        """)
        print("✅ Created bankbook table")
        
        # Create admin user
        password_hash = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, is_active, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('admin', 'admin@example.com', password_hash, 'admin', True, datetime.utcnow()))
        
        admin_id = cursor.lastrowid
        print("✅ Created admin user")
        
        # Create default company for admin
        cursor.execute("""
            INSERT INTO company (user_id, name, created_date)
            VALUES (?, ?, ?)
        """, (admin_id, 'Default Company', datetime.utcnow()))
        print("✅ Created default company")
        
        # Commit all changes
        conn.commit()
        print("✅ Database reset completed successfully!")
        
        print(f"\n🔑 Admin Login Credentials:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Database Reset Tool for Multi-User System")
    print("=" * 50)
    print("⚠️  WARNING: This will delete all existing data!")
    print("   Only use this if migration doesn't work.")
    print("=" * 50)
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        if reset_database():
            print("\n🎉 Database reset completed!")
            print("You can now run the application with multi-user support.")
        else:
            print("\n❌ Database reset failed!")
    else:
        print("❌ Operation cancelled.") 
 
 
 