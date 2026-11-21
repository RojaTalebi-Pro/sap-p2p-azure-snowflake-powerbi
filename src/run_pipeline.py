"""Runnable local landing, Silver and Gold equivalent using Python SQLite."""
import csv,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data"/"sample"
GOLD=ROOT/"data"/"gold"
GOLD.mkdir(parents=True,exist_ok=True)
def read(name):
    with (SOURCE/f"{name}.csv").open(newline="") as f:
        return list(csv.DictReader(f))
def export(name,query,db):
    cur=db.execute(query)
    cols=[x[0] for x in cur.description]
    with (GOLD/f"{name}.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(cols);w.writerows(cur.fetchall())
def main():
    db=sqlite3.connect(":memory:")
    for name in ["LFA1","EKKO","EKPO","INVOICE","GOODS_RECEIPT"]:
        rows=read(name);cols=list(rows[0])
        db.execute("CREATE TABLE "+name+" ("+",".join('"'+c+'" TEXT' for c in cols)+")")
        db.executemany("INSERT INTO "+name+" VALUES ("+",".join("?" for _ in cols)+")",[[r[c] for c in cols] for r in rows])
    db.executescript("""
    CREATE VIEW silver_po AS SELECT EBELN,BUKRS,LIFNR,substr(BEDAT,1,4)||'-'||substr(BEDAT,5,2)||'-'||substr(BEDAT,7,2) AS PO_DATE,WAERS
    FROM (SELECT *,ROW_NUMBER() OVER(PARTITION BY EBELN ORDER BY CAST(SOURCE_VERSION AS INTEGER) DESC,AEDAT DESC) rn FROM EKKO)
    WHERE rn=1 AND IS_DELETED='0';
    CREATE VIEW gold_po AS SELECT p.EBELN AS po_id,p.PO_DATE AS po_date,p.BUKRS AS company_code,p.LIFNR AS vendor_id,
    p.WAERS AS currency,ROUND(CAST(i.NETWR AS REAL),2) AS po_amount,
    CASE WHEN g.EBELN IS NOT NULL THEN 1 ELSE 0 END AS has_goods_receipt
    FROM silver_po p JOIN EKPO i ON i.EBELN=p.EBELN LEFT JOIN GOODS_RECEIPT g ON g.EBELN=p.EBELN;
    CREATE VIEW gold_invoice AS SELECT v.BELNR AS invoice_id,v.EBELN AS po_id,v.BUDAT AS invoice_date,
    p.BUKRS AS company_code,p.LIFNR AS vendor_id,ROUND(CAST(v.WRBTR AS REAL),2) AS invoice_amount,v.STATUS AS invoice_status
    FROM INVOICE v JOIN silver_po p ON p.EBELN=v.EBELN;
    """)
    export("fact_purchase_order","SELECT * FROM gold_po",db)
    export("fact_invoice","SELECT * FROM gold_invoice",db)
    export("dim_vendor","SELECT LIFNR AS vendor_id,NAME1 AS vendor_name,LAND1 AS country FROM LFA1",db)
    export("dim_company","SELECT DISTINCT BUKRS AS company_code FROM silver_po",db)
    export("dim_date","SELECT DISTINCT po_date AS calendar_date,substr(po_date,1,7) AS year_month FROM gold_po UNION SELECT DISTINCT invoice_date,substr(invoice_date,1,7) FROM gold_invoice",db)
    counts={name:db.execute("SELECT COUNT(*) FROM "+name).fetchone()[0] for name in ["gold_po","gold_invoice"]}
    assert counts["gold_po"]==400 and counts["gold_invoice"]>0
    assert db.execute("SELECT COUNT(DISTINCT po_id) FROM gold_po").fetchone()[0]==400
    print("SUCCESS: gold facts created",counts)
if __name__=="__main__":main()
