# Banking Ontology Design

## Purpose

The ontology provides a canonical semantic representation
for customer, account, card, loan, transaction, and branch
information sourced from multiple banking systems.

## Core Classes

- Customer
- FinancialAccount
- BankAccount
- Card
- Loan
- Transaction
- Branch

## Object Properties

- holdsAccount
- borrowerOf
- linkedCard
- hasTransaction
- maintainedAt

## Identity Strategy

Customer resources use Golden Customer IDs created after
entity resolution.

Example:

customer/GC0000001

Accounts use source-stable identifiers.

Example:

account/ACC0000001

## Design Principles

1. Separate source schemas from canonical semantics.
2. Use stable identifiers instead of names as identity.
3. Model real relationships as object properties.
4. Model scalar attributes as datatype properties.
5. Maintain clear domain and range semantics.
6. Use SHACL separately for validation constraints.
