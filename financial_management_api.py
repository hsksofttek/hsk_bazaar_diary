#!/usr/bin/env python3
"""
Advanced Financial Management API Endpoints
Flask Blueprint for comprehensive financial management functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from financial_management import FinancialManagementSystem
from datetime import datetime, date
import json

# Create Blueprint
financial_management_api = Blueprint('financial_management_api', __name__)

# Initialize Financial Management System
fms = FinancialManagementSystem()

@financial_management_api.route('/api/financial/accounts', methods=['POST'])
@login_required
def create_account():
    """Create a new chart of accounts entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['account_code', 'account_name', 'account_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create account
        result = fms.create_chart_of_accounts(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get list of chart of accounts"""
    try:
        import sqlite3
        
        # Get query parameters
        account_type = request.args.get('account_type')
        is_active = request.args.get('is_active', '1')
        
        # Build query
        query = '''
            SELECT 
                account_code, account_name, account_type, parent_account,
                account_level, opening_balance, current_balance, description
            FROM chart_of_accounts 
            WHERE user_id = ?
        '''
        params = [current_user.id]
        
        if account_type:
            query += ' AND account_type = ?'
            params.append(account_type)
        
        if is_active:
            query += ' AND is_active = ?'
            params.append(int(is_active))
        
        query += ' ORDER BY account_code'
        
        # Execute query
        conn = sqlite3.connect(fms.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Format results
        columns = ['account_code', 'account_name', 'account_type', 'parent_account',
                  'account_level', 'opening_balance', 'current_balance', 'description']
        
        accounts = []
        for row in rows:
            account = dict(zip(columns, [
                row[0], row[1], row[2], row[3], row[4],
                float(row[5] or 0), float(row[6] or 0), row[7]
            ]))
            accounts.append(account)
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'count': len(accounts)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/journal-entry', methods=['POST'])
@login_required
def create_journal_entry():
    """Create a journal entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('entry_date') or not data.get('details'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create journal entry
        result = fms.create_journal_entry(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/ledger', methods=['GET'])
@login_required
def get_ledger():
    """Get general ledger entries"""
    try:
        import sqlite3
        
        # Get query parameters
        account_code = request.args.get('account_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = '''
            SELECT 
                entry_date, voucher_no, voucher_type, account_code,
                debit_amount, credit_amount, balance, narration, party_cd
            FROM general_ledger 
            WHERE user_id = ?
        '''
        params = [current_user.id]
        
        if account_code:
            query += ' AND account_code = ?'
            params.append(account_code)
        
        if start_date:
            query += ' AND entry_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND entry_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY entry_date DESC, id DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # Execute query
        conn = sqlite3.connect(fms.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Format results
        columns = ['entry_date', 'voucher_no', 'voucher_type', 'account_code',
                  'debit_amount', 'credit_amount', 'balance', 'narration', 'party_cd']
        
        ledger_entries = []
        for row in rows:
            entry = dict(zip(columns, [
                row[0], row[1], row[2], row[3],
                float(row[4] or 0), float(row[5] or 0), float(row[6] or 0),
                row[7], row[8]
            ]))
            ledger_entries.append(entry)
        
        return jsonify({
            'success': True,
            'ledger_entries': ledger_entries,
            'count': len(ledger_entries)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/trial-balance', methods=['GET'])
@login_required
def get_trial_balance():
    """Get trial balance"""
    try:
        as_of_date = request.args.get('as_of_date')
        
        result = fms.get_trial_balance(current_user.id, as_of_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/balance-sheet', methods=['GET'])
@login_required
def get_balance_sheet():
    """Get balance sheet"""
    try:
        as_of_date = request.args.get('as_of_date')
        
        result = fms.get_balance_sheet(current_user.id, as_of_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/profit-loss', methods=['GET'])
@login_required
def get_profit_loss():
    """Get profit and loss statement"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Start date and end date are required'}), 400
        
        result = fms.get_profit_loss(current_user.id, start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/statistics', methods=['GET'])
@login_required
def get_financial_statistics():
    """Get financial statistics for dashboard"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(fms.db_path)
        cursor = conn.cursor()
        
        # Get total assets
        cursor.execute('''
            SELECT SUM(current_balance) FROM chart_of_accounts 
            WHERE user_id = ? AND account_type = 'ASSET' AND is_active = 1
        ''', (current_user.id,))
        total_assets = float(cursor.fetchone()[0] or 0)
        
        # Get total liabilities
        cursor.execute('''
            SELECT SUM(current_balance) FROM chart_of_accounts 
            WHERE user_id = ? AND account_type = 'LIABILITY' AND is_active = 1
        ''', (current_user.id,))
        total_liabilities = float(cursor.fetchone()[0] or 0)
        
        # Get total equity
        cursor.execute('''
            SELECT SUM(current_balance) FROM chart_of_accounts 
            WHERE user_id = ? AND account_type = 'EQUITY' AND is_active = 1
        ''', (current_user.id,))
        total_equity = float(cursor.fetchone()[0] or 0)
        
        # Get total revenue (current period)
        cursor.execute('''
            SELECT SUM(current_balance) FROM chart_of_accounts 
            WHERE user_id = ? AND account_type = 'REVENUE' AND is_active = 1
        ''', (current_user.id,))
        total_revenue = float(cursor.fetchone()[0] or 0)
        
        # Get total expenses (current period)
        cursor.execute('''
            SELECT SUM(current_balance) FROM chart_of_accounts 
            WHERE user_id = ? AND account_type = 'EXPENSE' AND is_active = 1
        ''', (current_user.id,))
        total_expenses = float(cursor.fetchone()[0] or 0)
        
        # Get recent journal entries
        cursor.execute('''
            SELECT entry_no, entry_date, narration, total_debit
            FROM journal_entries 
            WHERE user_id = ?
            ORDER BY entry_date DESC, entry_no DESC
            LIMIT 5
        ''', (current_user.id,))
        
        recent_entries = []
        for row in cursor.fetchall():
            recent_entries.append({
                'entry_no': row[0],
                'entry_date': row[1],
                'narration': row[2],
                'amount': float(row[3] or 0)
            })
        
        conn.close()
        
        # Calculate net profit
        net_profit = total_revenue - total_expenses
        
        statistics = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'recent_entries': recent_entries
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/account-types', methods=['GET'])
@login_required
def get_account_types():
    """Get available account types"""
    try:
        account_types = [
            {'code': 'ASSET', 'name': 'Asset', 'description': 'Resources owned by the business'},
            {'code': 'LIABILITY', 'name': 'Liability', 'description': 'Obligations to others'},
            {'code': 'EQUITY', 'name': 'Equity', 'description': 'Owner\'s investment and retained earnings'},
            {'code': 'REVENUE', 'name': 'Revenue', 'description': 'Income from business activities'},
            {'code': 'EXPENSE', 'name': 'Expense', 'description': 'Costs incurred in business operations'}
        ]
        
        return jsonify({
            'success': True,
            'account_types': account_types
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@financial_management_api.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Financial Management API endpoint not found'}), 404

@financial_management_api.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500 