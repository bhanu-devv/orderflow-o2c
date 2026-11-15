import sqlite3, unittest
from pathlib import Path
DB=Path(__file__).resolve().parents[1]/'data'/'orderflow.db'
class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.conn=sqlite3.connect(DB)
    @classmethod
    def tearDownClass(cls): cls.conn.close()
    def q(self,sql):return self.conn.execute(sql).fetchone()[0]
    def test_count(self):self.assertEqual(self.q('SELECT COUNT(*) FROM orders'),10000)
    def test_foreign_keys(self):self.assertEqual(len(self.conn.execute('PRAGMA foreign_key_check').fetchall()),0)
    def test_delivered_have_shipments(self):self.assertEqual(self.q("SELECT COUNT(*) FROM orders o LEFT JOIN shipments s USING(order_id) WHERE o.status='Delivered' AND s.order_id IS NULL"),0)
    def test_invoice_one_per_delivery(self):self.assertEqual(self.q('SELECT COUNT(*) FROM invoices'),self.q('SELECT COUNT(*) FROM shipments'))
    def test_nonnegative(self):self.assertEqual(self.q('SELECT COUNT(*) FROM orders WHERE ordered_qty<=0 OR order_amount<=0'),0)
    def test_expected_otif(self):self.assertEqual(self.q('SELECT SUM(otif_flag) FROM v_order_360'),5378)
    def test_case_orders_exist(self):self.assertEqual(self.q('SELECT COUNT(*) FROM cases c LEFT JOIN orders o USING(order_id) WHERE o.order_id IS NULL'),0)
if __name__=='__main__':unittest.main()
