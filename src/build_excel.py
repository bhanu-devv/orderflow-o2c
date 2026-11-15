"""Create spreadsheet using artifact_tool; no Excel/Power BI license required to generate it."""
import csv, sqlite3
from pathlib import Path
from artifact_tool import Workbook,SpreadsheetFile
ROOT=Path(__file__).resolve().parents[1]
wb=Workbook.create(); s=wb.worksheets.add('Daily Order Tracker'); summary=wb.worksheets.add('Executive Summary'); guide=wb.worksheets.add('Instructions')
with (ROOT/'data/orders.csv').open() as f:rows=list(csv.DictReader(f))[:250]
headers=['Order ID','Customer ID','Order Date','Promised Date','Qty','Unit Price','Order Value','Status','Priority','Blocked Reason','Queue Flag','Revenue Check']
data=[]
for i,r in enumerate(rows,2):
    data.append([r['order_id'],r['customer_id'],r['order_date'],r['promised_date'],int(r['ordered_qty']),float(r['unit_price']),None,r['status'],r['priority'],r['block_reason'],None,None])
s.get_range('A1:L1').values=[headers]
s.get_range('A2:L251').values=data
# Formula-driven flags; 250-row Excel sample, full 10k in data CSV and SQLite.
s.get_range('G2').formulas=[['=E2*F2']];s.get_range('G2:G251').fill_down()
s.get_range('K2').formulas=[['=IF(H2="Blocked","REVIEW",IF(H2="Open","MONITOR","—"))']];s.get_range('K2:K251').fill_down()
s.get_range('L2').formulas=[['=IF(ABS(G2-E2*F2)<0.01,"OK","CHECK")']];s.get_range('L2:L251').fill_down()
s.get_range('A1:L1').format={'fill':'#16324F','font':{'bold':True,'color':'#FFFFFF'},'row_height':32}
s.get_range('A1:L251').format.column_width=17
s.get_range('J1:J251').format.column_width=25
s.get_range('A1:A251').format.column_width=19
s.get_range('G2:G251').set_number_format('$#,##0.00')
s.get_range('F2:F251').set_number_format('$#,##0.00')
s.freeze_panes.freeze_rows(1)
s.get_range('H2:H251').data_validation={'rule':{'type':'list','values':['Open','Blocked','Delivered','Cancelled']}}
s.get_range('K2:K251').conditional_formats.add_custom('=K2="REVIEW"',{'fill':'#FECACA'})
summary.get_range('A1:F1').values=[['ORDERFLOW | OPERATIONS SCORECARD',None,None,None,None,None]]
summary.get_range('A1:F1').format={'fill':'#16324F','font':{'bold':True,'color':'#FFFFFF'},'row_height':36}
summary.get_range('A3:B10').values=[['Metric','Value'],['Orders in Excel sample',None],['Blocked orders',None],['Open orders',None],['Delivered orders',None],['Sample order value',None],['High / Critical priority',None],['Queue items for review',None]]
for row,form in [(4,'=COUNTA(\'Daily Order Tracker\'!A2:A251)'),(5,'=COUNTIF(\'Daily Order Tracker\'!H2:H251,"Blocked")'),(6,'=COUNTIF(\'Daily Order Tracker\'!H2:H251,"Open")'),(7,'=COUNTIF(\'Daily Order Tracker\'!H2:H251,"Delivered")'),(8,'=SUM(\'Daily Order Tracker\'!G2:G251)'),(9,'=COUNTIF(\'Daily Order Tracker\'!I2:I251,"High")+COUNTIF(\'Daily Order Tracker\'!I2:I251,"Critical")'),(10,'=COUNTIF(\'Daily Order Tracker\'!K2:K251,"REVIEW")')]:summary.get_range(f'B{row}').formulas=[[form]]
summary.get_range('A3:B3').format={'fill':'#167F85','font':{'bold':True,'color':'#FFFFFF'}}
summary.get_range('A1:F12').format.column_width=24
summary.get_range('B8').set_number_format('$#,##0.00')
summary.get_range('A13:B15').values=[['Important context',''],['Dataset sample','250 order lines from a deterministic 10,000-order synthetic data set'],['Full dataset','data/orders.csv and data/orderflow.db']]
summary.get_range('B14:B15').format.column_width=72
guide.get_range('A1:B7').values=[['ORDERFLOW | EXCEL OPERATIONS GUIDE',''],['Purpose','Demonstrate VLOOKUP-compatible order tracking, formulas, filters and case review'],['Scope','250-row editable tracker sample; complete 10,000-row data in CSV/database'],['Derived fields','Order Value (Qty x Unit Price), Queue Flag, Revenue Check'],['How to use','Filter Status=Blocked and Priority=High/Critical; review Queue Flag'],['PivotTables','In Excel use Insert > PivotTable, Source: Daily Order Tracker!A1:L251'],['Data disclaimer','All data fictional; this is not an actual Nestlé or Manpower system']]
guide.get_range('A1:B1').format={'fill':'#16324F','font':{'bold':True,'color':'#FFFFFF'}}
guide.get_range('A1:A7').format.column_width=25;guide.get_range('B1:B7').format.column_width=92
out=ROOT/'excel/OrderFlow_Operations_Tracker.xlsx';SpreadsheetFile.export_xlsx(wb).save(str(out));print('EXCEL CREATED',out,out.stat().st_size)
