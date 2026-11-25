"""
Tests for tracker.py. Run them with:

    python -m unittest test_tracker.py
"""

import unittest
from datetime import date
from decimal import Decimal

from tracker import (Transaction, categorise, find_duplicates, monthly_summary,
                     parse_amount, reconcile)


class TestParseAmount(unittest.TestCase):

    def test_plain_number(self):
        self.assertEqual(parse_amount("-12.50"), Decimal("-12.50"))

    def test_pound_sign_and_commas(self):
        self.assertEqual(parse_amount("£1,200.00"), Decimal("1200.00"))

    def test_rubbish_raises_error(self):
        with self.assertRaises(ValueError):
            parse_amount("twelve pounds")


class TestCategorise(unittest.TestCase):

    def test_known_keyword(self):
        t = Transaction(date(2026, 10, 1), "Tesco Stores Shirley", Decimal("-5"))
        categorise([t])
        self.assertEqual(t.category, "Groceries")

    def test_unknown_stays_uncategorised(self):
        t = Transaction(date(2026, 10, 1), "PAYPAL *VINTED", Decimal("-5"))
        categorise([t])
        self.assertEqual(t.category, "Uncategorised")


class TestChecks(unittest.TestCase):

    def test_finds_duplicate(self):
        a = Transaction(date(2026, 11, 1), "SPOTIFY", Decimal("-11.99"))
        b = Transaction(date(2026, 11, 1), "SPOTIFY", Decimal("-11.99"))
        c = Transaction(date(2026, 11, 2), "SPOTIFY", Decimal("-11.99"))
        self.assertEqual(len(find_duplicates([a, b, c])), 1)

    def test_reconcile_balances(self):
        ts = [Transaction(date(2026, 10, 1), "X", Decimal("-10.00")),
              Transaction(date(2026, 10, 2), "Y", Decimal("25.50"))]
        self.assertEqual(reconcile(ts, Decimal("100"), Decimal("115.50")), 0)

    def test_reconcile_spots_gap(self):
        ts = [Transaction(date(2026, 10, 1), "X", Decimal("-10.00"))]
        self.assertEqual(reconcile(ts, Decimal("100"), Decimal("80")), Decimal("-10.00"))

    def test_decimal_avoids_float_error(self):
        # 0.1 + 0.2 is 0.30000000000000004 with floats, but exact with Decimal
        ts = [Transaction(date(2026, 10, 1), "X", Decimal("0.10")),
              Transaction(date(2026, 10, 1), "Y", Decimal("0.20"))]
        self.assertEqual(reconcile(ts, Decimal("0"), Decimal("0.30")), 0)


class TestSummary(unittest.TestCase):

    def test_groups_by_month_and_category(self):
        ts = categorise([
            Transaction(date(2026, 10, 3), "TESCO", Decimal("-10")),
            Transaction(date(2026, 10, 9), "ALDI", Decimal("-5")),
            Transaction(date(2026, 11, 1), "TESCO", Decimal("-7")),
        ])
        summary = monthly_summary(ts)
        self.assertEqual(summary["2026-10"]["Groceries"], Decimal("-15"))
        self.assertEqual(summary["2026-11"]["Groceries"], Decimal("-7"))


if __name__ == "__main__":
    unittest.main()
