from flask import Blueprint, render_template, request, jsonify, render_template_string, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc
from datetime import datetime
from database import db
from models import Item, Party, Sale, Purchase
from forms import ItemForm

items_api = Blueprint('items_api', __name__)

@items_api.route('/api/items/test')
@login_required
def items_test():
    """Test endpoint to check if items API is working"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        # Test Item model
        item_count = Item.query.count()
        
        # Test user-specific items
        user_items = Item.query.filter_by(user_id=current_user.id).count()
        
        return jsonify({
            'success': True,
            'message': 'Items API is working',
            'total_items': item_count,
            'user_items': user_items,
            'user_id': current_user.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'user_id': current_user.id if current_user else 'No user'
        })

@items_api.route('/api/items/table')
@login_required
def items_table():
    """Get items table HTML"""
    try:
        print(f"Items table requested for user: {current_user.id}")
        
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        stock = request.args.get('stock', '')
        price = request.args.get('price', '')
        sort = request.args.get('sort', 'name')
        
        # Build query
        query = Item.query.filter_by(user_id=current_user.id)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Item.it_nm.ilike(f'%{search}%'),
                    Item.it_cd.ilike(f'%{search}%'),
                    Item.category.ilike(f'%{search}%')
                )
            )
        
        # Apply category filter
        if category:
            query = query.filter(Item.category == category)
        
        # Apply stock filter
        if stock == 'in_stock':
            query = query.filter(Item.closing_stock > 10)
        elif stock == 'low_stock':
            query = query.filter(and_(Item.closing_stock > 0, Item.closing_stock <= 10))
        elif stock == 'out_of_stock':
            query = query.filter(or_(Item.closing_stock == 0, Item.closing_stock.is_(None)))
        
        # Apply price filter
        if price:
            if price == '0-100':
                query = query.filter(and_(Item.rate >= 0, Item.rate <= 100))
            elif price == '100-500':
                query = query.filter(and_(Item.rate > 100, Item.rate <= 500))
            elif price == '500-1000':
                query = query.filter(and_(Item.rate > 500, Item.rate <= 1000))
            elif price == '1000+':
                query = query.filter(Item.rate > 1000)
        
        # Apply sorting
        if sort == 'name':
            query = query.order_by(Item.it_nm)
        elif sort == 'code':
            query = query.order_by(Item.it_cd)
        elif sort == 'category':
            query = query.order_by(Item.category)
        elif sort == 'rate':
            query = query.order_by(Item.rate)
        elif sort == 'stock':
            query = query.order_by(Item.closing_stock)
        else:
            query = query.order_by(Item.it_cd)
        
        # Get all items for this user (no pagination for now)
        items = query.all()
        print(f"Items after filters: {len(items)}")
        
        if not items:
            print("No items found - creating sample items")
            # Create some sample items for the user
            sample_items = [
                Item(
                    it_cd='I00001',
                    it_nm='Rice Premium',
                    category='Grains',
                    rate=45.00,
                    unit='Kg',
                    gst=5.0,
                    closing_stock=100,
                    user_id=current_user.id
                ),
                Item(
                    it_cd='I00002',
                    it_nm='Wheat Flour',
                    category='Grains',
                    rate=35.00,
                    unit='Kg',
                    gst=5.0,
                    closing_stock=75,
                    user_id=current_user.id
                ),
                Item(
                    it_cd='I00003',
                    it_nm='Sugar',
                    category='Essentials',
                    rate=42.00,
                    unit='Kg',
                    gst=5.0,
                    closing_stock=50,
                    user_id=current_user.id
                ),
                Item(
                    it_cd='I00004',
                    it_nm='Cooking Oil',
                    category='Oils',
                    rate=120.00,
                    unit='Litre',
                    gst=5.0,
                    closing_stock=25,
                    user_id=current_user.id
                ),
                Item(
                    it_cd='I00005',
                    it_nm='Tea Leaves',
                    category='Beverages',
                    rate=180.00,
                    unit='Kg',
                    gst=5.0,
                    closing_stock=30,
                    user_id=current_user.id
                )
            ]
            
            for item in sample_items:
                db.session.add(item)
            
            try:
                db.session.commit()
                print(f"Created {len(sample_items)} sample items")
                # Re-query items
                items = Item.query.filter_by(user_id=current_user.id).order_by(Item.it_cd).all()
            except Exception as e:
                print(f"Error creating sample items: {e}")
                db.session.rollback()
                return '''
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>Code</th>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>GST</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="7" class="text-center py-4">
                                    <div class="text-danger">
                                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                                        <p>Error loading items. Please try again.</p>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                '''
        
        if not items:
            return '''
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th>Code</th>
                            <th>Name</th>
                            <th>Category</th>
                            <th>Price</th>
                            <th>Stock</th>
                            <th>GST</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="7" class="text-center py-4">
                                <div class="text-muted">
                                    <i class="fas fa-box-open fa-3x mb-3"></i>
                                    <h5>No items found</h5>
                                    <p>Try adjusting your search criteria or add a new item.</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            '''
        
        # Build complete table HTML
        table_html = f'''
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-dark">
                    <tr>
                        <th>Code</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>GST</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        for item in items:
            # Determine stock badge class
            stock_class = 'success'
            if not item.closing_stock or item.closing_stock == 0:
                stock_class = 'danger'
            elif item.closing_stock <= 10:
                stock_class = 'warning'
            
            table_html += f'''
                    <tr>
                        <td>
                            <span class="item-code-badge">{item.it_cd}</span>
                        </td>
                        <td>
                            <div>
                                <strong>{item.it_nm}</strong>
                                {f'<br><small class="text-muted">Unit: {item.unit}</small>' if item.unit else ''}
                            </div>
                        </td>
                        <td>{item.category or 'N/A'}</td>
                        <td>₹{f'{item.rate:.2f}' if item.rate else '0.00'}</td>
                        <td>
                            <span class="stock-badge {stock_class}">
                                {item.closing_stock or 0}
                            </span>
                        </td>
                        <td>{f'{item.gst:.1f}' if item.gst else '0.0'}%</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-action btn-view" 
                                        data-item-code="{item.it_cd}"
                                        title="View Item">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn-action btn-edit" 
                                        data-item-code="{item.it_cd}"
                                        title="Edit Item">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn-action btn-delete" 
                                        onclick="deleteItem('{item.it_cd}')"
                                        title="Delete Item">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
            '''
        
        table_html += '''
                </tbody>
            </table>
        </div>
        '''
        
        return table_html
        
    except Exception as e:
        print(f"Items table error: {e}")
        return '''
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-dark">
                    <tr>
                        <th>Code</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>GST</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="7" class="text-center py-4">
                            <div class="text-danger">
                                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                                <p>Error loading items. Please try again.</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        '''

@items_api.route('/api/items/add-form')
@login_required
def items_add_form():
    """Get add item form"""
    try:
        # Generate next item code
        last_item = Item.query.filter_by(user_id=current_user.id).order_by(desc(Item.it_cd)).first()
        if last_item and last_item.it_cd:
            try:
                last_num = int(last_item.it_cd[1:])  # Remove 'I' prefix and convert to int
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
        
        next_item_code = f"I{next_num:05d}"
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title" id="itemModalLabel">
                    <i class="fas fa-box me-2"></i>Add New Item
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form hx-post="/api/items/add" hx-target="#itemModal .modal-content" hx-swap="innerHTML">
                <div class="modal-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="it_cd" class="form-label">Item Code *</label>
                            <input type="text" class="form-control" id="it_cd" name="it_cd" value="{{ next_code }}" required>
                        </div>
                        <div class="col-md-6">
                            <label for="it_nm" class="form-label">Item Name *</label>
                            <input type="text" class="form-control" id="it_nm" name="it_nm" required>
                        </div>
                        <div class="col-md-6">
                            <label for="category" class="form-label">Category</label>
                            <input type="text" class="form-control" id="category" name="category">
                        </div>
                        <div class="col-md-6">
                            <label for="unit" class="form-label">Unit</label>
                            <input type="text" class="form-control" id="unit" name="unit" value="PCS">
                        </div>
                        <div class="col-md-6">
                            <label for="rate" class="form-label">Rate</label>
                            <input type="number" step="0.01" class="form-control" id="rate" name="rate" value="0.00">
                        </div>
                        <div class="col-md-6">
                            <label for="gst" class="form-label">GST %</label>
                            <input type="number" step="0.1" class="form-control" id="gst" name="gst" value="18.0">
                        </div>
                        <div class="col-md-6">
                            <label for="opening_stock" class="form-label">Opening Stock</label>
                            <input type="number" step="0.01" class="form-control" id="opening_stock" name="opening_stock" value="0.00">
                        </div>
                        <div class="col-md-6">
                            <label for="closing_stock" class="form-label">Current Stock</label>
                            <input type="number" step="0.01" class="form-control" id="closing_stock" name="closing_stock" value="0.00">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-save me-1"></i>Save Item
                    </button>
                </div>
            </form>
        """, next_code=next_item_code)
    except Exception as e:
        print(f"Items add form error: {e}")
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading form</div></div>"

@items_api.route('/api/items/add', methods=['POST'])
@login_required
def items_add():
    """Add new item"""
    try:
        data = request.form
        new_item = Item(
            user_id=current_user.id,
            it_cd=data.get('it_cd'),
            it_nm=data.get('it_nm'),
            category=data.get('category', ''),
            unit=data.get('unit', 'PCS'),
            rate=float(data.get('rate', 0)),
            gst=float(data.get('gst', 18.0)),
            opening_stock=float(data.get('opening_stock', 0)),
            closing_stock=float(data.get('closing_stock', 0))
        )
        db.session.add(new_item)
        db.session.commit()
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title text-success">
                    <i class="fas fa-check-circle me-2"></i>Item Added Successfully
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Item "{{ item_name }}" has been added successfully!
                </div>
                <p class="text-muted">The item is now available for use in sales and purchases.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="location.reload()">Close</button>
            </div>
        """, item_name=data.get('it_nm'))
    except Exception as e:
        print(f"Items add error: {e}")
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
                    Error adding item: {{ error }}
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        """, error=str(e))

@items_api.route('/api/items/view/<item_code>')
@login_required
def items_view(item_code):
    """View item details"""
    try:
        item = Item.query.filter_by(user_id=current_user.id, it_cd=item_code).first()
        if not item:
            return "<div class='modal-body'><div class='alert alert-danger'>Item not found</div></div>"
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fas fa-eye me-2"></i>Item Details
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Item Code</label>
                        <p class="form-control-plaintext">{{ item.it_cd }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Item Name</label>
                        <p class="form-control-plaintext">{{ item.it_nm }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Category</label>
                        <p class="form-control-plaintext">{{ item.category or 'N/A' }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Unit</label>
                        <p class="form-control-plaintext">{{ item.unit or 'N/A' }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Rate</label>
                        <p class="form-control-plaintext">₹{{ "%.2f"|format(item.rate) if item.rate else '0.00' }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">GST %</label>
                        <p class="form-control-plaintext">{{ "%.1f"|format(item.gst) if item.gst else '0.0' }}%</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Opening Stock</label>
                        <p class="form-control-plaintext">{{ "%.2f"|format(item.opening_stock) if item.opening_stock else '0.00' }}</p>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Current Stock</label>
                        <p class="form-control-plaintext">{{ "%.2f"|format(item.closing_stock) if item.closing_stock else '0.00' }}</p>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-warning" onclick="loadEditForm('{{ item.it_cd }}')">
                    <i class="fas fa-edit me-1"></i>Edit Item
                </button>
            </div>
        """, item=item)
    except Exception as e:
        print(f"Items view error: {e}")
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading item details</div></div>"

@items_api.route('/api/items/edit/<item_code>')
@login_required
def items_edit_form(item_code):
    """Get edit item form"""
    try:
        item = Item.query.filter_by(user_id=current_user.id, it_cd=item_code).first()
        if not item:
            return "<div class='modal-body'><div class='alert alert-danger'>Item not found</div></div>"
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title" id="itemModalLabel">
                    <i class="fas fa-edit me-2"></i>Edit Item
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form hx-post="/api/items/update/{{ item.it_cd }}" hx-target="#itemModal .modal-content" hx-swap="innerHTML">
                <div class="modal-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="it_cd" class="form-label">Item Code *</label>
                            <input type="text" class="form-control" id="it_cd" name="it_cd" value="{{ item.it_cd }}" readonly>
                        </div>
                        <div class="col-md-6">
                            <label for="it_nm" class="form-label">Item Name *</label>
                            <input type="text" class="form-control" id="it_nm" name="it_nm" value="{{ item.it_nm }}" required>
                        </div>
                        <div class="col-md-6">
                            <label for="category" class="form-label">Category</label>
                            <input type="text" class="form-control" id="category" name="category" value="{{ item.category or '' }}">
                        </div>
                        <div class="col-md-6">
                            <label for="unit" class="form-label">Unit</label>
                            <input type="text" class="form-control" id="unit" name="unit" value="{{ item.unit or 'PCS' }}">
                        </div>
                        <div class="col-md-6">
                            <label for="rate" class="form-label">Rate</label>
                            <input type="number" step="0.01" class="form-control" id="rate" name="rate" value="{{ "%.2f"|format(item.rate) if item.rate else '0.00' }}">
                        </div>
                        <div class="col-md-6">
                            <label for="gst" class="form-label">GST %</label>
                            <input type="number" step="0.1" class="form-control" id="gst" name="gst" value="{{ "%.1f"|format(item.gst) if item.gst else '18.0' }}">
                        </div>
                        <div class="col-md-6">
                            <label for="opening_stock" class="form-label">Opening Stock</label>
                            <input type="number" step="0.01" class="form-control" id="opening_stock" name="opening_stock" value="{{ "%.2f"|format(item.opening_stock) if item.opening_stock else '0.00' }}">
                        </div>
                        <div class="col-md-6">
                            <label for="closing_stock" class="form-label">Current Stock</label>
                            <input type="number" step="0.01" class="form-control" id="closing_stock" name="closing_stock" value="{{ "%.2f"|format(item.closing_stock) if item.closing_stock else '0.00' }}">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-warning">
                        <i class="fas fa-save me-1"></i>Update Item
                    </button>
                </div>
            </form>
        """, item=item)
    except Exception as e:
        print(f"Items edit form error: {e}")
        return "<div class='modal-body'><div class='alert alert-danger'>Error loading form</div></div>"

@items_api.route('/api/items/update/<item_code>', methods=['POST'])
@login_required
def items_update(item_code):
    """Update item"""
    try:
        item = Item.query.filter_by(user_id=current_user.id, it_cd=item_code).first()
        if not item:
            return render_template_string("""
                <div class="modal-body">
                    <div class="alert alert-danger">Item not found</div>
                </div>
            """)
        
        data = request.form
        item.it_nm = data.get('it_nm')
        item.category = data.get('category', '')
        item.unit = data.get('unit', 'PCS')
        item.rate = float(data.get('rate', 0))
        item.gst = float(data.get('gst', 18.0))
        item.opening_stock = float(data.get('opening_stock', 0))
        item.closing_stock = float(data.get('closing_stock', 0))
        
        db.session.commit()
        
        return render_template_string("""
            <div class="modal-header">
                <h5 class="modal-title text-success">
                    <i class="fas fa-check-circle me-2"></i>Item Updated Successfully
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Item "{{ item_name }}" has been updated successfully!
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="location.reload()">Close</button>
            </div>
        """, item_name=item.it_nm)
    except Exception as e:
        print(f"Items update error: {e}")
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
                    Error updating item: {{ error }}
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        """, error=str(e))

@items_api.route('/api/items/delete/<item_code>', methods=['DELETE'])
@login_required
def items_delete(item_code):
    """Delete item"""
    try:
        item = Item.query.filter_by(user_id=current_user.id, it_cd=item_code).first()
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        
        # Check if item is used in purchases or sales
        purchase_count = Purchase.query.filter_by(user_id=current_user.id, it_cd=item_code).count()
        sale_count = Sale.query.filter_by(user_id=current_user.id, it_cd=item_code).count()
        
        if purchase_count > 0 or sale_count > 0:
            return jsonify({
                'success': False, 
                'message': f'Cannot delete item. It is used in {purchase_count} purchases and {sale_count} sales.'
            }), 400
        
        # Delete the item
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    except Exception as e:
        print(f"Items delete error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting item: {str(e)}'}), 500

@items_api.route('/api/items/export')
@login_required
def items_export():
    """Export items to CSV"""
    try:
        import csv
        import io
        from flask import make_response
        
        # Get filter parameters
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        stock = request.args.get('stock', '')
        price = request.args.get('price', '')
        sort = request.args.get('sort', 'name')
        
        # Build query (same as items_table)
        query = Item.query.filter_by(user_id=current_user.id)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Item.it_nm.ilike(f'%{search}%'),
                    Item.it_cd.ilike(f'%{search}%'),
                    Item.category.ilike(f'%{search}%')
                )
            )
        
        # Apply category filter
        if category:
            query = query.filter(Item.category == category)
        
        # Apply stock filter
        if stock == 'in_stock':
            query = query.filter(Item.closing_stock > 10)
        elif stock == 'low_stock':
            query = query.filter(and_(Item.closing_stock > 0, Item.closing_stock <= 10))
        elif stock == 'out_of_stock':
            query = query.filter(or_(Item.closing_stock == 0, Item.closing_stock.is_(None)))
        
        # Apply price filter
        if price:
            if price == '0-100':
                query = query.filter(and_(Item.rate >= 0, Item.rate <= 100))
            elif price == '100-500':
                query = query.filter(and_(Item.rate > 100, Item.rate <= 500))
            elif price == '500-1000':
                query = query.filter(and_(Item.rate > 500, Item.rate <= 1000))
            elif price == '1000+':
                query = query.filter(Item.rate > 1000)
        
        # Apply sorting
        if sort == 'name':
            query = query.order_by(Item.it_nm)
        elif sort == 'code':
            query = query.order_by(Item.it_cd)
        elif sort == 'category':
            query = query.order_by(Item.category)
        elif sort == 'rate':
            query = query.order_by(Item.rate)
        elif sort == 'stock':
            query = query.order_by(Item.closing_stock)
        else:
            query = query.order_by(Item.it_nm)
        
        items = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Item Code', 'Item Name', 'Category', 'Unit', 'Rate', 
            'GST %', 'Opening Stock', 'Current Stock', 'Created Date'
        ])
        
        # Write data
        for item in items:
            writer.writerow([
                item.it_cd or '',
                item.it_nm or '',
                item.category or '',
                item.unit or '',
                f"{item.rate:.2f}" if item.rate else '0.00',
                f"{item.gst:.1f}" if item.gst else '0.0',
                f"{item.opening_stock:.2f}" if item.opening_stock else '0.00',
                f"{item.closing_stock:.2f}" if item.closing_stock else '0.00',
                item.created_date.strftime('%Y-%m-%d') if item.created_date else ''
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=items_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Items export error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@items_api.route('/api/items/stats/test')
@login_required
def items_stats_test():
    """Test stats endpoint"""
    try:
        total = Item.query.filter_by(user_id=current_user.id).count()
        instock = Item.query.filter(
            and_(
                Item.user_id == current_user.id,
                Item.closing_stock > 10
            )
        ).count()
        lowstock = Item.query.filter(
            and_(
                Item.user_id == current_user.id,
                or_(
                    Item.closing_stock == 0,
                    Item.closing_stock.is_(None),
                    and_(Item.closing_stock > 0, Item.closing_stock <= 10)
                )
            )
        ).count()
        
        return jsonify({
            'success': True,
            'total': total,
            'instock': instock,
            'lowstock': lowstock,
            'user_id': current_user.id
        })
    except Exception as e:
        print(f"Stats test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'user_id': current_user.id if current_user else 'No user'
        })

@items_api.route('/api/items/stats/total')
@login_required
def items_stats_total():
    """Get total items count"""
    try:
        count = Item.query.filter_by(user_id=current_user.id).count()
        return str(count)
    except Exception as e:
        print(f"Error getting total items: {e}")
        return "0"

@items_api.route('/api/items/stats/instock')
@login_required
def items_stats_instock():
    """Get in-stock items count"""
    try:
        count = Item.query.filter(
            and_(
                Item.user_id == current_user.id,
                Item.closing_stock > 10
            )
        ).count()
        return str(count)
    except Exception as e:
        print(f"Error getting in-stock items: {e}")
        return "0"

@items_api.route('/api/items/stats/lowstock')
@login_required
def items_stats_lowstock():
    """Get low-stock items count"""
    try:
        count = Item.query.filter(
            and_(
                Item.user_id == current_user.id,
                or_(
                    Item.closing_stock == 0,
                    Item.closing_stock.is_(None),
                    and_(Item.closing_stock > 0, Item.closing_stock <= 10)
                )
            )
        ).count()
        return str(count)
    except Exception as e:
        print(f"Error getting low stock items: {e}")
        return "0" 

@items_api.route('/api/items/list')
@login_required
def items_list():
    """Get list of items for dropdowns"""
    try:
        items = Item.query.filter_by(user_id=current_user.id).all()
        items_data = []
        for item in items:
            items_data.append({
                'it_cd': item.it_cd,
                'it_nm': item.it_nm,
                'rate': float(item.rate) if item.rate else 0.0,
                'gst': float(item.gst) if item.gst else 0.0
            })
        
        return jsonify({
            'success': True,
            'items': items_data
        })
    except Exception as e:
        print(f"Error getting items list: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'items': []
        }) 