"""
Money Tracker
=============

Reads a bank statement exported as a CSV file and:

  1. sorts every transaction into a spending category
  2. flags possible duplicate payments
  3. reconciles the transactions against the bank's closing balance
  4. prints a monthly summary of spending by category

Run it from the command line, for example:

    python tracker.py sample_data/transactions.csv --opening 250.00 --closing 1106.61

Only Python's standard library is used, so there is nothing to install.
"""

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


# ---------------------------------------------------------------------------
# 1. The data
# ---------------------------------------------------------------------------

@dataclass
class Transaction:
    """One line from the bank statement."""
    when: date
    description: str
    amount: Decimal          # money in is positive, money out is negative
    category: str = "Uncategorised"


# Keywords we look for in a transaction description, and the category each
# one belongs to. The first keyword that matches wins.
CATEGORY_RULES = {
    "APPLE RETAIL": "Income",
    "SALARY": "Income",
    "TESCO": "Groceries",
    "ALDI": "Groceries",
    "SAINSBURY": "Groceries",
    "GREGGS": "Eating out",
    "NANDOS": "Eating out",
    "COSTA": "Eating out",
    "WEST MIDLANDS RAILWAY": "Transport",
    "NATIONAL EXPRESS": "Transport",
    "SHELL": "Transport",
    "SPOTIFY": "Subscriptions",
    "NETFLIX": "Subscriptions",
    "ICLOUD": "Subscriptions",
    "BCU": "University",
    "AMAZON": "Shopping",
}


# ---------------------------------------------------------------------------
# 2. Reading the file
# ---------------------------------------------------------------------------

def parse_amount(text):
    """Turn text like '-12.50' or '£1,200.00' into an exact Decimal."""
    cleaned = text.replace("£", "").replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Could not read the amount '{text}'")


def load_transactions(path):
    """Read the CSV file and return a list of Transaction objects."""
    transactions = []
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for line_number, row in enumerate(reader, start=2):  # line 1 is the header
            try:
                when = datetime.strptime(row["Date"].strip(), "%d/%m/%Y").date()
                amount = parse_amount(row["Amount"])
            except (KeyError, ValueError) as error:
                print(f"Skipping line {line_number}: {error}")
                continue
            transactions.append(Transaction(when, row["Description"].strip(), amount))
    return transactions


# ---------------------------------------------------------------------------
# 3. Categorising
# ---------------------------------------------------------------------------

def categorise(transactions, rules=CATEGORY_RULES):
    """Give each transaction a category based on keywords in its description."""
    for t in transactions:
        description = t.description.upper()
        for keyword, category in rules.items():
            if keyword in description:
                t.category = category
                break
    return transactions


# ---------------------------------------------------------------------------
# 4. Checking for problems
# ---------------------------------------------------------------------------

def find_duplicates(transactions):
    """Return groups of transactions with the same date, description and amount."""
    seen = defaultdict(list)
    for t in transactions:
        key = (t.when, t.description.upper(), t.amount)
        seen[key].append(t)
    return [group for group in seen.values() if len(group) > 1]


def reconcile(transactions, opening, closing):
    """
    Check that opening balance + all transactions = the bank's closing balance.
    Returns the difference. Zero means everything balances.
    """
    calculated = opening + sum((t.amount for t in transactions), Decimal("0"))
    return closing - calculated


# ---------------------------------------------------------------------------
# 5. Summarising
# ---------------------------------------------------------------------------

def monthly_summary(transactions):
    """Return {'2026-10': {'Groceries': Decimal('-45.20'), ...}, ...}"""
    summary = defaultdict(lambda: defaultdict(Decimal))
    for t in transactions:
        month = t.when.strftime("%Y-%m")
        summary[month][t.category] += t.amount
    return summary


def print_report(transactions, opening=None, closing=None):
    """Print everything in a readable layout."""
    print(f"\nLoaded {len(transactions)} transactions\n")

    for month, categories in sorted(monthly_summary(transactions).items()):
        month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
        print(month_name)
        print("-" * 34)
        for category, total in sorted(categories.items(), key=lambda item: item[1]):
            print(f"  {category:<20} £{total:>10,.2f}")
        net = sum(categories.values())
        print(f"  {'Net for month':<20} £{net:>10,.2f}\n")

    uncategorised = [t for t in transactions if t.category == "Uncategorised"]
    if uncategorised:
        print("Transactions needing a category:")
        for t in uncategorised:
            print(f"  {t.when:%d/%m/%Y}  {t.description}  £{t.amount:,.2f}")
        print()

    duplicates = find_duplicates(transactions)
    if duplicates:
        print("Possible duplicate payments:")
        for group in duplicates:
            t = group[0]
            print(f"  {len(group)} x {t.description} on {t.when:%d/%m/%Y} for £{t.amount:,.2f}")
        print()

    if opening is not None and closing is not None:
        difference = reconcile(transactions, opening, closing)
        if difference == 0:
            print("Reconciliation: balances match the bank statement.")
        else:
            print(f"Reconciliation: out by £{difference:,.2f}. Check for missing transactions.")


# ---------------------------------------------------------------------------
# 6. Running from the command line
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Summarise and check a bank statement CSV.")
    parser.add_argument("csv_file", help="path to the statement CSV")
    parser.add_argument("--opening", type=Decimal, help="opening balance on the statement")
    parser.add_argument("--closing", type=Decimal, help="closing balance on the statement")
    args = parser.parse_args()

    transactions = categorise(load_transactions(args.csv_file))
    print_report(transactions, args.opening, args.closing)


if __name__ == "__main__":
    main()
