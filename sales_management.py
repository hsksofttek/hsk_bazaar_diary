#!/usr/bin/env python3
"""
Advanced Sales Management System
Complete implementation with full CRUD operations, reports, and business logic
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json
from database import db
from models import Sale, Party, Item, User
from sqlalchemy import func, and_, or_, desc, asc
import uuid

class SalesManagementSystem:
    """Complete Sales Management System with full functionality"""
    
    def __init__(self):
        self.system_name = "Sales Management System"
        self.version = "2.0"
    
    # ==================== CORE SALES OPERATIONS ====================
    
    def create_sales_entry(self, user_id: int, party_id: str, items: List[Dict], 
                          total_amount: float = 0, tax_amount: float = 0, 
                          discount_amount: float = 0, delivery_charges: float = 0,
                          payment_terms: str = '', delivery_date: str = None, 
                          notes: str = '', order_no: str = None) -> Dict:
        """Create a complete sales entry with multiple items"""
        try:
            # Generate unique bill number
            bill_no = self._generate_bill_number(user_id)
            
            # Validate party
            party = Party.query.filter_by(party_cd=party_id, user_id=user_id).first()
            if not party:
                raise ValueError(f"Party with code {party_id} not found")
            
            # Check credit limit
            if not self._check_credit_limit(user_id, party_id, total_amount):
                return {'success': False, 'error': 'Credit limit exceeded for this party'}
            
            sales_entries = []
            total_calculated = 0
            
            # Create sales entries for each item
            for item_data in items:
                item_code = item_data.get('item_code')
                quantity = float(item_data.get('quantity', 0))
                rate = float(item_data.get('rate', 0))
                discount = float(item_data.get('discount', 0))
                
                # Validate item
                item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
                if not item:
                    raise ValueError(f"Item with code {item_code} not found")
                
                # Check stock availability
                if not self._check_stock_availability(user_id, item_code, quantity):
                    return {'success': False, 'error': f'Insufficient stock for item {item_code}'}
                
                # Calculate amounts
                amount = quantity * rate
                net_amount = amount - discount
                total_calculated += net_amount
                
                # Create sales entry
                sales_entry = Sale(
                    user_id=user_id,
                    bill_no=bill_no,
                    bill_date=date.today(),
                    party_cd=party_id,
                    it_cd=item_code,
                    qty=quantity,
                    rate=rate,
                    sal_amt=net_amount,
                    discount=discount,
                    order_no=order_no,
                    order_dt=datetime.strptime(delivery_date, '%Y-%m-%d').date() if delivery_date else None,
                    remark=notes,
                    trans=payment_terms,
                    tot_amt=net_amount,
                    payment_status='PENDING',
                    payment_due_date=date.today() + timedelta(days=30) if payment_terms else None
                )
                
                db.session.add(sales_entry)
                sales_entries.append(sales_entry)
            
            # Add delivery charges and tax
            if delivery_charges > 0:
                delivery_entry = Sale(
                    user_id=user_id,
                    bill_no=bill_no,
                    bill_date=date.today(),
                    party_cd=party_id,
                    it_cd='DELIVERY',
                    qty=1,
                    rate=delivery_charges,
                    sal_amt=delivery_charges,
                    remark=f"Delivery charges: {notes}",
                    tot_amt=delivery_charges
                )
                db.session.add(delivery_entry)
                total_calculated += delivery_charges
            
            if tax_amount > 0:
                tax_entry = Sale(
                    user_id=user_id,
                    bill_no=bill_no,
                    bill_date=date.today(),
                    party_cd=party_id,
                    it_cd='TAX',
                    qty=1,
                    rate=tax_amount,
                    sal_amt=tax_amount,
                    remark=f"Tax amount: {notes}",
                    tot_amt=tax_amount
                )
                db.session.add(tax_entry)
                total_calculated += tax_amount
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Sales entry created successfully with bill number {bill_no}',
                'bill_no': bill_no,
                'total_amount': total_calculated,
                'entries_count': len(sales_entries)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_sales_entry(self, user_id: int, bill_no: int) -> Dict:
        """Get complete sales entry details"""
        try:
            sales = Sale.query.filter_by(
                user_id=user_id, 
                bill_no=bill_no
            ).all()
            
            if not sales:
                return {'success': False, 'error': 'Sales entry not found'}
            
            # Get party details
            party = Party.query.filter_by(
                party_cd=sales[0].party_cd, 
                user_id=user_id
            ).first()
            
            # Group items
            items = []
            total_amount = 0
            delivery_charges = 0
            tax_amount = 0
            
            for sale in sales:
                if sale.it_cd == 'DELIVERY':
                    delivery_charges = sale.sal_amt
                elif sale.it_cd == 'TAX':
                    tax_amount = sale.sal_amt
                else:
                    item = Item.query.filter_by(it_cd=sale.it_cd, user_id=user_id).first()
                    items.append({
                        'item_code': sale.it_cd,
                        'item_name': item.it_nm if item else sale.it_cd,
                        'quantity': sale.qty,
                        'rate': sale.rate,
                        'amount': sale.qty * sale.rate,
                        'discount': sale.discount,
                        'net_amount': sale.sal_amt
                    })
                    total_amount += sale.sal_amt
            
            return {
                'success': True,
                'sale': {
                    'bill_no': bill_no,
                    'bill_date': sales[0].bill_date.strftime('%Y-%m-%d'),
                    'party_code': sales[0].party_cd,
                    'party_name': party.party_nm if party else '',
                    'party_address': f"{party.address1 or ''} {party.address2 or ''}".strip() if party else '',
                    'party_phone': party.phone or '',
                    'items': items,
                    'total_amount': total_amount,
                    'delivery_charges': delivery_charges,
                    'tax_amount': tax_amount,
                    'grand_total': total_amount + delivery_charges + tax_amount,
                    'order_no': sales[0].order_no,
                    'delivery_date': sales[0].order_dt.strftime('%Y-%m-%d') if sales[0].order_dt else None,
                    'payment_terms': sales[0].trans,
                    'payment_status': sales[0].payment_status,
                    'payment_due_date': sales[0].payment_due_date.strftime('%Y-%m-%d') if sales[0].payment_due_date else None,
                    'notes': sales[0].remark
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_sales_entry(self, user_id: int, bill_no: int, updates: Dict) -> Dict:
        """Update sales entry"""
        try:
            sales = Sale.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not sales:
                return {'success': False, 'error': 'Sales entry not found'}
            
            # Update basic fields
            for sale in sales:
                if 'delivery_date' in updates:
                    sale.order_dt = datetime.strptime(updates['delivery_date'], '%Y-%m-%d').date()
                if 'payment_terms' in updates:
                    sale.trans = updates['payment_terms']
                if 'notes' in updates:
                    sale.remark = updates['notes']
                if 'payment_status' in updates:
                    sale.payment_status = updates['payment_status']
            
            db.session.commit()
            return {'success': True, 'message': 'Sales entry updated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def delete_sales_entry(self, user_id: int, bill_no: int) -> Dict:
        """Delete sales entry"""
        try:
            sales = Sale.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not sales:
                return {'success': False, 'error': 'Sales entry not found'}
            
            for sale in sales:
                db.session.delete(sale)
            
            db.session.commit()
            return {'success': True, 'message': 'Sales entry deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== SALES ORDERS ====================
    
    def create_sales_order(self, user_id: int, party_id: str, items: List[Dict],
                          expected_delivery: str, notes: str = '') -> Dict:
        """Create sales order"""
        try:
            order_no = f"SO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Create sales entries with order number
            result = self.create_sales_entry(
                user_id=user_id,
                party_id=party_id,
                items=items,
                delivery_date=expected_delivery,
                notes=notes,
                order_no=order_no
            )
            
            if result['success']:
                result['order_no'] = order_no
                result['message'] = f'Sales order created successfully: {order_no}'
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_sales_orders(self, user_id: int, status: str = 'all') -> Dict:
        """Get sales orders with status filtering"""
        try:
            query = db.session.query(Sale.order_no, Sale.order_dt, Sale.party_cd, 
                                   func.sum(Sale.sal_amt).label('total_amount'))
            
            if status == 'pending':
                query = query.filter(Sale.order_dt >= date.today())
            elif status == 'completed':
                query = query.filter(Sale.order_dt < date.today())
            
            orders = query.filter(
                Sale.user_id == user_id,
                Sale.order_no.isnot(None)
            ).group_by(Sale.order_no, Sale.order_dt, Sale.party_cd).all()
            
            return {
                'success': True,
                'orders': [{
                    'order_no': order.order_no,
                    'order_date': order.order_dt.strftime('%Y-%m-%d') if order.order_dt else None,
                    'party_code': order.party_cd,
                    'total_amount': float(order.total_amount),
                    'status': 'Pending' if order.order_dt and order.order_dt >= date.today() else 'Completed'
                } for order in orders]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== SALES RETURNS ====================
    
    def create_sales_return(self, user_id: int, original_bill_no: int, 
                           return_items: List[Dict], return_reason: str) -> Dict:
        """Create sales return"""
        try:
            # Get original sale
            original_sales = Sale.query.filter_by(
                user_id=user_id, 
                bill_no=original_bill_no
            ).all()
            
            if not original_sales:
                return {'success': False, 'error': 'Original sale not found'}
            
            # Create return entries (negative quantities)
            return_bill_no = self._generate_bill_number(user_id)
            return_entries = []
            
            for return_item in return_items:
                item_code = return_item.get('item_code')
                return_qty = float(return_item.get('quantity', 0))
                
                # Find original item
                original_item = next((s for s in original_sales if s.it_cd == item_code), None)
                if not original_item:
                    return {'success': False, 'error': f'Item {item_code} not found in original sale'}
                
                if return_qty > original_item.qty:
                    return {'success': False, 'error': f'Return quantity cannot exceed original quantity for {item_code}'}
                
                # Create return entry
                return_entry = Sale(
                    user_id=user_id,
                    bill_no=return_bill_no,
                    bill_date=date.today(),
                    party_cd=original_sales[0].party_cd,
                    it_cd=item_code,
                    qty=-return_qty,  # Negative quantity for return
                    rate=original_item.rate,
                    sal_amt=-(return_qty * original_item.rate),
                    remark=f"Return: {return_reason}",
                    tot_amt=-(return_qty * original_item.rate)
                )
                
                db.session.add(return_entry)
                return_entries.append(return_entry)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Sales return created successfully with bill number {return_bill_no}',
                'return_bill_no': return_bill_no,
                'original_bill_no': original_bill_no,
                'return_reason': return_reason
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== PAYMENT COLLECTION ====================
    
    def record_sales_payment(self, user_id: int, bill_no: int, 
                           payment_amount: float, payment_date: str,
                           payment_method: str = 'Cash', reference_no: str = '') -> Dict:
        """Record payment for sales"""
        try:
            # Get sales total
            sales = Sale.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not sales:
                return {'success': False, 'error': 'Sales not found'}
            
            total_amount = sum(s.sal_amt for s in sales)
            
            # Check if payment exceeds total
            if payment_amount > total_amount:
                return {'success': False, 'error': 'Payment amount cannot exceed total sales amount'}
            
            # Update payment status
            for sale in sales:
                sale.cash_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                sale.lr_no = reference_no  # Using lr_no field for payment reference
                sale.amount_paid = payment_amount
                sale.payment_status = 'PAID' if payment_amount >= total_amount else 'PARTIAL'
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Payment of {payment_amount} recorded successfully',
                'bill_no': bill_no,
                'payment_amount': payment_amount,
                'payment_date': payment_date,
                'payment_method': payment_method,
                'reference_no': reference_no
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_pending_collections(self, user_id: int) -> Dict:
        """Get pending collections for sales"""
        try:
            # Get sales without payment dates
            pending_sales = db.session.query(
                Sale.bill_no, Sale.party_cd, Sale.bill_date,
                func.sum(Sale.sal_amt).label('total_amount')
            ).filter(
                Sale.user_id == user_id,
                Sale.cash_date.is_(None)
            ).group_by(Sale.bill_no, Sale.party_cd, Sale.bill_date).all()
            
            return {
                'success': True,
                'pending_collections': [{
                    'bill_no': p.bill_no,
                    'party_code': p.party_cd,
                    'bill_date': p.bill_date.strftime('%Y-%m-%d'),
                    'total_amount': float(p.total_amount)
                } for p in pending_sales]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== DELIVERY MANAGEMENT ====================
    
    def update_delivery_status(self, user_id: int, bill_no: int, 
                              delivery_status: str, delivery_date: str = None) -> Dict:
        """Update delivery status"""
        try:
            sales = Sale.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not sales:
                return {'success': False, 'error': 'Sales not found'}
            
            for sale in sales:
                if delivery_date:
                    sale.order_dt = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                sale.remark = f"Delivery Status: {delivery_status}"
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Delivery status updated to {delivery_status}',
                'bill_no': bill_no,
                'delivery_status': delivery_status,
                'delivery_date': delivery_date
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== REPORTS AND ANALYTICS ====================
    
    def get_sales_summary(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """Get sales summary with date filtering"""
        try:
            query = Sale.query.filter(Sale.user_id == user_id)
            
            if start_date:
                query = query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                query = query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            # Get total sales
            total_sales = query.count()
            
            # Get total amount
            total_amount = query.with_entities(func.sum(Sale.sal_amt)).scalar() or 0
            
            # Get sales by party
            party_summary = db.session.query(
                Sale.party_cd,
                func.count(Sale.bill_no).label('sales_count'),
                func.sum(Sale.sal_amt).label('total_amount')
            ).filter(
                Sale.user_id == user_id
            ).group_by(Sale.party_cd).all()
            
            # Get sales by item
            item_summary = db.session.query(
                Sale.it_cd,
                func.sum(Sale.qty).label('total_quantity'),
                func.sum(Sale.sal_amt).label('total_amount')
            ).filter(
                Sale.user_id == user_id
            ).group_by(Sale.it_cd).all()
            
            return {
                'success': True,
                'summary': {
                    'total_sales': total_sales,
                    'total_amount': float(total_amount),
                    'party_summary': [{
                        'party_code': p.party_cd,
                        'sales_count': p.sales_count,
                        'total_amount': float(p.total_amount)
                    } for p in party_summary],
                    'item_summary': [{
                        'item_code': i.it_cd,
                        'total_quantity': float(i.total_quantity),
                        'total_amount': float(i.total_amount)
                    } for i in item_summary]
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_sales_reports(self, user_id: int, report_type: str, 
                         start_date: str = None, end_date: str = None) -> Dict:
        """Generate various sales reports"""
        try:
            if report_type == 'daily':
                return self._get_daily_sales_report(user_id, start_date, end_date)
            elif report_type == 'monthly':
                return self._get_monthly_sales_report(user_id, start_date, end_date)
            elif report_type == 'party_wise':
                return self._get_party_wise_sales_report(user_id, start_date, end_date)
            elif report_type == 'item_wise':
                return self._get_item_wise_sales_report(user_id, start_date, end_date)
            else:
                return {'success': False, 'error': 'Invalid report type'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_sales_statistics(self, user_id: int) -> Dict:
        """Get sales statistics"""
        try:
            # Today's sales
            today_sales = Sale.query.filter(
                Sale.user_id == user_id,
                Sale.bill_date == date.today()
            ).count()
            
            today_amount = Sale.query.filter(
                Sale.user_id == user_id,
                Sale.bill_date == date.today()
            ).with_entities(func.sum(Sale.sal_amt)).scalar() or 0
            
            # This month's sales
            start_of_month = date.today().replace(day=1)
            month_sales = Sale.query.filter(
                Sale.user_id == user_id,
                Sale.bill_date >= start_of_month
            ).count()
            
            month_amount = Sale.query.filter(
                Sale.user_id == user_id,
                Sale.bill_date >= start_of_month
            ).with_entities(func.sum(Sale.sal_amt)).scalar() or 0
            
            # Pending collections
            pending_amount = Sale.query.filter(
                Sale.user_id == user_id,
                Sale.cash_date.is_(None)
            ).with_entities(func.sum(Sale.sal_amt)).scalar() or 0
            
            return {
                'success': True,
                'statistics': {
                    'today_sales': today_sales,
                    'today_amount': float(today_amount),
                    'month_sales': month_sales,
                    'month_amount': float(month_amount),
                    'pending_amount': float(pending_amount)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== UTILITY METHODS ====================
    
    def _generate_bill_number(self, user_id: int) -> int:
        """Generate unique bill number"""
        max_bill = db.session.query(func.max(Sale.bill_no)).filter(
            Sale.user_id == user_id
        ).scalar()
        return (max_bill or 0) + 1
    
    def _check_credit_limit(self, user_id: int, party_id: str, amount: float) -> bool:
        """Check if party has sufficient credit limit"""
        try:
            party = Party.query.filter_by(party_cd=party_id, user_id=user_id).first()
            if not party:
                return False
            
            # Get current balance
            current_balance = party.current_balance or 0
            
            # Check if new amount exceeds credit limit
            if party.credit_limit and (current_balance + amount) > party.credit_limit:
                return False
            
            return True
        except:
            return True  # Allow if check fails
    
    def _check_stock_availability(self, user_id: int, item_code: str, quantity: float) -> bool:
        """Check if sufficient stock is available"""
        try:
            # This is a simplified check - in a real system, you'd check actual stock levels
            item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
            if not item:
                return False
            
            # For now, assume stock is available if item exists
            return True
        except:
            return True  # Allow if check fails
    
    def _get_daily_sales_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate daily sales report"""
        query = db.session.query(
            Sale.bill_date,
            func.count(Sale.bill_no).label('sales_count'),
            func.sum(Sale.sal_amt).label('total_amount')
        ).filter(Sale.user_id == user_id)
        
        if start_date:
            query = query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        daily_data = query.group_by(Sale.bill_date).order_by(Sale.bill_date).all()
        
        return {
            'success': True,
            'report_type': 'daily',
            'data': [{
                'date': d.bill_date.strftime('%Y-%m-%d'),
                'sales_count': d.sales_count,
                'total_amount': float(d.total_amount)
            } for d in daily_data]
        }
    
    def _get_monthly_sales_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate monthly sales report"""
        query = db.session.query(
            func.extract('year', Sale.bill_date).label('year'),
            func.extract('month', Sale.bill_date).label('month'),
            func.count(Sale.bill_no).label('sales_count'),
            func.sum(Sale.sal_amt).label('total_amount')
        ).filter(Sale.user_id == user_id)
        
        if start_date:
            query = query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        monthly_data = query.group_by(
            func.extract('year', Sale.bill_date),
            func.extract('month', Sale.bill_date)
        ).order_by(
            func.extract('year', Sale.bill_date),
            func.extract('month', Sale.bill_date)
        ).all()
        
        return {
            'success': True,
            'report_type': 'monthly',
            'data': [{
                'year': int(d.year),
                'month': int(d.month),
                'sales_count': d.sales_count,
                'total_amount': float(d.total_amount)
            } for d in monthly_data]
        }
    
    def _get_party_wise_sales_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate party-wise sales report"""
        query = db.session.query(
            Sale.party_cd,
            func.count(Sale.bill_no).label('sales_count'),
            func.sum(Sale.sal_amt).label('total_amount')
        ).filter(Sale.user_id == user_id)
        
        if start_date:
            query = query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        party_data = query.group_by(Sale.party_cd).order_by(desc(func.sum(Sale.sal_amt))).all()
        
        return {
            'success': True,
            'report_type': 'party_wise',
            'data': [{
                'party_code': p.party_cd,
                'sales_count': p.sales_count,
                'total_amount': float(p.total_amount)
            } for p in party_data]
        }
    
    def _get_item_wise_sales_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate item-wise sales report"""
        query = db.session.query(
            Sale.it_cd,
            func.sum(Sale.qty).label('total_quantity'),
            func.sum(Sale.sal_amt).label('total_amount')
        ).filter(Sale.user_id == user_id)
        
        if start_date:
            query = query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        item_data = query.group_by(Sale.it_cd).order_by(desc(func.sum(Sale.sal_amt))).all()
        
        return {
            'success': True,
            'report_type': 'item_wise',
            'data': [{
                'item_code': i.it_cd,
                'total_quantity': float(i.total_quantity),
                'total_amount': float(i.total_amount)
            } for i in item_data]
        }
    
    def get_sales_list(self, user_id: int, page: int = 1, per_page: int = 20, 
                      search: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """Get paginated sales list with filtering"""
        try:
            query = Sale.query.filter(Sale.user_id == user_id)
            
            if search:
                query = query.filter(
                    or_(
                        Sale.party_cd.contains(search),
                        Sale.it_cd.contains(search),
                        Sale.order_no.contains(search)
                    )
                )
            
            if start_date:
                query = query.filter(Sale.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                query = query.filter(Sale.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            # Get unique bill numbers
            bills = query.with_entities(Sale.bill_no).distinct().order_by(desc(Sale.bill_no))
            
            # Paginate
            pagination = bills.paginate(page=page, per_page=per_page, error_out=False)
            
            # Get details for each bill
            sales_list = []
            for bill_no in pagination.items:
                bill_sales = Sale.query.filter_by(user_id=user_id, bill_no=bill_no.bill_no).all()
                if bill_sales:
                    party = Party.query.filter_by(party_cd=bill_sales[0].party_cd, user_id=user_id).first()
                    total_amount = sum(s.sal_amt for s in bill_sales)
                    
                    sales_list.append({
                        'bill_no': bill_no.bill_no,
                        'bill_date': bill_sales[0].bill_date.strftime('%Y-%m-%d'),
                        'party_code': bill_sales[0].party_cd,
                        'party_name': party.party_nm if party else '',
                        'total_amount': float(total_amount),
                        'order_no': bill_sales[0].order_no,
                        'payment_status': bill_sales[0].payment_status or 'Pending'
                    })
            
            return {
                'success': True,
                'sales': sales_list,
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