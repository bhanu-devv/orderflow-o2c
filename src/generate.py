"""Deterministic synthetic order-to-cash manufacturing/retail operations dataset."""
from __future__ import annotations
import csv, json, random, sqlite3
from datetime import date,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
rng=random.Random(20261114)
CUSTOMERS=[(f'C{i:03}',f'{name} {i:03}',rng.choice(['Grocery','Distributor','Convenience','E-commerce']),rng.choice(['Eastern','Central','Mountain','Pacific'])) for i,name in enumerate(['Summit Markets','Greenway Grocers','Cedar Foods','Metro Wholesale','Northstar Retail'],1) for _ in []]
CUSTOMERS=[(f'C{i:03}',f'{rng.choice(["Summit Markets","Greenway Grocers","Cedar Foods","Metro Wholesale","Northstar Retail","Harbor Foods"])} #{i:03}',rng.choice(['Grocery','Distributor','Convenience','E-commerce']),rng.choice(['East','Central','West'])) for i in range(1,81)]
SKUS=[(f'SKU{i:04}',f'{rng.choice(["Snack Bars","Coffee","Nutrition Drink","Breakfast Cereal","Water","Frozen Meals","Pet Food","Beverage Mix"])} {i:04}',rng.choice(['Food','Beverage','Nutrition','Pet Care']),round(rng.uniform(3.5,80),2)) for i in range(1,201)]
REASONS=['Inventory shortage','Credit hold','Incorrect pricing','Address validation','Warehouse picking issue','Carrier delay','Appointment scheduling','Demand capture error','Billing discrepancy']
orders=[]; shipments=[]; invoices=[]; cases=[]; activities=[]
start=date(2026,1,1); end=date(2026,11,14)
for i in range(1,10001):
    oid=f'SO{i:06}'; customer=rng.choice(CUSTOMERS); sku=rng.choice(SKUS)
    created=start+timedelta(days=rng.randrange((end-start).days+1))
    promised=created+timedelta(days=rng.randint(2,10))
    qty=rng.randint(8,220); price=sku[3]; amount=round(qty*price,2)
    u=rng.random()
    status='Delivered' if u<.79 else 'Open' if u<.88 else 'Blocked' if u<.96 else 'Cancelled'
    reason=rng.choice(REASONS[:4]+['Demand capture error']) if status=='Blocked' else ''
    priority=rng.choices(['Low','Medium','High','Critical'],weights=[18,52,24,6])[0]
    assigned=rng.choice(['Customer Solutions','Order Fulfillment','Billing','Transportation','Sales'])
    orders.append((oid,customer[0],sku[0],created.isoformat(),promised.isoformat(),qty,price,amount,status,reason,priority,assigned))
    if status=='Delivered':
        delivered=promised+timedelta(days=rng.choices([-2,-1,0,1,2,4,7],[8,12,54,12,7,5,2])[0])
        shipped=qty if rng.random()<.91 else max(1,qty-rng.randint(1,min(qty-1,20)))
        shipments.append((f'DN{i:06}',oid,delivered.isoformat(),shipped,rng.choice(['East DC','Central DC','West DC']),rng.choice(['Carrier A','Carrier B','Carrier C'])))
        invoice_amount=round(shipped*price,2)
        if rng.random()<.04: invoice_amount=round(invoice_amount+rng.choice([-1,1])*rng.uniform(2,60),2)
        invoices.append((f'INV{i:06}',oid,(delivered+timedelta(days=1)).isoformat(),invoice_amount,'Paid' if rng.random()<.85 else 'Outstanding'))
    if status=='Blocked' or (status=='Delivered' and rng.random()<.07) or (status=='Open' and rng.random()<.05):
        opened=created+timedelta(days=rng.randint(0,2)); reason=reason or rng.choice(REASONS[4:]); hours=rng.choice([4,8,24,48]); deadline=opened+timedelta(hours=hours) if False else opened+timedelta(days=1 if hours<=24 else 2)
        cstatus=rng.choices(['Open','Escalated','Resolved'],[32,12,56])[0]; resolved=opened+timedelta(days=rng.randint(0,5)) if cstatus=='Resolved' else None
        cases.append((f'CASE{i:06}',oid,reason,opened.isoformat(),deadline.isoformat(),resolved.isoformat() if resolved else '',cstatus,rng.choice(['Customer Solutions','Billing','Warehouse','Transportation']),priority))
    if i%500==0: print('generated',i)

def dump(name,header,rows):
    with (DATA/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(header);writer.writerows(rows)

dump('customers.csv',['customer_id','customer_name','segment','region'],CUSTOMERS)
dump('products.csv',['sku','product_name','category','unit_price'],SKUS)
dump('orders.csv',['order_id','customer_id','sku','order_date','promised_date','ordered_qty','unit_price','order_amount','status','block_reason','priority','owner'],orders)
dump('shipments.csv',['delivery_id','order_id','delivery_date','delivered_qty','warehouse','carrier'],shipments)
dump('invoices.csv',['invoice_id','order_id','invoice_date','invoice_amount','payment_status'],invoices)
dump('cases.csv',['case_id','order_id','reason_code','opened_date','sla_due_date','resolved_date','case_status','team','priority'],cases)
# Inventory snapshot determines hypothetical stock alerts; not a historical stock ledger.
inventory=[(sku[0], rng.choice(['East DC','Central DC','West DC']),rng.randint(0,1200),rng.randint(70,180)) for sku in SKUS]
dump('inventory_snapshot.csv',['sku','warehouse','on_hand_qty','reorder_point'],inventory)

DB=DATA/'orderflow.db'
if DB.exists(): DB.unlink()
con=sqlite3.connect(DB)
con.executescript('''
PRAGMA foreign_keys=ON;
CREATE TABLE customers(customer_id TEXT PRIMARY KEY,customer_name TEXT,segment TEXT,region TEXT);
CREATE TABLE products(sku TEXT PRIMARY KEY,product_name TEXT,category TEXT,unit_price REAL);
CREATE TABLE orders(order_id TEXT PRIMARY KEY,customer_id TEXT REFERENCES customers(customer_id),sku TEXT REFERENCES products(sku),order_date TEXT,promised_date TEXT,ordered_qty INTEGER,unit_price REAL,order_amount REAL,status TEXT,block_reason TEXT,priority TEXT,owner TEXT);
CREATE TABLE shipments(delivery_id TEXT PRIMARY KEY,order_id TEXT UNIQUE REFERENCES orders(order_id),delivery_date TEXT,delivered_qty INTEGER,warehouse TEXT,carrier TEXT);
CREATE TABLE invoices(invoice_id TEXT PRIMARY KEY,order_id TEXT UNIQUE REFERENCES orders(order_id),invoice_date TEXT,invoice_amount REAL,payment_status TEXT);
CREATE TABLE cases(case_id TEXT PRIMARY KEY,order_id TEXT REFERENCES orders(order_id),reason_code TEXT,opened_date TEXT,sla_due_date TEXT,resolved_date TEXT,case_status TEXT,team TEXT,priority TEXT);
CREATE TABLE inventory_snapshot(sku TEXT REFERENCES products(sku),warehouse TEXT,on_hand_qty INTEGER,reorder_point INTEGER,PRIMARY KEY(sku,warehouse));
CREATE TABLE activity_log(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, action TEXT, actor TEXT, note TEXT,changed_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX idx_orders_status ON orders(status);CREATE INDEX idx_orders_promised ON orders(promised_date);CREATE INDEX idx_cases_sla ON cases(sla_due_date);
CREATE VIEW v_order_360 AS SELECT o.*,c.customer_name,c.segment,c.region,p.product_name,p.category,s.delivery_date,s.delivered_qty,s.warehouse,s.carrier,i.invoice_amount,i.payment_status,
 CASE WHEN o.status='Delivered' THEN CASE WHEN s.delivery_date <= o.promised_date AND s.delivered_qty>=o.ordered_qty THEN 1 ELSE 0 END END AS otif_flag,
 CASE WHEN o.status='Delivered' THEN ROUND(COALESCE(i.invoice_amount,0)-s.delivered_qty*o.unit_price,2) END AS invoice_variance
 FROM orders o JOIN customers c USING(customer_id) JOIN products p USING(sku) LEFT JOIN shipments s USING(order_id) LEFT JOIN invoices i USING(order_id);
''')
for tbl,rows in [('customers',CUSTOMERS),('products',SKUS),('orders',orders),('shipments',shipments),('invoices',invoices),('cases',cases),('inventory_snapshot',inventory)]:
    marks=','.join(['?']*len(rows[0]));con.executemany(f'INSERT INTO {tbl} VALUES ({marks})',rows)
con.commit()
counts={t:con.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in ['customers','products','orders','shipments','invoices','cases','inventory_snapshot']}
metrics=dict(con.execute('''SELECT 'total_orders',count(*) FROM orders UNION ALL SELECT 'blocked_orders',count(*) FROM orders WHERE status='Blocked' UNION ALL SELECT 'delivered_orders',count(*) FROM orders WHERE status='Delivered' UNION ALL SELECT 'otif_orders',count(*) FROM v_order_360 WHERE otif_flag=1 UNION ALL SELECT 'invoice_discrepancies',count(*) FROM v_order_360 WHERE ABS(invoice_variance)>0.01''').fetchall())
metrics['otif_pct']=round(100*metrics['otif_orders']/metrics['delivered_orders'],2)
metrics['total_order_value']=round(con.execute('SELECT SUM(order_amount) FROM orders').fetchone()[0],2)
(DATA/'validation.json').write_text(json.dumps({'counts':counts,'metrics':metrics,'note':'Synthetic dataset; snapshot-based inventory not historical order-level stock availability.'},indent=2))
con.close()
print(json.dumps(metrics,indent=2))
