from flask import Blueprint, jsonify, request, render_template_string, Response
from flask_login import login_required, current_user
from models import db, Parties, Items, Sales, Purchases, Cashbook
from datetime import datetime, date, timedelta
import json
import time

api_enhanced = Blueprint('api_enhanced', __name__)

# Real-time dashboard data
@api_enhanced.route('/api/today-sales')
@login_required
def today_sales():
    """Get today's total sales for real-time dashboard"""
    today = date.today()
    total_sales = db.session.query(db.func.sum(Sales.total_amount)).filter(
        Sales.user_id == current_user.id,
        db.func.date(Sales.sale_date) == today
    ).scalar() or 0
    
    return f"₹{total_sales:,.2f}"

@api_enhanced.route('/api/today-purchases')
@login_required
def today_purchases():
    """Get today's total purchases for real-time dashboard"""
    today = date.today()
    total_purchases = db.session.query(db.func.sum(Purchases.total_amount)).filter(
        Purchases.user_id == current_user.id,
        db.func.date(Purchases.purchase_date) == today
    ).scalar() or 0
    
    return f"₹{total_purchases:,.2f}"

@api_enhanced.route('/api/active-parties')
@login_required
def active_parties():
    """Get count of active parties for real-time dashboard"""
    count = Parties.query.filter(Parties.user_id == current_user.id).count()
    return str(count)

@api_enhanced.route('/api/low-stock-items')
@login_required
def low_stock_items():
    """Get count of low stock items for real-time dashboard"""
    # Items with stock less than 10
    count = Items.query.filter(
        Items.user_id == current_user.id,
        Items.stock < 10
    ).count()
    return str(count)

# Live search functionality
@api_enhanced.route('/api/search-parties')
@login_required
def search_parties():
    """Live search for parties"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    parties = Parties.query.filter(
        Parties.user_id == current_user.id,
        Parties.party_nm.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'party_cd': p.party_cd,
        'party_nm': p.party_nm,
        'phone': p.phone,
        'balance': p.balance or 0
    } for p in parties])

@api_enhanced.route('/api/search-items')
@login_required
def search_items():
    """Live search for items"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    items = Items.query.filter(
        Items.user_id == current_user.id,
        Items.item_nm.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'item_cd': i.item_cd,
        'item_nm': i.item_nm,
        'category': i.category or 'General',
        'stock': i.stock or 0
    } for i in items])

# Dynamic form loading
@api_enhanced.route('/api/new-sale-form')
@login_required
def new_sale_form():
    """Load new sale form dynamically"""
    return render_template_string("""
    <div class="card">
        <div class="card-header bg-success text-white">
            <h6 class="mb-0">New Sale Entry</h6>
        </div>
        <div class="card-body">
            <form hx-post="/api/save-sale" hx-target="#saleTableBody" hx-swap="beforeend">
                <div class="row g-2">
                    <div class="col-md-3">
                        <label class="form-label small">Bill No</label>
                        <input type="number" class="form-control form-control-sm" name="bill_no" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Date</label>
                        <input type="date" class="form-control form-control-sm" name="sale_date" value="{{ today }}" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Party</label>
                        <select class="form-control form-control-sm" name="party_cd" required>
                            <option value="">Select Party</option>
                            {% for party in parties %}
                            <option value="{{ party.party_cd }}">{{ party.party_nm }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Amount</label>
                        <input type="number" step="0.01" class="form-control form-control-sm" name="amount" required>
                    </div>
                </div>
                <div class="mt-2">
                    <button type="submit" class="btn btn-success btn-sm">
                        <i class="fas fa-save"></i> Save Sale
                    </button>
                </div>
            </form>
        </div>
    </div>
    """, today=date.today().isoformat(), parties=Parties.query.filter_by(user_id=current_user.id).all())

@api_enhanced.route('/api/new-purchase-form')
@login_required
def new_purchase_form():
    """Load new purchase form dynamically"""
    return render_template_string("""
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h6 class="mb-0">New Purchase Entry</h6>
        </div>
        <div class="card-body">
            <form hx-post="/api/save-purchase" hx-target="#purchaseTableBody" hx-swap="beforeend">
                <div class="row g-2">
                    <div class="col-md-3">
                        <label class="form-label small">Date</label>
                        <input type="date" class="form-control form-control-sm" name="purchase_date" value="{{ today }}" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Party</label>
                        <select class="form-control form-control-sm" name="party_cd" required>
                            <option value="">Select Party</option>
                            {% for party in parties %}
                            <option value="{{ party.party_cd }}">{{ party.party_nm }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Item</label>
                        <select class="form-control form-control-sm" name="item_cd" required>
                            <option value="">Select Item</option>
                            {% for item in items %}
                            <option value="{{ item.item_cd }}">{{ item.item_nm }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Bags</label>
                        <input type="number" class="form-control form-control-sm" name="bags" required>
                    </div>
                </div>
                <div class="mt-2">
                    <button type="submit" class="btn btn-primary btn-sm">
                        <i class="fas fa-save"></i> Save Purchase
                    </button>
                </div>
            </form>
        </div>
    </div>
    """, today=date.today().isoformat(), 
         parties=Parties.query.filter_by(user_id=current_user.id).all(),
         items=Items.query.filter_by(user_id=current_user.id).all())

# Real-time table data
@api_enhanced.route('/api/purchase-entries')
@login_required
def purchase_entries():
    """Get real-time purchase entries"""
    purchases = Purchases.query.filter_by(user_id=current_user.id).order_by(Purchases.purchase_date.desc()).limit(10).all()
    
    return render_template_string("""
    {% for purchase in purchases %}
    <tr>
        <td>{{ loop.index }}</td>
        <td>{{ purchase.purchase_date.strftime('%d/%m/%Y') }}</td>
        <td>{{ purchase.party.party_nm if purchase.party else 'N/A' }}</td>
        <td>{{ purchase.item.item_nm if purchase.item else 'N/A' }}</td>
        <td>{{ purchase.bags or 0 }}</td>
        <td>₹{{ "%.2f"|format(purchase.total_amount or 0) }}</td>
        <td>
            <button class="btn btn-sm btn-outline-primary" 
                    hx-get="/api/edit-purchase/{{ purchase.id }}"
                    hx-target="#purchaseFormContainer">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    </tr>
    {% endfor %}
    """, purchases=purchases)

@api_enhanced.route('/api/sale-entries')
@login_required
def sale_entries():
    """Get real-time sale entries"""
    sales = Sales.query.filter_by(user_id=current_user.id).order_by(Sales.sale_date.desc()).limit(10).all()
    
    return render_template_string("""
    {% for sale in sales %}
    <tr>
        <td>{{ sale.bill_no }}</td>
        <td>{{ sale.sale_date.strftime('%d/%m/%Y') }}</td>
        <td>{{ sale.party.party_nm if sale.party else 'N/A' }}</td>
        <td>{{ sale.items_count or 1 }} items</td>
        <td>₹{{ "%.2f"|format(sale.total_amount or 0) }}</td>
        <td>
            <button class="btn btn-sm btn-outline-success"
                    hx-get="/api/edit-sale/{{ sale.id }}"
                    hx-target="#saleFormContainer">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    </tr>
    {% endfor %}
    """, sales=sales)

# Save operations with HTMX
@api_enhanced.route('/api/save-sale', methods=['POST'])
@login_required
def save_sale():
    """Save sale via HTMX"""
    try:
        data = request.form
        sale = Sales(
            user_id=current_user.id,
            bill_no=data.get('bill_no'),
            sale_date=datetime.strptime(data.get('sale_date'), '%Y-%m-%d').date(),
            party_cd=data.get('party_cd'),
            total_amount=float(data.get('amount', 0))
        )
        db.session.add(sale)
        db.session.commit()
        
        return render_template_string("""
        <tr class="table-success">
            <td>{{ sale.bill_no }}</td>
            <td>{{ sale.sale_date.strftime('%d/%m/%Y') }}</td>
            <td>{{ sale.party.party_nm if sale.party else 'N/A' }}</td>
            <td>1 items</td>
            <td>₹{{ "%.2f"|format(sale.total_amount or 0) }}</td>
            <td>
                <button class="btn btn-sm btn-outline-success">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
        """, sale=sale)
    except Exception as e:
        return f"<tr><td colspan='6' class='text-danger'>Error: {str(e)}</td></tr>"

@api_enhanced.route('/api/save-purchase', methods=['POST'])
@login_required
def save_purchase():
    """Save purchase via HTMX"""
    try:
        data = request.form
        purchase = Purchases(
            user_id=current_user.id,
            purchase_date=datetime.strptime(data.get('purchase_date'), '%Y-%m-%d').date(),
            party_cd=data.get('party_cd'),
            item_cd=data.get('item_cd'),
            bags=int(data.get('bags', 0)),
            total_amount=float(data.get('amount', 0))
        )
        db.session.add(purchase)
        db.session.commit()
        
        return render_template_string("""
        <tr class="table-primary">
            <td>{{ loop.index }}</td>
            <td>{{ purchase.purchase_date.strftime('%d/%m/%Y') }}</td>
            <td>{{ purchase.party.party_nm if purchase.party else 'N/A' }}</td>
            <td>{{ purchase.item.item_nm if purchase.item else 'N/A' }}</td>
            <td>{{ purchase.bags or 0 }}</td>
            <td>₹{{ "%.2f"|format(purchase.total_amount or 0) }}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
        """, purchase=purchase, loop=type('Loop', (), {'index': 1})())
    except Exception as e:
        return f"<tr><td colspan='7' class='text-danger'>Error: {str(e)}</td></tr>"

# Real-time notifications (Server-Sent Events)
@api_enhanced.route('/api/notifications')
@login_required
def notifications_stream():
    """Server-Sent Events for real-time notifications"""
    def generate():
        while True:
            # Check for new sales/purchases in the last minute
            recent_sales = Sales.query.filter(
                Sales.user_id == current_user.id,
                Sales.created_date >= datetime.now() - timedelta(minutes=1)
            ).count()
            
            if recent_sales > 0:
                yield f"data: {json.dumps({'id': datetime.now().timestamp(), 'title': 'New Sale', 'message': f'{recent_sales} new sale(s) recorded'})}\n\n"
            
            time.sleep(30)  # Check every 30 seconds
    
    return Response(generate(), mimetype='text/event-stream')

# Mobile-optimized endpoints
@api_enhanced.route('/api/mobile/dashboard')
@login_required
def mobile_dashboard():
    """Mobile-optimized dashboard data"""
    today = date.today()
    
    today_sales = db.session.query(db.func.sum(Sales.total_amount)).filter(
        Sales.user_id == current_user.id,
        db.func.date(Sales.sale_date) == today
    ).scalar() or 0
    
    today_purchases = db.session.query(db.func.sum(Purchases.total_amount)).filter(
        Purchases.user_id == current_user.id,
        db.func.date(Purchases.purchase_date) == today
    ).scalar() or 0
    
    recent_sales = Sales.query.filter_by(user_id=current_user.id).order_by(Sales.sale_date.desc()).limit(5).all()
    recent_purchases = Purchases.query.filter_by(user_id=current_user.id).order_by(Purchases.purchase_date.desc()).limit(5).all()
    
    return jsonify({
        'today_sales': float(today_sales),
        'today_purchases': float(today_purchases),
        'recent_sales': [{
            'bill_no': s.bill_no,
            'party': s.party.party_nm if s.party else 'N/A',
            'amount': float(s.total_amount or 0),
            'date': s.sale_date.strftime('%d/%m/%Y')
        } for s in recent_sales],
        'recent_purchases': [{
            'party': p.party.party_nm if p.party else 'N/A',
            'item': p.item.item_nm if p.item else 'N/A',
            'bags': p.bags or 0,
            'amount': float(p.total_amount or 0),
            'date': p.purchase_date.strftime('%d/%m/%Y')
        } for p in recent_purchases]
    })

# Print-friendly endpoints
@api_enhanced.route('/api/print/sale/<int:sale_id>')
@login_required
def print_sale(sale_id):
    """Generate print-friendly sale bill"""
    sale = Sales.query.filter_by(id=sale_id, user_id=current_user.id).first_or_404()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sale Bill - {{ sale.bill_no }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
            .bill-details { margin: 20px 0; }
            .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            .table th, .table td { border: 1px solid #000; padding: 8px; text-align: left; }
            .total { font-weight: bold; text-align: right; }
            @media print { .no-print { display: none; } }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Business Management System</h1>
            <h2>Sale Bill</h2>
        </div>
        
        <div class="bill-details">
            <p><strong>Bill No:</strong> {{ sale.bill_no }}</p>
            <p><strong>Date:</strong> {{ sale.sale_date.strftime('%d/%m/%Y') }}</p>
            <p><strong>Party:</strong> {{ sale.party.party_nm if sale.party else 'N/A' }}</p>
        </div>
        
        <table class="table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Rate</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>General Item</td>
                    <td>1</td>
                    <td>₹{{ "%.2f"|format(sale.total_amount or 0) }}</td>
                    <td>₹{{ "%.2f"|format(sale.total_amount or 0) }}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="total">
            <p><strong>Total Amount: ₹{{ "%.2f"|format(sale.total_amount or 0) }}</strong></p>
        </div>
        
        <div class="no-print" style="margin-top: 30px;">
            <button onclick="window.print()">Print Bill</button>
            <button onclick="window.close()">Close</button>
        </div>
    </body>
    </html>
    """, sale=sale) 
 
 
 