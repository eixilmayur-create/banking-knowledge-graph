from pathlib import Path
import os
from typing import Any, LiteralString, cast

import pandas as pd

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "neo4j"
)


BATCH_SIZE = 500


NEO4J_URI = get_required_env("NEO4J_URI")
NEO4J_USERNAME = get_required_env("NEO4J_USERNAME")
NEO4J_PASSWORD = get_required_env("NEO4J_PASSWORD")


driver = cast(
    Any,
    GraphDatabase.driver(  # type: ignore[reportCallIssue]
        NEO4J_URI,
        auth=(
            NEO4J_USERNAME,
            NEO4J_PASSWORD,
        ),
    ),
)


DATABASE = os.getenv(
    "NEO4J_DATABASE",
    "neo4j",
)


# ============================================================
# CONNECTION CHECK
# ============================================================

driver.verify_connectivity()

print(
    "Cloud Neo4j connection verified."
)


# ============================================================
# HELPERS
# ============================================================

def clean_rows(
    dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:

    records = dataframe.where(
        pd.notnull(dataframe),
        None,
    ).to_dict(
        orient="records"
    )

    return [
        {
            str(key): val
            for key, val in record.items()
        }
        for record in records
    ]


def run_batches(
    dataframe: pd.DataFrame,
    query: str,
    label: str,
) -> None:

    total = len(
        dataframe
    )

    print(
        f"\nLoading {label}: "
        f"{total} rows"
    )

    with driver.session(
        database=DATABASE
    ) as session:

        for start in range(
            0,
            total,
            BATCH_SIZE,
        ):

            batch = dataframe.iloc[
                start:
                start + BATCH_SIZE
            ]

            rows = clean_rows(
                batch
            )

            session.run(
                Query(cast(LiteralString, query)),
                rows=rows,
            ).consume()

            loaded = min(
                start + BATCH_SIZE,
                total,
            )

            print(
                f"{label}: "
                f"{loaded}/{total}"
            )


# ============================================================
# CONSTRAINTS
# ============================================================

constraints = [

    """
    CREATE CONSTRAINT customer_id_unique
    IF NOT EXISTS
    FOR (c:Customer)
    REQUIRE c.customerId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT account_id_unique
    IF NOT EXISTS
    FOR (a:BankAccount)
    REQUIRE a.accountId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT card_id_unique
    IF NOT EXISTS
    FOR (c:Card)
    REQUIRE c.cardId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT loan_id_unique
    IF NOT EXISTS
    FOR (l:Loan)
    REQUIRE l.loanId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT transaction_id_unique
    IF NOT EXISTS
    FOR (t:Transaction)
    REQUIRE t.transactionId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT branch_id_unique
    IF NOT EXISTS
    FOR (b:Branch)
    REQUIRE b.branchId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT address_id_unique
    IF NOT EXISTS
    FOR (a:Address)
    REQUIRE a.addressId IS UNIQUE
    """,

    """
    CREATE CONSTRAINT beneficiary_id_unique
    IF NOT EXISTS
    FOR (b:Beneficiary)
    REQUIRE b.beneficiaryId IS UNIQUE
    """,
]


with driver.session(
    database=DATABASE
) as session:

    for query in constraints:

        session.run(
            Query(cast(LiteralString, query))
        ).consume()


print(
    "Constraints created."
)


# ============================================================
# CUSTOMERS
# ============================================================

customers = pd.read_csv(
    DATA_DIR / "customers.csv"
)


run_batches(
    customers,

    """
    UNWIND $rows AS row

    MERGE (c:Customer {
        customerId: row.customerId
    })

    SET
        c.name =
            row.name,

        c.dateOfBirth =
            row.dateOfBirth,

        c.email =
            row.email,

        c.phone =
            row.phone,

        c.panNumber =
            row.panNumber,

        c.city =
            row.city,

        c.state =
            row.state,

        c.kycStatus =
            row.kycStatus,

        c.riskSegment =
            row.riskSegment
    """,

    "Customers",
)


# ============================================================
# ACCOUNTS
# ============================================================

accounts = pd.read_csv(
    DATA_DIR / "accounts.csv"
)


run_batches(
    accounts,

    """
    UNWIND $rows AS row

    MERGE (a:BankAccount {
        accountId: row.accountId
    })

    SET
        a.accountType =
            row.accountType,

        a.accountStatus =
            row.accountStatus,

        a.balance =
            toFloat(row.balance),

        a.currency =
            row.currency,

        a.openDate =
            row.openDate
    """,

    "Accounts",
)


# ============================================================
# CARDS
# ============================================================

cards = pd.read_csv(
    DATA_DIR / "cards.csv"
)


run_batches(
    cards,

    """
    UNWIND $rows AS row

    MERGE (c:Card {
        cardId: row.cardId
    })

    SET
        c.cardType =
            row.cardType,

        c.network =
            row.network,

        c.cardStatus =
            row.cardStatus,

        c.creditLimit =
            toFloat(row.creditLimit),

        c.issueDate =
            row.issueDate
    """,

    "Cards",
)


# ============================================================
# LOANS
# ============================================================

loans = pd.read_csv(
    DATA_DIR / "loans.csv"
)


run_batches(
    loans,

    """
    UNWIND $rows AS row

    MERGE (l:Loan {
        loanId: row.loanId
    })

    SET
        l.loanType =
            row.loanType,

        l.principal =
            toFloat(row.principal),

        l.interestRate =
            toFloat(row.interestRate),

        l.tenureMonths =
            toInteger(row.tenureMonths),

        l.loanStatus =
            row.loanStatus,

        l.sanctionDate =
            row.sanctionDate
    """,

    "Loans",
)


# ============================================================
# TRANSACTIONS
# ============================================================

transactions = pd.read_csv(
    DATA_DIR / "transactions.csv"
)


run_batches(
    transactions,

    """
    UNWIND $rows AS row

    MERGE (t:Transaction {
        transactionId: row.transactionId
    })

    SET
        t.transactionTimestamp =
            row.transactionTimestamp,

        t.transactionType =
            row.transactionType,

        t.direction =
            row.direction,

        t.amount =
            toFloat(row.amount),

        t.channel =
            row.channel,

        t.merchantCategory =
            row.merchantCategory
    """,

    "Transactions",
)


# ============================================================
# BRANCHES
# ============================================================

branches = pd.read_csv(
    DATA_DIR / "branches.csv"
)


run_batches(
    branches,

    """
    UNWIND $rows AS row

    MERGE (b:Branch {
        branchId: row.branchId
    })
    """,

    "Branches",
)


# ============================================================
# OPTIONAL NETWORK ENTITIES
# ============================================================

address_file = (
    DATA_DIR
    / "addresses.csv"
)


if address_file.exists():

    addresses = pd.read_csv(
        address_file
    )

    run_batches(
        addresses,

        """
        UNWIND $rows AS row

        MERGE (a:Address {
            addressId:
                row.addressId
        })

        SET
            a.city =
                row.city,

            a.postalCode =
                row.postalCode
        """,

        "Addresses",
    )


beneficiary_file = (
    DATA_DIR
    / "beneficiaries.csv"
)


if beneficiary_file.exists():

    beneficiaries = pd.read_csv(
        beneficiary_file
    )

    run_batches(
        beneficiaries,

        """
        UNWIND $rows AS row

        MERGE (b:Beneficiary {
            beneficiaryId:
                row.beneficiaryId
        })

        SET
            b.beneficiaryType =
                row.beneficiaryType
        """,

        "Beneficiaries",
    )


# ============================================================
# RELATIONSHIP LOADER
# ============================================================

relationship_jobs = [

    (
        "rel_customer_account.csv",

        """
        UNWIND $rows AS row

        MATCH (c:Customer {
            customerId:
                row.customerId
        })

        MATCH (a:BankAccount {
            accountId:
                row.accountId
        })

        MERGE
        (c)-[:HOLDS_ACCOUNT]->(a)
        """,

        "HOLDS_ACCOUNT",
    ),

    (
        "rel_customer_loan.csv",

        """
        UNWIND $rows AS row

        MATCH (c:Customer {
            customerId:
                row.customerId
        })

        MATCH (l:Loan {
            loanId:
                row.loanId
        })

        MERGE
        (c)-[:BORROWER_OF]->(l)
        """,

        "BORROWER_OF",
    ),

    (
        "rel_account_card.csv",

        """
        UNWIND $rows AS row

        MATCH (a:BankAccount {
            accountId:
                row.accountId
        })

        MATCH (c:Card {
            cardId:
                row.cardId
        })

        MERGE
        (a)-[:HAS_CARD]->(c)
        """,

        "HAS_CARD",
    ),

    (
        "rel_account_transaction.csv",

        """
        UNWIND $rows AS row

        MATCH (a:BankAccount {
            accountId:
                row.accountId
        })

        MATCH (t:Transaction {
            transactionId:
                row.transactionId
        })

        MERGE
        (a)-[:HAS_TRANSACTION]->(t)
        """,

        "HAS_TRANSACTION",
    ),

    (
        "rel_account_branch.csv",

        """
        UNWIND $rows AS row

        MATCH (a:BankAccount {
            accountId:
                row.accountId
        })

        MATCH (b:Branch {
            branchId:
                row.branchId
        })

        MERGE
        (a)-[:MAINTAINED_AT]->(b)
        """,

        "MAINTAINED_AT",
    ),

    (
        "rel_customer_address.csv",

        """
        UNWIND $rows AS row

        MATCH (c:Customer {
            customerId:
                row.customerId
        })

        MATCH (a:Address {
            addressId:
                row.addressId
        })

        MERGE
        (c)-[:HAS_ADDRESS]->(a)
        """,

        "HAS_ADDRESS",
    ),

    (
        "rel_customer_beneficiary.csv",

        """
        UNWIND $rows AS row

        MATCH (c:Customer {
            customerId:
                row.customerId
        })

        MATCH (b:Beneficiary {
            beneficiaryId:
                row.beneficiaryId
        })

        MERGE
        (c)-[:HAS_BENEFICIARY]->(b)
        """,

        "HAS_BENEFICIARY",
    ),
]


for (
    filename,
    query,
    label,
) in relationship_jobs:

    file_path = (
        DATA_DIR
        / filename
    )

    if not file_path.exists():

        print(
            f"Skipping {filename}: "
            "file not found"
        )

        continue


    dataframe = pd.read_csv(
        file_path
    )


    run_batches(
        dataframe,
        query,
        label,
    )


driver.close()


print(
    "\nCloud graph bootstrap complete."
)
