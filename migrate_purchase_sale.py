#!/usr/bin/env python3
"""
Migration script to add purchase_id field to sales table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from sqlalchemy import text

def migrate_purchase_sale():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if purchase_id column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('sales') 
                WHERE name = 'purchase_id'
            """))
            
            if result.scalar() == 0:
                print("Adding purchase_id column to sales table...")
                
                # Add purchase_id column
                db.session.execute(text("""
                    ALTER TABLE sales ADD COLUMN purchase_id INTEGER 
                    REFERENCES purchases(id)
                """))
                
                db.session.commit()
                print("✅ purchase_id column added successfully!")
            else:
                print("✅ purchase_id column already exists!")
            
            # Add some sample items if they don't exist
            result = db.session.execute(text("SELECT COUNT(*) FROM items"))
            if result.scalar() == 0:
                print("Adding sample items...")
                
                sample_items = [
                    ("TOMATO", "TOMATO SUP", "KG", 300.0, "Vegetables"),
                    ("ONION", "ONION", "KG", 50.0, "Vegetables"),
                    ("POTATO", "POTATO", "KG", 40.0, "Vegetables"),
                    ("RICE", "RICE", "KG", 60.0, "Grains"),
                    ("WHEAT", "WHEAT", "KG", 35.0, "Grains")
                ]
                
                for item_code, item_name, unit, rate, category in sample_items:
                    db.session.execute(text("""
                        INSERT INTO items (it_cd, it_nm, unit, rate, category)
                        VALUES (:item_code, :item_name, :unit, :rate, :category)
                    """), {
                        'item_code': item_code,
                        'item_name': item_name,
                        'unit': unit,
                        'rate': rate,
                        'category': category
                    })
                
                db.session.commit()
                print("✅ Sample items added successfully!")
            else:
                print("✅ Items already exist in database!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration error: {e}")

if __name__ == '__main__':
    migrate_purchase_sale() 
 
 
 