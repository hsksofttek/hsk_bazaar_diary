#!/usr/bin/env python3
"""
Bank Management System
Bank accounts, transactions, and reconciliation management
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import db
from models import BankAccount, BankTransaction
import json
import logging

class BankManagementSystem:
    """Comprehensive Bank Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_bank_account(self, account_data: Dict) -> Tuple[bool, str]:
        """Create new bank account"""
        try:
            # Validate required fields
            required_fields = ['account_name', 'bank_name', 'account_number']
            for field in required_fields:
                if not account_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Check if account number already exists
            existing = BankAccount.query.filter_by(account_number=account_data['account_number']).first()
            if existing:
                return False, "Account number already exists"
            
            # Create new bank account
            account = BankAccount(
                account_name=account_data['account_name'],
                bank_name=account_data['bank_name'],
                account_number=account_data['account_number'],
                ifsc_code=account_data.get('ifsc_code', ''),
                branch_name=account_data.get('branch_name', ''),
                account_type=account_data.get('account_type', 'SAVINGS'),
                opening_balance=float(account_data.get('opening_balance', 0)),
                current_balance=float(account_data.get('opening_balance', 0)),
                status=account_data.get('status', 'ACTIVE'),
                remarks=account_data.get('remarks', '')
            )
            
            db.session.add(account)
            db.session.commit()
            
            return True, "Bank account created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating bank account: {e}")
            return False, f"Error creating bank account: {str(e)}"
    
    def update_bank_account(self, account_id: int, account_data: Dict) -> Tuple[bool, str]:
        """Update existing bank account"""
        try:
            account = BankAccount.query.get(account_id)
            if not account:
                return False, "Bank account not found"
            
            # Update fields
            for key, value in account_data.items():
                if hasattr(account, key):
                    if key in ['opening_balance', 'current_balance']:
                        setattr(account, key, float(value))
                    else:
                        setattr(account, key, value)
            
            db.session.commit()
            return True, "Bank account updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating bank account: {e}")
            return False, f"Error updating bank account: {str(e)}"
    
    def delete_bank_account(self, account_id: int) -> Tuple[bool, str]:
        """Delete bank account"""
        try:
            account = BankAccount.query.get(account_id)
            if not account:
                return False, "Bank account not found"
            
            # Check if account has transactions
            transactions_count = BankTransaction.query.filter_by(account_id=account_id).count()
            if transactions_count > 0:
                return False, f"Cannot delete account. Associated with {transactions_count} transactions"
            
            db.session.delete(account)
            db.session.commit()
            return True, "Bank account deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting bank account: {e}")
            return False, f"Error deleting bank account: {str(e)}"
    
    def create_bank_transaction(self, transaction_data: Dict) -> Tuple[bool, str]:
        """Create new bank transaction"""
        try:
            # Validate required fields
            required_fields = ['account_id', 'transaction_date', 'amount', 'transaction_type']
            for field in required_fields:
                if not transaction_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Get account
            account = BankAccount.query.get(transaction_data['account_id'])
            if not account:
                return False, "Bank account not found"
            
            # Create transaction
            transaction = BankTransaction(
                account_id=transaction_data['account_id'],
                transaction_date=datetime.strptime(transaction_data['transaction_date'], '%Y-%m-%d').date(),
                amount=float(transaction_data['amount']),
                transaction_type=transaction_data['transaction_type'],  # CREDIT, DEBIT
                narration=transaction_data.get('narration', ''),
                reference_no=transaction_data.get('reference_no', ''),
                cheque_no=transaction_data.get('cheque_no', ''),
                party_cd=transaction_data.get('party_cd', ''),
                category=transaction_data.get('category', ''),
                status=transaction_data.get('status', 'COMPLETED')
            )
            
            db.session.add(transaction)
            
            # Update account balance
            if transaction_data['transaction_type'] == 'CREDIT':
                account.current_balance += float(transaction_data['amount'])
            else:
                account.current_balance -= float(transaction_data['amount'])
            
            db.session.commit()
            return True, "Bank transaction created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating bank transaction: {e}")
            return False, f"Error creating bank transaction: {str(e)}"
    
    def get_bank_accounts(self, filters: Dict = None) -> List[Dict]:
        """Get bank accounts with optional filters"""
        try:
            query = BankAccount.query
            
            if filters:
                if filters.get('status'):
                    query = query.filter(BankAccount.status == filters['status'])
                if filters.get('bank_name'):
                    query = query.filter(BankAccount.bank_name.like(f"%{filters['bank_name']}%"))
                if filters.get('account_type'):
                    query = query.filter(BankAccount.account_type == filters['account_type'])
            
            accounts = query.order_by(BankAccount.account_name).all()
            return [self._bank_account_to_dict(account) for account in accounts]
            
        except Exception as e:
            self.logger.error(f"Error getting bank accounts: {e}")
            return []
    
    def get_bank_transactions(self, filters: Dict = None) -> List[Dict]:
        """Get bank transactions with optional filters"""
        try:
            query = BankTransaction.query.join(BankAccount)
            
            if filters:
                if filters.get('account_id'):
                    query = query.filter(BankTransaction.account_id == filters['account_id'])
                if filters.get('transaction_type'):
                    query = query.filter(BankTransaction.transaction_type == filters['transaction_type'])
                if filters.get('date_from'):
                    query = query.filter(BankTransaction.transaction_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(BankTransaction.transaction_date <= filters['date_to'])
                if filters.get('status'):
                    query = query.filter(BankTransaction.status == filters['status'])
            
            transactions = query.order_by(BankTransaction.transaction_date.desc()).all()
            return [self._bank_transaction_to_dict(transaction) for transaction in transactions]
            
        except Exception as e:
            self.logger.error(f"Error getting bank transactions: {e}")
            return []
    
    def get_bank_account_by_id(self, account_id: int) -> Optional[Dict]:
        """Get bank account by ID"""
        try:
            account = BankAccount.query.get(account_id)
            return self._bank_account_to_dict(account) if account else None
        except Exception as e:
            self.logger.error(f"Error getting bank account by ID: {e}")
            return None
    
    def get_bank_statistics(self) -> Dict:
        """Get bank management statistics"""
        try:
            total_accounts = BankAccount.query.count()
            active_accounts = BankAccount.query.filter_by(status='ACTIVE').count()
            total_balance = db.session.query(db.func.sum(BankAccount.current_balance)).scalar() or 0
            
            # Get transaction statistics
            total_transactions = BankTransaction.query.count()
            credit_transactions = BankTransaction.query.filter_by(transaction_type='CREDIT').count()
            debit_transactions = BankTransaction.query.filter_by(transaction_type='DEBIT').count()
            
            # Get total credit and debit amounts
            total_credit = db.session.query(db.func.sum(BankTransaction.amount)).filter_by(transaction_type='CREDIT').scalar() or 0
            total_debit = db.session.query(db.func.sum(BankTransaction.amount)).filter_by(transaction_type='DEBIT').scalar() or 0
            
            # Get accounts by bank
            bank_stats = db.session.query(
                BankAccount.bank_name,
                db.func.count(BankAccount.id).label('count'),
                db.func.sum(BankAccount.current_balance).label('total_balance')
            ).group_by(BankAccount.bank_name).all()
            
            # Get recent transactions
            recent_transactions = BankTransaction.query.join(BankAccount).order_by(
                BankTransaction.transaction_date.desc()
            ).limit(10).all()
            
            return {
                'total_accounts': total_accounts,
                'active_accounts': active_accounts,
                'total_balance': total_balance,
                'total_transactions': total_transactions,
                'credit_transactions': credit_transactions,
                'debit_transactions': debit_transactions,
                'total_credit': total_credit,
                'total_debit': total_debit,
                'net_balance': total_credit - total_debit,
                'bank_distribution': [
                    {
                        'bank_name': stat.bank_name,
                        'count': stat.count,
                        'total_balance': stat.total_balance or 0
                    } for stat in bank_stats
                ],
                'recent_transactions': [
                    self._bank_transaction_to_dict(transaction) for transaction in recent_transactions
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting bank statistics: {e}")
            return {}
    
    def get_bank_reports(self, report_type: str, filters: Dict = None) -> List[Dict]:
        """Get bank reports"""
        try:
            if report_type == 'account_summary':
                return self._get_account_summary_report(filters)
            elif report_type == 'transaction_summary':
                return self._get_transaction_summary_report(filters)
            elif report_type == 'bank_wise':
                return self._get_bank_wise_report(filters)
            elif report_type == 'reconciliation':
                return self._get_reconciliation_report(filters)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting bank reports: {e}")
            return []
    
    def _get_account_summary_report(self, filters: Dict = None) -> List[Dict]:
        """Get account summary report"""
        try:
            query = """
                SELECT 
                    ba.id,
                    ba.account_name,
                    ba.bank_name,
                    ba.account_number,
                    ba.account_type,
                    ba.opening_balance,
                    ba.current_balance,
                    COUNT(bt.id) as total_transactions,
                    SUM(CASE WHEN bt.transaction_type = 'CREDIT' THEN bt.amount ELSE 0 END) as total_credit,
                    SUM(CASE WHEN bt.transaction_type = 'DEBIT' THEN bt.amount ELSE 0 END) as total_debit
                FROM bank_accounts ba
                LEFT JOIN bank_transactions bt ON ba.id = bt.account_id
            """
            
            where_clause = "WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('status'):
                    where_clause += " AND ba.status = ?"
                    params.append(filters['status'])
                if filters.get('bank_name'):
                    where_clause += " AND ba.bank_name LIKE ?"
                    params.append(f"%{filters['bank_name']}%")
            
            query += f" {where_clause} GROUP BY ba.id, ba.account_name, ba.bank_name, ba.account_number, ba.account_type, ba.opening_balance, ba.current_balance"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'account_id': result.id,
                    'account_name': result.account_name,
                    'bank_name': result.bank_name,
                    'account_number': result.account_number,
                    'account_type': result.account_type,
                    'opening_balance': result.opening_balance,
                    'current_balance': result.current_balance,
                    'total_transactions': result.total_transactions or 0,
                    'total_credit': result.total_credit or 0,
                    'total_debit': result.total_debit or 0
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting account summary report: {e}")
            return []
    
    def _get_transaction_summary_report(self, filters: Dict = None) -> List[Dict]:
        """Get transaction summary report"""
        try:
            query = """
                SELECT 
                    bt.transaction_date,
                    bt.transaction_type,
                    bt.amount,
                    bt.narration,
                    bt.reference_no,
                    bt.cheque_no,
                    bt.party_cd,
                    bt.category,
                    ba.account_name,
                    ba.bank_name
                FROM bank_transactions bt
                LEFT JOIN bank_accounts ba ON bt.account_id = ba.id
                WHERE 1=1
            """
            
            params = []
            
            if filters:
                if filters.get('account_id'):
                    query += " AND bt.account_id = ?"
                    params.append(filters['account_id'])
                if filters.get('transaction_type'):
                    query += " AND bt.transaction_type = ?"
                    params.append(filters['transaction_type'])
                if filters.get('date_from'):
                    query += " AND bt.transaction_date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    query += " AND bt.transaction_date <= ?"
                    params.append(filters['date_to'])
            
            query += " ORDER BY bt.transaction_date DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'transaction_date': result.transaction_date.isoformat() if result.transaction_date else None,
                    'transaction_type': result.transaction_type,
                    'amount': result.amount,
                    'narration': result.narration,
                    'reference_no': result.reference_no,
                    'cheque_no': result.cheque_no,
                    'party_cd': result.party_cd,
                    'category': result.category,
                    'account_name': result.account_name,
                    'bank_name': result.bank_name
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting transaction summary report: {e}")
            return []
    
    def _get_bank_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get bank-wise report"""
        try:
            query = """
                SELECT 
                    ba.bank_name,
                    COUNT(ba.id) as account_count,
                    SUM(ba.current_balance) as total_balance,
                    COUNT(bt.id) as transaction_count,
                    SUM(CASE WHEN bt.transaction_type = 'CREDIT' THEN bt.amount ELSE 0 END) as total_credit,
                    SUM(CASE WHEN bt.transaction_type = 'DEBIT' THEN bt.amount ELSE 0 END) as total_debit
                FROM bank_accounts ba
                LEFT JOIN bank_transactions bt ON ba.id = bt.account_id
            """
            
            where_clause = "WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('status'):
                    where_clause += " AND ba.status = ?"
                    params.append(filters['status'])
            
            query += f" {where_clause} GROUP BY ba.bank_name ORDER BY total_balance DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'bank_name': result.bank_name,
                    'account_count': result.account_count,
                    'total_balance': result.total_balance or 0,
                    'transaction_count': result.transaction_count or 0,
                    'total_credit': result.total_credit or 0,
                    'total_debit': result.total_debit or 0
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting bank-wise report: {e}")
            return []
    
    def _get_reconciliation_report(self, filters: Dict = None) -> List[Dict]:
        """Get reconciliation report"""
        try:
            # This would typically compare bank statement with internal records
            # For now, return a basic reconciliation report
            query = """
                SELECT 
                    ba.account_name,
                    ba.bank_name,
                    ba.current_balance as internal_balance,
                    COUNT(bt.id) as transaction_count,
                    SUM(CASE WHEN bt.transaction_type = 'CREDIT' THEN bt.amount ELSE 0 END) as total_credit,
                    SUM(CASE WHEN bt.transaction_type = 'DEBIT' THEN bt.amount ELSE 0 END) as total_debit
                FROM bank_accounts ba
                LEFT JOIN bank_transactions bt ON ba.id = bt.account_id
                WHERE ba.status = 'ACTIVE'
                GROUP BY ba.id, ba.account_name, ba.bank_name, ba.current_balance
            """
            
            results = db.session.execute(query).fetchall()
            
            return [
                {
                    'account_name': result.account_name,
                    'bank_name': result.bank_name,
                    'internal_balance': result.internal_balance,
                    'transaction_count': result.transaction_count or 0,
                    'total_credit': result.total_credit or 0,
                    'total_debit': result.total_debit or 0,
                    'calculated_balance': (result.total_credit or 0) - (result.total_debit or 0),
                    'difference': result.internal_balance - ((result.total_credit or 0) - (result.total_debit or 0))
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting reconciliation report: {e}")
            return []
    
    def validate_bank_account_data(self, account_data: Dict) -> Tuple[bool, str]:
        """Validate bank account data"""
        try:
            # Check required fields
            if not account_data.get('account_name'):
                return False, "Account name is required"
            
            if not account_data.get('bank_name'):
                return False, "Bank name is required"
            
            if not account_data.get('account_number'):
                return False, "Account number is required"
            
            # Check if account number already exists (for new entries)
            if 'id' not in account_data:
                existing = BankAccount.query.filter_by(account_number=account_data['account_number']).first()
                if existing:
                    return False, "Account number already exists"
            
            # Validate balance
            if account_data.get('opening_balance'):
                try:
                    float(account_data['opening_balance'])
                except ValueError:
                    return False, "Invalid opening balance"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating bank account data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def validate_bank_transaction_data(self, transaction_data: Dict) -> Tuple[bool, str]:
        """Validate bank transaction data"""
        try:
            # Check required fields
            if not transaction_data.get('account_id'):
                return False, "Account is required"
            
            if not transaction_data.get('transaction_date'):
                return False, "Transaction date is required"
            
            if not transaction_data.get('amount'):
                return False, "Amount is required"
            
            if not transaction_data.get('transaction_type'):
                return False, "Transaction type is required"
            
            # Validate amount
            try:
                amount = float(transaction_data['amount'])
                if amount <= 0:
                    return False, "Amount must be greater than 0"
            except ValueError:
                return False, "Invalid amount"
            
            # Validate transaction type
            if transaction_data['transaction_type'] not in ['CREDIT', 'DEBIT']:
                return False, "Transaction type must be CREDIT or DEBIT"
            
            # Validate date format
            try:
                datetime.strptime(transaction_data['transaction_date'], '%Y-%m-%d')
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating bank transaction data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _bank_account_to_dict(self, account: BankAccount) -> Dict:
        """Convert bank account object to dictionary"""
        if not account:
            return {}
        
        return {
            'id': account.id,
            'account_name': account.account_name,
            'bank_name': account.bank_name,
            'account_number': account.account_number,
            'ifsc_code': account.ifsc_code,
            'branch_name': account.branch_name,
            'account_type': account.account_type,
            'opening_balance': account.opening_balance,
            'current_balance': account.current_balance,
            'status': account.status,
            'remarks': account.remarks,
            'created_date': account.created_date.isoformat() if account.created_date else None,
            'modified_date': account.modified_date.isoformat() if account.modified_date else None
        }
    
    def _bank_transaction_to_dict(self, transaction: BankTransaction) -> Dict:
        """Convert bank transaction object to dictionary"""
        if not transaction:
            return {}
        
        return {
            'id': transaction.id,
            'account_id': transaction.account_id,
            'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type,
            'narration': transaction.narration,
            'reference_no': transaction.reference_no,
            'cheque_no': transaction.cheque_no,
            'party_cd': transaction.party_cd,
            'category': transaction.category,
            'status': transaction.status,
            'created_date': transaction.created_date.isoformat() if transaction.created_date else None
        } 