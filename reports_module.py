#!/usr/bin/env python3
"""
Advanced Reports Module
Provides comprehensive business reports for multi-user system
"""

from flask import Blueprint, render_template, request, jsonify, current_app, make_response
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from models import db, Party, Item, Purchase, Sale, Cashbook, Company
import csv
import io
from decimal import Decimal
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
        export_fmt = request.args.get('format')
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        sales_data = db.session.query(
            Sale.bill_no,
            Sale.bill_date,
            Party.party_nm,
            Sale.sal_amt,
            Sale.tot_amt.label('total_amount')
        ).join(Party, Sale.party_cd == Party.party_cd)\
         .filter(
             Sale.user_id == current_user.id,
             Sale.bill_date >= start_dt,
             Sale.bill_date < end_dt
         ).order_by(desc(Sale.bill_date)).all()

        total_sales = Decimal('0')
        export_rows = []
        for row in sales_data:
            amt = _row_amount(row)
            total_sales += amt
            export_rows.append({
                'Bill No': row.bill_no,
                'Date': row.bill_date.strftime('%Y-%m-%d') if row.bill_date else '',
                'Party': row.party_nm,
                'Amount': float(amt)
            })
        total_bills = len(sales_data)

        if export_fmt in ('csv', 'excel', 'xlsx', 'pdf'):
            df = pd.DataFrame(export_rows)
            return _export_dataframe(df, f'sales_summary_{start_date}_to_{end_date}', export_fmt)

        return render_template('reports/sales_summary.html',
                             user=current_user,
                             sales_data=sales_data,
                             total_sales=total_sales,
                             total_bills=total_bills,
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
        export_fmt = request.args.get('format')
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        purchase_data = db.session.query(
            Purchase.bill_no,
            Purchase.bill_date,
            Party.party_nm,
            Purchase.sal_amt,
            Purchase.tot_amt.label('total_amount')
        ).join(Party, Purchase.party_cd == Party.party_cd)\
         .filter(
             Purchase.user_id == current_user.id,
             Purchase.bill_date >= start_dt,
             Purchase.bill_date < end_dt
         ).order_by(desc(Purchase.bill_date)).all()

        total_purchases = Decimal('0')
        export_rows = []
        for row in purchase_data:
            amt = _row_amount(row)
            total_purchases += amt
            export_rows.append({
                'Bill No': row.bill_no,
                'Date': row.bill_date.strftime('%Y-%m-%d') if row.bill_date else '',
                'Party': row.party_nm,
                'Amount': float(amt)
            })
        total_bills = len(purchase_data)

        if export_fmt in ('csv', 'excel', 'xlsx', 'pdf'):
            df = pd.DataFrame(export_rows)
            return _export_dataframe(df, f'purchase_summary_{start_date}_to_{end_date}', export_fmt)

        return render_template('reports/purchase_summary.html',
                             user=current_user,
                             purchase_data=purchase_data,
                             total_purchases=total_purchases,
                             total_bills=total_bills,
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
        export_fmt = request.args.get('format')
        party = Party.query.filter_by(party_cd=party_cd, user_id=current_user.id).first()
        if not party:
            return jsonify({'error': 'Party not found'}), 404

        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        sales = Sale.query.filter(
            Sale.party_cd == party_cd,
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_dt,
            Sale.bill_date < end_dt
        ).order_by(Sale.bill_date).all()

        purchases = Purchase.query.filter(
            Purchase.party_cd == party_cd,
            Purchase.user_id == current_user.id,
            Purchase.bill_date >= start_dt,
            Purchase.bill_date < end_dt
        ).order_by(Purchase.bill_date).all()

        transactions = []
        for sale in sales:
            transactions.append({
                'date': sale.bill_date,
                'type': 'Sale',
                'bill_no': sale.bill_no,
                'debit': Decimal('0'),
                'credit': _row_amount(sale),
                'balance': 0
            })
        for purchase in purchases:
            transactions.append({
                'date': purchase.bill_date,
                'type': 'Purchase',
                'bill_no': purchase.bill_no,
                'debit': _row_amount(purchase),
                'credit': Decimal('0'),
                'balance': 0
            })

        transactions.sort(key=lambda x: x['date'])

        balance = Decimal(str(party.opening_bal or 0))
        export_rows = []
        for trans in transactions:
            balance += trans['credit'] - trans['debit']
            trans['balance'] = balance
            export_rows.append({
                'Date': trans['date'].strftime('%Y-%m-%d') if trans['date'] else '',
                'Type': trans['type'],
                'Bill No': trans['bill_no'],
                'Debit': float(trans['debit']),
                'Credit': float(trans['credit']),
                'Balance': float(balance)
            })

        if export_fmt in ('csv', 'excel', 'xlsx', 'pdf'):
            df = pd.DataFrame(export_rows)
            return _export_dataframe(df, f'party_ledger_{party_cd}_{start_date}_to_{end_date}', export_fmt)

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
        export_fmt = request.args.get('format')
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        item_sales = db.session.query(
            Item.it_cd,
            Item.it_nm,
            func.sum(Sale.qty).label('total_qty_sold'),
            func.sum(Sale.qty * Sale.rate).label('total_amount_sold'),
            func.avg(Sale.rate).label('avg_rate')
        ).join(Sale, Item.it_cd == Sale.it_cd)         .filter(
             Item.user_id == current_user.id,
             Sale.user_id == current_user.id,
             Sale.bill_date >= start_dt,
             Sale.bill_date < end_dt
         ).group_by(Item.it_cd, Item.it_nm)         .order_by(desc(func.sum(Sale.qty * Sale.rate))).all()

        item_purchases = db.session.query(
            Item.it_cd,
            Item.it_nm,
            func.sum(Purchase.qty).label('total_qty_purchased'),
            func.sum(Purchase.qty * Purchase.rate).label('total_amount_purchased'),
            func.avg(Purchase.rate).label('avg_purchase_rate')
        ).join(Purchase, Item.it_cd == Purchase.it_cd)         .filter(
             Item.user_id == current_user.id,
             Purchase.user_id == current_user.id,
             Purchase.bill_date >= start_dt,
             Purchase.bill_date < end_dt
         ).group_by(Item.it_cd, Item.it_nm)         .order_by(desc(func.sum(Purchase.qty * Purchase.rate))).all()

        if export_fmt in ('csv', 'excel', 'xlsx', 'pdf'):
            rows = []
            for r in item_sales:
                rows.append({
                    'Type': 'Sales',
                    'Item Code': r.it_cd,
                    'Item': r.it_nm,
                    'Quantity': float(r.total_qty_sold or 0),
                    'Amount': float(r.total_amount_sold or 0),
                    'Avg Rate': float(r.avg_rate or 0)
                })
            for r in item_purchases:
                rows.append({
                    'Type': 'Purchases',
                    'Item Code': r.it_cd,
                    'Item': r.it_nm,
                    'Quantity': float(r.total_qty_purchased or 0),
                    'Amount': float(r.total_amount_purchased or 0),
                    'Avg Rate': float(r.avg_purchase_rate or 0)
                })
            df = pd.DataFrame(rows)
            return _export_dataframe(df, f'item_analysis_{start_date}_to_{end_date}', export_fmt)

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
        export_fmt = request.args.get('format')
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        cash_receipts = db.session.query(
            func.date(Sale.bill_date).label('date'),
            func.sum(Sale.tot_amt).label('amount')
        ).filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_dt,
            Sale.bill_date < end_dt
        ).group_by(func.date(Sale.bill_date)).all()

        cash_payments = db.session.query(
            func.date(Purchase.bill_date).label('date'),
            func.sum(Purchase.tot_amt).label('amount')
        ).filter(
            Purchase.user_id == current_user.id,
            Purchase.bill_date >= start_dt,
            Purchase.bill_date < end_dt
        ).group_by(func.date(Purchase.bill_date)).all()

        cashbook_entries = db.session.query(
            func.date(Cashbook.date).label('date'),
            func.sum(Cashbook.amount).label('amount'),
            Cashbook.type
        ).filter(
            Cashbook.user_id == current_user.id,
            Cashbook.date >= start_dt,
            Cashbook.date < end_dt
        ).group_by(func.date(Cashbook.date), Cashbook.type).all()

        if export_fmt in ('csv', 'excel', 'xlsx', 'pdf'):
            rows = []
            for d, amt in cash_receipts:
                rows.append({'Date': str(d), 'Type': 'Receipt (Sales)', 'Amount': float(amt or 0)})
            for d, amt in cash_payments:
                rows.append({'Date': str(d), 'Type': 'Payment (Purchases)', 'Amount': float(amt or 0)})
            for d, amt, typ in cashbook_entries:
                rows.append({'Date': str(d), 'Type': f'Cashbook {typ}', 'Amount': float(amt or 0)})
            df = pd.DataFrame(rows)
            return _export_dataframe(df, f'cash_flow_{start_date}_to_{end_date}', export_fmt)

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
 
 
 

# -------- Helper utilities for exports --------

def _row_amount(obj):
    for attr in ('tot_amt', 'total_amount', 'sal_amt', 'amount'):
        if hasattr(obj, attr):
            val = getattr(obj, attr)
            if val is not None:
                try:
                    return Decimal(str(val))
                except Exception:
                    return Decimal('0')
    return Decimal('0')


def _export_dataframe(df, filename_prefix: str, fmt: str):
    if df is None or df.empty:
        df = pd.DataFrame([{'message': 'No data available'}])
    if fmt == 'csv':
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        resp = make_response(buf.getvalue())
        resp.headers['Content-Type'] = 'text/csv'
        resp.headers['Content-Disposition'] = f"attachment; filename={filename_prefix}.csv"
        return resp
    if fmt in ('excel', 'xlsx'):
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        resp = make_response(buf.getvalue())
        resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        resp.headers['Content-Disposition'] = f"attachment; filename={filename_prefix}.xlsx"
        return resp
    if fmt == 'pdf':
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(8.5, max(2.5, 0.35*len(df)+1)))
        ax.axis('off')
        tbl = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1, 1.2)
        plt.tight_layout()
        fig.savefig(buf, format='pdf')
        plt.close(fig)
        resp = make_response(buf.getvalue())
        resp.headers['Content-Type'] = 'application/pdf'
        resp.headers['Content-Disposition'] = f"attachment; filename={filename_prefix}.pdf"
        return resp
    return None

