from pathlib import Path
from rdflib import Graph, RDF, Namespace


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RDF_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
    / "banking_knowledge_graph.ttl"
)

BANK = Namespace(
    "http://example.org/banking/"
)


graph = Graph()

graph.parse(
    RDF_FILE,
    format="turtle"
)


# ============================================================
# COUNTS
# ============================================================

customers = set(
    graph.subjects(
        RDF.type,
        BANK.Customer
    )
)

accounts = set(
    graph.subjects(
        RDF.type,
        BANK.BankAccount
    )
)

cards = set(
    graph.subjects(
        RDF.type,
        BANK.Card
    )
)

loans = set(
    graph.subjects(
        RDF.type,
        BANK.Loan
    )
)

transactions = set(
    graph.subjects(
        RDF.type,
        BANK.Transaction
    )
)


print("=" * 60)
print("RDF VERIFICATION")
print("=" * 60)

print(
    "Total triples:",
    len(graph)
)

print(
    "Customers:",
    len(customers)
)

print(
    "Accounts:",
    len(accounts)
)

print(
    "Cards:",
    len(cards)
)

print(
    "Loans:",
    len(loans)
)

print(
    "Transactions:",
    len(transactions)
)
