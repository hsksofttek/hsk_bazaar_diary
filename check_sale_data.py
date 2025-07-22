from app import create_app, db
from models import Sale

app = create_app()
with app.app_context():
    sales = Sale.query.filter_by(bill_no=2002).all()
    print(f"Found {len(sales)} sales for bill 2002")
    for sale in sales:
        print(f"Sale: it_cd={sale.it_cd}, qty={sale.qty}, rate={sale.rate}, sal_amt={sale.sal_amt}, discount={sale.discount}") 