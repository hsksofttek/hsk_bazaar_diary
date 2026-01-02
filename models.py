"""
Database models for the web application
SQLAlchemy ORM models with user authentication
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from database import db

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user, manager
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Company(db.Model):
    """Company information"""
    __tablename__ = 'company'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    address1 = db.Column(db.String(200))
    address2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    password = db.Column(db.String(100))
    directory = db.Column(db.String(200))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='companies')

class Party(db.Model):
    """Parties/Customers/Suppliers"""
    __tablename__ = 'parties'
    
    party_cd = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    party_nm = db.Column(db.String(200), nullable=False)
    party_nm_hindi = db.Column(db.String(200))
    place = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    bal_cd = db.Column(db.String(1), default='D')
    ly_baln = db.Column(db.Float, default=0)
    ytd_dr = db.Column(db.Float, default=0)
    ytd_cr = db.Column(db.Float, default=0)
    
    # Extended fields
    address1 = db.Column(db.String(200))
    address2 = db.Column(db.String(200))
    address3 = db.Column(db.String(200))
    po = db.Column(db.String(50))
    dist = db.Column(db.String(50))
    contact = db.Column(db.String(100))
    state = db.Column(db.String(50))
    pin = db.Column(db.String(10))
    phone1 = db.Column(db.String(20))
    phone2 = db.Column(db.String(20))
    phone3 = db.Column(db.String(20))
    cst_no = db.Column(db.String(50))
    cst_dt = db.Column(db.Date)
    trate = db.Column(db.Float, default=0)
    agent_cd = db.Column(db.String(20))
    cat = db.Column(db.String(50))
    lpperc = db.Column(db.Float, default=0)
    limit = db.Column(db.Float, default=0)
    ledgtyp = db.Column(db.String(20))
    dis = db.Column(db.Float, default=0)
    trans_cd = db.Column(db.String(20))
    pgno = db.Column(db.Integer)
    agent_nm = db.Column(db.String(100))
    p_bal = db.Column(db.Float, default=0)
    phone4 = db.Column(db.String(20))
    phone5 = db.Column(db.String(20))
    phone6 = db.Column(db.String(20))
    phone7 = db.Column(db.String(20))
    phone8 = db.Column(db.String(20))
    bst_no = db.Column(db.String(50))
    
    # Enhanced Credit Management (Based on Legacy Analysis)
    credit_limit = db.Column(db.Float, default=0)  # Credit limit for the party
    current_balance = db.Column(db.Float, default=0)  # Real-time balance
    payment_terms = db.Column(db.String(50))  # Payment terms (e.g., "30 days")
    last_payment_date = db.Column(db.Date)  # Last payment received date
    credit_status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, SUSPENDED, BLOCKED
    opening_balance_date = db.Column(db.Date)  # Date of opening balance
    bst_dt = db.Column(db.Date)
    vat_no = db.Column(db.String(50))
    acode = db.Column(db.String(20))
    area = db.Column(db.String(50))
    ly_cd = db.Column(db.String(20))
    cr_dr = db.Column(db.String(1))
    amount = db.Column(db.Float, default=0)
    page_no = db.Column(db.Integer)
    group_cd = db.Column(db.String(20))
    group_nm = db.Column(db.String(100))
    gstin = db.Column(db.String(20))
    pan = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fax = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    opening_bal = db.Column(db.Float, default=0)
    closing_bal = db.Column(db.Float, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='parties')
    
    def __repr__(self):
        return f'<Party {self.party_cd}: {self.party_nm}>'

class Item(db.Model):
    """Items/Products"""
    __tablename__ = 'items'
    
    it_cd = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    it_nm = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.String(10), default='KG')
    rate = db.Column(db.Float, default=0)
    category = db.Column(db.String(100))
    
    # Extended fields
    it_size = db.Column(db.String(50))
    colo_cd = db.Column(db.String(20))
    pkgs = db.Column(db.String(50))
    mrp = db.Column(db.Float, default=0)
    sprc = db.Column(db.Float, default=0)
    pkt = db.Column(db.Float, default=0)
    cat_cd = db.Column(db.String(20))
    maxrt = db.Column(db.Float, default=0)
    minrt = db.Column(db.Float, default=0)
    taxpr = db.Column(db.Float, default=0)
    hamrt = db.Column(db.Float, default=0)
    itwt = db.Column(db.Float, default=0)
    ccess = db.Column(db.Integer, default=0)
    hsn = db.Column(db.String(20))
    gst = db.Column(db.Float, default=0)
    cess = db.Column(db.Float, default=0)
    batch = db.Column(db.String(50))
    exp_date = db.Column(db.Date)
    barcode = db.Column(db.String(50))
    rack = db.Column(db.String(50))
    shelf = db.Column(db.String(50))
    reorder_level = db.Column(db.Float, default=0)
    opening_stock = db.Column(db.Float, default=0)
    closing_stock = db.Column(db.Float, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='items')
    
    def __repr__(self):
        return f'<Item {self.it_cd}: {self.it_nm}>'

class Purchase(db.Model):
    """Purchase transactions"""
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bill_no = db.Column(db.Integer, nullable=False)
    bill_date = db.Column(db.Date, nullable=False)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'), nullable=False)
    it_cd = db.Column(db.String(20), db.ForeignKey('items.it_cd'), nullable=False)
    qty = db.Column(db.Float, nullable=False, default=0)
    katta = db.Column(db.Float, default=0)
    tot_smt = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, nullable=False, default=0)
    sal_amt = db.Column(db.Float, nullable=False, default=0)
    
    # Extended fields
    order_no = db.Column(db.String(50))
    order_dt = db.Column(db.Date)
    it_size = db.Column(db.String(50))
    colo_cd = db.Column(db.String(20))
    pack = db.Column(db.Float, default=0)
    smt = db.Column(db.Float, default=0)
    f_smt = db.Column(db.Float, default=0)
    b_code = db.Column(db.Integer)
    st = db.Column(db.Float, default=0)
    stcd = db.Column(db.String(20))
    discount = db.Column(db.Float, default=0)
    tot_amt = db.Column(db.Float, default=0)
    trans = db.Column(db.String(50))
    lrno = db.Column(db.String(50))
    lr_dt = db.Column(db.Date)
    agent_cd = db.Column(db.String(20))
    remark = db.Column(db.Text)
    gdn_cd = db.Column(db.String(20))
    name = db.Column(db.String(100))
    lo = db.Column(db.Integer, default=0)
    bc = db.Column(db.Integer, default=0)
    pkgs = db.Column(db.String(50))
    scheme = db.Column(db.String(100))
    less = db.Column(db.Float, default=0)
    otexp = db.Column(db.Float, default=0)
    expdt = db.Column(db.Date)
    sp = db.Column(db.Float, default=0)
    cd = db.Column(db.Float, default=0)
    comm = db.Column(db.Float, default=0)
    nara = db.Column(db.Text)
    short = db.Column(db.Float, default=0)
    truck_no = db.Column(db.String(20))
    exp1 = db.Column(db.Float, default=0)
    exp2 = db.Column(db.Float, default=0)
    exp3 = db.Column(db.Float, default=0)
    exp4 = db.Column(db.Float, default=0)
    exp5 = db.Column(db.Float, default=0)
    taxamt = db.Column(db.Float, default=0)
    cash_date = db.Column(db.Date)
    lr_no = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='purchases')
    party = db.relationship('Party', backref='purchases')
    item = db.relationship('Item', backref='purchases')
    
    def __repr__(self):
        return f'<Purchase {self.bill_no}: {self.party_cd} - {self.it_cd}>'

class Sale(db.Model):
    """Sales transactions"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bill_no = db.Column(db.Integer, nullable=False)
    bill_date = db.Column(db.Date, nullable=False)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'), nullable=False)
    it_cd = db.Column(db.String(20), db.ForeignKey('items.it_cd'), nullable=False)
    qty = db.Column(db.Float, nullable=False, default=0)
    katta = db.Column(db.Float, default=0)
    tot_smt = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, nullable=False, default=0)
    sal_amt = db.Column(db.Float, nullable=False, default=0)
    
    # Extended fields (similar to Purchase)
    order_no = db.Column(db.String(50))
    order_dt = db.Column(db.Date)
    it_size = db.Column(db.String(50))
    colo_cd = db.Column(db.String(20))
    pack = db.Column(db.Float, default=0)
    smt = db.Column(db.Float, default=0)
    f_smt = db.Column(db.Float, default=0)
    b_code = db.Column(db.Integer)
    st = db.Column(db.Float, default=0)
    stcd = db.Column(db.String(20))
    discount = db.Column(db.Float, default=0)
    tot_amt = db.Column(db.Float, default=0)
    trans = db.Column(db.String(50))
    lrno = db.Column(db.String(50))
    lr_dt = db.Column(db.Date)
    agent_cd = db.Column(db.String(20))
    remark = db.Column(db.Text)
    gdn_cd = db.Column(db.String(20))
    name = db.Column(db.String(100))
    lo = db.Column(db.Integer, default=0)
    bc = db.Column(db.Integer, default=0)
    pkgs = db.Column(db.String(50))
    scheme = db.Column(db.String(100))
    less = db.Column(db.Float, default=0)
    otexp = db.Column(db.Float, default=0)
    expdt = db.Column(db.Date)
    sp = db.Column(db.Float, default=0)
    cd = db.Column(db.Float, default=0)
    comm = db.Column(db.Float, default=0)
    nara = db.Column(db.Text)
    short = db.Column(db.Float, default=0)
    truck_no = db.Column(db.String(20))
    exp1 = db.Column(db.Float, default=0)
    exp2 = db.Column(db.Float, default=0)
    exp3 = db.Column(db.Float, default=0)
    exp4 = db.Column(db.Float, default=0)
    exp5 = db.Column(db.Float, default=0)
    taxamt = db.Column(db.Float, default=0)
    cash_date = db.Column(db.Date)
    lr_no = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Link to purchase (for tracking sold bags)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    
    # Enhanced Payment Tracking (Based on Legacy Analysis)
    payment_status = db.Column(db.String(20), default='PENDING')  # PENDING, PARTIAL, PAID
    payment_due_date = db.Column(db.Date)  # Due date for payment
    amount_paid = db.Column(db.Float, default=0)  # Amount paid so far
    payment_terms = db.Column(db.String(50))  # Payment terms for this sale
    credit_days = db.Column(db.Integer, default=0)  # Credit days allowed
    
    # Relationships
    user = db.relationship('User', backref='sales')
    party = db.relationship('Party', backref='sales')
    item = db.relationship('Item', backref='sales')
    purchase = db.relationship('Purchase', backref='sales')
    
    def __repr__(self):
        return f'<Sale {self.bill_no}: {self.party_cd} - {self.it_cd}>'

class Cashbook(db.Model):
    """Cashbook transactions"""
    __tablename__ = 'cashbook'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    narration = db.Column(db.Text)
    dr_amt = db.Column(db.Float, default=0)
    cr_amt = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'))
    voucher_type = db.Column(db.String(20))
    voucher_no = db.Column(db.String(20))
    
    # Enhanced Payment Tracking (Based on Legacy Analysis)
    related_sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))  # Link to specific sale
    payment_type = db.Column(db.String(20))  # CASH, CHEQUE, BANK_TRANSFER, etc.
    reference_no = db.Column(db.String(50))  # Cheque number, transaction ID, etc.
    payment_method = db.Column(db.String(50))  # Method of payment
    bank_name = db.Column(db.String(100))  # Bank name for cheque payments
    branch_name = db.Column(db.String(100))  # Branch name
    cheque_date = db.Column(db.Date)  # Cheque date
    transaction_date = db.Column(db.DateTime)  # Actual transaction date/time
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='cashbook_entries')
    party = db.relationship('Party', backref='cashbook_entries')
    related_sale = db.relationship('Sale', backref='cashbook_entries')
    
    def __repr__(self):
        return f'<Cashbook {self.date}: {self.narration}>'

class Bankbook(db.Model):
    """Bankbook transactions"""
    __tablename__ = 'bankbook'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    narration = db.Column(db.Text)
    dr_amt = db.Column(db.Float, default=0)
    cr_amt = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'))
    voucher_type = db.Column(db.String(20))
    voucher_no = db.Column(db.String(20))
    bank_name = db.Column(db.String(100))
    account_no = db.Column(db.String(50))
    cheque_no = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bankbook_entries')
    party = db.relationship('Party', backref='bankbook_entries')
    
    def __repr__(self):
        return f'<Bankbook {self.date}: {self.narration}>' 

class Ledger(db.Model):
    """Ledger for comprehensive financial tracking (Based on Legacy Analysis)"""
    __tablename__ = 'ledger'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'), nullable=False)
    narration = db.Column(db.Text)
    dr_amt = db.Column(db.Float, default=0)
    cr_amt = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    voucher_type = db.Column(db.String(20))  # SALE, PURCHASE, PAYMENT, RECEIPT, etc.
    voucher_no = db.Column(db.String(20))
    reference_no = db.Column(db.String(50))
    
    # Link to related transactions
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    cashbook_id = db.Column(db.Integer, db.ForeignKey('cashbook.id'))
    bankbook_id = db.Column(db.Integer, db.ForeignKey('bankbook.id'))
    
    # Financial year tracking
    financial_year = db.Column(db.String(10))  # e.g., "2024-25"
    month = db.Column(db.Integer)  # 1-12
    day = db.Column(db.Integer)  # 1-31
    
    # Balance indicators
    balance_type = db.Column(db.String(1))  # D for Debit, C for Credit
    running_balance = db.Column(db.Float, default=0)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='ledger_entries')
    party = db.relationship('Party', backref='ledger_entries')
    sale = db.relationship('Sale', backref='ledger_entries')
    purchase = db.relationship('Purchase', backref='ledger_entries')
    cashbook_entry = db.relationship('Cashbook', backref='ledger_entries')
    bankbook_entry = db.relationship('Bankbook', backref='ledger_entries')
    
    def __repr__(self):
        return f'<Ledger {self.id} - {self.party_cd} - {self.date}>' 

class Packing(db.Model):
    """Packing materials and charges"""
    __tablename__ = 'packing'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bill_no = db.Column(db.Integer)  # Bill number reference
    it_cd = db.Column(db.String(20), db.ForeignKey('items.it_cd'))
    packing_desc = db.Column(db.String(200))  # Packing description
    qty = db.Column(db.Float, default=0)  # Quantity
    mrp = db.Column(db.Float, default=0)  # Maximum Retail Price
    sprc = db.Column(db.Float, default=0)  # Sale Price
    pkt = db.Column(db.Float, default=0)  # Package rate
    bnd_dtl1 = db.Column(db.String(100))  # Bound detail 1
    bnd_dtl2 = db.Column(db.String(100))  # Bound detail 2
    cat_cd = db.Column(db.String(20))  # Category code
    maxrt = db.Column(db.Float, default=0)  # Maximum rate
    minrt = db.Column(db.Float, default=0)  # Minimum rate
    taxpr = db.Column(db.Float, default=0)  # Tax percentage
    hamrt = db.Column(db.Float, default=0)  # Hamali rate
    itwt = db.Column(db.Float, default=0)  # Item weight
    ccess = db.Column(db.Integer, default=0)  # CESS amount
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='packing_entries')
    item = db.relationship('Item', backref='packing_entries')
    
    def __repr__(self):
        return f'<Packing {self.it_cd} - {self.packing_desc}>' 

class TransportMaster(db.Model):
    """Transport companies and logistics management"""
    __tablename__ = 'transport_master'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trans_cd = db.Column(db.String(20), unique=True, nullable=False)
    trans_nm = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    dest = db.Column(db.String(100))  # Destination
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    vehicle_no = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    license_no = db.Column(db.String(50))
    gst_no = db.Column(db.String(20))
    pan_no = db.Column(db.String(20))
    commission = db.Column(db.Float, default=0)  # Commission percentage
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INACTIVE, SUSPENDED
    remarks = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='transport_companies')
    
    def __repr__(self):
        return f'<TransportMaster {self.trans_cd} - {self.trans_nm}>' 

class GatePass(db.Model):
    """Gate pass for vehicle entry and exit tracking"""
    __tablename__ = 'gate_pass'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gate_pass_no = db.Column(db.Integer, unique=True, nullable=False)
    gate_pass_date = db.Column(db.Date, nullable=False)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'), nullable=False)
    vehicle_no = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    license_no = db.Column(db.String(50))
    purpose = db.Column(db.String(200))
    items_description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    entry_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INSIDE, COMPLETED
    authorized_by = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='gate_passes')
    party = db.relationship('Party', backref='gate_passes')
    
    def __repr__(self):
        return f'<GatePass {self.gate_pass_no} - {self.party_cd}>'

class Agent(db.Model):
    """Sales agents and commission management"""
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_cd = db.Column(db.String(20), unique=True, nullable=False)
    agent_nm = db.Column(db.String(200), nullable=False)
    commission_rate = db.Column(db.Float, default=0)  # Commission percentage
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    email = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    gst_no = db.Column(db.String(20))
    pan_no = db.Column(db.String(20))
    bank_name = db.Column(db.String(100))
    account_no = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(20))
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INACTIVE, SUSPENDED
    joining_date = db.Column(db.Date)
    remarks = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='agents')
    
    def __repr__(self):
        return f'<Agent {self.agent_cd} - {self.agent_nm}>'

class BankAccount(db.Model):
    """Bank accounts management"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    bank_name = db.Column(db.String(200), nullable=False)
    account_number = db.Column(db.String(50), unique=True, nullable=False)
    ifsc_code = db.Column(db.String(20))
    branch_name = db.Column(db.String(200))
    account_type = db.Column(db.String(20), default='SAVINGS')  # SAVINGS, CURRENT, FIXED
    opening_balance = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INACTIVE, CLOSED
    remarks = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bank_accounts')
    transactions = db.relationship('BankTransaction', backref='account')
    
    def __repr__(self):
        return f'<BankAccount {self.account_name} - {self.bank_name}>'

class BankTransaction(db.Model):
    """Bank transactions"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # CREDIT, DEBIT
    narration = db.Column(db.Text)
    reference_no = db.Column(db.String(50))
    cheque_no = db.Column(db.String(20))
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'))
    category = db.Column(db.String(100))
    status = db.Column(db.String(20), default='COMPLETED')  # COMPLETED, PENDING, CANCELLED
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bank_transactions')
    party = db.relationship('Party', backref='bank_transactions')
    
    def __repr__(self):
        return f'<BankTransaction {self.id} - {self.transaction_type} - {self.amount}>'

class Schedule(db.Model):
    """Payment and delivery schedules"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_type = db.Column(db.String(20), nullable=False)  # PAYMENT, DELIVERY, REMINDER
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'), nullable=False)
    description = db.Column(db.Text)
    reference_no = db.Column(db.String(50))
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    status = db.Column(db.String(20), default='PENDING')  # PENDING, COMPLETED, OVERDUE, CANCELLED
    priority = db.Column(db.String(20), default='MEDIUM')  # LOW, MEDIUM, HIGH, URGENT
    reminder_days = db.Column(db.Integer, default=7)
    remarks = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='schedules')
    party = db.relationship('Party', backref='schedules')
    sale = db.relationship('Sale', backref='schedules')
    purchase = db.relationship('Purchase', backref='schedules')
    
    def __repr__(self):
        return f'<Schedule {self.id} - {self.schedule_type} - {self.due_date}>'

class Narration(db.Model):
    """Predefined narration templates"""
    __tablename__ = 'narrations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    narration_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., Sales, Purchase, Payment, General
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.String(100), default='system')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='narrations')
    
    def __repr__(self):
        return f'<Narration {self.id} - {self.category} - {self.narration_text[:30]}...>' 