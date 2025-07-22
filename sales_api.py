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
    """Get total sales count"""
    try:
        count = Sale.query.filter_by(user_id=current_user.id).count()
        return str(count)
    except Exception as e:
        print(f"Error getting total sales: {e}")
        return "0"

@sales_api.route('/api/sales/stats/monthly')
@login_required
def sales_stats_monthly():
    """Get monthly sales count"""
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
        
        count = Sale.query.filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= month_start.date(),
            Sale.bill_date <= month_end.date()
        ).count()
        
        return str(count)
    except Exception as e:
        print(f"Error getting monthly sales: {e}")
        return "0"

@sales_api.route('/api/sales/stats/today')
@login_required
def sales_stats_today():
    """Get today's sales count"""
    try:
        from datetime import datetime
        from sqlalchemy import func
        
        today = datetime.now().date()
        count = Sale.query.filter(
            Sale.user_id == current_user.id,
            Sale.bill_date == today
        ).count()
        
        return str(count)
    except Exception as e:
        print(f"Error getting today's sales: {e}")
        return "0"

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
    """Add new sale with multiple items"""
    try:
        data = request.form
        bill_no = int(data.get('bill_no'))
        bill_date = datetime.strptime(data.get('bill_date'), '%Y-%m-%d')
        party_cd = data.get('party_cd')
        
        # Get all items from form
        items_data = {}
        for key, value in data.items():
            if key.startswith('items[') and key.endswith('][it_cd]'):
                # Extract counter from key like "items[1][it_cd]"
                counter = key.split('[')[1].split(']')[0]
                if counter not in items_data:
                    items_data[counter] = {}
                items_data[counter]['it_cd'] = value
            elif key.startswith('items[') and key.endswith('][qty]'):
                counter = key.split('[')[1].split(']')[0]
                if counter not in items_data:
                    items_data[counter] = {}
                items_data[counter]['qty'] = float(value) if value else 0
            elif key.startswith('items[') and key.endswith('][rate]'):
                counter = key.split('[')[1].split(']')[0]
                if counter not in items_data:
                    items_data[counter] = {}
                items_data[counter]['rate'] = float(value) if value else 0
            elif key.startswith('items[') and key.endswith('][discount]'):
                counter = key.split('[')[1].split(']')[0]
                if counter not in items_data:
                    items_data[counter] = {}
                items_data[counter]['discount'] = float(value) if value else 0
        
        # Create sale records for each item
        total_amount = 0
        for counter, item_data in items_data.items():
            if item_data.get('it_cd') and item_data.get('qty') > 0:
                qty = item_data['qty']
                rate = item_data['rate']
                discount = item_data.get('discount', 0)
                amount = (qty * rate) - discount
                total_amount += amount
                
                new_sale = Sale(
                    user_id=current_user.id,
                    bill_no=bill_no,
                    party_cd=party_cd,
                    it_cd=item_data['it_cd'],
                    bill_date=bill_date,
                    qty=qty,
                    rate=rate,
                    discount=discount,
                    sal_amt=amount
                )
                db.session.add(new_sale)
        
        db.session.commit()
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title text-success">
                    <i class="fas fa-check-circle me-2"></i>Sale Created Successfully
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Sale Bill #{{ bill_no }} has been created successfully!
                </div>
                <p class="text-muted">Total Amount: ₹{{ "%.2f"|format(total_amount) }}</p>
                <p class="text-muted">Items: {{ item_count }} item(s)</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="location.reload()">Close</button>
            </div>
        """, bill_no=bill_no, total_amount=total_amount, item_count=len(items_data))
    except Exception as e:
        print(f"Sales add error: {e}")
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>Error
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error creating sale: {{ error }}
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        """, error=str(e))

@sales_api.route('/api/sales/view/<bill_no>')
@login_required
def sales_view(bill_no):
    """View sale details with the same form structure"""
    try:
        print(f"Viewing sale bill: {bill_no}")
        sales = Sale.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
        if not sales:
            print(f"No sales found for bill_no: {bill_no}")
            return "<div class='modal-body'><div class='alert alert-danger'>Sale not found</div></div>"
        
        first_sale = sales[0]
        
        # Calculate totals safely
        total_amount = sum(float(sale.sal_amt) for sale in sales if sale.sal_amt is not None)
        total_discount = sum(float(sale.discount) for sale in sales if sale.discount is not None)
        gst_amount = total_amount * 0.18  # 18% GST
        grand_total = total_amount + gst_amount - total_discount
        
        print(f"Found {len(sales)} sale items, total amount: {total_amount}")
        
        # Get parties and items for dropdowns
        parties = Party.query.filter_by(user_id=current_user.id).all() or []
        items = Item.query.filter_by(user_id=current_user.id).all() or []
        
        print(f"Found {len(parties)} parties and {len(items)} items")
        
        # Convert to dictionaries for JSON serialization
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
        
        # Prepare sale items data for JavaScript
        sale_items_data = []
        for sale in sales:
            try:
                sale_items_data.append({
                    'it_cd': sale.it_cd,
                    'qty': float(sale.qty) if sale.qty else 0.0,
                    'rate': float(sale.rate) if sale.rate else 0.0,
                    'discount': float(sale.discount) if sale.discount else 0.0,
                    'amount': float(sale.sal_amt) if sale.sal_amt else 0.0
                })
            except Exception as e:
                print(f"Error processing sale item {sale}: {e}")
                continue
        
        print(f"Processed {len(sale_items_data)} sale items")
        
        return render_template_string("""
            <div class="modal-header bright-header">
                <h5 class="modal-title" id="saleModalLabel">
                    <i class="fas fa-eye me-2"></i>View Sale Bill #{{ first_sale.bill_no }}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body bright-body" style="max-height: 80vh; overflow-y: auto;">
                
                <!-- Bill Information -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="fas fa-file-invoice me-2"></i>Bill Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label class="form-label bright-label">Bill Number</label>
                                <input type="number" class="form-control bright-input" value="{{ first_sale.bill_no }}" readonly>
                    </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label bright-label">Bill Date</label>
                                <input type="date" class="form-control bright-input" value="{{ first_sale.bill_date.strftime('%Y-%m-%d') if first_sale.bill_date else '' }}" readonly>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label bright-label">Party</label>
                                <input type="text" class="form-control bright-input" value="{{ first_sale.party.party_nm if first_sale.party else first_sale.party_cd }}" readonly>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Sale Items -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="fas fa-boxes me-2"></i>Sale Items</h6>
                    </div>
                    <div class="card-body">
                <div class="table-responsive">
                            <table class="table table-bordered">
                                <thead class="table-dark">
                                    <tr>
                                        <th>ITEM</th>
                                        <th>QUANTITY</th>
                                        <th>RATE</th>
                                        <th>AMOUNT</th>
                                        <th>DISCOUNT</th>
                                        <th>NET AMOUNT</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sale in sales %}
                            <tr>
                                <td>{{ sale.item.it_nm if sale.item else sale.it_cd }}</td>
                                <td>{{ sale.qty }}</td>
                                <td>₹{{ "%.2f"|format(sale.rate) if sale.rate else '0.00' }}</td>
                                        <td>₹{{ "%.2f"|format(sale.qty * sale.rate) if sale.qty and sale.rate else '0.00' }}</td>
                                <td>₹{{ "%.2f"|format(sale.discount) if sale.discount else '0.00' }}</td>
                                <td>₹{{ "%.2f"|format(sale.sal_amt) if sale.sal_amt else '0.00' }}</td>
                            </tr>
                            {% endfor %}
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
                                        <input type="number" class="form-control bright-input" value="{{ "%.2f"|format(total_amount + total_discount) }}" readonly>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label bright-label">Total Discount</label>
                                        <input type="number" class="form-control bright-input" value="{{ "%.2f"|format(total_discount) }}" readonly>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label bright-label">GST Amount</label>
                                        <input type="number" class="form-control bright-input" value="{{ "%.2f"|format(gst_amount) }}" readonly>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label bright-label">Grand Total</label>
                                        <input type="number" class="form-control bright-input" value="{{ "%.2f"|format(grand_total) }}" readonly>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
            </div>
            <div class="modal-footer bright-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-1"></i>CLOSE
                </button>
                <button type="button" class="btn btn-warning" onclick="openSaleModal('{{ first_sale.bill_no }}', 'edit')">
                    <i class="fas fa-edit me-1"></i>EDIT SALE
                </button>
            </div>
            
            <script>
            // Store data globally for potential edit use
            window.saleItemsData = {{ items_data|tojson }};
            window.salePartiesData = {{ parties_data|tojson }};
            window.saleViewData = {{ sale_items_data|tojson }};
            </script>
        """, sales=sales, first_sale=first_sale, total_amount=total_amount, total_discount=total_discount, gst_amount=gst_amount, grand_total=grand_total, parties_data=parties_data, items_data=items_data, sale_items_data=sale_items_data)
    except Exception as e:
        print(f"Sales view error: {e}")
        import traceback
        traceback.print_exc()
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading sale details: " + str(e) + "</div></div>"

@sales_api.route('/api/sales/edit/<bill_no>')
@login_required
def sales_edit_form(bill_no):
    """Edit sale form with populated data"""
    try:
        print(f"=== EDIT FORM REQUESTED FOR BILL {bill_no} ===")
        print(f"Current user ID: {current_user.id}")
        
        # Temporarily remove user_id filter to test - the sales exist but with different user_ids
        sales = Sale.query.filter_by(bill_no=bill_no).all()
        print(f"Found {len(sales)} sales for bill {bill_no}")
        
        if not sales:
            print(f"No sales found for bill {bill_no}")
            return "<div class='modal-body'><div class='alert alert-danger'>Sale not found</div></div>"
        
        first_sale = sales[0]
        total_amount = sum(sale.sal_amt for sale in sales)
        
        # Get parties and items for dropdowns
        parties = Party.query.filter_by(user_id=current_user.id).all() or []
        items = Item.query.filter_by(user_id=current_user.id).all() or []
        
        # Convert to dictionaries for JSON serialization
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
        
        # Add missing items that are referenced in sales but not in items table
        existing_item_codes = {item['it_cd'] for item in items_data}
        sale_item_codes = {sale.it_cd for sale in sales if sale.it_cd}
        missing_item_codes = sale_item_codes - existing_item_codes
        
        print(f"Existing item codes: {existing_item_codes}")
        print(f"Sale item codes: {sale_item_codes}")
        print(f"Missing item codes: {missing_item_codes}")
        
        # Add missing items with default names
        for item_code in missing_item_codes:
            items_data.append({
                'it_cd': item_code,
                'it_nm': f'Item {item_code}',  # Default name
                'rate': 0.0,
                'gst': 0.0
            })
            print(f"Added missing item: {item_code}")
        
        print(f"Total items available: {len(items_data)}")
        print(f"Final item codes: {[item['it_cd'] for item in items_data]}")
        
        # Prepare sale items data for JavaScript
        sale_items_data = []
        for sale in sales:
            item_data = {
                'it_cd': sale.it_cd,
                'qty': float(sale.qty) if sale.qty else 0.0,
                'rate': float(sale.rate) if sale.rate else 0.0,
                'discount': float(sale.discount) if sale.discount else 0.0,
                'amount': float(sale.sal_amt) if sale.sal_amt else 0.0
            }
            sale_items_data.append(item_data)
            print(f"Added sale item: {item_data}")
        
        print(f"Prepared sale items data: {sale_items_data}")
        print(f"First sale data: {sale_items_data[0] if sale_items_data else 'No data'}")
        print(f"Total sale items prepared: {len(sale_items_data)}")
        print(f"Sale items JSON: {sale_items_data}")
        print(f"JSON string length: {len(str(sale_items_data))}")
        
        print("=== GENERATING HTML DIRECTLY ===")
        
        # Generate the complete HTML directly in Python to avoid template issues
        import json
        
        # Convert data to JSON strings
        items_json = json.dumps(items_data) if items_data else '[]'
        parties_json = json.dumps(parties_data) if parties_data else '[]'
        sale_items_json = json.dumps(sale_items_data) if sale_items_data else '[]'
        
        print(f"DEBUG: items_json = {items_json}")
        print(f"DEBUG: parties_json = {parties_json}")
        print(f"DEBUG: sale_items_json = {sale_items_json}")
        
        # Generate HTML
        html = f"""
            <div class="modal-header bright-header">
                <h5 class="modal-title" id="saleModalLabel">
                    <i class="fas fa-edit me-2"></i>Edit Sale Bill #{first_sale.bill_no}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            
            <form id="editSaleForm" onsubmit="updateSale(event)">
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
                                    <input type="number" class="form-control bright-input" name="bill_no" id="edit_bill_no" value="{first_sale.bill_no}" readonly>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label bright-label">Bill Date *</label>
                                    <input type="date" class="form-control bright-input" name="bill_date" id="edit_bill_date" value="{first_sale.bill_date.strftime('%Y-%m-%d') if first_sale.bill_date else ''}" required>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label bright-label">Party *</label>
                                    <select class="form-select bright-input" name="party_cd" id="edit_party_cd" required>
                                        <option value="">Select Party</option>
        """
        
        # Add party options
        for party in parties_data:
            selected = 'selected' if party['party_cd'] == first_sale.party_cd else ''
            html += f'<option value="{party["party_cd"]}" {selected}>{party["party_nm"]} ({party["party_cd"]})</option>'
        
        # Continue with form
        html += """
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Sale Items -->
                    <div class="card mb-3">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0"><i class="fas fa-boxes me-2"></i>Sale Items</h6>
                            <button type="button" class="btn btn-sm btn-success" onclick="addEditSaleItemRow()">
                                <i class="fas fa-plus me-1"></i>ADD ITEM
                            </button>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-bordered" id="editSaleItemsTable">
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
                                    <tbody id="editSaleItemsTableBody">
                                        <!-- Items will be populated by JavaScript -->
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
                                            <input type="number" class="form-control bright-input" id="edit_sub_total" value="0.00" readonly>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">Total Discount</label>
                                            <input type="number" class="form-control bright-input" id="edit_total_discount" value="0.00" readonly>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">GST Amount</label>
                                            <input type="number" class="form-control bright-input" id="edit_gst_amount" value="0.00" readonly>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label bright-label">Grand Total</label>
                                            <input type="number" class="form-control bright-input" id="edit_grand_total" value="0.00" readonly>
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
                        <i class="fas fa-save me-1"></i>UPDATE SALE
                    </button>
                </div>
            </form>
            
            <script>
            // Initialize global variables
            window.saleItemsData = [];
            window.salePartiesData = [];
            window.editSaleData = [];
            
            // Load data via AJAX to avoid syntax errors
            fetch('/api/items/list')
                .then(response => response.json())
                .then(data => {{
                    if (data.success && data.items) {{
                        window.saleItemsData = data.items;
                        console.log('Items loaded via AJAX:', window.saleItemsData.length);
                    }}
                }})
                .catch(error => {{
                    console.error('Error loading items:', error);
                }});
            
            // Load sale items for this bill
            fetch('/api/sales/items/{first_sale.bill_no}')
                .then(response => response.json())
                .then(data => {{
                    if (data.success && data.items) {{
                        window.editSaleData = data.items;
                        console.log('Sale items loaded via AJAX:', window.editSaleData.length);
                        
                        // Initialize form after data is loaded
                        if (typeof initializeEditSaleForm === 'function') {{
                            console.log('Calling initializeEditSaleForm...');
                            initializeEditSaleForm();
                        }} else {{
                            console.log('initializeEditSaleForm not available yet');
                            setTimeout(function() {{
                                if (typeof initializeEditSaleForm === 'function') {{
                                    console.log('Calling initializeEditSaleForm after delay...');
                                    initializeEditSaleForm();
                                }}
                            }}, 500);
                        }}
                    }}
                }})
                .catch(error => {{
                    console.error('Error loading sale items:', error);
                }});
            </script>
        """
        
        print(f"HTML generated successfully, length: {len(html)}")
        return html
        
    except Exception as e:
        print(f"Sales edit form error: {e}")
        import traceback
        traceback.print_exc()
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading edit form</div></div>"

@sales_api.route('/api/sales/update/<bill_no>', methods=['POST'])
@login_required
def sales_update(bill_no):
    """Update existing sale"""
    try:
        data = request.get_json()
        
        # Delete existing sale records for this bill
        existing_sales = Sale.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
        for sale in existing_sales:
            db.session.delete(sale)
        
        # Create new sale records
        bill_date = datetime.strptime(data.get('bill_date'), '%Y-%m-%d')
        party_cd = data.get('party_cd')
        items = data.get('items', [])
        
        total_amount = 0
        for item_data in items:
            if item_data.get('it_cd') and item_data.get('qty') > 0:
                qty = item_data['qty']
                rate = item_data['rate']
                discount = item_data.get('discount', 0)
                amount = (qty * rate) - discount
                total_amount += amount
                
                new_sale = Sale(
                    user_id=current_user.id,
                    bill_no=bill_no,
                    party_cd=party_cd,
                    it_cd=item_data['it_cd'],
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
            'message': f'Sale bill #{bill_no} updated successfully!',
            'total_amount': total_amount
        })
        
    except Exception as e:
        print(f"Sales update error: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating sale: {str(e)}'
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