#!/usr/bin/env python3
"""
Fix Ledger Table Structure
Ensure the ledger table matches our model definition
"""

import os
import sys
from sqlalchemy import text, inspect

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db

def fix_ledger_table():
    """Fix the ledger table structure"""
    print("🔧 Fixing Ledger Table Structure")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            # Check current table structure
            inspector = inspect(db.engine)
            ledger_columns = [col['name'] for col in inspector.get_columns('ledger')]
            print(f"Current ledger columns: {ledger_columns}")
            
            # Drop and recreate the ledger table with correct structure
            print("\n📋 Recreating Ledger table...")
            
            # Drop existing table
            db.session.execute(text("DROP TABLE IF EXISTS ledger"))
            db.session.commit()
            
            # Create new table with correct structure
            create_ledger_sql = """
            CREATE TABLE ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                party_cd VARCHAR(20) NOT NULL,
                narration TEXT,
                dr_amt FLOAT DEFAULT 0,
                cr_amt FLOAT DEFAULT 0,
                balance FLOAT DEFAULT 0,
                voucher_type VARCHAR(20),
                voucher_no VARCHAR(20),
                reference_no VARCHAR(50),
                sale_id INTEGER,
                purchase_id INTEGER,
                cashbook_id INTEGER,
                bankbook_id INTEGER,
                financial_year VARCHAR(10),
                month INTEGER,
                day INTEGER,
                balance_type VARCHAR(1),
                running_balance FLOAT DEFAULT 0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (purchase_id) REFERENCES purchases (id),
                FOREIGN KEY (cashbook_id) REFERENCES cashbook (id),
                FOREIGN KEY (bankbook_id) REFERENCES bankbook (id)
            )
            """
            
            db.session.execute(text(create_ledger_sql))
            db.session.commit()
            
            # Verify the new structure
            inspector = inspect(db.engine)
            new_ledger_columns = [col['name'] for col in inspector.get_columns('ledger')]
            print(f"New ledger columns: {new_ledger_columns}")
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_ledger_party_date ON ledger(party_cd, date)",
                "CREATE INDEX IF NOT EXISTS idx_ledger_financial_year ON ledger(financial_year)",
                "CREATE INDEX IF NOT EXISTS idx_ledger_user_date ON ledger(user_id, date)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    db.session.commit()
                    print(f"✅ Created index")
                except Exception as e:
                    print(f"ℹ️ Index creation: {e}")
            
            print("\n✅ Ledger table fixed successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing ledger table: {e}")
            return False

if __name__ == "__main__":
    print("🔧 Ledger Table Fix Tool")
    print("=" * 60)
    
    success = fix_ledger_table()
    
    if success:
        print("\n🎉 Ledger table has been fixed!")
        print("The table now has the correct structure for the enhanced business logic.")
    else:
        print("\n❌ Failed to fix ledger table.") 