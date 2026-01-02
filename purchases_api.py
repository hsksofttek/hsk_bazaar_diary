from flask import Blueprint, render_template, request, jsonify, render_template_string
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from database import db
from models import Purchase, Party, Item
from forms import PurchaseForm

purchases_api = Blueprint('purchases_api', __name__)

@purchases_api.route('/api/purchases/stats/total')
@login_required
def purchases_stats_total():
    """Get total purchases count"""
    try:
        count = Purchase.query.filter_by(user_id=current_user.id).count()
        return str(count)
    except Exception as e:
        print(f"Error getting total purchases: {e}")
        return "0"

@purchases_api.route('/api/purchases/stats/monthly')
@login_required
def purchases_stats_monthly():
    """Get monthly purchases count"""
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
        
        count = Purchase.query.filter(
            Purchase.user_id == current_user.id,
            Purchase.bill_date >= month_start.date(),
            Purchase.bill_date <= month_end.date()
        ).count()
        
        return str(count)
    except Exception as e:
        print(f"Error getting monthly purchases: {e}")
        return "0"

@purchases_api.route('/api/purchases/stats/today')
@login_required
def purchases_stats_today():
    """Get today's purchases count"""
    try:
        from datetime import datetime
        from sqlalchemy import func
        
        today = datetime.now().date()
        count = Purchase.query.filter(
            Purchase.user_id == current_user.id,
            Purchase.bill_date == today
        ).count()
        
        return str(count)
    except Exception as e:
        print(f"Error getting today's purchases: {e}")
        return "0"

@purchases_api.route('/api/purchases/table')
@login_required
def purchases_table():
    """Get purchases table HTML"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        date_filter = request.args.get('date', '')
        supplier = request.args.get('supplier', '')
        amount = request.args.get('amount', '')
        
        # Build query
        query = Purchase.query.filter_by(user_id=current_user.id)
        
        # Apply search filter
        if search:
            query = query.join(Party).join(Item).filter(
                or_(
                    Purchase.bill_no.like(f'%{search}%'),
                    Party.party_nm.ilike(f'%{search}%'),
                    Item.it_nm.ilike(f'%{search}%')
                )
            )
        
        # Apply date filter
        if date_filter:
            today = datetime.now().date()
            if date_filter == 'today':
                query = query.filter(func.date(Purchase.bill_date) == today)
            elif date_filter == 'week':
                week_ago = today - timedelta(days=7)
                query = query.filter(func.date(Purchase.bill_date) >= week_ago)
            elif date_filter == 'month':
                month_ago = today - timedelta(days=30)
                query = query.filter(func.date(Purchase.bill_date) >= month_ago)
            elif date_filter == 'quarter':
                quarter_ago = today - timedelta(days=90)
                query = query.filter(func.date(Purchase.bill_date) >= quarter_ago)
        
        # Apply supplier filter
        if supplier:
            query = query.join(Party).filter(Party.party_cd == supplier)
        
        # Apply amount filter
        if amount:
            if amount == '0-1000':
                query = query.filter(and_(Purchase.sal_amt >= 0, Purchase.sal_amt <= 1000))
            elif amount == '1000-5000':
                query = query.filter(and_(Purchase.sal_amt > 1000, Purchase.sal_amt <= 5000))
            elif amount == '5000-10000':
                query = query.filter(and_(Purchase.sal_amt > 5000, Purchase.sal_amt <= 10000))
            elif amount == '10000+':
                query = query.filter(Purchase.sal_amt > 10000)
        
        # Group by bill number to get unique bills
        query = query.group_by(Purchase.bill_no).order_by(desc(Purchase.bill_date))
        
        # Get unique bills
        bills = query.all()
        
        if not bills:
            return '''
            <tr>
                <td colspan="6" class="text-center py-4">
                    <div class="text-muted">
                        <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                        <h5>No purchases found</h5>
                        <p>Try adjusting your search criteria or create a new purchase.</p>
                    </div>
                </td>
            </tr>
            '''
        
        rows = []
        for bill_no in [bill.bill_no for bill in bills]:
            # Get all items for this bill
            bill_items = Purchase.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
            if not bill_items:
                continue
            
            # Get bill details from first item
            first_item = bill_items[0]
            total_amount = sum(item.sal_amt for item in bill_items)
            item_count = len(bill_items)
            
            row = f'''
            <tr>
                <td>
                    <span class="bill-badge">{bill_no}</span>
                </td>
                <td>{first_item.bill_date.strftime('%d/%m/%Y') if first_item.bill_date else 'N/A'}</td>
                <td>
                    <strong>{first_item.party.party_nm if first_item.party else first_item.party_cd}</strong>
                    <br><small class="text-muted">{first_item.party_cd}</small>
                </td>
                <td>
                    <span class="badge bg-info">{item_count} item(s)</span>
                    <br><small class="text-muted">
                        {', '.join([item.item.it_nm if item.item else item.it_cd for item in bill_items[:3]])}
                        {f' +{item_count-3} more' if item_count > 3 else ''}
                    </small>
                </td>
                <td>
                    <span class="amount-badge">₹{total_amount:.2f}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-view" 
                                hx-get="/api/purchases/view/{bill_no}"
                                hx-target="#purchaseModal .modal-content"
                                hx-swap="innerHTML"
                                data-bs-toggle="modal"
                                data-bs-target="#purchaseModal"
                                title="View Purchase">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-action btn-edit" 
                                hx-get="/api/purchases/edit/{bill_no}"
                                hx-target="#purchaseModal .modal-content"
                                hx-swap="innerHTML"
                                data-bs-toggle="modal"
                                data-bs-target="#purchaseModal"
                                title="Edit Purchase">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-action btn-delete" 
                                onclick="deletePurchase('{bill_no}')"
                                title="Delete Purchase">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            '''
            rows.append(row)
        
        return '\n'.join(rows)
        
    except Exception as e:
        print(f"Purchases table error: {e}")
        return '''
        <tr>
            <td colspan="6" class="text-center py-4">
                <div class="text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Error loading purchases. Please try again.</p>
                </div>
            </td>
        </tr>
        '''

@purchases_api.route('/api/purchases/add-form')
@login_required
def purchases_add_form():
    """Get add purchase form with multiple items support"""
    try:
        # Get parties for dropdown
        parties = Party.query.filter_by(user_id=current_user.id).all()
        # Get items for dropdown
        items = Item.query.filter_by(user_id=current_user.id).all()
        
        # Generate next bill number
        last_purchase = Purchase.query.filter_by(user_id=current_user.id).order_by(desc(Purchase.bill_no)).first()
        bill_no = (last_purchase.bill_no + 1) if last_purchase else 1001
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title" id="purchaseModalLabel">
                    <i class="fas fa-shopping-cart me-2"></i>New Purchase Bill
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form hx-post="/api/purchases/add" hx-target="#purchaseModal .modal-content" hx-swap="innerHTML">
                <div class="modal-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="bill_no" class="form-label">Bill Number *</label>
                            <input type="number" class="form-control" id="bill_no" name="bill_no" value="{{ bill_no }}" required>
                        </div>
                        <div class="col-md-6">
                            <label for="bill_date" class="form-label">Bill Date *</label>
                            <input type="date" class="form-control" id="bill_date" name="bill_date" value="{{ today }}" required>
                        </div>
                        <div class="col-md-12">
                            <label for="party_cd" class="form-label">Supplier *</label>
                            <select class="form-select" id="party_cd" name="party_cd" required>
                                <option value="">Select Supplier</option>
                                {% for party in parties %}
                                <option value="{{ party.party_cd }}">{{ party.party_nm }} ({{ party.party_cd }})</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    
                    <hr class="my-4">
                    
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="mb-0"><i class="fas fa-list me-2"></i>Items</h6>
                        <button type="button" class="btn btn-sm btn-success" onclick="addItemRow()">
                            <i class="fas fa-plus me-1"></i>Add Item
                        </button>
                    </div>
                    
                    <div class="items-table">
                        <table class="table table-sm" id="itemsTable">
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th>Quantity</th>
                                    <th>Rate</th>
                                    <th>Discount</th>
                                    <th>Amount</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="itemsTableBody">
                                <!-- Items will be added here dynamically -->
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-6 offset-md-6">
                            <div class="d-flex justify-content-between">
                                <strong>Total Amount:</strong>
                                <strong id="totalAmount">₹0.00</strong>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-warning">
                        <i class="fas fa-save me-1"></i>Record Purchase
                    </button>
                </div>
            </form>
            
            <script>
            let itemCounter = 0;
            
            function addItemRow() {
                itemCounter++;
                const tbody = document.getElementById('itemsTableBody');
                const row = document.createElement('tr');
                row.id = 'item-row-' + itemCounter;
                
                row.innerHTML = `
                    <td>
                        <select class="form-select form-select-sm" name="items[${itemCounter}][it_cd]" required onchange="updateRate(${itemCounter})">
                            <option value="">Select Item</option>
                            {% for item in items %}
                            <option value="{{ item.it_cd }}" data-rate="{{ item.rate or 0 }}">{{ item.it_nm }} ({{ item.it_cd }})</option>
                            {% endfor %}
                        </select>
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" name="items[${itemCounter}][qty]" value="1" required onchange="calculateAmount(${itemCounter})">
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" name="items[${itemCounter}][rate]" value="0.00" required onchange="calculateAmount(${itemCounter})">
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" name="items[${itemCounter}][discount]" value="0.00" onchange="calculateAmount(${itemCounter})">
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" name="items[${itemCounter}][amount]" value="0.00" readonly>
                    </td>
                    <td>
                        <button type="button" class="remove-item-btn" onclick="removeItemRow(${itemCounter})">
                            <i class="fas fa-times"></i>
                        </button>
                    </td>
                `;
                
                tbody.appendChild(row);
            }
            
            function removeItemRow(counter) {
                const row = document.getElementById('item-row-' + counter);
                if (row) {
                    row.remove();
                    calculateTotal();
                }
            }
            
            function updateRate(counter) {
                const select = document.querySelector(`#item-row-${counter} select[name="items[${counter}][it_cd]"]`);
                const rateInput = document.querySelector(`#item-row-${counter} input[name="items[${counter}][rate]"]`);
                const selectedOption = select.options[select.selectedIndex];
                
                if (selectedOption && selectedOption.dataset.rate) {
                    rateInput.value = selectedOption.dataset.rate;
                    calculateAmount(counter);
                }
            }
            
            function calculateAmount(counter) {
                const qty = parseFloat(document.querySelector(`#item-row-${counter} input[name="items[${counter}][qty]"]`).value) || 0;
                const rate = parseFloat(document.querySelector(`#item-row-${counter} input[name="items[${counter}][rate]"]`).value) || 0;
                const discount = parseFloat(document.querySelector(`#item-row-${counter} input[name="items[${counter}][discount]"]`).value) || 0;
                
                const amount = (qty * rate) - discount;
                document.querySelector(`#item-row-${counter} input[name="items[${counter}][amount]"]`).value = amount.toFixed(2);
                
                calculateTotal();
            }
            
            function calculateTotal() {
                let total = 0;
                const amountInputs = document.querySelectorAll('input[name$="[amount]"]');
                
                amountInputs.forEach(input => {
                    total += parseFloat(input.value) || 0;
                });
                
                document.getElementById('totalAmount').textContent = '₹' + total.toFixed(2);
            }
            
            // Add first row on load
            document.addEventListener('DOMContentLoaded', function() {
                addItemRow();
            });
            </script>
        """, parties=parties, items=items, bill_no=bill_no, today=datetime.now().strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"Purchases add form error: {e}")
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading form</div></div>"

@purchases_api.route('/api/purchases/add', methods=['POST'])
@login_required
def purchases_add():
    """Add new purchase with multiple items"""
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
        
        # Create purchase records for each item
        total_amount = 0
        for counter, item_data in items_data.items():
            if item_data.get('it_cd') and item_data.get('qty') > 0:
                qty = item_data['qty']
                rate = item_data['rate']
                discount = item_data.get('discount', 0)
                amount = (qty * rate) - discount
                total_amount += amount
                
                new_purchase = Purchase(
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
                db.session.add(new_purchase)
        
        db.session.commit()
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title text-success">
                    <i class="fas fa-check-circle me-2"></i>Purchase Recorded Successfully
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Purchase Bill #{{ bill_no }} has been recorded successfully!
                </div>
                <p class="text-muted">Total Amount: ₹{{ "%.2f"|format(total_amount) }}</p>
                <p class="text-muted">Items: {{ item_count }} item(s)</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="location.reload()">Close</button>
            </div>
        """, bill_no=bill_no, total_amount=total_amount, item_count=len(items_data))
    except Exception as e:
        print(f"Purchases add error: {e}")
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
                    Error recording purchase: {{ error }}
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        """, error=str(e))

@purchases_api.route('/api/purchases/view/<bill_no>')
@login_required
def purchases_view(bill_no):
    """View purchase details"""
    try:
        purchases = Purchase.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
        if not purchases:
            return "<div class='modal-body'><div class='alert alert-danger'>Purchase not found</div></div>"
        
        first_purchase = purchases[0]
        total_amount = sum(purchase.sal_amt for purchase in purchases)
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fas fa-eye me-2"></i>Purchase Details
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row g-3 mb-4">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Bill Number</label>
                        <p class="form-control-plaintext">{{ first_purchase.bill_no }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Bill Date</label>
                        <p class="form-control-plaintext">{{ first_purchase.bill_date.strftime('%d/%m/%Y') if first_purchase.bill_date else 'N/A' }}</p>
                    </div>
                    <div class="col-md-12">
                        <label class="form-label fw-bold">Supplier</label>
                        <p class="form-control-plaintext">{{ first_purchase.party.party_nm if first_purchase.party else first_purchase.party_cd }}</p>
                    </div>
                </div>
                
                <h6 class="mb-3"><i class="fas fa-list me-2"></i>Items</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Quantity</th>
                                <th>Rate</th>
                                <th>Discount</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for purchase in purchases %}
                            <tr>
                                <td>{{ purchase.item.it_nm if purchase.item else purchase.it_cd }}</td>
                                <td>{{ purchase.qty }}</td>
                                <td>₹{{ "%.2f"|format(purchase.rate) if purchase.rate else '0.00' }}</td>
                                <td>₹{{ "%.2f"|format(purchase.discount) if purchase.discount else '0.00' }}</td>
                                <td>₹{{ "%.2f"|format(purchase.sal_amt) if purchase.sal_amt else '0.00' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                        <tfoot>
                            <tr class="table-info">
                                <th colspan="4" class="text-end">Total Amount:</th>
                                <th>₹{{ "%.2f"|format(total_amount) }}</th>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-warning"
                        hx-get="/api/purchases/edit/{{ first_purchase.bill_no }}"
                        hx-target="#purchaseModal .modal-content"
                        hx-swap="innerHTML">
                    <i class="fas fa-edit me-1"></i>Edit Purchase
                </button>
            </div>
        """, purchases=purchases, first_purchase=first_purchase, total_amount=total_amount)
    except Exception as e:
        print(f"Purchases view error: {e}")
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading purchase details</div></div>"

@purchases_api.route('/api/purchases/delete/<bill_no>', methods=['DELETE'])
@login_required
def purchases_delete(bill_no):
    """Delete purchase"""
    try:
        purchases = Purchase.query.filter_by(user_id=current_user.id, bill_no=bill_no).all()
        if not purchases:
            return jsonify({'success': False, 'message': 'Purchase not found'}), 404
        
        for purchase in purchases:
            db.session.delete(purchase)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Purchase deleted successfully'})
    except Exception as e:
        print(f"Purchases delete error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500 