# Money Tracker

A command line tool, written in Python, that reads a bank statement exported as a CSV file and turns it into something useful.

It sorts each transaction into a spending category, flags possible duplicate payments, reconciles the transactions against the bank's closing balance and prints a month by month summary of where the money went.

The idea came from part-time work reconciling income and expenditure in Xero, where the same checks were done by hand.

## Running it

Python 3.9 or later is needed. Nothing else has to be installed, because only the standard library is used.

```
python tracker.py sample_data/transactions.csv --opening 250.00 --closing 1106.61
```

The opening and closing balances are optional. If they are given, the program checks that the opening balance plus every transaction equals the closing balance on the statement.

## Example output

```
October 2026
----------------------------------
  Groceries            £    -61.98
  Transport            £    -53.60
  ...
  Income               £    612.45
  Net for month        £    407.30

Possible duplicate payments:
  2 x SPOTIFY P1234 on 01/11/2026 for £-11.99

Reconciliation: balances match the bank statement.
```

## Input format

The CSV file needs three columns with these headings.

| Date | Description | Amount |
| --- | --- | --- |
| 02/10/2026 | TESCO STORES SHIRLEY | -23.40 |

Dates are day/month/year. Money going out is negative and money coming in is positive.

## Tests

```
python -m unittest test_tracker.py
```

The tests cover reading amounts, categorising, duplicate detection, reconciliation and the monthly summary.

## Design choices

Money is stored as `Decimal` rather than `float`. Floating point numbers cannot represent values such as 0.10 exactly, so small errors build up when many amounts are added together, which matters when a reconciliation has to come out at exactly zero.
