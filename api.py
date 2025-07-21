"""
API blueprint for RESTful endpoints and AJAX operations
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Party, Item, Purchase, Sale, Cashbook, Bankbook, User
from forms import PartyForm, ItemForm, PurchaseForm, SaleForm, CashbookForm, BankbookForm
from datetime import datetime, date
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Helper function to serialize models
def serialize_party(party):
    return {
        'party_cd': party.party_cd,
        'party_nm': party.party_nm,
        'party_nm_hindi': party.party_nm_hindi,
        'place': party.place,
        'phone': party.phone,
        'bal_cd': party.bal_cd,
        'ly_baln': party.ly_baln,
        'ytd_dr': party.ytd_dr,
        'ytd_cr': party.ytd_cr,
        'address1': party.address1,
        'address2': party.address2,
        'address3': party.address3,
        'gstin': party.gstin,
        'pan': party.pan,
        'email': party.email,
        'mobile': party.mobile,
        'opening_bal': party.opening_bal,
        'closing_bal': party.closing_bal,
        'created_date': party.created_date.isoformat() if party.created_date else None,
        'modified_date': party.modified_date.isoformat() if party.modified_date else None
    }

def serialize_item(item):
    return {
        'it_cd': item.it_cd,
        'it_nm': item.it_nm,
        'unit': item.unit,
        'rate': item.rate,
        'category': item.category,
        'mrp': item.mrp,
        'sprc': item.sprc,
        'hsn': item.hsn,
        'gst': item.gst,
        'opening_stock': item.opening_stock,
        'closing_stock': item.closing_stock,
        'created_date': item.created_date.isoformat() if item.created_date else None,
        'modified_date': item.modified_date.isoformat() if item.modified_date else None
    }

def serialize_purchase(purchase):
    # Calculate sold bags from related sales
    sold_bags = 0
    if hasattr(purchase, 'sales'):
        sold_bags = sum(sale.qty for sale in purchase.sales)
    
    return {
        'id': purchase.id,
        'bill_no': purchase.bill_no,
        'bill_date': purchase.bill_date.isoformat() if purchase.bill_date else None,
        'party_cd': purchase.party_cd,
        'party_nm': purchase.party.party_nm if purchase.party else None,
        'it_cd': purchase.it_cd,
        'it_nm': purchase.item.it_nm if purchase.item else None,
        'qty': purchase.qty,
        'rate': purchase.rate,
        'sal_amt': purchase.sal_amt,
        'discount': purchase.discount,
        'tot_amt': purchase.tot_amt,
        'taxamt': purchase.taxamt,
        'sold_bags': sold_bags,
        'created_date': purchase.created_date.isoformat() if purchase.created_date else None
    }

def serialize_sale(sale):
    return {
        'id': sale.id,
        'bill_no': sale.bill_no,
        'bill_date': sale.bill_date.isoformat() if sale.bill_date else None,
        'party_cd': sale.party_cd,
        'party_nm': sale.party.party_nm if sale.party else None,
        'it_cd': sale.it_cd,
        'it_nm': sale.item.it_nm if sale.item else None,
        'qty': sale.qty,
        'rate': sale.rate,
        'sal_amt': sale.sal_amt,
        'discount': sale.discount,
        'tot_amt': sale.tot_amt,
        'taxamt': sale.taxamt,
        'created_date': sale.created_date.isoformat() if sale.created_date else None
    }

# Parties API
@api_bp.route('/parties', methods=['GET'])
@login_required
def get_parties():
    """Get all parties with pagination and search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Party.query
    if search:
        query = query.filter(Party.party_nm.contains(search) | Party.party_cd.contains(search))
    
    parties = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'parties': [serialize_party(party) for party in parties.items],
        'total': parties.total,
        'pages': parties.pages,
        'current_page': parties.page,
        'has_next': parties.has_next,
        'has_prev': parties.has_prev
    })

@api_bp.route('/parties/<party_cd>', methods=['GET'])
@login_required
def get_party(party_cd):
    """Get specific party by code"""
    party = Party.query.get_or_404(party_cd)
    return jsonify(serialize_party(party))

@api_bp.route('/parties', methods=['POST'])
@login_required
def create_party():
    """Create new party"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # Check if party code already exists
    if Party.query.filter_by(party_cd=data.get('party_cd')).first():
        return jsonify({'success': False, 'message': 'Party code already exists'}), 400
    
    try:
        party = Party(
            party_cd=data.get('party_cd'),
            party_nm=data.get('party_nm'),
            party_nm_hindi=data.get('party_nm_hindi'),
            place=data.get('place'),
            phone=data.get('phone'),
            bal_cd=data.get('bal_cd', 'D'),
            ly_baln=data.get('ly_baln', 0),
            ytd_dr=data.get('ytd_dr', 0),
            ytd_cr=data.get('ytd_cr', 0),
            address1=data.get('address1'),
            address2=data.get('address2'),
            address3=data.get('address3'),
            gstin=data.get('gstin'),
            pan=data.get('pan'),
            email=data.get('email'),
            mobile=data.get('mobile'),
            opening_bal=data.get('opening_bal', 0),
            closing_bal=data.get('closing_bal', 0)
        )
        
        db.session.add(party)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Party created successfully', 'party': serialize_party(party)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Party creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create party'}), 500

@api_bp.route('/parties/<party_cd>', methods=['PUT'])
@login_required
def update_party(party_cd):
    """Update party"""
    party = Party.query.get_or_404(party_cd)
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    try:
        # Update fields
        for field, value in data.items():
            if hasattr(party, field):
                setattr(party, field, value)
        
        party.modified_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Party updated successfully', 'party': serialize_party(party)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Party update error: {e}")
        return jsonify({'success': False, 'message': 'Failed to update party'}), 500

@api_bp.route('/parties/<party_cd>', methods=['DELETE'])
@login_required
def delete_party(party_cd):
    """Delete party"""
    party = Party.query.get_or_404(party_cd)
    
    try:
        db.session.delete(party)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Party deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Party deletion error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete party'}), 500

# Items API
@api_bp.route('/items', methods=['GET'])
@login_required
def get_items():
    """Get all items with pagination and search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Item.query
    if search:
        query = query.filter(Item.it_nm.contains(search) | Item.it_cd.contains(search))
    
    items = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_item(item) for item in items.items],
        'total': items.total,
        'pages': items.pages,
        'current_page': items.page,
        'has_next': items.has_next,
        'has_prev': items.has_prev
    })

@api_bp.route('/items/<it_cd>', methods=['GET'])
@login_required
def get_item(it_cd):
    """Get specific item by code"""
    item = Item.query.get_or_404(it_cd)
    return jsonify(serialize_item(item))

@api_bp.route('/items', methods=['POST'])
@login_required
def create_item():
    """Create new item"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # Check if item code already exists
    if Item.query.filter_by(it_cd=data.get('it_cd')).first():
        return jsonify({'success': False, 'message': 'Item code already exists'}), 400
    
    try:
        item = Item(
            it_cd=data.get('it_cd'),
            it_nm=data.get('it_nm'),
            unit=data.get('unit', 'KG'),
            rate=data.get('rate', 0),
            category=data.get('category'),
            mrp=data.get('mrp', 0),
            sprc=data.get('sprc', 0),
            hsn=data.get('hsn'),
            gst=data.get('gst', 0),
            opening_stock=data.get('opening_stock', 0),
            closing_stock=data.get('closing_stock', 0)
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item created successfully', 'item': serialize_item(item)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Item creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create item'}), 500

@api_bp.route('/items/<it_cd>', methods=['PUT'])
@login_required
def update_item(it_cd):
    """Update item"""
    item = Item.query.get_or_404(it_cd)
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    try:
        # Update fields
        for field, value in data.items():
            if hasattr(item, field):
                setattr(item, field, value)
        
        item.modified_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item updated successfully', 'item': serialize_item(item)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Item update error: {e}")
        return jsonify({'success': False, 'message': 'Failed to update item'}), 500

@api_bp.route('/items/<it_cd>', methods=['DELETE'])
@login_required
def delete_item(it_cd):
    """Delete item"""
    item = Item.query.get_or_404(it_cd)
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Item deletion error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete item'}), 500

# Purchases API
@api_bp.route('/purchases', methods=['GET'])
@login_required
def get_purchases():
    """Get all purchases with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    purchases = Purchase.query.order_by(Purchase.bill_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'purchases': [serialize_purchase(purchase) for purchase in purchases.items],
        'total': purchases.total,
        'pages': purchases.pages,
        'current_page': purchases.page,
        'has_next': purchases.has_next,
        'has_prev': purchases.has_prev
    })

@api_bp.route('/purchases/<int:purchase_id>', methods=['GET'])
@login_required
def get_purchase(purchase_id):
    """Get specific purchase by ID"""
    purchase = Purchase.query.get_or_404(purchase_id)
    return jsonify(serialize_purchase(purchase))

@api_bp.route('/purchases', methods=['POST'])
@login_required
def create_purchase():
    """Create new purchase with multiple items"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # Check if this is a multi-item purchase or single item
    if 'items' in data and isinstance(data['items'], list):
        # Multi-item purchase
        return create_multi_item_purchase(data)
    else:
        # Single item purchase (backward compatibility)
        return create_single_item_purchase(data)

def create_single_item_purchase(data):
    """Create single item purchase (legacy support)"""
    try:
        purchase = Purchase(
            bill_no=data.get('bill_no'),
            bill_date=datetime.strptime(data.get('bill_date'), '%Y-%m-%d').date() if data.get('bill_date') else date.today(),
            party_cd=data.get('party_cd'),
            it_cd=data.get('it_cd'),
            qty=data.get('qty', 0),
            rate=data.get('rate', 0),
            sal_amt=data.get('sal_amt', 0),
            discount=data.get('discount', 0),
            tot_amt=data.get('tot_amt', 0),
            taxamt=data.get('taxamt', 0)
        )
        
        db.session.add(purchase)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Purchase created successfully', 'purchase': serialize_purchase(purchase)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Purchase creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create purchase'}), 500

def create_multi_item_purchase(data):
    """Create multi-item purchase"""
    try:
        bill_no = data.get('bill_no')
        bill_date = datetime.strptime(data.get('bill_date'), '%Y-%m-%d').date() if data.get('bill_date') else date.today()
        party_cd = data.get('party_cd')
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'message': 'No items provided'}), 400
        
        # Check if bill number already exists
        existing_purchase = Purchase.query.filter_by(bill_no=bill_no).first()
        if existing_purchase:
            return jsonify({'success': False, 'message': 'Bill number already exists'}), 400
        
        purchases = []
        for item_data in items:
            purchase = Purchase(
                bill_no=bill_no,
                bill_date=bill_date,
                party_cd=party_cd,
                it_cd=item_data.get('it_cd'),
                qty=item_data.get('qty', 0),
                rate=item_data.get('rate', 0),
                sal_amt=item_data.get('qty', 0) * item_data.get('rate', 0),
                discount=item_data.get('discount', 0),
                tot_amt=(item_data.get('qty', 0) * item_data.get('rate', 0)) - item_data.get('discount', 0),
                taxamt=data.get('gst_amount', 0) / len(items) if data.get('gst_amount') else 0
            )
            purchases.append(purchase)
        
        # Add all purchases to session
        for purchase in purchases:
            db.session.add(purchase)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Purchase bill with {len(items)} items created successfully',
            'bill_no': bill_no,
            'items_count': len(items)
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Multi-item purchase creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create purchase bill'}), 500

# Sales API
@api_bp.route('/sales', methods=['GET'])
@login_required
def get_sales():
    """Get all sales with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    sales = Sale.query.order_by(Sale.bill_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'sales': [serialize_sale(sale) for sale in sales.items],
        'total': sales.total,
        'pages': sales.pages,
        'current_page': sales.page,
        'has_next': sales.has_next,
        'has_prev': sales.has_prev
    })

@api_bp.route('/sales/<int:sale_id>', methods=['GET'])
@login_required
def get_sale(sale_id):
    """Get specific sale by ID"""
    sale = Sale.query.get_or_404(sale_id)
    return jsonify(serialize_sale(sale))

@api_bp.route('/sales', methods=['POST'])
@login_required
def create_sale():
    """Create new sale with multiple items"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # Check if this is a multi-item sale or single item
    if 'items' in data and isinstance(data['items'], list):
        # Multi-item sale
        return create_multi_item_sale(data)
    else:
        # Single item sale (backward compatibility)
        return create_single_item_sale(data)

def create_single_item_sale(data):
    """Create single item sale (legacy support)"""
    try:
        sale = Sale(
            bill_no=data.get('bill_no'),
            bill_date=datetime.strptime(data.get('bill_date'), '%Y-%m-%d').date() if data.get('bill_date') else date.today(),
            party_cd=data.get('party_cd'),
            it_cd=data.get('it_cd'),
            qty=data.get('qty', 0),
            rate=data.get('rate', 0),
            sal_amt=data.get('sal_amt', 0),
            discount=data.get('discount', 0),
            tot_amt=data.get('tot_amt', 0),
            taxamt=data.get('taxamt', 0),
            purchase_id=data.get('purchase_id')  # Link to purchase
        )
        
        db.session.add(sale)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Sale created successfully', 'sale': serialize_sale(sale)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Sale creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create sale'}), 500

def create_multi_item_sale(data):
    """Create multi-item sale"""
    try:
        bill_no = data.get('bill_no')
        bill_date = datetime.strptime(data.get('bill_date'), '%Y-%m-%d').date() if data.get('bill_date') else date.today()
        party_cd = data.get('party_cd')
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'message': 'No items provided'}), 400
        
        # Check if bill number already exists
        existing_sale = Sale.query.filter_by(bill_no=bill_no).first()
        if existing_sale:
            return jsonify({'success': False, 'message': 'Bill number already exists'}), 400
        
        sales = []
        for item_data in items:
            sale = Sale(
                bill_no=bill_no,
                bill_date=bill_date,
                party_cd=party_cd,
                it_cd=item_data.get('it_cd'),
                qty=item_data.get('qty', 0),
                rate=item_data.get('rate', 0),
                sal_amt=item_data.get('qty', 0) * item_data.get('rate', 0),
                discount=item_data.get('discount', 0),
                tot_amt=(item_data.get('qty', 0) * item_data.get('rate', 0)) - item_data.get('discount', 0),
                taxamt=data.get('gst_amount', 0) / len(items) if data.get('gst_amount') else 0
            )
            sales.append(sale)
        
        # Add all sales to session
        for sale in sales:
            db.session.add(sale)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Sale bill with {len(items)} items created successfully',
            'bill_no': bill_no,
            'items_count': len(items)
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Multi-item sale creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create sale bill'}), 500

# Dashboard statistics API
@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_parties = Party.query.count()
        total_items = Item.query.count()
        total_purchases = Purchase.query.count()
        total_sales = Sale.query.count()
        
        # Recent transactions
        recent_purchases = Purchase.query.order_by(Purchase.created_date.desc()).limit(5).all()
        recent_sales = Sale.query.order_by(Sale.created_date.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_parties': total_parties,
                'total_items': total_items,
                'total_purchases': total_purchases,
                'total_sales': total_sales
            },
            'recent_purchases': [serialize_purchase(p) for p in recent_purchases],
            'recent_sales': [serialize_sale(s) for s in recent_sales]
        })
    
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'success': False, 'message': 'Failed to get dashboard statistics'}), 500

# Cashbook API
@api_bp.route('/cashbook', methods=['GET'])
@login_required
def get_cashbook():
    """Get all cashbook entries with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    cashbook_entries = Cashbook.query.order_by(Cashbook.transaction_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'cashbook_entries': [serialize_cashbook(entry) for entry in cashbook_entries.items],
        'total': cashbook_entries.total,
        'pages': cashbook_entries.pages,
        'current_page': cashbook_entries.page,
        'has_next': cashbook_entries.has_next,
        'has_prev': cashbook_entries.has_prev
    })

@api_bp.route('/cashbook/<int:entry_id>', methods=['GET'])
@login_required
def get_cashbook_entry(entry_id):
    """Get specific cashbook entry by ID"""
    entry = Cashbook.query.get_or_404(entry_id)
    return jsonify(serialize_cashbook(entry))

@api_bp.route('/cashbook', methods=['POST'])
@login_required
def create_cashbook_entry():
    """Create new cashbook entry"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    try:
        # Calculate running balance
        last_entry = Cashbook.query.order_by(Cashbook.id.desc()).first()
        current_balance = last_entry.balance if last_entry else 0
        
        # Calculate new balance
        amount = float(data.get('amount', 0))
        if data.get('transaction_type') == 'Receipt':
            new_balance = current_balance + amount
        else:
            new_balance = current_balance - amount
        
        entry = Cashbook(
            date=datetime.strptime(data.get('transaction_date'), '%Y-%m-%d').date() if data.get('transaction_date') else date.today(),
            voucher_type=data.get('transaction_type'),
            party_cd=data.get('party_code'),
            dr_amt=amount if data.get('transaction_type') == 'Payment' else 0,
            cr_amt=amount if data.get('transaction_type') == 'Receipt' else 0,
            balance=new_balance,
            narration=data.get('narration')
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cashbook entry created successfully', 'entry': serialize_cashbook(entry)})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cashbook creation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create cashbook entry'}), 500

@api_bp.route('/cashbook/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_cashbook_entry(entry_id):
    """Delete cashbook entry"""
    entry = Cashbook.query.get_or_404(entry_id)
    
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cashbook entry deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cashbook deletion error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete cashbook entry'}), 500

def serialize_cashbook(entry):
    """Serialize cashbook entry"""
    return {
        'id': entry.id,
        'transaction_date': entry.date.isoformat() if entry.date else None,
        'transaction_type': entry.voucher_type,
        'party_code': entry.party_cd,
        'party_nm': entry.party.party_nm if entry.party else None,
        'amount': entry.dr_amt + entry.cr_amt,
        'balance': entry.balance,
        'narration': entry.narration,
        'created_date': entry.created_date.isoformat() if entry.created_date else None
    }

# Ledger Report API
@api_bp.route('/ledger-report', methods=['POST'])
@login_required
def generate_ledger_report():
    """Generate ledger report for a party"""
    data = request.get_json()
    
    if not data or not data.get('party_code'):
        return jsonify({'success': False, 'message': 'Party code required'}), 400
    
    try:
        party_code = data.get('party_code')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        
        # Get party details
        party = Party.query.filter_by(party_cd=party_code).first()
        if not party:
            return jsonify({'success': False, 'message': 'Party not found'}), 404
        
        # Get transactions
        transactions = []
        
        # Get purchases (debit to party)
        purchases_query = Purchase.query.filter_by(party_cd=party_code)
        if from_date:
            purchases_query = purchases_query.filter(Purchase.bill_date >= from_date)
        if to_date:
            purchases_query = purchases_query.filter(Purchase.bill_date <= to_date)
        
        purchases = purchases_query.all()
        for purchase in purchases:
            transactions.append({
                'date': purchase.bill_date.strftime('%d/%m/%Y'),
                'particulars': f'Purchase Bill No. {purchase.bill_no}',
                'type': 'debit',
                'amount': purchase.tot_amt,
                'reference': f'PUR-{purchase.bill_no}'
            })
        
        # Get sales (credit to party)
        sales_query = Sale.query.filter_by(party_cd=party_code)
        if from_date:
            sales_query = sales_query.filter(Sale.bill_date >= from_date)
        if to_date:
            sales_query = sales_query.filter(Sale.bill_date <= to_date)
        
        sales = sales_query.all()
        for sale in sales:
            transactions.append({
                'date': sale.bill_date.strftime('%d/%m/%Y'),
                'particulars': f'Sale Bill No. {sale.bill_no}',
                'type': 'credit',
                'amount': sale.tot_amt,
                'reference': f'SAL-{sale.bill_no}'
            })
        
        # Get cashbook entries
        cashbook_query = Cashbook.query.filter_by(party_cd=party_code)
        if from_date:
            cashbook_query = cashbook_query.filter(Cashbook.date >= from_date)
        if to_date:
            cashbook_query = cashbook_query.filter(Cashbook.date <= to_date)
        
        cashbook_entries = cashbook_query.all()
        for entry in cashbook_entries:
            transactions.append({
                'date': entry.date.strftime('%d/%m/%Y'),
                'particulars': f'Cash {entry.voucher_type} - {entry.narration or "No narration"}',
                'type': 'debit' if entry.voucher_type == 'Payment' else 'credit',
                'amount': entry.dr_amt + entry.cr_amt,
                'reference': f'CB-{entry.id}'
            })
        
        # Sort transactions by date
        transactions.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y'))
        
        # Calculate summary
        total_debit = sum(t['amount'] for t in transactions if t['type'] == 'debit')
        total_credit = sum(t['amount'] for t in transactions if t['type'] == 'credit')
        
        # Calculate opening balance (simplified - you might want to implement proper opening balance logic)
        opening_balance = party.opening_bal or 0
        
        return jsonify({
            'success': True,
            'data': {
                'party': serialize_party(party),
                'transactions': transactions,
                'summary': {
                    'opening_balance': opening_balance,
                    'total_debit': total_debit,
                    'total_credit': total_credit
                },
                'from_date': from_date or 'All',
                'to_date': to_date or 'All'
            }
        })
    
    except Exception as e:
        logger.error(f"Ledger report error: {e}")
        return jsonify({'success': False, 'message': 'Failed to generate ledger report'}), 500

# Search API
@api_bp.route('/search', methods=['GET'])
@login_required
def search():
    """Search across parties and items"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'message': 'Search query required'}), 400
    
    try:
        parties = Party.query.filter(Party.party_nm.contains(query) | Party.party_cd.contains(query)).limit(10).all()
        items = Item.query.filter(Item.it_nm.contains(query) | Item.it_cd.contains(query)).limit(10).all()
        
        return jsonify({
            'success': True,
            'parties': [serialize_party(p) for p in parties],
            'items': [serialize_item(i) for i in items]
        })
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'success': False, 'message': 'Search failed'}), 500 

# Transaction Summary API
@api_bp.route('/transactions/summary', methods=['GET'])
@login_required
def get_transaction_summary():
    """Get combined purchase and sale transactions summary"""
    try:
        item_code = request.args.get('item_code')
        
        # Get purchases
        purchases_query = Purchase.query
        if item_code:
            purchases_query = purchases_query.filter_by(it_cd=item_code)
        purchases = purchases_query.order_by(Purchase.bill_date.desc()).all()
        
        # Get sales
        sales_query = Sale.query
        if item_code:
            sales_query = sales_query.filter_by(it_cd=item_code)
        sales = sales_query.order_by(Sale.bill_date.desc()).all()
        
        # Combine and format transactions
        transactions = []
        
        for purchase in purchases:
            transactions.append({
                'id': f'p_{purchase.id}',
                'type': 'purchase',
                'date': purchase.bill_date.isoformat(),
                'party_name': purchase.party.party_nm if purchase.party else purchase.party_cd,
                'item_name': purchase.item.it_nm if purchase.item else purchase.it_cd,
                'bags': purchase.qty,  # Assuming qty represents bags
                'weight': purchase.tot_smt or 0,
                'rate': purchase.rate,
                'amount': purchase.sal_amt,
                'balance': purchase.tot_smt or 0
            })
        
        for sale in sales:
            transactions.append({
                'id': f's_{sale.id}',
                'type': 'sale',
                'date': sale.bill_date.isoformat(),
                'party_name': sale.party.party_nm if sale.party else sale.party_cd,
                'item_name': sale.item.it_nm if sale.item else sale.it_cd,
                'bags': sale.qty,  # Assuming qty represents bags
                'weight': sale.tot_smt or 0,
                'rate': sale.rate,
                'amount': sale.sal_amt,
                'balance': -(sale.tot_smt or 0)
            })
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate summary for specific item if requested
        summary = {}
        if item_code:
            total_purchased = sum(t['bags'] for t in transactions if t['type'] == 'purchase')
            total_sold = sum(t['bags'] for t in transactions if t['type'] == 'sale')
            summary = {
                'total_purchased': total_purchased,
                'total_sold': total_sold,
                'available': total_purchased - total_sold
            }
        
        return jsonify({
            'success': True,
            'data': transactions,
            'summary': summary
        })
    
    except Exception as e:
        logger.error(f"Transaction summary error: {e}")
        return jsonify({'success': False, 'message': 'Failed to get transaction summary'}), 500

@api_bp.route('/transactions/<transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    """Get specific transaction by ID"""
    try:
        if transaction_id.startswith('p_'):
            # Purchase transaction
            purchase_id = int(transaction_id[2:])
            purchase = Purchase.query.get_or_404(purchase_id)
            return jsonify({
                'success': True,
                'data': {
                    'type': 'purchase',
                    'bill_no': purchase.bill_no,
                    'bill_date': purchase.bill_date.isoformat(),
                    'party_cd': purchase.party_cd,
                    'party_name': purchase.party.party_nm if purchase.party else purchase.party_cd,
                    'it_cd': purchase.it_cd,
                    'item_name': purchase.item.it_nm if purchase.item else purchase.it_cd,
                    'bags': purchase.qty,
                    'weight': purchase.tot_smt or 0,
                    'rate': purchase.rate,
                    'amount': purchase.sal_amt,
                    'narration': getattr(purchase, 'remark', '')
                }
            })
        elif transaction_id.startswith('s_'):
            # Sale transaction
            sale_id = int(transaction_id[2:])
            sale = Sale.query.get_or_404(sale_id)
            return jsonify({
                'success': True,
                'data': {
                    'type': 'sale',
                    'bill_no': sale.bill_no,
                    'bill_date': sale.bill_date.isoformat(),
                    'party_cd': sale.party_cd,
                    'party_name': sale.party.party_nm if sale.party else sale.party_cd,
                    'it_cd': sale.it_cd,
                    'item_name': sale.item.it_nm if sale.item else sale.it_cd,
                    'bags': sale.qty,
                    'weight': sale.tot_smt or 0,
                    'rate': sale.rate,
                    'amount': sale.sal_amt,
                    'narration': getattr(sale, 'remark', '')
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid transaction ID'}), 400
    
    except Exception as e:
        logger.error(f"Get transaction error: {e}")
        return jsonify({'success': False, 'message': 'Failed to get transaction'}), 500

@api_bp.route('/transactions/<transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """Delete specific transaction by ID"""
    try:
        if transaction_id.startswith('p_'):
            # Delete purchase transaction
            purchase_id = int(transaction_id[2:])
            purchase = Purchase.query.get_or_404(purchase_id)
            db.session.delete(purchase)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Purchase transaction deleted successfully'})
        elif transaction_id.startswith('s_'):
            # Delete sale transaction
            sale_id = int(transaction_id[2:])
            sale = Sale.query.get_or_404(sale_id)
            db.session.delete(sale)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Sale transaction deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Invalid transaction ID'}), 400
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete transaction error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete transaction'}), 500 