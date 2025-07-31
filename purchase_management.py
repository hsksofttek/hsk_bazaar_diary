#!/usr/bin/env python3
"""
Advanced Purchase Management System
Complete implementation with full CRUD operations, reports, and business logic
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json
from database import db
from models import Purchase, Party, Item, User
from sqlalchemy import func, and_, or_, desc, asc
import uuid

class PurchaseManagementSystem:
    """Complete Purchase Management System with full functionality"""
    
    def __init__(self):
        self.system_name = "Purchase Management System"
        self.version = "2.0"
    
    # ==================== CORE PURCHASE OPERATIONS ====================
    
    def create_purchase_entry(self, user_id: int, party_id: str, items: List[Dict], 
                            total_amount: float = 0, tax_amount: float = 0, 
                            discount_amount: float = 0, transport_charges: float = 0,
                            payment_terms: str = '', delivery_date: str = None, 
                            notes: str = '', order_no: str = None) -> Dict:
        """Create a complete purchase entry with multiple items"""
        try:
            # Generate unique bill number
            bill_no = self._generate_bill_number(user_id)
            
            # Validate party
            party = Party.query.filter_by(party_cd=party_id, user_id=user_id).first()
            if not party:
                raise ValueError(f"Party with code {party_id} not found")
            
            purchase_entries = []
            total_calculated = 0
            
            # Create purchase entries for each item
            for item_data in items:
                item_code = item_data.get('item_code')
                quantity = float(item_data.get('quantity', 0))
                rate = float(item_data.get('rate', 0))
                discount = float(item_data.get('discount', 0))
                
                # Validate item
                item = Item.query.filter_by(it_cd=item_code, user_id=user_id).first()
                if not item:
                    raise ValueError(f"Item with code {item_code} not found")
                
                # Calculate amounts
                amount = quantity * rate
                net_amount = amount - discount
                total_calculated += net_amount
                
                # Create purchase entry
                purchase_entry = Purchase(
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
                    tot_amt=net_amount
                )
                
                db.session.add(purchase_entry)
                purchase_entries.append(purchase_entry)
            
            # Add transport charges and tax
            if transport_charges > 0:
                transport_entry = Purchase(
                    user_id=user_id,
                    bill_no=bill_no,
                    bill_date=date.today(),
                    party_cd=party_id,
                    it_cd='TRANSPORT',
                    qty=1,
                    rate=transport_charges,
                    sal_amt=transport_charges,
                    remark=f"Transport charges: {notes}",
                    tot_amt=transport_charges
                )
                db.session.add(transport_entry)
                total_calculated += transport_charges
            
            if tax_amount > 0:
                tax_entry = Purchase(
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
                'message': f'Purchase entry created successfully with bill number {bill_no}',
                'bill_no': bill_no,
                'total_amount': total_calculated,
                'entries_count': len(purchase_entries)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_purchase_entry(self, user_id: int, bill_no: int) -> Dict:
        """Get complete purchase entry details"""
        try:
            purchases = Purchase.query.filter_by(
                user_id=user_id, 
                bill_no=bill_no
            ).all()
            
            if not purchases:
                return {'success': False, 'error': 'Purchase entry not found'}
            
            # Get party details
            party = Party.query.filter_by(
                party_cd=purchases[0].party_cd, 
                user_id=user_id
            ).first()
            
            # Group items
            items = []
            total_amount = 0
            transport_charges = 0
            tax_amount = 0
            
            for purchase in purchases:
                if purchase.it_cd == 'TRANSPORT':
                    transport_charges = purchase.sal_amt
                elif purchase.it_cd == 'TAX':
                    tax_amount = purchase.sal_amt
                else:
                    item = Item.query.filter_by(it_cd=purchase.it_cd, user_id=user_id).first()
                    items.append({
                        'item_code': purchase.it_cd,
                        'item_name': item.it_nm if item else purchase.it_cd,
                        'quantity': purchase.qty,
                        'rate': purchase.rate,
                        'amount': purchase.qty * purchase.rate,
                        'discount': purchase.discount,
                        'net_amount': purchase.sal_amt
                    })
                    total_amount += purchase.sal_amt
            
            return {
                'success': True,
                'purchase': {
                    'bill_no': bill_no,
                    'bill_date': purchases[0].bill_date.strftime('%Y-%m-%d'),
                    'party_code': purchases[0].party_cd,
                    'party_name': party.party_nm if party else '',
                    'party_address': f"{party.address1 or ''} {party.address2 or ''}".strip() if party else '',
                    'party_phone': party.phone or '',
                    'items': items,
                    'total_amount': total_amount,
                    'transport_charges': transport_charges,
                    'tax_amount': tax_amount,
                    'grand_total': total_amount + transport_charges + tax_amount,
                    'order_no': purchases[0].order_no,
                    'delivery_date': purchases[0].order_dt.strftime('%Y-%m-%d') if purchases[0].order_dt else None,
                    'payment_terms': purchases[0].trans,
                    'notes': purchases[0].remark
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_purchase_entry(self, user_id: int, bill_no: int, updates: Dict) -> Dict:
        """Update purchase entry"""
        try:
            purchases = Purchase.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not purchases:
                return {'success': False, 'error': 'Purchase entry not found'}
            
            # Update basic fields
            for purchase in purchases:
                if 'delivery_date' in updates:
                    purchase.order_dt = datetime.strptime(updates['delivery_date'], '%Y-%m-%d').date()
                if 'payment_terms' in updates:
                    purchase.trans = updates['payment_terms']
                if 'notes' in updates:
                    purchase.remark = updates['notes']
            
            db.session.commit()
            return {'success': True, 'message': 'Purchase entry updated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def delete_purchase_entry(self, user_id: int, bill_no: int) -> Dict:
        """Delete purchase entry"""
        try:
            purchases = Purchase.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not purchases:
                return {'success': False, 'error': 'Purchase entry not found'}
            
            for purchase in purchases:
                db.session.delete(purchase)
            
            db.session.commit()
            return {'success': True, 'message': 'Purchase entry deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== PURCHASE ORDERS ====================
    
    def create_purchase_order(self, user_id: int, party_id: str, items: List[Dict],
                            expected_delivery: str, notes: str = '') -> Dict:
        """Create purchase order"""
        try:
            order_no = f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Create purchase entries with order number
            result = self.create_purchase_entry(
                user_id=user_id,
                party_id=party_id,
                items=items,
                delivery_date=expected_delivery,
                notes=notes,
                order_no=order_no
            )
            
            if result['success']:
                result['order_no'] = order_no
                result['message'] = f'Purchase order created successfully: {order_no}'
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_purchase_orders(self, user_id: int, status: str = 'all') -> Dict:
        """Get purchase orders with status filtering"""
        try:
            query = db.session.query(Purchase.order_no, Purchase.order_dt, Purchase.party_cd, 
                                   func.sum(Purchase.sal_amt).label('total_amount'))
            
            if status == 'pending':
                query = query.filter(Purchase.order_dt >= date.today())
            elif status == 'completed':
                query = query.filter(Purchase.order_dt < date.today())
            
            orders = query.filter(
                Purchase.user_id == user_id,
                Purchase.order_no.isnot(None)
            ).group_by(Purchase.order_no, Purchase.order_dt, Purchase.party_cd).all()
            
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
    
    # ==================== PURCHASE RETURNS ====================
    
    def create_purchase_return(self, user_id: int, original_bill_no: int, 
                             return_items: List[Dict], return_reason: str) -> Dict:
        """Create purchase return"""
        try:
            # Get original purchase
            original_purchases = Purchase.query.filter_by(
                user_id=user_id, 
                bill_no=original_bill_no
            ).all()
            
            if not original_purchases:
                return {'success': False, 'error': 'Original purchase not found'}
            
            # Create return entries (negative quantities)
            return_bill_no = self._generate_bill_number(user_id)
            return_entries = []
            
            for return_item in return_items:
                item_code = return_item.get('item_code')
                return_qty = float(return_item.get('quantity', 0))
                
                # Find original item
                original_item = next((p for p in original_purchases if p.it_cd == item_code), None)
                if not original_item:
                    return {'success': False, 'error': f'Item {item_code} not found in original purchase'}
                
                if return_qty > original_item.qty:
                    return {'success': False, 'error': f'Return quantity cannot exceed original quantity for {item_code}'}
                
                # Create return entry
                return_entry = Purchase(
                    user_id=user_id,
                    bill_no=return_bill_no,
                    bill_date=date.today(),
                    party_cd=original_purchases[0].party_cd,
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
                'message': f'Purchase return created successfully with bill number {return_bill_no}',
                'return_bill_no': return_bill_no,
                'original_bill_no': original_bill_no,
                'return_reason': return_reason
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== PAYMENT TRACKING ====================
    
    def record_purchase_payment(self, user_id: int, bill_no: int, 
                              payment_amount: float, payment_date: str,
                              payment_method: str = 'Cash', reference_no: str = '') -> Dict:
        """Record payment for purchase"""
        try:
            # Get purchase total
            purchases = Purchase.query.filter_by(user_id=user_id, bill_no=bill_no).all()
            if not purchases:
                return {'success': False, 'error': 'Purchase not found'}
            
            total_amount = sum(p.sal_amt for p in purchases)
            
            # Check if payment exceeds total
            if payment_amount > total_amount:
                return {'success': False, 'error': 'Payment amount cannot exceed total purchase amount'}
            
            # Create payment record (this would typically go to a payments table)
            # For now, we'll update the purchase record with payment info
            for purchase in purchases:
                purchase.cash_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                purchase.lr_no = reference_no  # Using lr_no field for payment reference
            
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
    
    def get_pending_payments(self, user_id: int) -> Dict:
        """Get pending payments for purchases"""
        try:
            # Get purchases without payment dates
            pending_purchases = db.session.query(
                Purchase.bill_no, Purchase.party_cd, Purchase.bill_date,
                func.sum(Purchase.sal_amt).label('total_amount')
            ).filter(
                Purchase.user_id == user_id,
                Purchase.cash_date.is_(None)
            ).group_by(Purchase.bill_no, Purchase.party_cd, Purchase.bill_date).all()
            
            return {
                'success': True,
                'pending_payments': [{
                    'bill_no': p.bill_no,
                    'party_code': p.party_cd,
                    'bill_date': p.bill_date.strftime('%Y-%m-%d'),
                    'total_amount': float(p.total_amount)
                } for p in pending_purchases]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== REPORTS AND ANALYTICS ====================
    
    def get_purchase_summary(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """Get purchase summary with date filtering"""
        try:
            query = Purchase.query.filter(Purchase.user_id == user_id)
            
            if start_date:
                query = query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                query = query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            # Get total purchases
            total_purchases = query.count()
            
            # Get total amount
            total_amount = query.with_entities(func.sum(Purchase.sal_amt)).scalar() or 0
            
            # Get purchases by party
            party_summary = db.session.query(
                Purchase.party_cd,
                func.count(Purchase.bill_no).label('purchase_count'),
                func.sum(Purchase.sal_amt).label('total_amount')
            ).filter(
                Purchase.user_id == user_id
            ).group_by(Purchase.party_cd).all()
            
            # Get purchases by item
            item_summary = db.session.query(
                Purchase.it_cd,
                func.sum(Purchase.qty).label('total_quantity'),
                func.sum(Purchase.sal_amt).label('total_amount')
            ).filter(
                Purchase.user_id == user_id
            ).group_by(Purchase.it_cd).all()
            
            return {
                'success': True,
                'summary': {
                    'total_purchases': total_purchases,
                    'total_amount': float(total_amount),
                    'party_summary': [{
                        'party_code': p.party_cd,
                        'purchase_count': p.purchase_count,
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
    
    def get_purchase_reports(self, user_id: int, report_type: str, 
                           start_date: str = None, end_date: str = None) -> Dict:
        """Generate various purchase reports"""
        try:
            if report_type == 'daily':
                return self._get_daily_purchase_report(user_id, start_date, end_date)
            elif report_type == 'monthly':
                return self._get_monthly_purchase_report(user_id, start_date, end_date)
            elif report_type == 'party_wise':
                return self._get_party_wise_purchase_report(user_id, start_date, end_date)
            elif report_type == 'item_wise':
                return self._get_item_wise_purchase_report(user_id, start_date, end_date)
            else:
                return {'success': False, 'error': 'Invalid report type'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_purchase_statistics(self, user_id: int) -> Dict:
        """Get purchase statistics"""
        try:
            # Today's purchases
            today_purchases = Purchase.query.filter(
                Purchase.user_id == user_id,
                Purchase.bill_date == date.today()
            ).count()
            
            today_amount = Purchase.query.filter(
                Purchase.user_id == user_id,
                Purchase.bill_date == date.today()
            ).with_entities(func.sum(Purchase.sal_amt)).scalar() or 0
            
            # This month's purchases
            start_of_month = date.today().replace(day=1)
            month_purchases = Purchase.query.filter(
                Purchase.user_id == user_id,
                Purchase.bill_date >= start_of_month
            ).count()
            
            month_amount = Purchase.query.filter(
                Purchase.user_id == user_id,
                Purchase.bill_date >= start_of_month
            ).with_entities(func.sum(Purchase.sal_amt)).scalar() or 0
            
            # Pending payments
            pending_amount = Purchase.query.filter(
                Purchase.user_id == user_id,
                Purchase.cash_date.is_(None)
            ).with_entities(func.sum(Purchase.sal_amt)).scalar() or 0
            
            return {
                'success': True,
                'statistics': {
                    'today_purchases': today_purchases,
                    'today_amount': float(today_amount),
                    'month_purchases': month_purchases,
                    'month_amount': float(month_amount),
                    'pending_amount': float(pending_amount)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== UTILITY METHODS ====================
    
    def _generate_bill_number(self, user_id: int) -> int:
        """Generate unique bill number"""
        max_bill = db.session.query(func.max(Purchase.bill_no)).filter(
            Purchase.user_id == user_id
        ).scalar()
        return (max_bill or 0) + 1
    
    def _get_daily_purchase_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate daily purchase report"""
        query = db.session.query(
            Purchase.bill_date,
            func.count(Purchase.bill_no).label('purchase_count'),
            func.sum(Purchase.sal_amt).label('total_amount')
        ).filter(Purchase.user_id == user_id)
        
        if start_date:
            query = query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        daily_data = query.group_by(Purchase.bill_date).order_by(Purchase.bill_date).all()
        
        return {
            'success': True,
            'report_type': 'daily',
            'data': [{
                'date': d.bill_date.strftime('%Y-%m-%d'),
                'purchase_count': d.purchase_count,
                'total_amount': float(d.total_amount)
            } for d in daily_data]
        }
    
    def _get_monthly_purchase_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate monthly purchase report"""
        query = db.session.query(
            func.extract('year', Purchase.bill_date).label('year'),
            func.extract('month', Purchase.bill_date).label('month'),
            func.count(Purchase.bill_no).label('purchase_count'),
            func.sum(Purchase.sal_amt).label('total_amount')
        ).filter(Purchase.user_id == user_id)
        
        if start_date:
            query = query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        monthly_data = query.group_by(
            func.extract('year', Purchase.bill_date),
            func.extract('month', Purchase.bill_date)
        ).order_by(
            func.extract('year', Purchase.bill_date),
            func.extract('month', Purchase.bill_date)
        ).all()
        
        return {
            'success': True,
            'report_type': 'monthly',
            'data': [{
                'year': int(d.year),
                'month': int(d.month),
                'purchase_count': d.purchase_count,
                'total_amount': float(d.total_amount)
            } for d in monthly_data]
        }
    
    def _get_party_wise_purchase_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate party-wise purchase report"""
        query = db.session.query(
            Purchase.party_cd,
            func.count(Purchase.bill_no).label('purchase_count'),
            func.sum(Purchase.sal_amt).label('total_amount')
        ).filter(Purchase.user_id == user_id)
        
        if start_date:
            query = query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        party_data = query.group_by(Purchase.party_cd).order_by(desc(func.sum(Purchase.sal_amt))).all()
        
        return {
            'success': True,
            'report_type': 'party_wise',
            'data': [{
                'party_code': p.party_cd,
                'purchase_count': p.purchase_count,
                'total_amount': float(p.total_amount)
            } for p in party_data]
        }
    
    def _get_item_wise_purchase_report(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Generate item-wise purchase report"""
        query = db.session.query(
            Purchase.it_cd,
            func.sum(Purchase.qty).label('total_quantity'),
            func.sum(Purchase.sal_amt).label('total_amount')
        ).filter(Purchase.user_id == user_id)
        
        if start_date:
            query = query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        item_data = query.group_by(Purchase.it_cd).order_by(desc(func.sum(Purchase.sal_amt))).all()
        
        return {
            'success': True,
            'report_type': 'item_wise',
            'data': [{
                'item_code': i.it_cd,
                'total_quantity': float(i.total_quantity),
                'total_amount': float(i.total_amount)
            } for i in item_data]
        }
    
    def get_purchase_list(self, user_id: int, page: int = 1, per_page: int = 20, 
                         search: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """Get paginated purchase list with filtering"""
        try:
            query = Purchase.query.filter(Purchase.user_id == user_id)
            
            if search:
                query = query.filter(
                    or_(
                        Purchase.party_cd.contains(search),
                        Purchase.it_cd.contains(search),
                        Purchase.order_no.contains(search)
                    )
                )
            
            if start_date:
                query = query.filter(Purchase.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                query = query.filter(Purchase.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            # Get unique bill numbers
            bills = query.with_entities(Purchase.bill_no).distinct().order_by(desc(Purchase.bill_no))
            
            # Paginate
            pagination = bills.paginate(page=page, per_page=per_page, error_out=False)
            
            # Get details for each bill
            purchase_list = []
            for bill_no in pagination.items:
                bill_purchases = Purchase.query.filter_by(user_id=user_id, bill_no=bill_no.bill_no).all()
                if bill_purchases:
                    party = Party.query.filter_by(party_cd=bill_purchases[0].party_cd, user_id=user_id).first()
                    total_amount = sum(p.sal_amt for p in bill_purchases)
                    
                    purchase_list.append({
                        'bill_no': bill_no.bill_no,
                        'bill_date': bill_purchases[0].bill_date.strftime('%Y-%m-%d'),
                        'party_code': bill_purchases[0].party_cd,
                        'party_name': party.party_nm if party else '',
                        'total_amount': float(total_amount),
                        'order_no': bill_purchases[0].order_no,
                        'payment_status': 'Paid' if bill_purchases[0].cash_date else 'Pending'
                    })
            
            return {
                'success': True,
                'purchases': purchase_list,
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