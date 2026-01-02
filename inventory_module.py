#!/usr/bin/env python3
"""
Advanced Inventory Management Module
Provides comprehensive inventory tracking and management
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc, case
from datetime import datetime, timedelta
from models import db, Item, Purchase, Sale, Party
import json

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@login_required
def inventory_dashboard():
    """Inventory dashboard"""
    try:
        # Get inventory summary
        total_items = Item.query.filter_by(user_id=current_user.id).count()
        
        # Get low stock items (less than 10 units)
        low_stock_items = get_low_stock_items()
        
        # Get recent stock movements
        recent_movements = get_recent_stock_movements()
        
        # Get inventory value
        inventory_value = calculate_inventory_value()
        
        return render_template('inventory/dashboard.html',
                             user=current_user,
                             total_items=total_items,
                             low_stock_items=low_stock_items,
                             recent_movements=recent_movements,
                             inventory_value=inventory_value)
                             
    except Exception as e:
        current_app.logger.error(f"Inventory dashboard error: {e}")
        flash('Error loading inventory dashboard', 'error')
        return redirect(url_for('dashboard'))

@inventory_bp.route('/inventory/stock-status')
@login_required
def stock_status():
    """Current stock status"""
    try:
        # Get all items with current stock
        items = Item.query.filter_by(user_id=current_user.id).all()
        
        stock_data = []
        for item in items:
            # Calculate current stock
            current_stock = calculate_current_stock(item.item_cd)
            
            # Get last purchase and sale
            last_purchase = get_last_purchase(item.item_cd)
            last_sale = get_last_sale(item.item_cd)
            
            stock_data.append({
                'item_cd': item.item_cd,
                'item_nm': item.item_nm,
                'current_stock': current_stock,
                'unit': item.unit or 'PCS',
                'rate': item.rate or 0,
                'last_purchase': last_purchase,
                'last_sale': last_sale,
                'status': get_stock_status(current_stock)
            })
        
        # Sort by current stock (lowest first)
        stock_data.sort(key=lambda x: x['current_stock'])
        
        return render_template('inventory/stock_status.html',
                             user=current_user,
                             stock_data=stock_data)
                             
    except Exception as e:
        current_app.logger.error(f"Stock status error: {e}")
        flash('Error loading stock status', 'error')
        return redirect(url_for('inventory.inventory_dashboard'))

@inventory_bp.route('/inventory/stock-movements')
@login_required
def stock_movements():
    """Stock movement history"""
    try:
        # Get date range from request
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                  datetime.now().strftime('%Y-%m-%d'))
        item_cd = request.args.get('item_cd', '')
        
        # Convert to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get purchase movements
        purchase_movements = db.session.query(
            Purchase.bill_date,
            Purchase.bill_no,
            Item.item_nm,
            Party.party_nm,
            Purchase.qty,
            Purchase.rate,
            (Purchase.qty * Purchase.rate).label('amount'),
            func.literal('IN').label('movement_type')
        ).join(Item, Purchase.item_cd == Item.item_cd)\
         .join(Party, Purchase.party_cd == Party.party_cd)\
         .filter(
             Purchase.user_id == current_user.id,
             Purchase.bill_date >= start_dt,
             Purchase.bill_date < end_dt
         )
        
        if item_cd:
            purchase_movements = purchase_movements.filter(Purchase.item_cd == item_cd)
        
        purchase_movements = purchase_movements.order_by(desc(Purchase.bill_date)).all()
        
        # Get sale movements
        sale_movements = db.session.query(
            Sale.bill_date,
            Sale.bill_no,
            Item.item_nm,
            Party.party_nm,
            Sale.qty,
            Sale.rate,
            (Sale.qty * Sale.rate).label('amount'),
            func.literal('OUT').label('movement_type')
        ).join(Item, Sale.item_cd == Item.item_cd)\
         .join(Party, Sale.party_cd == Party.party_cd)\
         .filter(
             Sale.user_id == current_user.id,
             Sale.bill_date >= start_dt,
             Sale.bill_date < end_dt
         )
        
        if item_cd:
            sale_movements = sale_movements.filter(Sale.item_cd == item_cd)
        
        sale_movements = sale_movements.order_by(desc(Sale.bill_date)).all()
        
        # Combine and sort movements
        movements = list(purchase_movements) + list(sale_movements)
        movements.sort(key=lambda x: x.bill_date, reverse=True)
        
        # Get all items for filter dropdown
        items = Item.query.filter_by(user_id=current_user.id).all()
        
        return render_template('inventory/stock_movements.html',
                             user=current_user,
                             movements=movements,
                             items=items,
                             selected_item=item_cd,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        current_app.logger.error(f"Stock movements error: {e}")
        flash('Error loading stock movements', 'error')
        return redirect(url_for('inventory.inventory_dashboard'))

@inventory_bp.route('/inventory/low-stock-alerts')
@login_required
def low_stock_alerts():
    """Low stock alerts"""
    try:
        # Get low stock items
        low_stock_items = get_low_stock_items()
        
        # Get items with no stock
        no_stock_items = get_no_stock_items()
        
        return render_template('inventory/low_stock_alerts.html',
                             user=current_user,
                             low_stock_items=low_stock_items,
                             no_stock_items=no_stock_items)
                             
    except Exception as e:
        current_app.logger.error(f"Low stock alerts error: {e}")
        flash('Error loading low stock alerts', 'error')
        return redirect(url_for('inventory.inventory_dashboard'))

@inventory_bp.route('/inventory/valuation')
@login_required
def inventory_valuation():
    """Inventory valuation report"""
    try:
        # Get all items
        items = Item.query.filter_by(user_id=current_user.id).all()
        
        valuation_data = []
        total_value = 0
        
        for item in items:
            current_stock = calculate_current_stock(item.item_cd)
            avg_cost = calculate_average_cost(item.item_cd)
            value = current_stock * avg_cost
            
            valuation_data.append({
                'item_cd': item.item_cd,
                'item_nm': item.item_nm,
                'current_stock': current_stock,
                'unit': item.unit or 'PCS',
                'avg_cost': avg_cost,
                'current_rate': item.rate or 0,
                'value_at_cost': value,
                'value_at_rate': current_stock * (item.rate or 0),
                'profit_margin': ((item.rate or 0) - avg_cost) if avg_cost > 0 else 0
            })
            
            total_value += value
        
        return render_template('inventory/valuation.html',
                             user=current_user,
                             valuation_data=valuation_data,
                             total_value=total_value)
                             
    except Exception as e:
        current_app.logger.error(f"Inventory valuation error: {e}")
        flash('Error loading inventory valuation', 'error')
        return redirect(url_for('inventory.inventory_dashboard'))

@inventory_bp.route('/api/inventory/stock-chart')
@login_required
def stock_chart_data():
    """API endpoint for stock chart data"""
    try:
        # Get top 10 items by stock value
        items = Item.query.filter_by(user_id=current_user.id).all()
        
        stock_data = []
        for item in items:
            current_stock = calculate_current_stock(item.item_cd)
            avg_cost = calculate_average_cost(item.item_cd)
            value = current_stock * avg_cost
            
            stock_data.append({
                'item': item.item_nm,
                'stock': current_stock,
                'value': value
            })
        
        # Sort by value and take top 10
        stock_data.sort(key=lambda x: x['value'], reverse=True)
        stock_data = stock_data[:10]
        
        chart_data = {
            'labels': [item['item'] for item in stock_data],
            'datasets': [{
                'label': 'Stock Value',
                'data': [float(item['value']) for item in stock_data],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)',
                    'rgba(83, 102, 255, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)'
                ]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        current_app.logger.error(f"Stock chart error: {e}")
        return jsonify({'error': 'Error generating chart data'}), 500

# Helper functions
def calculate_current_stock(item_cd):
    """Calculate current stock for an item"""
    try:
        # Get total purchases
        total_purchases = db.session.query(func.sum(Purchase.qty))\
            .filter(
                Purchase.item_cd == item_cd,
                Purchase.user_id == current_user.id
            ).scalar() or 0
        
        # Get total sales
        total_sales = db.session.query(func.sum(Sale.qty))\
            .filter(
                Sale.item_cd == item_cd,
                Sale.user_id == current_user.id
            ).scalar() or 0
        
        return total_purchases - total_sales
        
    except Exception as e:
        current_app.logger.error(f"Calculate current stock error: {e}")
        return 0

def calculate_average_cost(item_cd):
    """Calculate average cost for an item"""
    try:
        # Get weighted average cost
        result = db.session.query(
            func.sum(Purchase.qty * Purchase.rate) / func.sum(Purchase.qty)
        ).filter(
            Purchase.item_cd == item_cd,
            Purchase.user_id == current_user.id
        ).scalar()
        
        return result or 0
        
    except Exception as e:
        current_app.logger.error(f"Calculate average cost error: {e}")
        return 0

def get_low_stock_items(threshold=10):
    """Get items with low stock"""
    try:
        items = Item.query.filter_by(user_id=current_user.id).all()
        low_stock = []
        
        for item in items:
            current_stock = calculate_current_stock(item.item_cd)
            if current_stock <= threshold and current_stock > 0:
                low_stock.append({
                    'item_cd': item.item_cd,
                    'item_nm': item.item_nm,
                    'current_stock': current_stock,
                    'unit': item.unit or 'PCS',
                    'threshold': threshold
                })
        
        return low_stock
        
    except Exception as e:
        current_app.logger.error(f"Get low stock items error: {e}")
        return []

def get_no_stock_items():
    """Get items with no stock"""
    try:
        items = Item.query.filter_by(user_id=current_user.id).all()
        no_stock = []
        
        for item in items:
            current_stock = calculate_current_stock(item.item_cd)
            if current_stock <= 0:
                no_stock.append({
                    'item_cd': item.item_cd,
                    'item_nm': item.item_nm,
                    'unit': item.unit or 'PCS'
                })
        
        return no_stock
        
    except Exception as e:
        current_app.logger.error(f"Get no stock items error: {e}")
        return []

def get_recent_stock_movements(limit=10):
    """Get recent stock movements"""
    try:
        # Get recent purchases
        purchases = db.session.query(
            Purchase.bill_date,
            Purchase.bill_no,
            Item.item_nm,
            Purchase.qty,
            func.literal('IN').label('type')
        ).join(Item, Purchase.item_cd == Item.item_cd)\
         .filter(Purchase.user_id == current_user.id)\
         .order_by(desc(Purchase.bill_date))\
         .limit(limit).all()
        
        # Get recent sales
        sales = db.session.query(
            Sale.bill_date,
            Sale.bill_no,
            Item.item_nm,
            Sale.qty,
            func.literal('OUT').label('type')
        ).join(Item, Sale.item_cd == Item.item_cd)\
         .filter(Sale.user_id == current_user.id)\
         .order_by(desc(Sale.bill_date))\
         .limit(limit).all()
        
        # Combine and sort
        movements = list(purchases) + list(sales)
        movements.sort(key=lambda x: x.bill_date, reverse=True)
        
        return movements[:limit]
        
    except Exception as e:
        current_app.logger.error(f"Get recent movements error: {e}")
        return []

def get_last_purchase(item_cd):
    """Get last purchase for an item"""
    try:
        purchase = Purchase.query.filter(
            Purchase.item_cd == item_cd,
            Purchase.user_id == current_user.id
        ).order_by(desc(Purchase.bill_date)).first()
        
        return purchase.bill_date if purchase else None
        
    except Exception as e:
        current_app.logger.error(f"Get last purchase error: {e}")
        return None

def get_last_sale(item_cd):
    """Get last sale for an item"""
    try:
        sale = Sale.query.filter(
            Sale.item_cd == item_cd,
            Sale.user_id == current_user.id
        ).order_by(desc(Sale.bill_date)).first()
        
        return sale.bill_date if sale else None
        
    except Exception as e:
        current_app.logger.error(f"Get last sale error: {e}")
        return None

def get_stock_status(current_stock):
    """Get stock status"""
    if current_stock <= 0:
        return 'Out of Stock'
    elif current_stock <= 10:
        return 'Low Stock'
    elif current_stock <= 50:
        return 'Medium Stock'
    else:
        return 'Good Stock'

def calculate_inventory_value():
    """Calculate total inventory value"""
    try:
        items = Item.query.filter_by(user_id=current_user.id).all()
        total_value = 0
        
        for item in items:
            current_stock = calculate_current_stock(item.item_cd)
            avg_cost = calculate_average_cost(item.item_cd)
            total_value += current_stock * avg_cost
        
        return total_value
        
    except Exception as e:
        current_app.logger.error(f"Calculate inventory value error: {e}")
        return 0 
 
 
 