from pathlib import Path
from typing import Any
import pandas as pd

from rdflib import (
    Graph,
    Namespace,
    RDF,
    RDFS,
    Literal,
)

from rdflib.namespace import XSD


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

ER_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "entity_resolution"
)

ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "ontology"
    / "banking_ontology.ttl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

customers = pd.read_csv(
    ER_DIR / "golden_customers.csv"
)

accounts = pd.read_csv(
    PROCESSED_DIR / "accounts_clean.csv"
)

cards = pd.read_csv(
    PROCESSED_DIR / "cards_clean.csv"
)

loans = pd.read_csv(
    PROCESSED_DIR / "loans_clean.csv"
)

transactions = pd.read_csv(
    PROCESSED_DIR / "transactions_clean.csv"
)


# ============================================================
# NAMESPACE
# ============================================================

BANK = Namespace(
    "http://example.org/banking/"
)


# ============================================================
# CREATE RDF GRAPH
# ============================================================

graph = Graph()

graph.bind(
    "bank",
    BANK
)

graph.bind(
    "rdf",
    RDF
)

graph.bind(
    "rdfs",
    RDFS
)


# ============================================================
# LOAD ONTOLOGY
# ============================================================

graph.parse(
    ONTOLOGY_FILE,
    format="turtle"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_literal(
    subject: Any,
    predicate: Any,
    value: Any,
    datatype: Any = None,
) -> None:

    if pd.isna(value):
        return

    if datatype:

        graph.add(
            (
                subject,
                predicate,
                Literal(
                    value,
                    datatype=datatype,
                ),
            )
        )

    else:

        graph.add(
            (
                subject,
                predicate,
                Literal(value),
            )
        )


# ============================================================
# CUSTOMER LOOKUP
# ============================================================

customer_lookup = dict(
    zip(
        customers["crm_customer_id"],
        customers["golden_customer_id"]
    )
)


# ============================================================
# 1. CUSTOMERS
# ============================================================

for _, row in customers.iterrows():

    golden_id = row[
        "golden_customer_id"
    ]

    customer_uri = BANK[
        f"customer/{golden_id}"
    ]

    graph.add(
        (
            customer_uri,
            RDF.type,
            BANK.Customer
        )
    )

    graph.add(
        (
            customer_uri,
            RDFS.label,
            Literal(
                row["full_name"]
            )
        )
    )

    add_literal(
        customer_uri,
        BANK.customerId,
        golden_id
    )

    add_literal(
        customer_uri,
        BANK.fullName,
        row["full_name"]
    )

    add_literal(
        customer_uri,
        BANK.email,
        row["email"]
    )

    add_literal(
        customer_uri,
        BANK.phone,
        row["phone"]
    )

    add_literal(
        customer_uri,
        BANK.panNumber,
        row["pan_number"]
    )

    add_literal(
        customer_uri,
        BANK.kycStatus,
        row["kyc_status"]
    )

    add_literal(
        customer_uri,
        BANK.riskSegment,
        row["risk_segment"]
    )

    add_literal(
        customer_uri,
        BANK.dateOfBirth,
        row["date_of_birth"],
        XSD.date
    )


# ============================================================
# 2. ACCOUNTS
# ============================================================

branch_ids: set[str] = set()


for _, row in accounts.iterrows():

    account_id = row[
        "account_id"
    ]

    account_uri = BANK[
        f"account/{account_id}"
    ]

    graph.add(
        (
            account_uri,
            RDF.type,
            BANK.BankAccount
        )
    )

    add_literal(
        account_uri,
        BANK.accountId,
        account_id
    )

    add_literal(
        account_uri,
        BANK.accountType,
        row["account_type"]
    )

    add_literal(
        account_uri,
        BANK.accountStatus,
        row["account_status"]
    )

    add_literal(
        account_uri,
        BANK.balance,
        row["balance_inr"],
        XSD.decimal
    )

    add_literal(
        account_uri,
        BANK.currency,
        row["currency"]
    )

    add_literal(
        account_uri,
        BANK.openDate,
        row["open_date"],
        XSD.date
    )


    # CUSTOMER → ACCOUNT
    crm_customer_id = row[
        "customer_ref"
    ]

    golden_id = customer_lookup.get(
        crm_customer_id
    )

    if golden_id:

        customer_uri = BANK[
            f"customer/{golden_id}"
        ]

        graph.add(
            (
                customer_uri,
                BANK.holdsAccount,
                account_uri
            )
        )


    # ACCOUNT → BRANCH
    branch_id = row[
        "branch_id"
    ]

    if pd.notna(branch_id):

        branch_ids.add(
            branch_id
        )

        branch_uri = BANK[
            f"branch/{branch_id}"
        ]

        graph.add(
            (
                account_uri,
                BANK.maintainedAt,
                branch_uri
            )
        )


# ============================================================
# 3. BRANCHES
# ============================================================

for branch_id in branch_ids:

    branch_uri = BANK[
        f"branch/{branch_id}"
    ]

    graph.add(
        (
            branch_uri,
            RDF.type,
            BANK.Branch
        )
    )

    add_literal(
        branch_uri,
        BANK.branchId,
        branch_id
    )


# ============================================================
# 4. CARDS
# ============================================================

for _, row in cards.iterrows():

    card_id = row[
        "card_id"
    ]

    card_uri = BANK[
        f"card/{card_id}"
    ]

    graph.add(
        (
            card_uri,
            RDF.type,
            BANK.Card
        )
    )

    add_literal(
        card_uri,
        BANK.cardId,
        card_id
    )

    add_literal(
        card_uri,
        BANK.cardType,
        row["card_type"]
    )

    add_literal(
        card_uri,
        BANK.network,
        row["network"]
    )

    add_literal(
        card_uri,
        BANK.cardStatus,
        row["card_status"]
    )

    add_literal(
        card_uri,
        BANK.creditLimit,
        row["credit_limit_inr"],
        XSD.decimal
    )

    add_literal(
        card_uri,
        BANK.issueDate,
        row["issue_date"],
        XSD.date
    )


    # ACCOUNT → CARD
    account_id = row[
        "linked_account_id"
    ]

    account_uri = BANK[
        f"account/{account_id}"
    ]

    graph.add(
        (
            account_uri,
            BANK.linkedCard,
            card_uri
        )
    )


# ============================================================
# 5. LOANS
# ============================================================

for _, row in loans.iterrows():

    loan_id = row[
        "loan_id"
    ]

    loan_uri = BANK[
        f"loan/{loan_id}"
    ]

    graph.add(
        (
            loan_uri,
            RDF.type,
            BANK.Loan
        )
    )

    add_literal(
        loan_uri,
        BANK.loanId,
        loan_id
    )

    add_literal(
        loan_uri,
        BANK.loanType,
        row["loan_type"]
    )

    add_literal(
        loan_uri,
        BANK.principalAmount,
        row["principal_inr"],
        XSD.decimal
    )

    add_literal(
        loan_uri,
        BANK.interestRate,
        row["interest_rate"],
        XSD.decimal
    )

    add_literal(
        loan_uri,
        BANK.tenureMonths,
        row["tenure_months"],
        XSD.integer
    )

    add_literal(
        loan_uri,
        BANK.loanStatus,
        row["loan_status"]
    )

    add_literal(
        loan_uri,
        BANK.sanctionDate,
        row["sanction_date"],
        XSD.date
    )


    # CUSTOMER → LOAN
    crm_customer_id = row[
        "borrower_customer_ref"
    ]

    golden_id = customer_lookup.get(
        crm_customer_id
    )

    if golden_id:

        customer_uri = BANK[
            f"customer/{golden_id}"
        ]

        graph.add(
            (
                customer_uri,
                BANK.borrowerOf,
                loan_uri
            )
        )


# ============================================================
# 6. TRANSACTIONS
# ============================================================

for _, row in transactions.iterrows():

    transaction_id = row[
        "transaction_id"
    ]

    transaction_uri = BANK[
        f"transaction/{transaction_id}"
    ]

    graph.add(
        (
            transaction_uri,
            RDF.type,
            BANK.Transaction
        )
    )

    add_literal(
        transaction_uri,
        BANK.transactionId,
        transaction_id
    )

    add_literal(
        transaction_uri,
        BANK.transactionType,
        row["transaction_type"]
    )

    add_literal(
        transaction_uri,
        BANK.direction,
        row["direction"]
    )

    add_literal(
        transaction_uri,
        BANK.amount,
        row["amount_inr"],
        XSD.decimal
    )

    add_literal(
        transaction_uri,
        BANK.merchantCategory,
        row["merchant_category"]
    )

    add_literal(
        transaction_uri,
        BANK.channel,
        row["channel"]
    )

    add_literal(
        transaction_uri,
        BANK.transactionTimestamp,
        row["transaction_ts"],
        XSD.dateTime
    )


    # ACCOUNT → TRANSACTION
    account_id = row[
        "account_id"
    ]

    account_uri = BANK[
        f"account/{account_id}"
    ]

    graph.add(
        (
            account_uri,
            BANK.hasTransaction,
            transaction_uri
        )
    )


# ============================================================
# SERIALIZE RDF
# ============================================================

output_file = (
    OUTPUT_DIR
    / "banking_knowledge_graph.ttl"
)

graph.serialize(
    destination=str(output_file),
    format="turtle"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 65)

print(
    "BANKING KNOWLEDGE GRAPH CREATED"
)

print("=" * 65)

print(
    f"Total RDF triples: {len(graph)}"
)

print(
    f"Customers: {len(customers)}"
)

print(
    f"Accounts: {len(accounts)}"
)

print(
    f"Cards: {len(cards)}"
)

print(
    f"Loans: {len(loans)}"
)

print(
    f"Transactions: {len(transactions)}"
)

print(
    f"Branches: {len(branch_ids)}"
)

print(
    f"\nRDF saved to:\n{output_file}"
)
