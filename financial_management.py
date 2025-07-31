#!/usr/bin/env python3
"""
Advanced Financial Management System
Complete implementation with Chart of Accounts, Journal Entries, General Ledger, and Financial Reports
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json
from database import db
from models import User, Party, Purchase, Sale, Cashbook, Bankbook
from sqlalchemy import func, and_, or_, desc, asc
import uuid

class FinancialManagementSystem:
    """Complete Financial Management System with full functionality"""
    
    def __init__(self):
        self.system_name = "Financial Management System"
        self.version = "2.0"
    
    # ==================== CHART OF ACCOUNTS ====================
    
    def create_account(self, user_id: int, account_data: Dict) -> Dict:
        """Create new account in Chart of Accounts"""
        try:
            # In a real system, you'd have a separate ChartOfAccounts table
            # For now, we'll use the Party table to represent accounts
            account_code = account_data.get('account_code')
            account_name = account_data.get('account_name')
            account_type = account_data.get('account_type', 'LIABILITY')
            
            # Check if account already exists
            existing_account = Party.query.filter_by(party_cd=account_code, user_id=user_id).first()
            if existing_account:
                return {'success': False, 'error': f"Account with code {account_code} already exists"}
            
            # Create new account
            new_account = Party(
                user_id=user_id,
                party_cd=account_code,
                party_nm=account_name,
                ledgtyp=account_type,
                opening_bal=float(account_data.get('opening_balance', 0)),
                current_balance=float(account_data.get('opening_balance', 0)),
                credit_limit=float(account_data.get('credit_limit', 0)),
                created_date=datetime.now()
            )
            
            db.session.add(new_account)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Account {account_name} created successfully',
                'account_code': account_code
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_accounts(self, user_id: int, account_type: str = None) -> Dict:
        """Get accounts from Chart of Accounts"""
        try:
            query = Party.query.filter(Party.user_id == user_id)
            
            if account_type:
                query = query.filter(Party.ledgtyp == account_type)
            
            accounts = query.all()
            
            return {
                'success': True,
                'accounts': [{
                    'account_code': account.party_cd,
                    'account_name': account.party_nm,
                    'account_type': account.ledgtyp,
                    'opening_balance': float(account.opening_bal),
                    'current_balance': float(account.current_balance),
                    'credit_limit': float(account.credit_limit),
                    'created_date': account.created_date.strftime('%Y-%m-%d') if account.created_date else None
                } for account in accounts]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_account(self, user_id: int, account_code: str, updates: Dict) -> Dict:
        """Update account in Chart of Accounts"""
        try:
            account = Party.query.filter_by(party_cd=account_code, user_id=user_id).first()
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            # Update fields
            if 'account_name' in updates:
                account.party_nm = updates['account_name']
            if 'account_type' in updates:
                account.ledgtyp = updates['account_type']
            if 'opening_balance' in updates:
                account.opening_bal = float(updates['opening_balance'])
            if 'credit_limit' in updates:
                account.credit_limit = float(updates['credit_limit'])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Account {account_code} updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def delete_account(self, user_id: int, account_code: str) -> Dict:
        """Delete account from Chart of Accounts"""
        try:
            account = Party.query.filter_by(party_cd=account_code, user_id=user_id).first()
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            # Check if account has transactions
            transaction_count = self._get_account_transaction_count(user_id, account_code)
            if transaction_count > 0:
                return {'success': False, 'error': 'Cannot delete account with transaction history'}
            
            db.session.delete(account)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Account {account_code} deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== JOURNAL ENTRIES ====================
    
    def create_journal_entry(self, user_id: int, entry_data: Dict) -> Dict:
        """Create journal entry"""
        try:
            entry_date = datetime.strptime(entry_data['entry_date'], '%Y-%m-%d').date()
            narration = entry_data.get('narration', '')
            voucher_no = entry_data.get('voucher_no', f"JV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}")
            
            # Validate entries
            entries = entry_data.get('entries', [])
            if not entries:
                return {'success': False, 'error': 'No entries provided'}
            
            # Check if debits equal credits
            total_debit = sum(float(entry.get('debit', 0)) for entry in entries)
            total_credit = sum(float(entry.get('credit', 0)) for entry in entries)
            
            if abs(total_debit - total_credit) > 0.01:  # Allow for small rounding differences
                return {'success': False, 'error': 'Debits and credits must be equal'}
            
            # Create journal entries
            for entry in entries:
                account_code = entry.get('account_code')
                debit_amount = float(entry.get('debit', 0))
                credit_amount = float(entry.get('credit', 0))
                
                # Validate account
                account = Party.query.filter_by(party_cd=account_code, user_id=user_id).first()
                if not account:
                    return {'success': False, 'error': f'Account {account_code} not found'}
                
                # Create cashbook entry for journal entry
                journal_entry = Cashbook(
                    user_id=user_id,
                    date=entry_date,
                    narration=f"Journal Entry: {narration}",
                    dr_amt=debit_amount,
                    cr_amt=credit_amount,
                    balance=credit_amount - debit_amount,
                    party_cd=account_code,
                    voucher_type='JOURNAL',
                    voucher_no=voucher_no
                )
                
                db.session.add(journal_entry)
                
                # Update account balance
                if debit_amount > 0:
                    account.current_balance += debit_amount
                if credit_amount > 0:
                    account.current_balance -= credit_amount
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Journal entry created successfully',
                'voucher_no': voucher_no,
                'total_debit': total_debit,
                'total_credit': total_credit
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_journal_entries(self, user_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """Get journal entries"""
        try:
            query = Cashbook.query.filter(
                Cashbook.user_id == user_id,
                Cashbook.voucher_type == 'JOURNAL'
            )
            
            if start_date:
                query = query.filter(Cashbook.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                query = query.filter(Cashbook.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            entries = query.order_by(desc(Cashbook.date)).all()
            
            # Group by voucher number
            journal_entries = {}
            for entry in entries:
                voucher_no = entry.voucher_no
                if voucher_no not in journal_entries:
                    journal_entries[voucher_no] = {
                        'voucher_no': voucher_no,
                        'entry_date': entry.date.strftime('%Y-%m-%d'),
                        'narration': entry.narration,
                        'entries': []
                    }
                
                journal_entries[voucher_no]['entries'].append({
                    'account_code': entry.party_cd,
                    'debit': float(entry.dr_amt),
                    'credit': float(entry.cr_amt)
                })
            
            return {
                'success': True,
                'journal_entries': list(journal_entries.values())
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== GENERAL LEDGER ====================
    
    def get_ledger(self, user_id: int, account_code: str, start_date: str = None, end_date: str = None) -> Dict:
        """Get general ledger for an account"""
        try:
            # Validate account
            account = Party.query.filter_by(party_cd=account_code, user_id=user_id).first()
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            # Get all transactions for the account
            query = db.session.query(
                Cashbook.date,
                Cashbook.narration,
                Cashbook.dr_amt,
                Cashbook.cr_amt,
                Cashbook.voucher_type,
                Cashbook.voucher_no
            ).filter(
                Cashbook.user_id == user_id,
                Cashbook.party_cd == account_code
            )
            
            if start_date:
                query = query.filter(Cashbook.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            if end_date:
                query = query.filter(Cashbook.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
            transactions = query.order_by(Cashbook.date).all()
            
            # Calculate running balance
            opening_balance = float(account.opening_bal)
            running_balance = opening_balance
            ledger_entries = []
            
            for transaction in transactions:
                debit = float(transaction.dr_amt)
                credit = float(transaction.cr_amt)
                running_balance += credit - debit
                
                ledger_entries.append({
                    'date': transaction.date.strftime('%Y-%m-%d'),
                    'narration': transaction.narration,
                    'debit': debit,
                    'credit': credit,
                    'balance': running_balance,
                    'voucher_type': transaction.voucher_type,
                    'voucher_no': transaction.voucher_no
                })
            
            return {
                'success': True,
                'ledger': {
                    'account_code': account_code,
                    'account_name': account.party_nm,
                    'opening_balance': opening_balance,
                    'closing_balance': running_balance,
                    'entries': ledger_entries
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== TRIAL BALANCE ====================
    
    def get_trial_balance(self, user_id: int, as_of_date: str = None) -> Dict:
        """Get trial balance"""
        try:
            if as_of_date:
                as_of = datetime.strptime(as_of_date, '%Y-%m-%d').date()
            else:
                as_of = date.today()
            
            # Get all accounts
            accounts = Party.query.filter_by(user_id=user_id).all()
            
            trial_balance = []
            total_debit = 0
            total_credit = 0
            
            for account in accounts:
                # Calculate account balance as of date
                balance = self._calculate_account_balance_as_of(user_id, account.party_cd, as_of)
                
                if balance != 0:
                    if balance > 0:
                        debit = balance
                        credit = 0
                    else:
                        debit = 0
                        credit = abs(balance)
                    
                    trial_balance.append({
                        'account_code': account.party_cd,
                        'account_name': account.party_nm,
                        'debit': debit,
                        'credit': credit
                    })
                    
                    total_debit += debit
                    total_credit += credit
            
            return {
                'success': True,
                'trial_balance': {
                    'as_of_date': as_of.strftime('%Y-%m-%d'),
                    'accounts': trial_balance,
                    'total_debit': total_debit,
                    'total_credit': total_credit,
                    'is_balanced': abs(total_debit - total_credit) < 0.01
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== BALANCE SHEET ====================
    
    def get_balance_sheet(self, user_id: int, as_of_date: str = None) -> Dict:
        """Get balance sheet"""
        try:
            if as_of_date:
                as_of = datetime.strptime(as_of_date, '%Y-%m-%d').date()
            else:
                as_of = date.today()
            
            # Get accounts by type
            assets = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'ASSET'
            ).all()
            
            liabilities = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'LIABILITY'
            ).all()
            
            equity = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'EQUITY'
            ).all()
            
            # Calculate balances
            total_assets = 0
            asset_details = []
            for asset in assets:
                balance = self._calculate_account_balance_as_of(user_id, asset.party_cd, as_of)
                if balance > 0:
                    asset_details.append({
                        'account_code': asset.party_cd,
                        'account_name': asset.party_nm,
                        'balance': balance
                    })
                    total_assets += balance
            
            total_liabilities = 0
            liability_details = []
            for liability in liabilities:
                balance = self._calculate_account_balance_as_of(user_id, liability.party_cd, as_of)
                if balance < 0:
                    liability_details.append({
                        'account_code': liability.party_cd,
                        'account_name': liability.party_nm,
                        'balance': abs(balance)
                    })
                    total_liabilities += abs(balance)
            
            total_equity = 0
            equity_details = []
            for eq in equity:
                balance = self._calculate_account_balance_as_of(user_id, eq.party_cd, as_of)
                if balance < 0:
                    equity_details.append({
                        'account_code': eq.party_cd,
                        'account_name': eq.party_nm,
                        'balance': abs(balance)
                    })
                    total_equity += abs(balance)
            
            return {
                'success': True,
                'balance_sheet': {
                    'as_of_date': as_of.strftime('%Y-%m-%d'),
                    'assets': {
                        'total': total_assets,
                        'details': asset_details
                    },
                    'liabilities': {
                        'total': total_liabilities,
                        'details': liability_details
                    },
                    'equity': {
                        'total': total_equity,
                        'details': equity_details
                    },
                    'total_liabilities_and_equity': total_liabilities + total_equity,
                    'is_balanced': abs(total_assets - (total_liabilities + total_equity)) < 0.01
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== PROFIT & LOSS ====================
    
    def get_profit_loss(self, user_id: int, start_date: str, end_date: str) -> Dict:
        """Get profit and loss statement"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Get income accounts
            income_accounts = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'INCOME'
            ).all()
            
            # Get expense accounts
            expense_accounts = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'EXPENSE'
            ).all()
            
            # Calculate income
            total_income = 0
            income_details = []
            for income in income_accounts:
                balance = self._calculate_account_balance_for_period(user_id, income.party_cd, start, end)
                if balance < 0:  # Income is credit balance
                    income_details.append({
                        'account_code': income.party_cd,
                        'account_name': income.party_nm,
                        'amount': abs(balance)
                    })
                    total_income += abs(balance)
            
            # Calculate expenses
            total_expenses = 0
            expense_details = []
            for expense in expense_accounts:
                balance = self._calculate_account_balance_for_period(user_id, expense.party_cd, start, end)
                if balance > 0:  # Expense is debit balance
                    expense_details.append({
                        'account_code': expense.party_cd,
                        'account_name': expense.party_nm,
                        'amount': balance
                    })
                    total_expenses += balance
            
            net_profit = total_income - total_expenses
            
            return {
                'success': True,
                'profit_loss': {
                    'period': f"{start_date} to {end_date}",
                    'income': {
                        'total': total_income,
                        'details': income_details
                    },
                    'expenses': {
                        'total': total_expenses,
                        'details': expense_details
                    },
                    'net_profit': net_profit,
                    'is_profit': net_profit > 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== FINANCIAL REPORTS ====================
    
    def get_financial_reports(self, user_id: int, report_type: str, 
                            start_date: str = None, end_date: str = None) -> Dict:
        """Generate financial reports"""
        try:
            if report_type == 'trial_balance':
                return self.get_trial_balance(user_id, end_date)
            elif report_type == 'balance_sheet':
                return self.get_balance_sheet(user_id, end_date)
            elif report_type == 'profit_loss':
                if not start_date or not end_date:
                    return {'success': False, 'error': 'Start date and end date required for profit & loss'}
                return self.get_profit_loss(user_id, start_date, end_date)
            elif report_type == 'ledger':
                if not start_date:
                    return {'success': False, 'error': 'Account code required for ledger'}
                return self.get_ledger(user_id, start_date, end_date)
            else:
                return {'success': False, 'error': 'Invalid report type'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_financial_statistics(self, user_id: int) -> Dict:
        """Get financial statistics"""
        try:
            # Get total assets
            assets = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'ASSET'
            ).all()
            
            total_assets = 0
            for asset in assets:
                balance = self._calculate_account_balance_as_of(user_id, asset.party_cd, date.today())
                if balance > 0:
                    total_assets += balance
            
            # Get total liabilities
            liabilities = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'LIABILITY'
            ).all()
            
            total_liabilities = 0
            for liability in liabilities:
                balance = self._calculate_account_balance_as_of(user_id, liability.party_cd, date.today())
                if balance < 0:
                    total_liabilities += abs(balance)
            
            # Calculate equity
            total_equity = total_assets - total_liabilities
            
            # Get this month's income and expenses
            start_of_month = date.today().replace(day=1)
            
            income_accounts = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'INCOME'
            ).all()
            
            expense_accounts = Party.query.filter(
                Party.user_id == user_id,
                Party.ledgtyp == 'EXPENSE'
            ).all()
            
            monthly_income = 0
            for income in income_accounts:
                balance = self._calculate_account_balance_for_period(user_id, income.party_cd, start_of_month, date.today())
                if balance < 0:
                    monthly_income += abs(balance)
            
            monthly_expenses = 0
            for expense in expense_accounts:
                balance = self._calculate_account_balance_for_period(user_id, expense.party_cd, start_of_month, date.today())
                if balance > 0:
                    monthly_expenses += balance
            
            monthly_profit = monthly_income - monthly_expenses
            
            return {
                'success': True,
                'statistics': {
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'total_equity': total_equity,
                    'monthly_income': monthly_income,
                    'monthly_expenses': monthly_expenses,
                    'monthly_profit': monthly_profit,
                    'debt_to_equity_ratio': total_liabilities / total_equity if total_equity > 0 else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== UTILITY METHODS ====================
    
    def _get_account_transaction_count(self, user_id: int, account_code: str) -> int:
        """Get transaction count for an account"""
        try:
            count = Cashbook.query.filter(
                Cashbook.user_id == user_id,
                Cashbook.party_cd == account_code
            ).count()
            return count
        except:
            return 0
    
    def _calculate_account_balance_as_of(self, user_id: int, account_code: str, as_of_date: date) -> float:
        """Calculate account balance as of a specific date"""
        try:
            # Get opening balance
            account = Party.query.filter_by(party_cd=account_code, user_id=user_id).first()
            if not account:
                return 0
            
            opening_balance = float(account.opening_bal)
            
            # Get transactions up to the date
            transactions = Cashbook.query.filter(
                Cashbook.user_id == user_id,
                Cashbook.party_cd == account_code,
                Cashbook.date <= as_of_date
            ).all()
            
            balance = opening_balance
            for transaction in transactions:
                balance += float(transaction.cr_amt) - float(transaction.dr_amt)
            
            return balance
            
        except Exception as e:
            return 0
    
    def _calculate_account_balance_for_period(self, user_id: int, account_code: str, 
                                            start_date: date, end_date: date) -> float:
        """Calculate account balance for a specific period"""
        try:
            # Get transactions for the period
            transactions = Cashbook.query.filter(
                Cashbook.user_id == user_id,
                Cashbook.party_cd == account_code,
                Cashbook.date >= start_date,
                Cashbook.date <= end_date
            ).all()
            
            balance = 0
            for transaction in transactions:
                balance += float(transaction.cr_amt) - float(transaction.dr_amt)
            
            return balance
            
        except Exception as e:
            return 0
    
    def get_account_types(self) -> Dict:
        """Get available account types"""
        try:
            account_types = [
                {'code': 'ASSET', 'name': 'Asset', 'description': 'Resources owned by the business'},
                {'code': 'LIABILITY', 'name': 'Liability', 'description': 'Obligations of the business'},
                {'code': 'EQUITY', 'name': 'Equity', 'description': 'Owner\'s investment in the business'},
                {'code': 'INCOME', 'name': 'Income', 'description': 'Revenue earned by the business'},
                {'code': 'EXPENSE', 'name': 'Expense', 'description': 'Costs incurred by the business'}
            ]
            
            return {
                'success': True,
                'account_types': account_types
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)} 