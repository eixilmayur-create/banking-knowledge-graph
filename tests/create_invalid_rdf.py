from pathlib import Path

from rdflib import (
    Graph,
    Namespace,
    RDF,
    Literal,
)

from rdflib.namespace import XSD


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
    / "banking_knowledge_graph.ttl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
    / "banking_knowledge_graph_invalid.ttl"
)


BANK = Namespace(
    "http://example.org/banking/"
)


graph = Graph()

graph.parse(
    SOURCE_FILE,
    format="turtle"
)


# ============================================================
# INVALID CUSTOMER
# No customerId
# Invalid KYC
# ============================================================

bad_customer = BANK[
    "customer/TEST_BAD_CUSTOMER"
]

graph.add(
    (
        bad_customer,
        RDF.type,
        BANK.Customer
    )
)

graph.add(
    (
        bad_customer,
        BANK.fullName,
        Literal("Test Customer")
    )
)

graph.add(
    (
        bad_customer,
        BANK.kycStatus,
        Literal("UNKNOWN")
    )
)


# ============================================================
# INVALID LOAN
# Negative principal
# ============================================================

bad_loan = BANK[
    "loan/TEST_BAD_LOAN"
]

graph.add(
    (
        bad_loan,
        RDF.type,
        BANK.Loan
    )
)

graph.add(
    (
        bad_loan,
        BANK.loanId,
        Literal("TEST_BAD_LOAN")
    )
)

graph.add(
    (
        bad_loan,
        BANK.loanType,
        Literal("PERSONAL")
    )
)

graph.add(
    (
        bad_loan,
        BANK.principalAmount,
        Literal(
            "-50000",
            datatype=XSD.decimal
        )
    )
)

graph.add(
    (
        bad_loan,
        BANK.interestRate,
        Literal(
            "10",
            datatype=XSD.decimal
        )
    )
)

graph.add(
    (
        bad_loan,
        BANK.tenureMonths,
        Literal(
            "12",
            datatype=XSD.integer
        )
    )
)


# ============================================================
# INVALID TRANSACTION
# Zero amount and invalid direction
# ============================================================

bad_transaction = BANK[
    "transaction/TEST_BAD_TXN"
]

graph.add(
    (
        bad_transaction,
        RDF.type,
        BANK.Transaction
    )
)

graph.add(
    (
        bad_transaction,
        BANK.transactionId,
        Literal("TEST_BAD_TXN")
    )
)

graph.add(
    (
        bad_transaction,
        BANK.amount,
        Literal(
            "0",
            datatype=XSD.decimal
        )
    )
)

graph.add(
    (
        bad_transaction,
        BANK.direction,
        Literal("UNKNOWN")
    )
)


graph.serialize(
    destination=str(OUTPUT_FILE),
    format="turtle"
)


print(
    f"Invalid test graph created:\n"
    f"{OUTPUT_FILE}"
)
