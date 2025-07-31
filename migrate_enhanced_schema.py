#!/usr/bin/env python3
"""
Database Migration Script for Enhanced Schema
Based on Legacy Software Analysis
"""

import os
import sys
from datetime import datetime, date
from sqlalchemy import text, inspect

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models import Party, Sale, Cashbook, Ledger

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_column_if_not_exists(table_name, column_name, column_type, default_value=None):
    """Add a column if it doesn't exist"""
    if not check_column_exists(table_name, column_name):
        try:
            if default_value is not None:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            
            db.session.execute(text(sql))
            db.session.commit()
            print(f"✅ Added column {column_name} to {table_name}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding column {column_name} to {table_name}: {e}")
            return False
    else:
        print(f"ℹ️ Column {column_name} already exists in {table_name}")
        return True

def create_table_if_not_exists(table_name, create_sql):
    """Create a table if it doesn't exist"""
    try:
        # Check if table exists
        result = db.session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
        if not result.fetchone():
            db.session.execute(text(create_sql))
            db.session.commit()
            print(f"✅ Created table {table_name}")
            return True
        else:
            print(f"ℹ️ Table {table_name} already exists")
            return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating table {table_name}: {e}")
        return False

def migrate_enhanced_schema():
    """Migrate database to enhanced schema based on legacy analysis"""
    print("🚀 Starting Enhanced Schema Migration...")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            # 1. Enhance Party table with credit management
            print("\n📋 Enhancing Party table...")
            party_enhancements = [
                ('parties', 'credit_limit', 'FLOAT DEFAULT 0'),
                ('parties', 'current_balance', 'FLOAT DEFAULT 0'),
                ('parties', 'payment_terms', 'VARCHAR(50)'),
                ('parties', 'last_payment_date', 'DATE'),
                ('parties', 'credit_status', 'VARCHAR(20) DEFAULT "ACTIVE"'),
                ('parties', 'opening_balance_date', 'DATE')
            ]
            
            for table, column, column_type in party_enhancements:
                add_column_if_not_exists(table, column, column_type)
            
            # 2. Enhance Sale table with payment tracking
            print("\n📋 Enhancing Sale table...")
            sale_enhancements = [
                ('sales', 'payment_status', 'VARCHAR(20) DEFAULT "PENDING"'),
                ('sales', 'payment_due_date', 'DATE'),
                ('sales', 'amount_paid', 'FLOAT DEFAULT 0'),
                ('sales', 'payment_terms', 'VARCHAR(50)'),
                ('sales', 'credit_days', 'INTEGER DEFAULT 0')
            ]
            
            for table, column, column_type in sale_enhancements:
                add_column_if_not_exists(table, column, column_type)
            
            # 3. Enhance Cashbook table with payment tracking
            print("\n📋 Enhancing Cashbook table...")
            cashbook_enhancements = [
                ('cashbook', 'related_sale_id', 'INTEGER'),
                ('cashbook', 'payment_type', 'VARCHAR(20)'),
                ('cashbook', 'reference_no', 'VARCHAR(50)'),
                ('cashbook', 'payment_method', 'VARCHAR(50)'),
                ('cashbook', 'bank_name', 'VARCHAR(100)'),
                ('cashbook', 'branch_name', 'VARCHAR(100)'),
                ('cashbook', 'cheque_date', 'DATE'),
                ('cashbook', 'transaction_date', 'DATETIME')
            ]
            
            for table, column, column_type in cashbook_enhancements:
                add_column_if_not_exists(table, column, column_type)
            
            # 4. Create Ledger table
            print("\n📋 Creating Ledger table...")
            ledger_create_sql = """
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
            create_table_if_not_exists('ledger', ledger_create_sql)
            
            # 5. Create indexes for better performance
            print("\n📋 Creating indexes...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_ledger_party_date ON ledger(party_cd, date)",
                "CREATE INDEX IF NOT EXISTS idx_ledger_financial_year ON ledger(financial_year)",
                "CREATE INDEX IF NOT EXISTS idx_sales_payment_status ON sales(payment_status)",
                "CREATE INDEX IF NOT EXISTS idx_cashbook_related_sale ON cashbook(related_sale_id)",
                "CREATE INDEX IF NOT EXISTS idx_parties_credit_status ON parties(credit_status)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    db.session.commit()
                    print(f"✅ Created index")
                except Exception as e:
                    db.session.rollback()
                    print(f"ℹ️ Index already exists or error: {e}")
            
            # 6. Update existing data
            print("\n📋 Updating existing data...")
            
            # Update party current balances
            parties = Party.query.all()
            for party in parties:
                try:
                    # Calculate current balance
                    from business_logic import CreditBusinessLogic
                    balance_info = CreditBusinessLogic.calculate_party_balance(party.party_cd, party.user_id)
                    party.current_balance = balance_info['current_balance']
                    party.modified_date = datetime.utcnow()
                    print(f"✅ Updated balance for party {party.party_cd}: {balance_info['current_balance']}")
                except Exception as e:
                    print(f"⚠️ Error updating party {party.party_cd}: {e}")
            
            # Update sale payment statuses
            sales = Sale.query.all()
            for sale in sales:
                try:
                    if sale.amount_paid >= sale.sal_amt:
                        sale.payment_status = 'PAID'
                    elif sale.amount_paid > 0:
                        sale.payment_status = 'PARTIAL'
                    else:
                        sale.payment_status = 'PENDING'
                    print(f"✅ Updated payment status for sale {sale.id}")
                except Exception as e:
                    print(f"⚠️ Error updating sale {sale.id}: {e}")
            
            db.session.commit()
            
            print("\n✅ Migration completed successfully!")
            print("\n📊 Migration Summary:")
            print("=" * 60)
            print("✅ Enhanced Party table with credit management")
            print("✅ Enhanced Sale table with payment tracking")
            print("✅ Enhanced Cashbook table with payment details")
            print("✅ Created comprehensive Ledger table")
            print("✅ Created performance indexes")
            print("✅ Updated existing data with new fields")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            return False

def verify_migration():
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            # Check if new columns exist
            inspector = inspect(db.engine)
            
            # Check Party table
            party_columns = [col['name'] for col in inspector.get_columns('parties')]
            required_party_columns = ['credit_limit', 'current_balance', 'payment_terms', 'credit_status']
            for col in required_party_columns:
                if col in party_columns:
                    print(f"✅ Party.{col} - OK")
                else:
                    print(f"❌ Party.{col} - Missing")
            
            # Check Sale table
            sale_columns = [col['name'] for col in inspector.get_columns('sales')]
            required_sale_columns = ['payment_status', 'amount_paid', 'payment_terms']
            for col in required_sale_columns:
                if col in sale_columns:
                    print(f"✅ Sale.{col} - OK")
                else:
                    print(f"❌ Sale.{col} - Missing")
            
            # Check Cashbook table
            cashbook_columns = [col['name'] for col in inspector.get_columns('cashbook')]
            required_cashbook_columns = ['related_sale_id', 'payment_type', 'reference_no']
            for col in required_cashbook_columns:
                if col in cashbook_columns:
                    print(f"✅ Cashbook.{col} - OK")
                else:
                    print(f"❌ Cashbook.{col} - Missing")
            
            # Check Ledger table
            ledger_columns = [col['name'] for col in inspector.get_columns('ledger')]
            if ledger_columns:
                print(f"✅ Ledger table exists with {len(ledger_columns)} columns")
            else:
                print(f"❌ Ledger table missing")
            
            print("\n✅ Verification completed!")
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Schema Migration Tool")
    print("Based on Legacy Software Analysis")
    print("=" * 60)
    
    # Run migration
    success = migrate_enhanced_schema()
    
    if success:
        # Verify migration
        verify_migration()
        
        print("\n🎉 Migration completed successfully!")
        print("The database now supports enhanced credit-based business logic.")
        print("You can now use the new business logic functions for:")
        print("• Real-time balance calculations")
        print("• Payment tracking and processing")
        print("• Credit limit management")
        print("• Comprehensive ledger entries")
    else:
        print("\n❌ Migration failed. Please check the errors above.") 