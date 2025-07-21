"""
Database models for the web application
SQLAlchemy ORM models with user authentication
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

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

class Party(db.Model):
    """Parties/Customers/Suppliers"""
    __tablename__ = 'parties'
    
    party_cd = db.Column(db.String(20), primary_key=True)
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
    
    def __repr__(self):
        return f'<Party {self.party_cd}: {self.party_nm}>'

class Item(db.Model):
    """Items/Products"""
    __tablename__ = 'items'
    
    it_cd = db.Column(db.String(20), primary_key=True)
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
    
    def __repr__(self):
        return f'<Item {self.it_cd}: {self.it_nm}>'

class Purchase(db.Model):
    """Purchase transactions"""
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    party = db.relationship('Party', backref='purchases')
    item = db.relationship('Item', backref='purchases')
    
    def __repr__(self):
        return f'<Purchase {self.bill_no}: {self.party_cd} - {self.it_cd}>'

class Sale(db.Model):
    """Sales transactions"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    
    # Relationships
    party = db.relationship('Party', backref='sales')
    item = db.relationship('Item', backref='sales')
    purchase = db.relationship('Purchase', backref='sales')
    
    def __repr__(self):
        return f'<Sale {self.bill_no}: {self.party_cd} - {self.it_cd}>'

class Cashbook(db.Model):
    """Cashbook transactions"""
    __tablename__ = 'cashbook'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    narration = db.Column(db.Text)
    dr_amt = db.Column(db.Float, default=0)
    cr_amt = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    party_cd = db.Column(db.String(20), db.ForeignKey('parties.party_cd'))
    voucher_type = db.Column(db.String(20))
    voucher_no = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    party = db.relationship('Party', backref='cashbook_entries')
    
    def __repr__(self):
        return f'<Cashbook {self.date}: {self.narration}>'

class Bankbook(db.Model):
    """Bankbook transactions"""
    __tablename__ = 'bankbook'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    party = db.relationship('Party', backref='bankbook_entries')
    
    def __repr__(self):
        return f'<Bankbook {self.date}: {self.narration}>' 