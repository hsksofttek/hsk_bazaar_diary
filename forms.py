"""
Flask-WTF forms for the web application
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from models import User, Party, Item
from datetime import date

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class UserForm(FlaskForm):
    """User edit form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password')])
    role = SelectField('Role', choices=[('user', 'User'), ('manager', 'Manager'), ('admin', 'Admin')])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Changes')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if not kwargs.get('obj'):
            self.password.validators = [DataRequired(), Length(min=6)]
            self.confirm_password.validators = [DataRequired(), EqualTo('password')]

class PartyForm(FlaskForm):
    """Party/Customer/Supplier form"""
    party_cd = StringField('Party Code', validators=[DataRequired(), Length(max=20)])
    party_nm = StringField('Party Name', validators=[DataRequired(), Length(max=200)])
    party_nm_hindi = StringField('Party Name (Hindi)', validators=[Optional(), Length(max=200)])
    place = StringField('Place', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    bal_cd = SelectField('Balance Code', choices=[('D', 'Debit'), ('C', 'Credit')])
    ly_baln = FloatField('Last Year Balance', validators=[Optional()])
    ytd_dr = FloatField('Year to Date Debit', validators=[Optional()])
    ytd_cr = FloatField('Year to Date Credit', validators=[Optional()])
    
    # Extended fields
    address1 = StringField('Address Line 1', validators=[Optional(), Length(max=200)])
    address2 = StringField('Address Line 2', validators=[Optional(), Length(max=200)])
    address3 = StringField('Address Line 3', validators=[Optional(), Length(max=200)])
    po = StringField('P.O.', validators=[Optional(), Length(max=50)])
    dist = StringField('District', validators=[Optional(), Length(max=50)])
    contact = StringField('Contact Person', validators=[Optional(), Length(max=100)])
    state = StringField('State', validators=[Optional(), Length(max=50)])
    pin = StringField('PIN Code', validators=[Optional(), Length(max=10)])
    phone1 = StringField('Phone 1', validators=[Optional(), Length(max=20)])
    phone2 = StringField('Phone 2', validators=[Optional(), Length(max=20)])
    phone3 = StringField('Phone 3', validators=[Optional(), Length(max=20)])
    cst_no = StringField('CST Number', validators=[Optional(), Length(max=50)])
    cst_dt = DateField('CST Date', validators=[Optional()])
    trate = FloatField('Tax Rate', validators=[Optional()])
    agent_cd = StringField('Agent Code', validators=[Optional(), Length(max=20)])
    cat = StringField('Category', validators=[Optional(), Length(max=50)])
    lpperc = FloatField('LP Percentage', validators=[Optional()])
    limit = FloatField('Credit Limit', validators=[Optional()])
    ledgtyp = StringField('Ledger Type', validators=[Optional(), Length(max=20)])
    dis = FloatField('Discount', validators=[Optional()])
    trans_cd = StringField('Transport Code', validators=[Optional(), Length(max=20)])
    pgno = IntegerField('Page Number', validators=[Optional()])
    agent_nm = StringField('Agent Name', validators=[Optional(), Length(max=100)])
    p_bal = FloatField('Previous Balance', validators=[Optional()])
    gstin = StringField('GSTIN', validators=[Optional(), Length(max=20)])
    pan = StringField('PAN', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    fax = StringField('Fax', validators=[Optional(), Length(max=20)])
    mobile = StringField('Mobile', validators=[Optional(), Length(max=20)])
    opening_bal = FloatField('Opening Balance', validators=[Optional()])
    closing_bal = FloatField('Closing Balance', validators=[Optional()])
    
    submit = SubmitField('Save Party')
    
    def validate_party_cd(self, party_cd):
        # Check if party code already exists (for new parties)
        if not self.party_cd.data:  # This is a new party
            party = Party.query.filter_by(party_cd=party_cd.data).first()
            if party:
                raise ValidationError('Party code already exists. Please choose a different one.')

class ItemForm(FlaskForm):
    """Item/Product form"""
    it_cd = StringField('Item Code', validators=[DataRequired(), Length(max=20)])
    it_nm = StringField('Item Name', validators=[DataRequired(), Length(max=200)])
    unit = StringField('Unit', validators=[Optional(), Length(max=10)])
    rate = FloatField('Rate', validators=[Optional()])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    
    # Extended fields
    it_size = StringField('Size', validators=[Optional(), Length(max=50)])
    colo_cd = StringField('Color Code', validators=[Optional(), Length(max=20)])
    pkgs = StringField('Packages', validators=[Optional(), Length(max=50)])
    mrp = FloatField('MRP', validators=[Optional()])
    sprc = FloatField('Sale Price', validators=[Optional()])
    pkt = FloatField('Packet', validators=[Optional()])
    cat_cd = StringField('Category Code', validators=[Optional(), Length(max=20)])
    maxrt = FloatField('Maximum Rate', validators=[Optional()])
    minrt = FloatField('Minimum Rate', validators=[Optional()])
    taxpr = FloatField('Tax Percentage', validators=[Optional()])
    hamrt = FloatField('Ham Rate', validators=[Optional()])
    itwt = FloatField('Item Weight', validators=[Optional()])
    ccess = IntegerField('Cess', validators=[Optional()])
    hsn = StringField('HSN Code', validators=[Optional(), Length(max=20)])
    gst = FloatField('GST', validators=[Optional()])
    cess = FloatField('CESS', validators=[Optional()])
    batch = StringField('Batch', validators=[Optional(), Length(max=50)])
    exp_date = DateField('Expiry Date', validators=[Optional()])
    barcode = StringField('Barcode', validators=[Optional(), Length(max=50)])
    rack = StringField('Rack', validators=[Optional(), Length(max=50)])
    shelf = StringField('Shelf', validators=[Optional(), Length(max=50)])
    reorder_level = FloatField('Reorder Level', validators=[Optional()])
    opening_stock = FloatField('Opening Stock', validators=[Optional()])
    closing_stock = FloatField('Closing Stock', validators=[Optional()])
    
    submit = SubmitField('Save Item')
    
    def validate_it_cd(self, it_cd):
        # Check if item code already exists (for new items)
        if not self.it_cd.data:  # This is a new item
            item = Item.query.filter_by(it_cd=it_cd.data).first()
            if item:
                raise ValidationError('Item code already exists. Please choose a different one.')

class PurchaseForm(FlaskForm):
    """Purchase transaction form"""
    bill_no = IntegerField('Bill Number', validators=[DataRequired()])
    bill_date = DateField('Bill Date', validators=[DataRequired()], default=date.today)
    party_cd = SelectField('Party', coerce=str, validators=[DataRequired()])
    it_cd = SelectField('Item', coerce=str, validators=[DataRequired()])
    qty = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    katta = FloatField('Katta', validators=[Optional()])
    tot_smt = FloatField('Total SMT', validators=[Optional()])
    rate = FloatField('Rate', validators=[DataRequired(), NumberRange(min=0)])
    sal_amt = FloatField('Sale Amount', validators=[DataRequired(), NumberRange(min=0)])
    
    # Extended fields
    order_no = StringField('Order Number', validators=[Optional(), Length(max=50)])
    order_dt = DateField('Order Date', validators=[Optional()])
    discount = FloatField('Discount', validators=[Optional()])
    tot_amt = FloatField('Total Amount', validators=[Optional()])
    trans = StringField('Transport', validators=[Optional(), Length(max=50)])
    lrno = StringField('LR Number', validators=[Optional(), Length(max=50)])
    lr_dt = DateField('LR Date', validators=[Optional()])
    agent_cd = StringField('Agent Code', validators=[Optional(), Length(max=20)])
    remark = TextAreaField('Remarks', validators=[Optional()])
    truck_no = StringField('Truck Number', validators=[Optional(), Length(max=20)])
    taxamt = FloatField('Tax Amount', validators=[Optional()])
    
    submit = SubmitField('Save Purchase')
    
    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        # Populate party choices
        self.party_cd.choices = [(p.party_cd, f"{p.party_cd} - {p.party_nm}") 
                                for p in Party.query.order_by(Party.party_nm).all()]
        # Populate item choices
        self.it_cd.choices = [(i.it_cd, f"{i.it_cd} - {i.it_nm}") 
                             for i in Item.query.order_by(Item.it_nm).all()]

class SaleForm(FlaskForm):
    """Sale transaction form"""
    bill_no = IntegerField('Bill Number', validators=[DataRequired()])
    bill_date = DateField('Bill Date', validators=[DataRequired()], default=date.today)
    party_cd = SelectField('Party', coerce=str, validators=[DataRequired()])
    it_cd = SelectField('Item', coerce=str, validators=[DataRequired()])
    qty = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    katta = FloatField('Katta', validators=[Optional()])
    tot_smt = FloatField('Total SMT', validators=[Optional()])
    rate = FloatField('Rate', validators=[DataRequired(), NumberRange(min=0)])
    sal_amt = FloatField('Sale Amount', validators=[DataRequired(), NumberRange(min=0)])
    
    # Extended fields
    order_no = StringField('Order Number', validators=[Optional(), Length(max=50)])
    order_dt = DateField('Order Date', validators=[Optional()])
    discount = FloatField('Discount', validators=[Optional()])
    tot_amt = FloatField('Total Amount', validators=[Optional()])
    trans = StringField('Transport', validators=[Optional(), Length(max=50)])
    lrno = StringField('LR Number', validators=[Optional(), Length(max=50)])
    lr_dt = DateField('LR Date', validators=[Optional()])
    agent_cd = StringField('Agent Code', validators=[Optional(), Length(max=20)])
    remark = TextAreaField('Remarks', validators=[Optional()])
    truck_no = StringField('Truck Number', validators=[Optional(), Length(max=20)])
    taxamt = FloatField('Tax Amount', validators=[Optional()])
    
    submit = SubmitField('Save Sale')
    
    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        # Populate party choices
        self.party_cd.choices = [(p.party_cd, f"{p.party_cd} - {p.party_nm}") 
                                for p in Party.query.order_by(Party.party_nm).all()]
        # Populate item choices
        self.it_cd.choices = [(i.it_cd, f"{i.it_cd} - {i.it_nm}") 
                             for i in Item.query.order_by(Item.it_nm).all()]

class CashbookForm(FlaskForm):
    """Cashbook transaction form"""
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    narration = TextAreaField('Narration', validators=[DataRequired()])
    dr_amt = FloatField('Debit Amount', validators=[Optional()])
    cr_amt = FloatField('Credit Amount', validators=[Optional()])
    balance = FloatField('Balance', validators=[Optional()])
    party_cd = SelectField('Party', coerce=str, validators=[Optional()])
    voucher_type = StringField('Voucher Type', validators=[Optional(), Length(max=20)])
    voucher_no = StringField('Voucher Number', validators=[Optional(), Length(max=20)])
    
    submit = SubmitField('Save Entry')
    
    def __init__(self, *args, **kwargs):
        super(CashbookForm, self).__init__(*args, **kwargs)
        # Populate party choices
        self.party_cd.choices = [('', 'Select Party')] + [(p.party_cd, f"{p.party_cd} - {p.party_nm}") 
                                                         for p in Party.query.order_by(Party.party_nm).all()]

class BankbookForm(FlaskForm):
    """Bankbook transaction form"""
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    narration = TextAreaField('Narration', validators=[DataRequired()])
    dr_amt = FloatField('Debit Amount', validators=[Optional()])
    cr_amt = FloatField('Credit Amount', validators=[Optional()])
    balance = FloatField('Balance', validators=[Optional()])
    party_cd = SelectField('Party', coerce=str, validators=[Optional()])
    voucher_type = StringField('Voucher Type', validators=[Optional(), Length(max=20)])
    voucher_no = StringField('Voucher Number', validators=[Optional(), Length(max=20)])
    bank_name = StringField('Bank Name', validators=[Optional(), Length(max=100)])
    account_no = StringField('Account Number', validators=[Optional(), Length(max=50)])
    cheque_no = StringField('Cheque Number', validators=[Optional(), Length(max=20)])
    
    submit = SubmitField('Save Entry')
    
    def __init__(self, *args, **kwargs):
        super(BankbookForm, self).__init__(*args, **kwargs)
        # Populate party choices
        self.party_cd.choices = [('', 'Select Party')] + [(p.party_cd, f"{p.party_cd} - {p.party_nm}") 
                                                         for p in Party.query.order_by(Party.party_nm).all()]

class SearchForm(FlaskForm):
    """Generic search form"""
    search = StringField('Search', validators=[Optional()])
    submit = SubmitField('Search')

class DateRangeForm(FlaskForm):
    """Date range form for reports"""
    from_date = DateField('From Date', validators=[DataRequired()])
    to_date = DateField('To Date', validators=[DataRequired()])
    submit = SubmitField('Generate Report') 