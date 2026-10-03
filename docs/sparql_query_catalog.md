# SPARQL Query Catalog

## Purpose

This catalog documents semantic quality and business queries
used against the Banking Knowledge Graph.

## Q01 — Customers Without Products

Purpose:
Identify Customer entities that do not have an Account or Loan.

Type:
Data quality / orphan detection.

## Q02 — Accounts Without Customer

Purpose:
Detect BankAccount entities that are not linked to a Customer.

Type:
Relationship integrity.

## Q03 — Loans Without Borrower

Purpose:
Detect Loan entities without a Customer borrower relationship.

Type:
Relationship integrity.

## Q04 — Transactions Without Account

Purpose:
Detect Transaction entities that are not connected to a
BankAccount.

Type:
Orphan detection.

## Q05 — High-Risk Customers With Active Loans

Purpose:
Retrieve HIGH risk-segment customers connected to ACTIVE loans.

Type:
Business review query.

## Q06 — Customer Product Summary

Purpose:
Count Accounts and Loans associated with each Customer.

Type:
Customer 360 / graph analytics.

## Q07 — Account Transaction Summary

Purpose:
Calculate transaction counts and aggregate transaction value
per BankAccount.

Type:
Graph analytics.

## Q08 — Multi-Product Customers

Purpose:
Identify customers that hold both Accounts and Loans.

Type:
Customer 360.

## Q09 — Customer Transaction Traversal

Purpose:
Traverse Customer → BankAccount → Transaction.

Type:
Graph traversal.
