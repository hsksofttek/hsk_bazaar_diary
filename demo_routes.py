from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, Party, Item, Sale, Purchase
from datetime import datetime, date, timedelta
from flask import Response
import json

demo = Blueprint('demo', __name__)

@demo.route('/demo/enhanced')
@login_required
def enhanced_demo():
    """Demo page showing modern Flask features"""
    return render_template('demo_enhanced_purchase_sale.html', 
                         current_time=datetime.now().strftime('%H:%M:%S'))

@demo.route('/demo/features')
@login_required
def features_demo():
    """Showcase of all modern features"""
    return render_template('features_showcase.html')

@demo.route('/demo/mobile')
@login_required
def mobile_demo():
    """Mobile-optimized demo"""
    return render_template('mobile_demo.html')

@demo.route('/demo/real-time')
@login_required
def real_time_demo():
    """Real-time updates demo"""
    return render_template('real_time_demo.html')

# API endpoints for demo data
@demo.route('/api/demo/today-sales')
@login_required
def demo_today_sales():
    """Demo: Get today's sales with random data"""
    import random
    sales = random.randint(50000, 150000)
    return f"₹{sales:,.2f}"

@demo.route('/api/demo/today-purchases')
@login_required
def demo_today_purchases():
    """Demo: Get today's purchases with random data"""
    import random
    purchases = random.randint(30000, 100000)
    return f"₹{purchases:,.2f}"

@demo.route('/api/demo/active-parties')
@login_required
def demo_active_parties():
    """Demo: Get active parties count"""
    count = Parties.query.filter_by(user_id=current_user.id).count()
    return str(count)

@demo.route('/api/demo/low-stock-items')
@login_required
def demo_low_stock_items():
    """Demo: Get low stock items count"""
    import random
    return str(random.randint(3, 15))

@demo.route('/api/demo/search-parties')
@login_required
def demo_search_parties():
    """Demo: Search parties with sample data"""
    query = request.args.get('q', '').lower()
    
    # Sample party data for demo
    sample_parties = [
        {'party_cd': 'P001', 'party_nm': 'ABC Traders', 'phone': '9876543210', 'balance': 15000},
        {'party_cd': 'P002', 'party_nm': 'XYZ Suppliers', 'phone': '9876543211', 'balance': 25000},
        {'party_cd': 'P003', 'party_nm': 'MNO Enterprises', 'phone': '9876543212', 'balance': 5000},
        {'party_cd': 'P004', 'party_nm': 'PQR Corporation', 'phone': '9876543213', 'balance': 35000},
        {'party_cd': 'P005', 'party_nm': 'STU Limited', 'phone': '9876543214', 'balance': 12000},
    ]
    
    if query:
        filtered_parties = [p for p in sample_parties if query in p['party_nm'].lower()]
        return jsonify(filtered_parties[:5])
    
    return jsonify(sample_parties[:5])

@demo.route('/api/demo/search-items')
@login_required
def demo_search_items():
    """Demo: Search items with sample data"""
    query = request.args.get('q', '').lower()
    
    # Sample item data for demo
    sample_items = [
        {'item_cd': 'I001', 'item_nm': 'Rice', 'category': 'Grains', 'stock': 150},
        {'item_cd': 'I002', 'item_nm': 'Wheat', 'category': 'Grains', 'stock': 200},
        {'item_cd': 'I003', 'item_nm': 'Sugar', 'category': 'Essentials', 'stock': 75},
        {'item_cd': 'I004', 'item_nm': 'Oil', 'category': 'Essentials', 'stock': 50},
        {'item_cd': 'I005', 'item_nm': 'Pulses', 'category': 'Grains', 'stock': 100},
    ]
    
    if query:
        filtered_items = [i for i in sample_items if query in i['item_nm'].lower()]
        return jsonify(filtered_items[:5])
    
    return jsonify(sample_items[:5])

@demo.route('/api/demo/purchase-entries')
@login_required
def demo_purchase_entries():
    """Demo: Get sample purchase entries"""
    import random
    
    sample_purchases = [
        {'id': 1, 'date': '15/07/2025', 'party': 'ABC Traders', 'item': 'Rice', 'bags': 50, 'amount': 25000},
        {'id': 2, 'date': '14/07/2025', 'party': 'XYZ Suppliers', 'item': 'Wheat', 'bags': 30, 'amount': 18000},
        {'id': 3, 'date': '13/07/2025', 'party': 'MNO Enterprises', 'item': 'Sugar', 'bags': 25, 'amount': 12500},
    ]
    
    return render_template_string("""
    {% for purchase in purchases %}
    <tr>
        <td>{{ loop.index }}</td>
        <td>{{ purchase.date }}</td>
        <td>{{ purchase.party }}</td>
        <td>{{ purchase.item }}</td>
        <td>{{ purchase.bags }}</td>
        <td>₹{{ "{:,.2f}".format(purchase.amount) }}</td>
        <td>
            <button class="btn btn-sm btn-outline-primary">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    </tr>
    {% endfor %}
    """, purchases=sample_purchases)

@demo.route('/api/demo/sale-entries')
@login_required
def demo_sale_entries():
    """Demo: Get sample sale entries"""
    import random
    
    sample_sales = [
        {'id': 1, 'bill_no': 'S001', 'date': '15/07/2025', 'party': 'PQR Corporation', 'items': 3, 'amount': 15000},
        {'id': 2, 'bill_no': 'S002', 'date': '14/07/2025', 'party': 'STU Limited', 'items': 2, 'amount': 12000},
        {'id': 3, 'bill_no': 'S003', 'date': '13/07/2025', 'party': 'ABC Traders', 'items': 4, 'amount': 20000},
    ]
    
    return render_template_string("""
    {% for sale in sales %}
    <tr>
        <td>{{ sale.bill_no }}</td>
        <td>{{ sale.date }}</td>
        <td>{{ sale.party }}</td>
        <td>{{ sale.items }} items</td>
        <td>₹{{ "{:,.2f}".format(sale.amount) }}</td>
        <td>
            <button class="btn btn-sm btn-outline-success">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    </tr>
    {% endfor %}
    """, sales=sample_sales)

@demo.route('/api/demo/notifications')
@login_required
def demo_notifications():
    """Demo: Server-Sent Events for notifications"""
    def generate():
        notifications = [
            "New sale recorded: Bill #S001",
            "Low stock alert: Rice (5 bags remaining)",
            "Payment received from ABC Traders",
            "New purchase: 50 bags of Wheat",
            "Monthly report generated successfully"
        ]
        
        for i, notification in enumerate(notifications):
            yield f"data: {json.dumps({'id': i+1, 'title': 'System Alert', 'message': notification})}\n\n"
            time.sleep(5)  # Send notification every 5 seconds
    
    return Response(generate(), mimetype='text/event-stream')

# Demo forms
@demo.route('/api/demo/new-sale-form')
@login_required
def demo_new_sale_form():
    """Demo: New sale form"""
    return render_template_string("""
    <div class="card">
        <div class="card-header bg-success text-white">
            <h6 class="mb-0">New Sale Entry (Demo)</h6>
        </div>
        <div class="card-body">
            <form hx-post="/api/demo/save-sale" hx-target="#saleTableBody" hx-swap="beforeend">
                <div class="row g-2">
                    <div class="col-md-3">
                        <label class="form-label small">Bill No</label>
                        <input type="number" class="form-control form-control-sm" name="bill_no" value="S{{ "%.3d"|format(random.randint(1, 999)) }}" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Date</label>
                        <input type="date" class="form-control form-control-sm" name="sale_date" value="{{ today }}" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Party</label>
                        <select class="form-control form-control-sm" name="party_cd" required>
                            <option value="">Select Party</option>
                            <option value="P001">ABC Traders</option>
                            <option value="P002">XYZ Suppliers</option>
                            <option value="P003">MNO Enterprises</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Amount</label>
                        <input type="number" step="0.01" class="form-control form-control-sm" name="amount" value="{{ random.randint(5000, 25000) }}" required>
                    </div>
                </div>
                <div class="mt-2">
                    <button type="submit" class="btn btn-success btn-sm">
                        <i class="fas fa-save"></i> Save Sale (Demo)
                    </button>
                </div>
            </form>
        </div>
    </div>
    """, today=date.today().isoformat())

@demo.route('/api/demo/new-purchase-form')
@login_required
def demo_new_purchase_form():
    """Demo: New purchase form"""
    return render_template_string("""
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h6 class="mb-0">New Purchase Entry (Demo)</h6>
        </div>
        <div class="card-body">
            <form hx-post="/api/demo/save-purchase" hx-target="#purchaseTableBody" hx-swap="beforeend">
                <div class="row g-2">
                    <div class="col-md-3">
                        <label class="form-label small">Date</label>
                        <input type="date" class="form-control form-control-sm" name="purchase_date" value="{{ today }}" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Party</label>
                        <select class="form-control form-control-sm" name="party_cd" required>
                            <option value="">Select Party</option>
                            <option value="P001">ABC Traders</option>
                            <option value="P002">XYZ Suppliers</option>
                            <option value="P003">MNO Enterprises</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Item</label>
                        <select class="form-control form-control-sm" name="item_cd" required>
                            <option value="">Select Item</option>
                            <option value="I001">Rice</option>
                            <option value="I002">Wheat</option>
                            <option value="I003">Sugar</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small">Bags</label>
                        <input type="number" class="form-control form-control-sm" name="bags" value="{{ random.randint(10, 100) }}" required>
                    </div>
                </div>
                <div class="mt-2">
                    <button type="submit" class="btn btn-primary btn-sm">
                        <i class="fas fa-save"></i> Save Purchase (Demo)
                    </button>
                </div>
            </form>
        </div>
    </div>
    """, today=date.today().isoformat())

# Demo save operations
@demo.route('/api/demo/save-sale', methods=['POST'])
@login_required
def demo_save_sale():
    """Demo: Save sale with sample data"""
    import random
    data = request.form
    
    sample_sale = {
        'bill_no': data.get('bill_no', f'S{random.randint(100, 999)}'),
        'date': data.get('sale_date', date.today().strftime('%d/%m/%Y')),
        'party': 'Demo Party',
        'items': random.randint(1, 5),
        'amount': float(data.get('amount', random.randint(5000, 25000)))
    }
    
    return render_template_string("""
    <tr class="table-success">
        <td>{{ sale.bill_no }}</td>
        <td>{{ sale.date }}</td>
        <td>{{ sale.party }}</td>
        <td>{{ sale.items }} items</td>
        <td>₹{{ "{:,.2f}".format(sale.amount) }}</td>
        <td>
            <button class="btn btn-sm btn-outline-success">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    </tr>
    """, sale=sample_sale)

@demo.route('/api/demo/save-purchase', methods=['POST'])
@login_required
def demo_save_purchase():
    """Demo: Save purchase with sample data"""
    import random
    data = request.form
    
    sample_purchase = {
        'date': data.get('purchase_date', date.today().strftime('%d/%m/%Y')),
        'party': 'Demo Supplier',
        'item': 'Demo Item',
        'bags': int(data.get('bags', random.randint(10, 100))),
        'amount': random.randint(5000, 25000)
    }
    
    return render_template_string("""
    <tr class="table-primary">
        <td>{{ loop.index }}</td>
        <td>{{ purchase.date }}</td>
        <td>{{ purchase.party }}</td>
        <td>{{ purchase.item }}</td>
        <td>{{ purchase.bags }}</td>
        <td>₹{{ "{:,.2f}".format(purchase.amount) }}</td>
        <td>
            <button class="btn btn-sm btn-outline-primary">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    </tr>
    """, purchase=sample_purchase, loop=type('Loop', (), {'index': random.randint(1, 10)})())

# Mobile demo data
@demo.route('/api/demo/mobile/dashboard')
@login_required
def demo_mobile_dashboard():
    """Demo: Mobile dashboard data"""
    import random
    
    return jsonify({
        'today_sales': random.randint(50000, 150000),
        'today_purchases': random.randint(30000, 100000),
        'recent_sales': [
            {'bill_no': 'S001', 'party': 'ABC Traders', 'amount': 15000, 'date': '15/07/2025'},
            {'bill_no': 'S002', 'party': 'XYZ Suppliers', 'amount': 12000, 'date': '14/07/2025'},
            {'bill_no': 'S003', 'party': 'MNO Enterprises', 'amount': 20000, 'date': '13/07/2025'},
        ],
        'recent_purchases': [
            {'party': 'PQR Corporation', 'item': 'Rice', 'bags': 50, 'amount': 25000, 'date': '15/07/2025'},
            {'party': 'STU Limited', 'item': 'Wheat', 'bags': 30, 'amount': 18000, 'date': '14/07/2025'},
            {'party': 'ABC Traders', 'item': 'Sugar', 'bags': 25, 'amount': 12500, 'date': '13/07/2025'},
        ]
    }) 
 
 
 