from flask import Blueprint, render_template, request, jsonify, render_template_string
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from database import db
from models import Sale, Party, Item
from forms import SaleForm

sales_api = Blueprint('sales_api', __name__)

@sales_api.route('/api/sales/stats/total')
@login_required
def sales_stats_total():
    """Get total sales amount"""
    try:
        total = db.session.query(func.sum(Sale.sal_amt)).filter(
            Sale.user_id == current_user.id
        ).scalar() or 0
        return f"{total:.2f}"
    except Exception as e:
        print(f"Error getting total sales: {e}")
        return "0"

@sales_api.route('/api/sales/stats/monthly')
@login_required
def sales_stats_monthly():
    """Get monthly sales amount"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Get current month's start and end dates
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
        
        total = db.session.query(func.sum(Sale.sal_amt)).filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= month_start.date(),
            Sale.bill_date <= month_end.date()
        ).scalar() or 0
        
        return f"{total:.2f}"
    except Exception as e:
        print(f"Error getting monthly sales: {e}")
        return "0"

@sales_api.route('/api/sales/stats/today')
@login_required
def sales_stats_today():
    """Get today's sales amount"""
    try:
        from datetime import datetime
        from sqlalchemy import func
        
        today = datetime.now().date()
        total = db.session.query(func.sum(Sale.sal_amt)).filter(
            Sale.user_id == current_user.id,
            Sale.bill_date == today
        ).scalar() or 0
        
        return f"{total:.2f}"
    except Exception as e:
        print(f"Error getting today's sales: {e}")
        return "0"

@sales_api.route('/api/sales/next-bill')
@login_required
def sales_next_bill():
    """Get next available sales bill number for current user"""
    try:
        last_sale = Sale.query.filter_by(user_id=current_user.id).order_by(desc(Sale.bill_no)).first()
        next_no = (last_sale.bill_no + 1) if last_sale else 2001
        return jsonify({'success': True, 'bill_no': next_no})
    except Exception as e:
        print(f"Error getting next bill number: {e}")
        return jsonify({'success': False, 'bill_no': 2001, 'error': str(e)}), 500

@sales_api.route('/api/sales/table')
@login_required
def sales_table():
    """Get sales table HTML"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        date_filter = request.args.get('date', '')
        customer = request.args.get('customer', '')
        amount = request.args.get('amount', '')
        sort_by = request.args.get('sort', 'date')
        
        # Build query
        query = Sale.query.filter_by(user_id=current_user.id)
        
        # Apply search filter
        if search:
            query = query.join(Party).join(Item).filter(
                or_(
                    Sale.bill_no.like(f'%{search}%'),
                    Party.party_nm.ilike(f'%{search}%'),
                    Item.it_nm.ilike(f'%{search}%')
                )
            )
        
        # Apply date filter
        if date_filter:
            today = datetime.now().date()
            if date_filter == 'today':
                query = query.filter(func.date(Sale.bill_date) == today)
            elif date_filter == 'week':
                week_ago = today - timedelta(days=7)
                query = query.filter(func.date(Sale.bill_date) >= week_ago)
            elif date_filter == 'month':
                month_ago = today - timedelta(days=30)
                query = query.filter(func.date(Sale.bill_date) >= month_ago)
            elif date_filter == 'quarter':
                quarter_ago = today - timedelta(days=90)
                query = query.filter(func.date(Sale.bill_date) >= quarter_ago)
        
        # Apply customer filter
        if customer:
            query = query.join(Party).filter(Party.party_cd == customer)
        
        # Apply amount filter
        if amount:
            if amount == '0-1000':
                query = query.filter(and_(Sale.sal_amt >= 0, Sale.sal_amt <= 1000))
            elif amount == '1000-5000':
                query = query.filter(and_(Sale.sal_amt > 1000, Sale.sal_amt <= 5000))
            elif amount == '5000-10000':
                query = query.filter(and_(Sale.sal_amt > 5000, Sale.sal_amt <= 10000))
            elif amount == '10000+':
                query = query.filter(Sale.sal_amt > 10000)
        
        # Group by bill number to get unique bills
        query = query.group_by(Sale.bill_no)
        
        # Apply sorting
        if sort_by == 'date':
            query = query.order_by(desc(Sale.bill_date))
        elif sort_by == 'amount':
            query = query.order_by(desc(Sale.sal_amt))
        elif sort_by == 'customer':
            query = query.join(Party).order_by(Party.party_nm)
        elif sort_by == 'bill_no':
            query = query.order_by(Sale.bill_no)
        
        # Get unique bills
        bills = query.all()
        
        if not bills:
            return '''
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Bill No</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Items</th>
                        <th>Total Amount</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="6" class="text-center py-4">
                            <div class="text-muted">
                                <i class="fas fa-receipt fa-3x mb-3"></i>
                                <h5>No sales found</h5>
                                <p>Try adjusting your search criteria or create a new sale.</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            '''
        
        table_html = '''
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Bill No</th>
                    <th>Date</th>
                    <th>Customer</th>
                    <th>Items</th>
                    <th>Total Amount</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for bill_no in [bill.bill_no for bill in bills]:
            # Get all items for this bill
            bill_items = Sale.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
            if not bill_items:
                continue
            
            # Get bill details from first item
            first_item = bill_items[0]
            total_amount = sum(item.sal_amt for item in bill_items)
            item_count = len(bill_items)
            
            table_html += f'''
            <tr>
                <td>
                    <span class="sale-badge">{bill_no}</span>
                </td>
                <td>{first_item.bill_date.strftime('%d/%m/%Y') if first_item.bill_date else 'N/A'}</td>
                <td>
                    <strong>{first_item.party.party_nm if first_item.party else first_item.party_cd}</strong>
                    <br><small class="text-muted">{first_item.party_cd}</small>
                </td>
                <td>
                    <span class="items-badge">{item_count} item(s)</span>
                    <br><small class="text-muted">
                        {', '.join([item.item.it_nm if item.item else item.it_cd for item in bill_items[:3]])}
                        {f' and {len(bill_items) - 3} more...' if len(bill_items) > 3 else ''}
                    </small>
                </td>
                <td>
                    <strong>₹{total_amount:.2f}</strong>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-action btn-view" data-bill-no="{bill_no}" title="View Sale">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-action btn-edit" data-bill-no="{bill_no}" title="Edit Sale">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-action btn-delete" data-bill-no="{bill_no}" title="Delete Sale">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            '''
        
        table_html += '''
            </tbody>
        </table>
        '''
        
        return table_html
        
    except Exception as e:
        print(f"Error loading sales table: {e}")
        return '''
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Bill No</th>
                    <th>Date</th>
                    <th>Customer</th>
                    <th>Items</th>
                    <th>Total Amount</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error loading sales table. Please try again.
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        '''

@sales_api.route('/api/sales/add-form')
@login_required
def sales_add_form():
    """Get add sale form with multiple items support"""
    try:
        # Get parties for dropdown with error handling
        parties = Party.query.filter_by(user_id=current_user.id).all() or []
        
        # Get items for dropdown with error handling
        items = Item.query.filter_by(user_id=current_user.id).all() or []
        
        # Generate next bill number with error handling
        last_sale = Sale.query.filter_by(user_id=current_user.id).order_by(desc(Sale.bill_no)).first()
        bill_no = (last_sale.bill_no + 1) if last_sale else 2001
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Convert items to dictionaries for JSON serialization with error handling
        items_data = []
        for item in items:
            try:
                items_data.append({
                    'it_cd': str(item.it_cd) if item.it_cd else '',
                    'it_nm': str(item.it_nm) if item.it_nm else '',
                    'rate': float(item.rate) if item.rate else 0.0,
                    'gst': float(item.gst) if item.gst else 0.0
                })
            except Exception as e:
                print(f"Error processing item {item}: {e}")
                continue
        
        # Convert parties to dictionaries for JSON serialization with error handling
        parties_data = []
        for party in parties:
            try:
                parties_data.append({
                    'party_cd': str(party.party_cd) if party.party_cd else '',
                    'party_nm': str(party.party_nm) if party.party_nm else '',
                    'phone': str(party.phone) if party.phone else '',
                    'mobile': str(party.mobile) if party.mobile else '',
                    'place': str(party.place) if party.place else ''
                })
            except Exception as e:
                print(f"Error processing party {party}: {e}")
                continue
        
        return render_template_string("""
            <div class="modal-header bright-header">
                <h5 class="modal-title" id="saleModalLabel">
                    <i class="fas fa-plus me-2"></i>Add New Sale Bill
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form id="addSaleForm" onsubmit="saveSale(event)">
                <div class="modal-body bright-body" style="max-height: 80vh; overflow-y: auto;">
                    
                    <!-- Bill Information -->
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6 class="mb-0"><i class="fas fa-file-invoice me-2"></i>Bill Information</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label bright-label">Bill Number *</label>
                                    <input type="number" class="form-control bright-input" name="bill_no" id="sale_bill_no" value="{{ bill_no }}" required>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label bright-label">Bill Date *</label>
                                    <input type="date" class="form-control bright-input" name="bill_date" id="sale_bill_date" value="{{ today }}" required>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label bright-label">Party *</label>
                                    <select class="form-select bright-input" name="party_cd" id="sale_party_cd" required>
                                        <option value="">Select Party</option>
                                        {% for party in parties_data %}
                                        {% if party and party.party_cd and party.party_nm %}
                                        <option value="{{ party.party_cd }}">{{ party.party_nm }} ({{ party.party_cd }})</option>
                                        {% endif %}
                                        {% endfor %}
                                    </select>
                                </div>
                                </div>
                        </div>
                    </div>
                    
                    <!-- Sale Items -->
                    <div class="card mb-3">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0"><i class="fas fa-boxes me-2"></i>Sale Items</h6>
                            <button type="button" class="btn btn-sm btn-success" onclick="addSaleItemRow()">
                                <i class="fas fa-plus me-1"></i>ADD ITEM
                                </button>
                            </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-bordered" id="saleItemsTable">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>ITEM</th>
                                            <th>QUANTITY</th>
                                            <th>RATE</th>
                                            <th>AMOUNT</th>
                                            <th>DISCOUNT</th>
                                            <th>NET AMOUNT</th>
                                            <th>ACTION</th>
                                        </tr>
                                    </thead>
                                    <tbody id="saleItemsTableBody">
                                        <!-- Items will be added here dynamically -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Bill Summary -->
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0"><i class="fas fa-calculator me-2"></i>Bill Summary</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">Sub Total</label>
                                            <input type="number" class="form-control bright-input" id="sale_sub_total" value="0.00" readonly>
                                </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">Total Discount</label>
                                            <input type="number" class="form-control bright-input" id="sale_total_discount" value="0.00" readonly>
                                </div>
                                </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">GST Amount</label>
                                            <input type="number" class="form-control bright-input" id="sale_gst_amount" value="0.00" readonly>
                                </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">Grand Total</label>
                                            <input type="number" class="form-control bright-input" id="sale_grand_total" value="0.00" readonly>
                                </div>
                            </div>
                        </div>
                    </div>
                        </div>
                    </div>
                    
                </div>
                <div class="modal-footer bright-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-1"></i>CANCEL
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save me-1"></i>SAVE SALE BILL
                    </button>
                </div>
            </form>
            
            <script>
            // Store items data globally
            window.saleItemsData = {{ items_data|tojson }};
            window.salePartiesData = {{ parties_data|tojson }};
            console.log('Items data loaded:', window.saleItemsData);
            console.log('Parties data loaded:', window.salePartiesData);
            
            // Initialize form when modal loads
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Modal DOM loaded, initializing form...');
                
                // Reset form when modal opens
                saleItemRowCounter = 0;
                const tbody = document.getElementById('saleItemsTableBody');
                if (tbody) {
                    tbody.innerHTML = '';
                }
                
                // Set today's date
                const today = new Date().toISOString().split('T')[0];
                const dateInput = document.getElementById('sale_bill_date');
                if (dateInput) {
                    dateInput.value = today;
                }
                
                // Add first item row immediately
                addSaleItemRow();
            });
            </script>
        """, bill_no=bill_no or 2001, today=today or datetime.now().strftime('%Y-%m-%d'), parties_data=parties_data or [], items_data=items_data or [])
        
    except Exception as e:
        return f"Error loading form: {str(e)}", 500

@sales_api.route('/api/sales/add', methods=['POST'])
@login_required
def sales_add():
    """Add new sale with multiple items (JSON or form)"""
    try:
        if request.is_json:
            data = request.get_json() or {}
            bill_no = int(data.get('bill_no') or 0) or 2001
            bill_date = datetime.strptime(data.get('bill_date'), '%Y-%m-%d')
            party_cd = data.get('party_cd')
            items_payload = data.get('items', [])
        else:
            data = request.form
            bill_no = int(data.get('bill_no'))
            bill_date = datetime.strptime(data.get('bill_date'), '%Y-%m-%d')
            party_cd = data.get('party_cd')
            items_data = {}
            for key, value in data.items():
                if key.startswith('items[') and key.endswith('][it_cd]'):
                    counter = key.split('[')[1].split(']')[0]
                    items_data.setdefault(counter, {})['it_cd'] = value
                elif key.startswith('items[') and key.endswith('][qty]'):
                    counter = key.split('[')[1].split(']')[0]
                    items_data.setdefault(counter, {})['qty'] = float(value) if value else 0
                elif key.startswith('items[') and key.endswith('][rate]'):
                    counter = key.split('[')[1].split(']')[0]
                    items_data.setdefault(counter, {})['rate'] = float(value) if value else 0
                elif key.startswith('items[') and key.endswith('][discount]'):
                    counter = key.split('[')[1].split(']')[0]
                    items_data.setdefault(counter, {})['discount'] = float(value) if value else 0
            items_payload = list(items_data.values())

        if not party_cd:
            return jsonify({'success': False, 'message': 'Party code is required'}), 400
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one item is required'}), 400

        total_amount = 0
        for item_data in items_payload:
            it_cd = item_data.get('it_cd') or item_data.get('item_code')
            qty = float(item_data.get('qty') or item_data.get('quantity') or 0)
            rate = float(item_data.get('rate') or 0)
            discount = float(item_data.get('discount') or item_data.get('discount_percent') or 0)
            if not it_cd or qty <= 0:
                continue
            amount = (qty * rate) - discount
            total_amount += amount
            new_sale = Sale(
                user_id=current_user.id,
                bill_no=bill_no,
                party_cd=party_cd,
                it_cd=it_cd,
                bill_date=bill_date,
                qty=qty,
                rate=rate,
                discount=discount,
                sal_amt=amount
            )
            db.session.add(new_sale)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Sale bill #{bill_no} recorded successfully!',
            'total_amount': total_amount
        })

    except Exception as e:
        print(f"Sales add error: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error recording sale: {str(e)}'
        }), 500

@sales_api.route('/api/sales/delete/<bill_no>', methods=['DELETE'])
@login_required
def sales_delete(bill_no):
    """Delete sale"""
    try:
        sales = Sale.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
        if not sales:
            return jsonify({'success': False, 'message': 'Sale not found'}), 404
        
        for sale in sales:
            db.session.delete(sale)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Sale deleted successfully'})
    except Exception as e:
        print(f"Sales delete error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500 

@sales_api.route('/api/sales/items/<bill_no>')
@login_required
def sales_items(bill_no):
    """Get sale items for a specific bill"""
    try:
        print(f"=== FETCHING SALE ITEMS FOR BILL {bill_no} ===")
        
        # Get sales for this bill
        sales = Sale.query.filter_by(bill_no=bill_no).all()
        print(f"Found {len(sales)} sales for bill {bill_no}")
        
        if not sales:
            print(f"No sales found for bill {bill_no}")
            return jsonify({
                'success': True,
                'items': []
            })
        
        # Convert to list of dictionaries
        items = []
        for sale in sales:
            item_data = {
                'it_cd': sale.it_cd,
                'qty': float(sale.qty) if sale.qty else 0.0,
                'rate': float(sale.rate) if sale.rate else 0.0,
                'discount': float(sale.discount) if sale.discount else 0.0,
                'amount': float(sale.sal_amt) if sale.sal_amt else 0.0
            }
            items.append(item_data)
            print(f"Added item: {item_data}")
        
        print(f"Returning {len(items)} items")
        return jsonify({
            'success': True,
            'items': items
        })
        
    except Exception as e:
        print(f"Error fetching sale items: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error fetching sale items: {str(e)}'
        }), 500

@sales_api.route('/api/sales/export')
@login_required
def sales_export():
    """Export sales to CSV"""
    try:
        import csv
        import io
        from flask import make_response
        
        search = request.args.get('search', '')
        date_filter = request.args.get('date', '')
        customer = request.args.get('customer', '')
        amount = request.args.get('amount', '')
        sort_by = request.args.get('sort', 'date')
        
        # Build query
        query = Sale.query.filter_by(user_id=current_user.id)
        
        # Apply search filter
        if search:
            query = query.join(Party).join(Item).filter(
                or_(
                    Sale.bill_no.like(f'%{search}%'),
                    Party.party_nm.ilike(f'%{search}%'),
                    Item.it_nm.ilike(f'%{search}%')
                )
            )
        
        # Apply date filter
        if date_filter:
            today = datetime.now().date()
            if date_filter == 'today':
                query = query.filter(func.date(Sale.bill_date) == today)
            elif date_filter == 'week':
                week_ago = today - timedelta(days=7)
                query = query.filter(func.date(Sale.bill_date) >= week_ago)
            elif date_filter == 'month':
                month_ago = today - timedelta(days=30)
                query = query.filter(func.date(Sale.bill_date) >= month_ago)
            elif date_filter == 'quarter':
                quarter_ago = today - timedelta(days=90)
                query = query.filter(func.date(Sale.bill_date) >= quarter_ago)
        
        # Apply customer filter
        if customer:
            query = query.join(Party).filter(Party.party_cd == customer)
        
        # Apply amount filter
        if amount:
            if amount == '0-1000':
                query = query.filter(and_(Sale.sal_amt >= 0, Sale.sal_amt <= 1000))
            elif amount == '1000-5000':
                query = query.filter(and_(Sale.sal_amt > 1000, Sale.sal_amt <= 5000))
            elif amount == '5000-10000':
                query = query.filter(and_(Sale.sal_amt > 5000, Sale.sal_amt <= 10000))
            elif amount == '10000+':
                query = query.filter(Sale.sal_amt > 10000)
        
        # Group by bill number to get unique bills
        query = query.group_by(Sale.bill_no)
        
        # Apply sorting
        if sort_by == 'date':
            query = query.order_by(desc(Sale.bill_date))
        elif sort_by == 'amount':
            query = query.order_by(desc(Sale.sal_amt))
        elif sort_by == 'customer':
            query = query.join(Party).order_by(Party.party_nm)
        elif sort_by == 'bill_no':
            query = query.order_by(Sale.bill_no)
        
        # Get unique bills
        bills = query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Bill No', 'Date', 'Customer Code', 'Customer Name', 'Items Count', 'Total Amount', 'Created Date'])
        
        for bill_no in [bill.bill_no for bill in bills]:
            # Get all items for this bill
            bill_items = Sale.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
            if not bill_items:
                continue
            
            # Get bill details from first item
            first_item = bill_items[0]
            total_amount = sum(item.sal_amt for item in bill_items)
            item_count = len(bill_items)
            
            writer.writerow([
                bill_no,
                first_item.bill_date.strftime('%d/%m/%Y') if first_item.bill_date else '',
                first_item.party_cd or '',
                first_item.party.party_nm if first_item.party else '',
                item_count,
                f"{total_amount:.2f}",
                first_item.created_date.strftime('%Y-%m-%d') if first_item.created_date else ''
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=sales_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
        
    except Exception as e:
        print(f"Error exporting sales: {e}")
        return jsonify({'success': False, 'message': f'Error exporting sales: {str(e)}'}), 500 


# Detail fetch fallback for modern Sales Management
@sales_api.route('/api/sales/<int:bill_no>', methods=['GET'])
@login_required
def sales_detail_fallback(bill_no):
    """Return sale details for given bill number (current user)."""
    try:
        from sales_management import SalesManagementSystem
        sms = SalesManagementSystem()
        result = sms.get_sales_entry(current_user.id, bill_no)
        status = 200 if result.get('success') else 404
        return jsonify(result), status
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
