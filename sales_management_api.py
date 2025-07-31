#!/usr/bin/env python3
"""
Advanced Sales Management API Endpoints
Flask Blueprint for comprehensive sales management functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sales_management import SalesManagementSystem
from datetime import datetime, date
import json

# Create Blueprint
sales_management_api = Blueprint('sales_management_api', __name__)

# Initialize Sales Management System
sms = SalesManagementSystem()

@sales_management_api.route('/api/sales/entry', methods=['POST'])
@login_required
def create_sales_entry():
    """Create a new sales entry with credit limit validation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Add user_id to data
        data['user_id'] = current_user.id
        
        # Validate required fields
        required_fields = ['bill_no', 'bill_date', 'party_cd', 'it_cd']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create sales entry
        result = sms.create_sales_entry(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/<int:bill_no>', methods=['GET'])
@login_required
def get_sales(bill_no):
    """Get sales details by bill number"""
    try:
        result = sms.get_sales_by_bill_no(current_user.id, bill_no)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/summary', methods=['GET'])
@login_required
def get_sales_summary():
    """Get sales summary with optional date filters"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        result = sms.get_sales_summary(current_user.id, start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/order', methods=['POST'])
@login_required
def create_sales_order():
    """Create a new sales order"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['order_no', 'order_date', 'party_cd']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create sales order
        result = sms.create_sales_order(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/return', methods=['POST'])
@login_required
def create_sales_return():
    """Create a sales return entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['return_no', 'return_date', 'original_bill_no', 'party_cd', 'it_cd']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create sales return
        result = sms.create_sales_return(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/payment', methods=['POST'])
@login_required
def create_sales_payment():
    """Create a sales payment entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['payment_no', 'payment_date', 'party_cd', 'payment_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create sales payment
        result = sms.create_sales_payment(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/delivery', methods=['POST'])
@login_required
def create_sales_delivery():
    """Create a sales delivery entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['delivery_no', 'bill_no', 'delivery_date', 'party_cd']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create sales delivery
        result = sms.create_sales_delivery(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/credit-check', methods=['POST'])
@login_required
def check_credit_limit():
    """Check credit limit for a party"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['party_cd', 'amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Check credit limit
        result = sms.check_credit_limit(current_user.id, data['party_cd'], data['amount'])
        
        return jsonify(result), 200 if result['success'] else 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/reports/<report_type>', methods=['GET'])
@login_required
def get_sales_reports(report_type):
    """Get various sales reports"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_cd = request.args.get('party_cd')
        it_cd = request.args.get('it_cd')
        agent_cd = request.args.get('agent_cd')
        
        # Prepare kwargs for report
        kwargs = {}
        if start_date:
            kwargs['start_date'] = start_date
        if end_date:
            kwargs['end_date'] = end_date
        if party_cd:
            kwargs['party_cd'] = party_cd
        if it_cd:
            kwargs['it_cd'] = it_cd
        if agent_cd:
            kwargs['agent_cd'] = agent_cd
        
        # Get report
        result = sms.get_sales_reports(current_user.id, report_type, **kwargs)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/list', methods=['GET'])
@login_required
def get_sales_list():
    """Get list of sales with filters"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_cd = request.args.get('party_cd')
        it_cd = request.args.get('it_cd')
        payment_status = request.args.get('payment_status')
        delivery_status = request.args.get('delivery_status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = '''
            SELECT 
                bill_no, bill_date, party_cd, it_cd, qty, katta, tot_smt, 
                rate, sal_amt, tot_amt, payment_status, delivery_status, 
                commission_amount, created_date
            FROM sales 
            WHERE user_id = ?
        '''
        params = [current_user.id]
        
        if start_date:
            query += ' AND bill_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND bill_date <= ?'
            params.append(end_date)
        
        if party_cd:
            query += ' AND party_cd = ?'
            params.append(party_cd)
        
        if it_cd:
            query += ' AND it_cd = ?'
            params.append(it_cd)
        
        if payment_status:
            query += ' AND payment_status = ?'
            params.append(payment_status)
        
        if delivery_status:
            query += ' AND delivery_status = ?'
            params.append(delivery_status)
        
        query += ' ORDER BY bill_date DESC, bill_no DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # Execute query
        import sqlite3
        conn = sqlite3.connect(sms.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Get total count
        count_query = '''
            SELECT COUNT(*) FROM sales WHERE user_id = ?
        '''
        count_params = [current_user.id]
        
        if start_date:
            count_query += ' AND bill_date >= ?'
            count_params.append(start_date)
        
        if end_date:
            count_query += ' AND bill_date <= ?'
            count_params.append(end_date)
        
        if party_cd:
            count_query += ' AND party_cd = ?'
            count_params.append(party_cd)
        
        if it_cd:
            count_query += ' AND it_cd = ?'
            count_params.append(it_cd)
        
        if payment_status:
            count_query += ' AND payment_status = ?'
            count_params.append(payment_status)
        
        if delivery_status:
            count_query += ' AND delivery_status = ?'
            count_params.append(delivery_status)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Format results
        columns = ['bill_no', 'bill_date', 'party_cd', 'it_cd', 'qty', 'katta', 
                  'tot_smt', 'rate', 'sal_amt', 'tot_amt', 'payment_status', 
                  'delivery_status', 'commission_amount', 'created_date']
        
        sales = []
        for row in rows:
            sale = dict(zip(columns, [
                row[0], row[1], row[2], row[3], row[4], row[5],
                float(row[6] or 0), float(row[7] or 0), float(row[8] or 0),
                float(row[9] or 0), row[10], row[11], float(row[12] or 0), row[13]
            ]))
            sales.append(sale)
        
        return jsonify({
            'success': True,
            'sales': sales,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/pending-payments', methods=['GET'])
@login_required
def get_pending_payments():
    """Get list of sales with pending payments"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_cd = request.args.get('party_cd')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = '''
            SELECT 
                bill_no, bill_date, party_cd, tot_amt, amount_paid,
                (tot_amt - amount_paid) as pending_amount,
                payment_due_date, payment_status
            FROM sales 
            WHERE user_id = ? AND payment_status != 'PAID'
        '''
        params = [current_user.id]
        
        if start_date:
            query += ' AND bill_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND bill_date <= ?'
            params.append(end_date)
        
        if party_cd:
            query += ' AND party_cd = ?'
            params.append(party_cd)
        
        query += ' ORDER BY payment_due_date ASC, bill_date DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # Execute query
        import sqlite3
        conn = sqlite3.connect(sms.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Format results
        columns = ['bill_no', 'bill_date', 'party_cd', 'tot_amt', 'amount_paid',
                  'pending_amount', 'payment_due_date', 'payment_status']
        
        pending_payments = []
        for row in rows:
            payment = dict(zip(columns, [
                row[0], row[1], row[2], float(row[3] or 0), float(row[4] or 0),
                float(row[5] or 0), row[6], row[7]
            ]))
            pending_payments.append(payment)
        
        return jsonify({
            'success': True,
            'pending_payments': pending_payments,
            'total_pending_amount': sum(p['pending_amount'] for p in pending_payments),
            'count': len(pending_payments)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/pending-deliveries', methods=['GET'])
@login_required
def get_pending_deliveries():
    """Get list of sales with pending deliveries"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_cd = request.args.get('party_cd')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = '''
            SELECT 
                bill_no, bill_date, party_cd, tot_amt, delivery_status,
                delivery_date
            FROM sales 
            WHERE user_id = ? AND delivery_status != 'DELIVERED'
        '''
        params = [current_user.id]
        
        if start_date:
            query += ' AND bill_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND bill_date <= ?'
            params.append(end_date)
        
        if party_cd:
            query += ' AND party_cd = ?'
            params.append(party_cd)
        
        query += ' ORDER BY bill_date DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # Execute query
        import sqlite3
        conn = sqlite3.connect(sms.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Format results
        columns = ['bill_no', 'bill_date', 'party_cd', 'tot_amt', 'delivery_status', 'delivery_date']
        
        pending_deliveries = []
        for row in rows:
            delivery = dict(zip(columns, [
                row[0], row[1], row[2], float(row[3] or 0), row[4], row[5]
            ]))
            pending_deliveries.append(delivery)
        
        return jsonify({
            'success': True,
            'pending_deliveries': pending_deliveries,
            'count': len(pending_deliveries)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_management_api.route('/api/sales/statistics', methods=['GET'])
@login_required
def get_sales_statistics():
    """Get sales statistics for dashboard"""
    try:
        # Get current month statistics
        current_month = datetime.now().strftime('%Y-%m')
        start_date = f"{current_month}-01"
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get current month summary
        current_month_summary = sms.get_sales_summary(current_user.id, start_date, end_date)
        
        # Get previous month summary
        from datetime import datetime, timedelta
        prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        prev_start_date = f"{prev_month}-01"
        prev_end_date = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        prev_month_summary = sms.get_sales_summary(current_user.id, prev_start_date, prev_end_date)
        
        # Get pending payments count
        import sqlite3
        conn = sqlite3.connect(sms.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(DISTINCT bill_no) as pending_bills,
                   SUM(tot_amt - amount_paid) as total_pending_amount
            FROM sales 
            WHERE user_id = ? AND payment_status != 'PAID'
        ''', (current_user.id,))
        
        pending_result = cursor.fetchone()
        pending_bills = pending_result[0] or 0
        total_pending_amount = float(pending_result[1] or 0)
        
        # Get pending deliveries count
        cursor.execute('''
            SELECT COUNT(DISTINCT bill_no) as pending_deliveries
            FROM sales 
            WHERE user_id = ? AND delivery_status != 'DELIVERED'
        ''', (current_user.id,))
        
        delivery_result = cursor.fetchone()
        pending_deliveries = delivery_result[0] or 0
        
        # Get top customers
        cursor.execute('''
            SELECT party_cd, COUNT(DISTINCT bill_no) as bill_count, SUM(tot_amt) as total_amount
            FROM sales 
            WHERE user_id = ? AND bill_date >= ?
            GROUP BY party_cd 
            ORDER BY total_amount DESC 
            LIMIT 5
        ''', (current_user.id, start_date))
        
        top_customers = []
        for row in cursor.fetchall():
            top_customers.append({
                'party_cd': row[0],
                'bill_count': row[1],
                'total_amount': float(row[2] or 0)
            })
        
        # Get commission statistics
        cursor.execute('''
            SELECT SUM(commission_amount) as total_commission,
                   SUM(paid_amount) as paid_commission
            FROM sales_commission 
            WHERE user_id = ? AND created_date >= ?
        ''', (current_user.id, start_date))
        
        commission_result = cursor.fetchone()
        total_commission = float(commission_result[0] or 0)
        paid_commission = float(commission_result[1] or 0)
        pending_commission = total_commission - paid_commission
        
        conn.close()
        
        # Calculate growth
        current_amount = current_month_summary['summary']['total_amount']
        prev_amount = prev_month_summary['summary']['total_amount']
        
        if prev_amount > 0:
            growth_percentage = ((current_amount - prev_amount) / prev_amount) * 100
        else:
            growth_percentage = 0
        
        statistics = {
            'current_month': {
                'total_bills': current_month_summary['summary']['total_bills'],
                'total_amount': current_amount,
                'total_items': current_month_summary['summary']['total_items'],
                'total_commission': total_commission
            },
            'previous_month': {
                'total_bills': prev_month_summary['summary']['total_bills'],
                'total_amount': prev_amount,
                'total_items': prev_month_summary['summary']['total_items']
            },
            'growth_percentage': round(growth_percentage, 2),
            'pending_payments': {
                'bill_count': pending_bills,
                'total_amount': total_pending_amount
            },
            'pending_deliveries': {
                'count': pending_deliveries
            },
            'commission': {
                'total_commission': total_commission,
                'paid_commission': paid_commission,
                'pending_commission': pending_commission
            },
            'top_customers': top_customers
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@sales_management_api.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Sales Management API endpoint not found'}), 404

@sales_management_api.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500 