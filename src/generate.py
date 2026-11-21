"""Generate reproducible fictional SAP-shaped procurement extracts."""
import csv, random
from datetime import date, timedelta
from pathlib import Path
R=random.Random(42)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"sample"
OUT.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (OUT/f"{name}.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
vendors=[{"LIFNR":f"V{i:04d}","NAME1":f"Synthetic Supplier {i:02d}","LAND1":R.choice(["PL","DE","DK"])} for i in range(1,21)]
orders=[];items=[];invoices=[];receipts=[]
for i in range(1,401):
    po=f"{4500000000+i}"
    d=date(2025,1,1)+timedelta(days=R.randrange(660))
    vendor=R.choice(vendors)["LIFNR"]
    amount=round(R.uniform(150,25000),2)
    orders.append({"EBELN":po,"BUKRS":R.choice(["PL01","DE01"]),"LIFNR":vendor,"BEDAT":d.strftime("%Y%m%d"),"AEDAT":(d+timedelta(days=R.randrange(4))).strftime("%Y%m%d"),"WAERS":"EUR","SOURCE_VERSION":1,"IS_DELETED":0})
    items.append({"EBELN":po,"EBELP":"00010","NETWR":amount,"MENGE":R.randint(1,30),"MEINS":"EA"})
    if R.random()<.85:
        receipts.append({"EBELN":po,"EBELP":"00010","GR_DATE":(d+timedelta(days=R.randint(1,25))).isoformat(),"GR_AMOUNT":amount})
    if R.random()<.78:
        invoices.append({"BELNR":f"{5100000000+i}","EBELN":po,"BUDAT":(d+timedelta(days=R.randint(2,45))).isoformat(),"WRBTR":round(amount*R.uniform(.9,1.12),2),"STATUS":R.choice(["POSTED"]*9+["BLOCKED"])})
for old in orders[:12]:
    revision=dict(old)
    revision["SOURCE_VERSION"]=2
    revision["AEDAT"]="20261120"
    orders.append(revision)
for name,rows in [("LFA1",vendors),("EKKO",orders),("EKPO",items),("INVOICE",invoices),("GOODS_RECEIPT",receipts)]:
    save(name,rows)
print("Generated",len(orders),"PO events,",len(invoices),"invoices")
