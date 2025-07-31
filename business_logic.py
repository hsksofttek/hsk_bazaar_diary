"""
Business Logic Module for Credit-Based Balance Calculations
Based on Legacy Software Analysis
"""

from datetime import datetime, date
from sqlalchemy import func, and_, or_
from models import db, Party, Sale, Purchase, Cashbook, Ledger
from typing import Dict, List, Tuple, Optional

class CreditBusinessLogic:
    """Credit-based business logic based on legacy analysis"""
    
    @staticmethod
    def calculate_party_balance(party_cd: str, user_id: int, as_of_date: date = None) -> Dict:
        """
        Calculate real-time party balance based on legacy logic
        Party Balance = Total Sales - Total Payments Received
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get total sales for the party
        sales_query = Sale.query.filter(
            Sale.party_cd == party_cd,
            Sale.user_id == user_id,
            Sale.bill_date <= as_of_date
        )
        total_sales = sales_query.with_entities(func.sum(Sale.sal_amt)).scalar() or 0
        
        # Get total payments received for the party
        payments_query = Cashbook.query.filter(
            Cashbook.party_cd == party_cd,
            Cashbook.user_id == user_id,
            Cashbook.date <= as_of_date,
            Cashbook.cr_amt > 0  # Only credit entries (payments received)
        )
        total_payments = payments_query.with_entities(func.sum(Cashbook.cr_amt)).scalar() or 0
        
        # Calculate balance
        current_balance = total_sales - total_payments
        balance_type = 'C' if current_balance < 0 else 'D'  # C for Credit, D for Debit
        
        return {
            'party_cd': party_cd,
            'total_sales': total_sales,
            'total_payments': total_payments,
            'current_balance': abs(current_balance),
            'balance_type': balance_type,
            'as_of_date': as_of_date
        }
    
    @staticmethod
    def calculate_inventory_balance(item_cd: str, user_id: int, as_of_date: date = None) -> Dict:
        """
        Calculate inventory balance for an item
        Inventory Balance = Total Purchases - Total Sales
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get total purchases for the item
        purchases_query = Purchase.query.filter(
            Purchase.it_cd == item_cd,
            Purchase.user_id == user_id,
            Purchase.bill_date <= as_of_date
        )
        total_purchases = purchases_query.with_entities(func.sum(Purchase.qty)).scalar() or 0
        
        # Get total sales for the item
        sales_query = Sale.query.filter(
            Sale.it_cd == item_cd,
            Sale.user_id == user_id,
            Sale.bill_date <= as_of_date
        )
        total_sales = sales_query.with_entities(func.sum(Sale.qty)).scalar() or 0
        
        # Calculate balance
        current_balance = total_purchases - total_sales
        
        return {
            'item_cd': item_cd,
            'total_purchases': total_purchases,
            'total_sales': total_sales,
            'current_balance': current_balance,
            'as_of_date': as_of_date
        }
    
    @staticmethod
    def update_party_balance(party_cd: str, user_id: int) -> bool:
        """
        Update party's current balance in the database
        """
        try:
            balance_info = CreditBusinessLogic.calculate_party_balance(party_cd, user_id)
            
            party = Party.query.filter_by(party_cd=party_cd, user_id=user_id).first()
            if party:
                party.current_balance = balance_info['current_balance']
                party.modified_date = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error updating party balance: {e}")
            return False
    
    @staticmethod
    def process_payment(sale_id: int, amount: float, payment_type: str, 
                       payment_date: date, user_id: int, **kwargs) -> Dict:
        """
        Process payment and update all related balances
        Based on legacy cashbook logic
        """
        try:
            # Get the sale record
            sale = Sale.query.filter_by(id=sale_id, user_id=user_id).first()
            if not sale:
                return {'success': False, 'message': 'Sale not found'}
            
            # Create cashbook entry
            cashbook_entry = Cashbook(
                user_id=user_id,
                date=payment_date,
                party_cd=sale.party_cd,
                narration=f"Payment for Sale Bill No. {sale.bill_no}",
                cr_amt=amount,  # Credit amount (payment received)
                dr_amt=0,
                voucher_type='PAYMENT',
                voucher_no=str(sale.bill_no),
                related_sale_id=sale_id,
                payment_type=payment_type,
                reference_no=kwargs.get('reference_no'),
                payment_method=kwargs.get('payment_method'),
                bank_name=kwargs.get('bank_name'),
                branch_name=kwargs.get('branch_name'),
                cheque_date=kwargs.get('cheque_date'),
                transaction_date=datetime.utcnow()
            )
            
            db.session.add(cashbook_entry)
            
            # Update sale payment status
            sale.amount_paid += amount
            if sale.amount_paid >= sale.sal_amt:
                sale.payment_status = 'PAID'
            elif sale.amount_paid > 0:
                sale.payment_status = 'PARTIAL'
            
            # Create ledger entry
            ledger_entry = Ledger(
                user_id=user_id,
                date=payment_date,
                party_cd=sale.party_cd,
                narration=f"Payment received for Sale Bill No. {sale.bill_no}",
                dr_amt=0,
                cr_amt=amount,
                voucher_type='PAYMENT',
                voucher_no=str(sale.bill_no),
                reference_no=kwargs.get('reference_no'),
                cashbook_id=cashbook_entry.id,
                sale_id=sale_id,
                financial_year=f"{payment_date.year}-{payment_date.year + 1}",
                month=payment_date.month,
                day=payment_date.day,
                balance_type='C'
            )
            
            db.session.add(ledger_entry)
            
            # Update party balance
            CreditBusinessLogic.update_party_balance(sale.party_cd, user_id)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Payment processed successfully',
                'cashbook_id': cashbook_entry.id,
                'ledger_id': ledger_entry.id
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error processing payment: {str(e)}'}
    
    @staticmethod
    def create_sale_entry(sale_data: Dict, user_id: int) -> Dict:
        """
        Create sale entry with proper balance updates
        Based on legacy sale logic
        """
        try:
            # Create sale entry
            sale = Sale(
                user_id=user_id,
                bill_no=sale_data['bill_no'],
                bill_date=sale_data['bill_date'],
                party_cd=sale_data['party_cd'],
                it_cd=sale_data['it_cd'],
                qty=sale_data['qty'],
                rate=sale_data['rate'],
                sal_amt=sale_data['sal_amt'],
                purchase_id=sale_data.get('purchase_id'),
                payment_status='PENDING',
                payment_due_date=sale_data.get('payment_due_date'),
                amount_paid=0,
                payment_terms=sale_data.get('payment_terms'),
                credit_days=sale_data.get('credit_days', 0)
            )
            
            db.session.add(sale)
            
            # Create ledger entry for sale
            ledger_entry = Ledger(
                user_id=user_id,
                date=sale_data['bill_date'],
                party_cd=sale_data['party_cd'],
                narration=f"Sale Bill No. {sale_data['bill_no']} - {sale_data.get('item_name', '')}",
                dr_amt=sale_data['sal_amt'],
                cr_amt=0,
                voucher_type='SALE',
                voucher_no=str(sale_data['bill_no']),
                sale_id=sale.id,
                financial_year=f"{sale_data['bill_date'].year}-{sale_data['bill_date'].year + 1}",
                month=sale_data['bill_date'].month,
                day=sale_data['bill_date'].day,
                balance_type='D'
            )
            
            db.session.add(ledger_entry)
            
            # Update party balance
            CreditBusinessLogic.update_party_balance(sale_data['party_cd'], user_id)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Sale entry created successfully',
                'sale_id': sale.id,
                'ledger_id': ledger_entry.id
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error creating sale entry: {str(e)}'}
    
    @staticmethod
    def get_party_statement(party_cd: str, user_id: int, 
                           from_date: date = None, to_date: date = None) -> Dict:
        """
        Get comprehensive party statement
        Based on legacy ledger format
        """
        if from_date is None:
            from_date = date(date.today().year, 4, 1)  # Start of financial year
        
        if to_date is None:
            to_date = date.today()
        
        # Get opening balance
        opening_balance = CreditBusinessLogic.calculate_party_balance(
            party_cd, user_id, from_date - date.resolution
        )
        
        # Get ledger entries
        ledger_entries = Ledger.query.filter(
            Ledger.party_cd == party_cd,
            Ledger.user_id == user_id,
            Ledger.date >= from_date,
            Ledger.date <= to_date
        ).order_by(Ledger.date, Ledger.id).all()
        
        # Calculate running balance
        running_balance = opening_balance['current_balance']
        if opening_balance['balance_type'] == 'C':
            running_balance = -running_balance
        
        statement_entries = []
        for entry in ledger_entries:
            if entry.dr_amt > 0:
                running_balance += entry.dr_amt
            else:
                running_balance -= entry.cr_amt
            
            statement_entries.append({
                'date': entry.date,
                'narration': entry.narration,
                'debit': entry.dr_amt,
                'credit': entry.cr_amt,
                'balance': abs(running_balance),
                'balance_type': 'C' if running_balance < 0 else 'D',
                'voucher_type': entry.voucher_type,
                'voucher_no': entry.voucher_no
            })
        
        # Get closing balance
        closing_balance = CreditBusinessLogic.calculate_party_balance(party_cd, user_id, to_date)
        
        return {
            'party_cd': party_cd,
            'from_date': from_date,
            'to_date': to_date,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'entries': statement_entries,
            'total_debits': sum(entry['debit'] for entry in statement_entries),
            'total_credits': sum(entry['credit'] for entry in statement_entries)
        }
    
    @staticmethod
    def get_pending_payments(user_id: int, party_cd: str = None) -> List[Dict]:
        """
        Get list of pending payments
        """
        query = Sale.query.filter(
            Sale.user_id == user_id,
            Sale.payment_status.in_(['PENDING', 'PARTIAL'])
        )
        
        if party_cd:
            query = query.filter(Sale.party_cd == party_cd)
        
        pending_sales = query.all()
        
        pending_payments = []
        for sale in pending_sales:
            pending_amount = sale.sal_amt - sale.amount_paid
            pending_payments.append({
                'sale_id': sale.id,
                'bill_no': sale.bill_no,
                'bill_date': sale.bill_date,
                'party_cd': sale.party_cd,
                'party_name': sale.party.party_nm if sale.party else '',
                'total_amount': sale.sal_amt,
                'amount_paid': sale.amount_paid,
                'pending_amount': pending_amount,
                'payment_status': sale.payment_status,
                'payment_due_date': sale.payment_due_date
            })
        
        return pending_payments
    
    @staticmethod
    def check_credit_limit(party_cd: str, user_id: int, new_sale_amount: float) -> Dict:
        """
        Check if party has sufficient credit limit
        """
        party = Party.query.filter_by(party_cd=party_cd, user_id=user_id).first()
        if not party:
            return {'allowed': False, 'message': 'Party not found'}
        
        current_balance = CreditBusinessLogic.calculate_party_balance(party_cd, user_id)
        total_exposure = current_balance['current_balance'] + new_sale_amount
        
        if party.credit_limit > 0 and total_exposure > party.credit_limit:
            return {
                'allowed': False,
                'message': f'Credit limit exceeded. Limit: {party.credit_limit}, Exposure: {total_exposure}',
                'credit_limit': party.credit_limit,
                'current_exposure': total_exposure
            }
        
        return {
            'allowed': True,
            'message': 'Credit limit check passed',
            'credit_limit': party.credit_limit,
            'current_exposure': total_exposure
        }

# Utility functions for legacy compatibility
def get_financial_year(date_obj: date) -> str:
    """Get financial year string (e.g., '2024-25')"""
    if date_obj.month >= 4:
        return f"{date_obj.year}-{date_obj.year + 1}"
    else:
        return f"{date_obj.year - 1}-{date_obj.year}"

def format_balance_for_display(balance: float, balance_type: str) -> str:
    """Format balance for display (legacy style)"""
    if balance_type == 'C':
        return f"({balance:,.2f})"
    else:
        return f"{balance:,.2f}" 