"""
Enhanced API Endpoints for Credit-Based Business Logic
Based on Legacy Software Analysis
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, date
from sqlalchemy import func, and_, or_
from models import db, Party, Sale, Purchase, Cashbook, Ledger, Item
from business_logic import CreditBusinessLogic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
enhanced_api = Blueprint('enhanced_api', __name__)

@enhanced_api.route('/parties/<party_cd>/balance', methods=['GET'])
@login_required
def get_party_balance(party_cd):
    """Get real-time party balance"""
    try:
        as_of_date = request.args.get('as_of_date')
        if as_of_date:
            as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
        
        balance_info = CreditBusinessLogic.calculate_party_balance(
            party_cd, current_user.id, as_of_date
        )
        
        return jsonify({
            'success': True,
            'data': balance_info
        })
    except Exception as e:
        logger.error(f"Error getting party balance: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/parties/<party_cd>/payment-history', methods=['GET'])
@login_required
def get_party_payment_history(party_cd):
    """Get party payment history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get cashbook entries for the party
        payments = Cashbook.query.filter(
            Cashbook.party_cd == party_cd,
            Cashbook.user_id == current_user.id,
            Cashbook.cr_amt > 0  # Only payments received
        ).order_by(Cashbook.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        payment_history = []
        for payment in payments.items:
            payment_history.append({
                'id': payment.id,
                'date': payment.date.isoformat(),
                'amount': payment.cr_amt,
                'narration': payment.narration,
                'payment_type': payment.payment_type,
                'reference_no': payment.reference_no,
                'bank_name': payment.bank_name,
                'related_sale_id': payment.related_sale_id
            })
        
        return jsonify({
            'success': True,
            'data': {
                'payments': payment_history,
                'total': payments.total,
                'pages': payments.pages,
                'current_page': page
            }
        })
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/parties/<party_cd>/credit-limit', methods=['PUT'])
@login_required
def update_credit_limit(party_cd):
    """Update party credit limit"""
    try:
        data = request.get_json()
        credit_limit = data.get('credit_limit', 0)
        
        party = Party.query.filter_by(
            party_cd=party_cd, user_id=current_user.id
        ).first()
        
        if not party:
            return jsonify({
                'success': False,
                'message': 'Party not found'
            }), 404
        
        party.credit_limit = credit_limit
        party.modified_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Credit limit updated successfully',
            'data': {
                'party_cd': party_cd,
                'credit_limit': credit_limit
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating credit limit: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/sales/<int:sale_id>/payments', methods=['GET'])
@login_required
def get_sale_payments(sale_id):
    """Get payments for a specific sale"""
    try:
        payments = Cashbook.query.filter(
            Cashbook.related_sale_id == sale_id,
            Cashbook.user_id == current_user.id
        ).order_by(Cashbook.date).all()
        
        payment_list = []
        for payment in payments:
            payment_list.append({
                'id': payment.id,
                'date': payment.date.isoformat(),
                'amount': payment.cr_amt,
                'payment_type': payment.payment_type,
                'reference_no': payment.reference_no,
                'bank_name': payment.bank_name,
                'narration': payment.narration
            })
        
        return jsonify({
            'success': True,
            'data': payment_list
        })
    except Exception as e:
        logger.error(f"Error getting sale payments: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/sales/<int:sale_id>/payments', methods=['POST'])
@login_required
def add_sale_payment(sale_id):
    """Add payment for a specific sale"""
    try:
        data = request.get_json()
        
        result = CreditBusinessLogic.process_payment(
            sale_id=sale_id,
            amount=data['amount'],
            payment_type=data.get('payment_type', 'CASH'),
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
            user_id=current_user.id,
            reference_no=data.get('reference_no'),
            payment_method=data.get('payment_method'),
            bank_name=data.get('bank_name'),
            branch_name=data.get('branch_name'),
            cheque_date=datetime.strptime(data['cheque_date'], '%Y-%m-%d').date() if data.get('cheque_date') else None
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error adding sale payment: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/sales/pending-payments', methods=['GET'])
@login_required
def get_pending_payments():
    """Get all pending payments"""
    try:
        party_cd = request.args.get('party_cd')
        pending_payments = CreditBusinessLogic.get_pending_payments(
            current_user.id, party_cd
        )
        
        return jsonify({
            'success': True,
            'data': pending_payments
        })
    except Exception as e:
        logger.error(f"Error getting pending payments: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/ledger/party/<party_cd>', methods=['GET'])
@login_required
def get_party_ledger(party_cd):
    """Get party ledger entries"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        statement = CreditBusinessLogic.get_party_statement(
            party_cd, current_user.id, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': statement
        })
    except Exception as e:
        logger.error(f"Error getting party ledger: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/ledger/trial-balance', methods=['GET'])
@login_required
def get_trial_balance():
    """Get trial balance for all parties"""
    try:
        as_of_date = request.args.get('as_of_date')
        if as_of_date:
            as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
        
        # Get all parties for the user
        parties = Party.query.filter_by(user_id=current_user.id).all()
        
        trial_balance = []
        total_debits = 0
        total_credits = 0
        
        for party in parties:
            balance_info = CreditBusinessLogic.calculate_party_balance(
                party.party_cd, current_user.id, as_of_date
            )
            
            trial_balance.append({
                'party_cd': party.party_cd,
                'party_name': party.party_nm,
                'balance': balance_info['current_balance'],
                'balance_type': balance_info['balance_type'],
                'total_sales': balance_info['total_sales'],
                'total_payments': balance_info['total_payments']
            })
            
            if balance_info['balance_type'] == 'D':
                total_debits += balance_info['current_balance']
            else:
                total_credits += balance_info['current_balance']
        
        return jsonify({
            'success': True,
            'data': {
                'trial_balance': trial_balance,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'as_of_date': as_of_date.isoformat() if as_of_date else date.today().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting trial balance: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/ledger/year/<financial_year>', methods=['GET'])
@login_required
def get_ledger_by_year(financial_year):
    """Get ledger entries for a specific financial year"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        ledger_entries = Ledger.query.filter(
            Ledger.user_id == current_user.id,
            Ledger.financial_year == financial_year
        ).order_by(Ledger.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        entries = []
        for entry in ledger_entries.items:
            entries.append({
                'id': entry.id,
                'date': entry.date.isoformat(),
                'party_cd': entry.party_cd,
                'narration': entry.narration,
                'debit': entry.dr_amt,
                'credit': entry.cr_amt,
                'balance': entry.balance,
                'voucher_type': entry.voucher_type,
                'voucher_no': entry.voucher_no,
                'balance_type': entry.balance_type
            })
        
        return jsonify({
            'success': True,
            'data': {
                'entries': entries,
                'total': ledger_entries.total,
                'pages': ledger_entries.pages,
                'current_page': page,
                'financial_year': financial_year
            }
        })
    except Exception as e:
        logger.error(f"Error getting ledger by year: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/reports/party-statement/<party_cd>', methods=['GET'])
@login_required
def get_party_statement_report(party_cd):
    """Get comprehensive party statement report"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        statement = CreditBusinessLogic.get_party_statement(
            party_cd, current_user.id, from_date, to_date
        )
        
        # Get party details
        party = Party.query.filter_by(
            party_cd=party_cd, user_id=current_user.id
        ).first()
        
        if party:
            statement['party_details'] = {
                'party_cd': party.party_cd,
                'party_name': party.party_nm,
                'place': party.place,
                'phone': party.phone,
                'credit_limit': party.credit_limit,
                'current_balance': party.current_balance,
                'credit_status': party.credit_status
            }
        
        return jsonify({
            'success': True,
            'data': statement
        })
    except Exception as e:
        logger.error(f"Error getting party statement report: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/reports/trial-balance/<financial_year>', methods=['GET'])
@login_required
def get_trial_balance_report(financial_year):
    """Get trial balance report for a financial year"""
    try:
        # Get trial balance
        trial_balance_data = get_trial_balance().get_json()
        
        if not trial_balance_data['success']:
            return jsonify(trial_balance_data), 500
        
        # Add financial year information
        trial_balance_data['data']['financial_year'] = financial_year
        
        return jsonify(trial_balance_data)
    except Exception as e:
        logger.error(f"Error getting trial balance report: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/reports/sales-summary/<financial_year>', methods=['GET'])
@login_required
def get_sales_summary_report(financial_year):
    """Get sales summary report for a financial year"""
    try:
        # Parse financial year to get date range
        year_start = int(financial_year.split('-')[0])
        start_date = date(year_start, 4, 1)  # April 1st
        end_date = date(year_start + 1, 3, 31)  # March 31st
        
        # Get sales for the financial year
        sales = Sale.query.filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_date,
            Sale.bill_date <= end_date
        ).all()
        
        # Calculate summary
        total_sales = sum(sale.sal_amt for sale in sales)
        total_quantity = sum(sale.qty for sale in sales)
        pending_amount = sum(sale.sal_amt - sale.amount_paid for sale in sales if sale.payment_status != 'PAID')
        
        # Group by party
        party_sales = {}
        for sale in sales:
            if sale.party_cd not in party_sales:
                party_sales[sale.party_cd] = {
                    'party_name': sale.party.party_nm if sale.party else '',
                    'total_sales': 0,
                    'total_quantity': 0,
                    'pending_amount': 0,
                    'bill_count': 0
                }
            
            party_sales[sale.party_cd]['total_sales'] += sale.sal_amt
            party_sales[sale.party_cd]['total_quantity'] += sale.qty
            party_sales[sale.party_cd]['bill_count'] += 1
            
            if sale.payment_status != 'PAID':
                party_sales[sale.party_cd]['pending_amount'] += (sale.sal_amt - sale.amount_paid)
        
        return jsonify({
            'success': True,
            'data': {
                'financial_year': financial_year,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'summary': {
                    'total_sales': total_sales,
                    'total_quantity': total_quantity,
                    'pending_amount': pending_amount,
                    'total_bills': len(sales)
                },
                'party_wise_sales': party_sales
            }
        })
    except Exception as e:
        logger.error(f"Error getting sales summary report: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/credit-check', methods=['POST'])
@login_required
def check_credit_limit():
    """Check credit limit before creating sale"""
    try:
        data = request.get_json()
        party_cd = data.get('party_cd')
        sale_amount = data.get('sale_amount', 0)
        
        if not party_cd:
            return jsonify({
                'success': False,
                'message': 'Party code is required'
            }), 400
        
        credit_check = CreditBusinessLogic.check_credit_limit(
            party_cd, current_user.id, sale_amount
        )
        
        return jsonify({
            'success': True,
            'data': credit_check
        })
    except Exception as e:
        logger.error(f"Error checking credit limit: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@enhanced_api.route('/inventory/balance/<item_cd>', methods=['GET'])
@login_required
def get_inventory_balance(item_cd):
    """Get inventory balance for an item"""
    try:
        as_of_date = request.args.get('as_of_date')
        if as_of_date:
            as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
        
        balance_info = CreditBusinessLogic.calculate_inventory_balance(
            item_cd, current_user.id, as_of_date
        )
        
        return jsonify({
            'success': True,
            'data': balance_info
        })
    except Exception as e:
        logger.error(f"Error getting inventory balance: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 