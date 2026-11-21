import csv,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,str(ROOT/"src/generate.py")],check=True)
        subprocess.run([sys.executable,str(ROOT/"src/run_pipeline.py")],check=True)
    def test_no_duplicate_purchase_orders(self):
        with (ROOT/"data/gold/fact_purchase_order.csv").open() as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),400)
        self.assertEqual(len({r["po_id"] for r in rows}),400)
        self.assertTrue(all(float(r["po_amount"])>0 for r in rows))
    def test_invoice_references(self):
        with (ROOT/"data/gold/fact_purchase_order.csv").open() as f: po={r["po_id"] for r in csv.DictReader(f)}
        with (ROOT/"data/gold/fact_invoice.csv").open() as f: inv=list(csv.DictReader(f))
        self.assertTrue(inv)
        self.assertTrue(all(r["po_id"] in po for r in inv))
if __name__=="__main__":unittest.main()
