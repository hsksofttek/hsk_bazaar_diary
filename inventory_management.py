#!/usr/bin/env python3
"""
Advanced Inventory Management System
Complete implementation with stock management, movements, adjustments, and reports
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json
from database import db
from models import Item, Purchase, Sale, User
from sqlalchemy import func, and_, or_, desc, asc
import uuid

class InventoryManagementSystem:
    """Complete Inventory Management System with full functionality"""
    
    def __init__(self):
        self.system_name = "Inventory Management System"
        self.version = "2.0"
    
    # ==================== ITEM MANAGEMENT ====================
    
    def add_inventory_item(self, user_id: int, item_data: Dict) -> Dict:
        """Add new inventory item"""
        try:
            # Check if item code already exists
            existing_item = Item.query.filter_by(it_cd=item_data['item_code'], user_id=user_id).first()
            if existing_item:
                return {'success': False, 'error': f"Item with code {item_data['item_code']} already exists"}
            
            # Create new item
            new_item = Item(
                user_id=user_id,
                it_cd=item_data['item_code'],
                it_nm=item_data['item_name'],
                unit=item_data.get('unit', 'KG'),
                rate=float(item_data.get('rate', 0)),
                category=item_data.get('category', ''),
                it_size=item_data.get('size', ''),
                mrp=float(item_data.get('mrp', 0)),
                sprc=float(item_data.get('sale_price', 0)),
                taxpr=float(item_data.get('tax_percentage', 0)),
                hsn=item_data.get('hsn_code', ''),
                gst=float(item_data.get('gst_rate', 0)),
                reorder_level=float(item_data.get('reorder_level', 0)),
                opening_stock=float(item_data.get('opening_stock', 0)),
                closing_stock=float(item_data.get('opening_stock', 0))  # Initially same as opening
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Item {item_data["item_name"]} added successfully',
                'item_code': item_data['item_code']
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def update_inventory_item(self, user_id: int, item_code: str, updates: Dict) -> Dict:
        """Update inventory item"""
        try:
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Update fields
            if 'item_name' in updates:
                item.it_nm = updates['item_name']
            if 'unit' in updates:
                item.unit = updates['unit']
            if 'rate' in updates:
                item.rate = float(updates['rate'])
            if 'category' in updates:
                item.category = updates['category']
            if 'mrp' in updates:
                item.mrp = float(updates['mrp'])
            if 'sale_price' in updates:
                item.sprc = float(updates['sale_price'])
            if 'reorder_level' in updates:
                item.reorder_level = float(updates['reorder_level'])
            if 'tax_percentage' in updates:
                item.taxpr = float(updates['tax_percentage'])
            if 'gst_rate' in updates:
                item.gst = float(updates['gst_rate'])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Item {item_code} updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def delete_inventory_item(self, user_id: int, item_code: str) -> Dict:
        """Delete inventory item"""
        try:
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Check if item is used in transactions
            purchase_count = Purchase.query.filter_by(it_cd=item_code, user_id=user_id).count()
            sale_count = Sale.query.filter_by(it_cd=item_code, user_id=user_id).count()
            
            if purchase_count > 0 or sale_count > 0:
                return {'success': False, 'error': 'Cannot delete item that has transaction history'}
            
            db.session.delete(item)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Item {item_code} deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_inventory_item(self, user_id: int, item_code: str) -> Dict:
        """Get inventory item details"""
        try:
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Calculate current stock
            current_stock = self._calculate_current_stock(user_id, item_code)
            
            return {
                'success': True,
                'item': {
                    'item_code': item.it_cd,
                    'item_name': item.it_nm,
                    'unit': item.unit,
                    'rate': float(item.rate),
                    'category': item.category,
                    'size': item.it_size,
                    'mrp': float(item.mrp),
                    'sale_price': float(item.sprc),
                    'tax_percentage': float(item.taxpr),
                    'gst_rate': float(item.gst),
                    'reorder_level': float(item.reorder_level),
                    'opening_stock': float(item.opening_stock),
                    'current_stock': current_stock,
                    'hsn_code': item.hsn,
                    'created_date': item.created_date.strftime('%Y-%m-%d') if item.created_date else None
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== STOCK MANAGEMENT ====================
    
    def update_stock(self, user_id: int, item_code: str, quantity: float, 
                    movement_type: str, reference: str = '', notes: str = '') -> Dict:
        """Update stock levels"""
        try:
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            current_stock = self._calculate_current_stock(user_id, item_code)
            
            # Calculate new stock
            if movement_type == 'IN':
                new_stock = current_stock + quantity
            elif movement_type == 'OUT':
                if current_stock < quantity:
                    return {'success': False, 'error': 'Insufficient stock for this movement'}
                new_stock = current_stock - quantity
            else:
                return {'success': False, 'error': 'Invalid movement type'}
            
            # Update closing stock
            item.closing_stock = new_stock
            
            # Create stock movement record (in a real system, you'd have a separate table)
            # For now, we'll use the item's remark field to track movements
            movement_note = f"{movement_type}: {quantity} {item.unit} - {notes} (Ref: {reference})"
            item.remark = movement_note
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Stock updated successfully',
                'item_code': item_code,
                'movement_type': movement_type,
                'quantity': quantity,
                'previous_stock': current_stock,
                'new_stock': new_stock
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_stock_status(self, user_id: int, item_code: str = None) -> Dict:
        """Get stock status for items"""
        try:
            if item_code:
                # Get specific item stock
                item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
                if not item:
                    return {'success': False, 'error': 'Item not found'}
                
                current_stock = self._calculate_current_stock(user_id, item_code)
                
                return {
                    'success': True,
                    'stock_status': {
                        'item_code': item.it_cd,
                        'item_name': item.it_nm,
                        'current_stock': current_stock,
                        'unit': item.unit,
                        'reorder_level': float(item.reorder_level),
                        'status': 'Low Stock' if current_stock <= item.reorder_level else 'Normal',
                        'rate': float(item.rate),
                        'value': current_stock * item.rate
                    }
                }
            else:
                # Get all items stock status
                items = Item.query.filter_by(user_id=user_id).all()
                stock_status = []
                
                for item in items:
                    current_stock = self._calculate_current_stock(user_id, item.it_cd)
                    stock_status.append({
                        'item_code': item.it_cd,
                        'item_name': item.it_nm,
                        'current_stock': current_stock,
                        'unit': item.unit,
                        'reorder_level': float(item.reorder_level),
                        'status': 'Low Stock' if current_stock <= item.reorder_level else 'Normal',
                        'rate': float(item.rate),
                        'value': current_stock * item.rate
                    })
                
                return {
                    'success': True,
                    'stock_status': stock_status
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_low_stock_alerts(self, user_id: int) -> Dict:
        """Get low stock alerts"""
        try:
            items = Item.query.filter_by(user_id=user_id).all()
            low_stock_items = []
            
            for item in items:
                current_stock = self._calculate_current_stock(user_id, item.it_cd)
                if current_stock <= item.reorder_level:
                    low_stock_items.append({
                        'item_code': item.it_cd,
                        'item_name': item.it_nm,
                        'current_stock': current_stock,
                        'reorder_level': float(item.reorder_level),
                        'unit': item.unit,
                        'shortage': item.reorder_level - current_stock
                    })
            
            return {
                'success': True,
                'low_stock_alerts': low_stock_items,
                'alert_count': len(low_stock_items)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== STOCK MOVEMENTS ====================
    
    def get_stock_movements(self, user_id: int, item_code: str = None, 
                           start_date: str = None, end_date: str = None) -> Dict:
        """Get stock movements"""
        try:
            movements = []
            
            # Get purchase movements (IN)
            purchase_query = Purchase.query.filter(Purchase.user_id == user_id)
            if item_code:
                purchase_query = purchase_query.filter(Purchase.it_cd == item_code)
            if start_date:
                purchase_query = purchase_query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                purchase_query = purchase_query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            purchases = purchase_query.all()
            for purchase in purchases:
                movements.append({
                    'date': purchase.bill_date.strftime('%Y-%m-%d'),
                    'item_code': purchase.it_cd,
                    'movement_type': 'IN',
                    'quantity': float(purchase.qty),
                    'reference': f"Purchase Bill {purchase.bill_no}",
                    'party_code': purchase.party_cd,
                    'rate': float(purchase.rate),
                    'amount': float(purchase.sal_amt)
                })
            
            # Get sales movements (OUT)
            sale_query = Sale.query.filter(Sale.user_id == user_id)
            if item_code:
                sale_query = sale_query.filter(Sale.it_cd == item_code)
            if start_date:
                sale_query = sale_query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                sale_query = sale_query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            sales = sale_query.all()
            for sale in sales:
                movements.append({
                    'date': sale.bill_date.strftime('%Y-%m-%d'),
                    'item_code': sale.it_cd,
                    'movement_type': 'OUT',
                    'quantity': float(sale.qty),
                    'reference': f"Sales Bill {sale.bill_no}",
                    'party_code': sale.party_cd,
                    'rate': float(sale.rate),
                    'amount': float(sale.sal_amt)
                })
            
            # Sort by date
            movements.sort(key=lambda x: x['date'], reverse=True)
            
            return {
                'success': True,
                'stock_movements': movements
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== STOCK ADJUSTMENTS ====================
    
    def create_stock_adjustment(self, user_id: int, item_code: str, 
                              adjustment_type: str, quantity: float, 
                              reason: str, reference: str = '') -> Dict:
        """Create stock adjustment"""
        try:
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            current_stock = self._calculate_current_stock(user_id, item_code)
            
            # Calculate new stock
            if adjustment_type == 'ADD':
                new_stock = current_stock + quantity
                movement_type = 'IN'
            elif adjustment_type == 'REDUCE':
                if current_stock < quantity:
                    return {'success': False, 'error': 'Insufficient stock for reduction'}
                new_stock = current_stock - quantity
                movement_type = 'OUT'
            else:
                return {'success': False, 'error': 'Invalid adjustment type'}
            
            # Update stock
            item.closing_stock = new_stock
            
            # Record adjustment note
            adjustment_note = f"ADJUSTMENT {adjustment_type}: {quantity} {item.unit} - {reason} (Ref: {reference})"
            item.remark = adjustment_note
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Stock adjustment created successfully',
                'item_code': item_code,
                'adjustment_type': adjustment_type,
                'quantity': quantity,
                'reason': reason,
                'previous_stock': current_stock,
                'new_stock': new_stock
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== INVENTORY VALUATION ====================
    
    def get_inventory_valuation(self, user_id: int, valuation_method: str = 'FIFO') -> Dict:
        """Get inventory valuation"""
        try:
            items = Item.query.filter_by(user_id=user_id).all()
            total_value = 0
            item_valuations = []
            
            for item in items:
                current_stock = self._calculate_current_stock(user_id, item.it_cd)
                
                # Calculate value based on method
                if valuation_method == 'FIFO':
                    # For simplicity, use current rate
                    value = current_stock * item.rate
                elif valuation_method == 'LIFO':
                    # For simplicity, use current rate
                    value = current_stock * item.rate
                else:  # Average
                    # For simplicity, use current rate
                    value = current_stock * item.rate
                
                total_value += value
                
                item_valuations.append({
                    'item_code': item.it_cd,
                    'item_name': item.it_nm,
                    'current_stock': current_stock,
                    'unit': item.unit,
                    'rate': float(item.rate),
                    'value': value
                })
            
            return {
                'success': True,
                'valuation': {
                    'valuation_method': valuation_method,
                    'total_value': total_value,
                    'item_valuations': item_valuations
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== REPORTS AND ANALYTICS ====================
    
    def get_inventory_summary(self, user_id: int) -> Dict:
        """Get inventory summary"""
        try:
            items = Item.query.filter_by(user_id=user_id).all()
            
            total_items = len(items)
            total_stock_value = 0
            low_stock_count = 0
            out_of_stock_count = 0
            
            for item in items:
                current_stock = self._calculate_current_stock(user_id, item.it_cd)
                stock_value = current_stock * item.rate
                total_stock_value += stock_value
                
                if current_stock <= item.reorder_level:
                    low_stock_count += 1
                
                if current_stock <= 0:
                    out_of_stock_count += 1
            
            return {
                'success': True,
                'summary': {
                    'total_items': total_items,
                    'total_stock_value': total_stock_value,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'average_stock_value': total_stock_value / total_items if total_items > 0 else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_inventory_reports(self, user_id: int, report_type: str) -> Dict:
        """Generate inventory reports"""
        try:
            if report_type == 'stock_status':
                return self.get_stock_status(user_id)
            elif report_type == 'low_stock':
                return self.get_low_stock_alerts(user_id)
            elif report_type == 'valuation':
                return self.get_inventory_valuation(user_id)
            elif report_type == 'movements':
                return self.get_stock_movements(user_id)
            else:
                return {'success': False, 'error': 'Invalid report type'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_inventory_statistics(self, user_id: int) -> Dict:
        """Get inventory statistics"""
        try:
            items = Item.query.filter_by(user_id=user_id).all()
            
            # Calculate statistics
            total_items = len(items)
            total_stock_value = 0
            low_stock_items = 0
            out_of_stock_items = 0
            
            for item in items:
                current_stock = self._calculate_current_stock(user_id, item.it_cd)
                stock_value = current_stock * item.rate
                total_stock_value += stock_value
                
                if current_stock <= item.reorder_level:
                    low_stock_items += 1
                
                if current_stock <= 0:
                    out_of_stock_items += 1
            
            return {
                'success': True,
                'statistics': {
                    'total_items': total_items,
                    'total_stock_value': total_stock_value,
                    'low_stock_items': low_stock_items,
                    'out_of_stock_items': out_of_stock_items,
                    'average_stock_value': total_stock_value / total_items if total_items > 0 else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== UTILITY METHODS ====================
    
    def _calculate_current_stock(self, user_id: int, item_code: str) -> float:
        """Calculate current stock for an item"""
        try:
            # Get opening stock
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return 0
            
            opening_stock = item.opening_stock or 0
            
            # Calculate purchases (IN)
            total_purchases = db.session.query(func.sum(Purchase.qty)).filter(
                Purchase.user_id == user_id,
                Purchase.it_cd == item_code
            ).scalar() or 0
            
            # Calculate sales (OUT)
            total_sales = db.session.query(func.sum(Sale.qty)).filter(
                Sale.user_id == user_id,
                Sale.it_cd == item_code
            ).scalar() or 0
            
            # Calculate current stock
            current_stock = opening_stock + total_purchases - total_sales
            
            return float(current_stock)
            
        except Exception as e:
            return 0
    
    def get_categories(self, user_id: int) -> Dict:
        """Get all item categories"""
        try:
            categories = db.session.query(Item.category).filter(
                Item.user_id == user_id,
                Item.category.isnot(None),
                Item.category != ''
            ).distinct().all()
            
            return {
                'success': True,
                'categories': [cat.category for cat in categories]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_inventory_list(self, user_id: int, page: int = 1, per_page: int = 20, 
                          search: str = None, category: str = None) -> Dict:
        """Get paginated inventory list with filtering"""
        try:
            query = Item.query.filter(Item.user_id == user_id)
            
            if search:
                query = query.filter(
                    or_(
                        Item.it_cd.contains(search),
                        Item.it_nm.contains(search)
                    )
                )
            
            if category:
                query = query.filter(Item.category == category)
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Get details for each item
            inventory_list = []
            for item in pagination.items:
                current_stock = self._calculate_current_stock(user_id, item.it_cd)
                
                inventory_list.append({
                    'item_code': item.it_cd,
                    'item_name': item.it_nm,
                    'category': item.category,
                    'unit': item.unit,
                    'current_stock': current_stock,
                    'reorder_level': float(item.reorder_level),
                    'rate': float(item.rate),
                    'stock_value': current_stock * item.rate,
                    'status': 'Low Stock' if current_stock <= item.reorder_level else 'Normal'
                })
            
            return {
                'success': True,
                'inventory': inventory_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)} 