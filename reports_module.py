#!/usr/bin/env python3
"""
Advanced Reports Module
Provides comprehensive business reports for multi-user system
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from models import db, Party, Item, Purchase, Sale, Cashbook, Company

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def reports_dashboard():
    """Main reports dashboard"""
    return render_template('reports/dashboard.html', user=current_user)

@reports_bp.route('/reports/sales-summary')
@login_required
def sales_summary():
    """Sales summary report"""
    try:
        # Get date range from request
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                  datetime.now().strftime('%Y-%m-%d'))
        
        # Convert to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get sales data for current user
        sales_data = db.session.query(
            Sale.bill_no,
            Sale.bill_date,
            Party.party_nm,
            Sale.total_amount,
            Sale.payment_mode
        ).join(Party, Sale.party_cd == Party.party_cd)\
         .filter(
             Sale.user_id == current_user.id,
             Sale.bill_date >= start_dt,
             Sale.bill_date < end_dt
         ).order_by(desc(Sale.bill_date)).all()
        
        # Calculate totals
        total_sales = sum(sale.total_amount for sale in sales_data)
        total_bills = len(sales_data)
        
        # Group by payment mode
        payment_modes = {}
        for sale in sales_data:
            mode = sale.payment_mode or 'Cash'
            if mode not in payment_modes:
                payment_modes[mode] = 0
            payment_modes[mode] += sale.total_amount
        
        return render_template('reports/sales_summary.html',
                             user=current_user,
                             sales_data=sales_data,
                             total_sales=total_sales,
                             total_bills=total_bills,
                             payment_modes=payment_modes,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        current_app.logger.error(f"Sales summary error: {e}")
        return jsonify({'error': 'Error generating sales summary'}), 500

@reports_bp.route('/reports/purchase-summary')
@login_required
def purchase_summary():
    """Purchase summary report"""
    try:
        # Get date range from request
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                  datetime.now().strftime('%Y-%m-%d'))
        
        # Convert to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get purchase data for current user
        purchase_data = db.session.query(
            Purchase.bill_no,
            Purchase.bill_date,
            Party.party_nm,
            Purchase.total_amount,
            Purchase.payment_mode
        ).join(Party, Purchase.party_cd == Party.party_cd)\
         .filter(
             Purchase.user_id == current_user.id,
             Purchase.bill_date >= start_dt,
             Purchase.bill_date < end_dt
         ).order_by(desc(Purchase.bill_date)).all()
        
        # Calculate totals
        total_purchases = sum(purchase.total_amount for purchase in purchase_data)
        total_bills = len(purchase_data)
        
        # Group by payment mode
        payment_modes = {}
        for purchase in purchase_data:
            mode = purchase.payment_mode or 'Cash'
            if mode not in payment_modes:
                payment_modes[mode] = 0
            payment_modes[mode] += purchase.total_amount
        
        return render_template('reports/purchase_summary.html',
                             user=current_user,
                             purchase_data=purchase_data,
                             total_purchases=total_purchases,
                             total_bills=total_bills,
                             payment_modes=payment_modes,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        current_app.logger.error(f"Purchase summary error: {e}")
        return jsonify({'error': 'Error generating purchase summary'}), 500

@reports_bp.route('/reports/party-ledger/<party_cd>')
@login_required
def party_ledger(party_cd):
    """Party ledger report"""
    try:
        # Get party details
        party = Party.query.filter_by(
            party_cd=party_cd, 
            user_id=current_user.id
        ).first()
        
        if not party:
            return jsonify({'error': 'Party not found'}), 404
        
        # Get date range from request
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                  datetime.now().strftime('%Y-%m-%d'))
        
        # Convert to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get sales transactions
        sales = Sale.query.filter(
            Sale.party_cd == party_cd,
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_dt,
            Sale.bill_date < end_dt
        ).order_by(Sale.bill_date).all()
        
        # Get purchase transactions
        purchases = Purchase.query.filter(
            Purchase.party_cd == party_cd,
            Purchase.user_id == current_user.id,
            Purchase.bill_date >= start_dt,
            Purchase.bill_date < end_dt
        ).order_by(Purchase.bill_date).all()
        
        # Combine and sort transactions
        transactions = []
        for sale in sales:
            transactions.append({
                'date': sale.bill_date,
                'type': 'Sale',
                'bill_no': sale.bill_no,
                'debit': 0,
                'credit': sale.total_amount,
                'balance': 0  # Will be calculated
            })
        
        for purchase in purchases:
            transactions.append({
                'date': purchase.bill_date,
                'type': 'Purchase',
                'bill_no': purchase.bill_no,
                'debit': purchase.total_amount,
                'credit': 0,
                'balance': 0  # Will be calculated
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate running balance
        balance = party.opening_bal or 0
        for trans in transactions:
            balance += trans['credit'] - trans['debit']
            trans['balance'] = balance
        
        return render_template('reports/party_ledger.html',
                             user=current_user,
                             party=party,
                             transactions=transactions,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        current_app.logger.error(f"Party ledger error: {e}")
        return jsonify({'error': 'Error generating party ledger'}), 500

@reports_bp.route('/reports/item-analysis')
@login_required
def item_analysis():
    """Item analysis report"""
    try:
        # Get date range from request
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                  datetime.now().strftime('%Y-%m-%d'))
        
        # Convert to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get item-wise sales data
        item_sales = db.session.query(
            Item.item_cd,
            Item.item_nm,
            func.sum(Sale.qty).label('total_qty_sold'),
            func.sum(Sale.qty * Sale.rate).label('total_amount_sold'),
            func.avg(Sale.rate).label('avg_rate')
        ).join(Sale, Item.item_cd == Sale.item_cd)\
         .filter(
             Item.user_id == current_user.id,
             Sale.user_id == current_user.id,
             Sale.bill_date >= start_dt,
             Sale.bill_date < end_dt
         ).group_by(Item.item_cd, Item.item_nm)\
         .order_by(desc(func.sum(Sale.qty * Sale.rate))).all()
        
        # Get item-wise purchase data
        item_purchases = db.session.query(
            Item.item_cd,
            Item.item_nm,
            func.sum(Purchase.qty).label('total_qty_purchased'),
            func.sum(Purchase.qty * Purchase.rate).label('total_amount_purchased'),
            func.avg(Purchase.rate).label('avg_purchase_rate')
        ).join(Purchase, Item.item_cd == Purchase.item_cd)\
         .filter(
             Item.user_id == current_user.id,
             Purchase.user_id == current_user.id,
             Purchase.bill_date >= start_dt,
             Purchase.bill_date < end_dt
         ).group_by(Item.item_cd, Item.item_nm)\
         .order_by(desc(func.sum(Purchase.qty * Purchase.rate))).all()
        
        return render_template('reports/item_analysis.html',
                             user=current_user,
                             item_sales=item_sales,
                             item_purchases=item_purchases,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        current_app.logger.error(f"Item analysis error: {e}")
        return jsonify({'error': 'Error generating item analysis'}), 500

@reports_bp.route('/reports/cash-flow')
@login_required
def cash_flow():
    """Cash flow report"""
    try:
        # Get date range from request
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                  datetime.now().strftime('%Y-%m-%d'))
        
        # Convert to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get cash receipts (sales)
        cash_receipts = db.session.query(
            func.date(Sale.bill_date).label('date'),
            func.sum(Sale.total_amount).label('amount')
        ).filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_dt,
            Sale.bill_date < end_dt,
            Sale.payment_mode == 'Cash'
        ).group_by(func.date(Sale.bill_date)).all()
        
        # Get cash payments (purchases)
        cash_payments = db.session.query(
            func.date(Purchase.bill_date).label('date'),
            func.sum(Purchase.total_amount).label('amount')
        ).filter(
            Purchase.user_id == current_user.id,
            Purchase.bill_date >= start_dt,
            Purchase.bill_date < end_dt,
            Purchase.payment_mode == 'Cash'
        ).group_by(func.date(Purchase.bill_date)).all()
        
        # Get cashbook entries
        cashbook_entries = db.session.query(
            func.date(Cashbook.date).label('date'),
            func.sum(Cashbook.amount).label('amount'),
            Cashbook.type
        ).filter(
            Cashbook.user_id == current_user.id,
            Cashbook.date >= start_dt,
            Cashbook.date < end_dt
        ).group_by(func.date(Cashbook.date), Cashbook.type).all()
        
        return render_template('reports/cash_flow.html',
                             user=current_user,
                             cash_receipts=cash_receipts,
                             cash_payments=cash_payments,
                             cashbook_entries=cashbook_entries,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        current_app.logger.error(f"Cash flow error: {e}")
        return jsonify({'error': 'Error generating cash flow report'}), 500

@reports_bp.route('/api/reports/sales-chart')
@login_required
def sales_chart_data():
    """API endpoint for sales chart data"""
    try:
        # Get last 30 days of sales data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        sales_data = db.session.query(
            func.date(Sale.bill_date).label('date'),
            func.sum(Sale.total_amount).label('amount')
        ).filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_date,
            Sale.bill_date <= end_date
        ).group_by(func.date(Sale.bill_date)).all()
        
        # Format data for chart
        chart_data = {
            'labels': [str(row.date) for row in sales_data],
            'datasets': [{
                'label': 'Sales Amount',
                'data': [float(row.amount) for row in sales_data],
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        current_app.logger.error(f"Sales chart error: {e}")
        return jsonify({'error': 'Error generating chart data'}), 500 
 
 
 