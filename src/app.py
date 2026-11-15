"""OrderFlow local interactive operations console. Run: streamlit run src/app.py"""
import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

DB=Path(__file__).resolve().parents[1]/'data'/'orderflow.db'
st.set_page_config(page_title='OrderFlow | Operations Control Center',layout='wide',page_icon='📦')
st.markdown('''<style>.block-container{padding-top:1.8rem} .stMetric{background:#eff5fa;border:1px solid #dbe7f2;border-radius:12px;padding:14px}</style>''',unsafe_allow_html=True)
st.title('OrderFlow · Operations Control Center')
st.caption('Synthetic order-to-cash operations | simulated food-and-beverage distributor | data is not from Nestlé')

def fetch(query,params=()):
    with sqlite3.connect(DB) as con:return pd.read_sql_query(query,con,params=params)

if not DB.exists():st.error('Run python src/generate.py first.');st.stop()
page=st.sidebar.radio('Workspace',['Executive overview','Order filter','Exception case management','Customer 360°','Billing reconciliation','Inventory alerts','Data quality'])
if page=='Executive overview':
    m=fetch('''SELECT COUNT(*) orders, SUM(status='Blocked') blocked,SUM(status='Open') open_orders, SUM(status='Delivered') delivered, SUM(COALESCE(otif_flag,0)) ontime_infull,ROUND(SUM(order_amount),2) order_value FROM v_order_360''').iloc[0]
    c=st.columns(5)
    for col,title,value in zip(c,['Total orders','Open orders','Blocked orders','OTIF %','Order value'],[f'{int(m.orders):,}',f'{int(m.open_orders):,}',f'{int(m.blocked):,}',f'{100*m.ontime_infull/m.delivered:.1f}%',f'${m.order_value/1e6:.2f}M']):col.metric(title,value)
    a,b=st.columns(2)
    with a:
        st.subheader('Order state')
        st.bar_chart(fetch('SELECT status,COUNT(*) order_count FROM orders GROUP BY status').set_index('status'))
        st.subheader('Top blocked reasons')
        st.dataframe(fetch("SELECT block_reason,COUNT(*) affected_orders FROM orders WHERE status='Blocked' GROUP BY block_reason ORDER BY affected_orders DESC"),hide_index=True,use_container_width=True)
    with b:
        st.subheader('OTIF by region')
        st.bar_chart(fetch('''SELECT region,ROUND(100.0*SUM(otif_flag)/COUNT(*),1) otif_percent FROM v_order_360 WHERE status='Delivered' GROUP BY region''').set_index('region'))
        st.subheader('Monthly order revenue (ordered, not collected)')
        st.line_chart(fetch("SELECT substr(order_date,1,7) month,ROUND(SUM(order_amount),2) amount FROM orders GROUP BY 1 ORDER BY 1").set_index('month'))
elif page=='Order filter':
    st.subheader('Daily activity queue')
    statuses=st.multiselect('Order statuses',['Blocked','Open','Delivered','Cancelled'],default=['Blocked','Open'])
    priorities=st.multiselect('Priorities',['Critical','High','Medium','Low'],default=['Critical','High','Medium','Low'])
    if statuses and priorities:
        sql=f"SELECT order_id,customer_name,product_name,order_date,promised_date,status,priority,block_reason,owner,ordered_qty,ROUND(order_amount,2) order_amount FROM v_order_360 WHERE status IN ({','.join('?' for _ in statuses)}) AND priority IN ({','.join('?' for _ in priorities)}) ORDER BY CASE priority WHEN 'Critical' THEN 0 WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,promised_date LIMIT 2000"
        df=fetch(sql,tuple(statuses+priorities));st.metric('Matching queued orders',len(df));st.dataframe(df,hide_index=True,use_container_width=True)
    else:st.info('Select at least one status and priority.')
    st.caption('This is a demonstration queue; status changes are recorded in the local database using the case-management page.')
elif page=='Exception case management':
    st.subheader('Case workflow & SLA controls')
    cases=fetch("SELECT c.case_id,c.order_id,c.reason_code,c.opened_date,c.sla_due_date,c.resolved_date,c.case_status,c.team,c.priority,o.customer_id FROM cases c JOIN orders o ON c.order_id=o.order_id ORDER BY c.case_status,c.sla_due_date")
    st.dataframe(cases.head(1000),hide_index=True,use_container_width=True)
    active=cases[cases.case_status!='Resolved']
    st.metric('Unresolved cases',len(active))
    with st.form('case_action'):
        case_id=st.selectbox('Select case',active.case_id.tolist() if len(active) else ['No open cases'])
        action=st.selectbox('Update status',['Escalated','Resolved'])
        actor=st.text_input('Actor',value='Portfolio demo user')
        note=st.text_area('Resolution / escalation notes',placeholder='Example: contacted transportation, confirmed rescheduled delivery')
        submit=st.form_submit_button('Apply case update')
    if submit:
        if not note.strip():st.error('Provide a reason note for the audit log.')
        else:
            with sqlite3.connect(DB) as conn:
                conn.execute('UPDATE cases SET case_status=?,resolved_date=? WHERE case_id=?',(action,datetime.now().date().isoformat() if action=='Resolved' else '',case_id))
                order_id=conn.execute('SELECT order_id FROM cases WHERE case_id=?',(case_id,)).fetchone()[0]
                conn.execute('INSERT INTO activity_log(order_id,action,actor,note) VALUES (?,?,?,?)',(order_id,action,actor,note))
                conn.commit()
            st.success(f'Case {case_id} updated and logged. Refresh to see latest status.')
    st.subheader('Audit trail')
    st.dataframe(fetch('SELECT * FROM activity_log ORDER BY id DESC LIMIT 30'),hide_index=True,use_container_width=True)
elif page=='Customer 360°':
    customers=fetch('SELECT customer_id,customer_name FROM customers ORDER BY customer_name')
    cid=st.selectbox('Customer',customers.customer_id.tolist(),format_func=lambda x:customers.set_index('customer_id').loc[x,'customer_name'])
    detail=fetch('SELECT order_id,order_date,promised_date,product_name,ordered_qty,status,block_reason,delivery_date,delivered_qty,invoice_amount,otif_flag FROM v_order_360 WHERE customer_id=? ORDER BY order_date DESC',(cid,))
    a,b,c=st.columns(3);a.metric('Orders',len(detail));b.metric('Blocked',int((detail.status=='Blocked').sum()));c.metric('Delivered OTIF',f"{detail.loc[detail.status=='Delivered','otif_flag'].mean()*100:.1f}%" if (detail.status=='Delivered').sum() else 'N/A')
    st.dataframe(detail,hide_index=True,use_container_width=True)
elif page=='Billing reconciliation':
    st.subheader('Invoice discrepancies versus delivered value')
    df=fetch("SELECT order_id,customer_name,delivered_qty,unit_price,ROUND(delivered_qty*unit_price,2) expected_invoice,invoice_amount,invoice_variance,payment_status FROM v_order_360 WHERE ABS(invoice_variance)>0.01 ORDER BY ABS(invoice_variance) DESC")
    st.metric('Invoice discrepancies',len(df));st.dataframe(df,hide_index=True,use_container_width=True)
    st.caption('Expected invoice = delivered quantity × contracted unit price. Taxes, discounts, and freight are intentionally out of scope in this simulated model.')
elif page=='Inventory alerts':
    st.subheader('Reorder point monitoring')
    df=fetch('''SELECT i.sku,p.product_name,i.warehouse,i.on_hand_qty,i.reorder_point,(i.reorder_point-i.on_hand_qty) shortage_to_reorder FROM inventory_snapshot i JOIN products p USING(sku) WHERE i.on_hand_qty<i.reorder_point ORDER BY shortage_to_reorder DESC''')
    st.metric('SKUs below reorder point',len(df));st.dataframe(df,hide_index=True,use_container_width=True)
    st.caption('Inventory snapshots are current hypothetical levels. They are not reconciled to historical shipping movements.')
else:
    st.subheader('Data quality / contract checks')
    sql={
    'Orders with missing customer':"SELECT COUNT(*) FROM orders o LEFT JOIN customers c USING(customer_id) WHERE c.customer_id IS NULL",
    'Orders with missing product':"SELECT COUNT(*) FROM orders o LEFT JOIN products p USING(sku) WHERE p.sku IS NULL",
    'Shipments without delivered orders':"SELECT COUNT(*) FROM shipments s JOIN orders o USING(order_id) WHERE o.status!='Delivered'",
    'Invoices without shipment':"SELECT COUNT(*) FROM invoices i LEFT JOIN shipments s USING(order_id) WHERE s.order_id IS NULL",
    'Negative quantities':"SELECT COUNT(*) FROM orders WHERE ordered_qty<=0",
    'Invoice discrepancies (review expected)':"SELECT COUNT(*) FROM v_order_360 WHERE ABS(invoice_variance)>0.01"}
    st.dataframe(pd.DataFrame([{'Check':k,'Count':fetch(v).iloc[0,0]} for k,v in sql.items()]),hide_index=True,use_container_width=True)
