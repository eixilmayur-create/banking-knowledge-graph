import os
from typing import Any, cast

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


neo4j_uri = os.getenv("NEO4J_URI") or "bolt://localhost:7687"
neo4j_username = os.getenv("NEO4J_USERNAME") or "neo4j"
neo4j_password = os.getenv("NEO4J_PASSWORD")
if not neo4j_password:
    raise RuntimeError("Missing required configuration value: NEO4J_PASSWORD")

driver: Any = GraphDatabase.driver(  # type: ignore[reportUnknownMemberType]
    neo4j_uri,
    auth=(neo4j_username, neo4j_password),
)


DATABASE = os.getenv(
    "NEO4J_DATABASE",
    "neo4j"
)


QUERIES = {


    # ========================================================
    # CUSTOMER 360
    # ========================================================

    "CUSTOMER_360": """

    MATCH (c:Customer {
        customerId: $customer_id
    })

    OPTIONAL MATCH
    (c)-[:HOLDS_ACCOUNT]->
    (a:BankAccount)

    OPTIONAL MATCH
    (c)-[:BORROWER_OF]->
    (l:Loan)

    OPTIONAL MATCH
    (a)-[:HAS_CARD]->
    (card:Card)

    OPTIONAL MATCH
    (a)-[:HAS_TRANSACTION]->
    (t:Transaction)

    RETURN

        c.customerId AS customerId,
        c.name AS customerName,
        c.city AS city,
        c.kycStatus AS kycStatus,
        c.riskSegment AS riskSegment,

        collect(
            DISTINCT {
                accountId:
                    a.accountId,

                accountType:
                    a.accountType,

                balance:
                    a.balance
            }
        ) AS accounts,

        collect(
            DISTINCT {
                loanId:
                    l.loanId,

                loanType:
                    l.loanType,

                principal:
                    l.principal,

                status:
                    l.loanStatus
            }
        ) AS loans,

        collect(
            DISTINCT card.cardId
        ) AS cards,

        count(
            DISTINCT t
        ) AS transactionCount

    """,


    # ========================================================
    # CUSTOMER ACCOUNTS
    # ========================================================

    "CUSTOMER_ACCOUNTS": """

    MATCH
    (c:Customer {
        customerId: $customer_id
    })
    -[:HOLDS_ACCOUNT]->
    (a:BankAccount)

    RETURN
        c.customerId AS customerId,
        c.name AS customerName,
        a.accountId AS accountId,
        a.accountType AS accountType,
        a.accountStatus AS status,
        a.balance AS balance,
        a.currency AS currency

    ORDER BY
        a.accountId

    """,


    # ========================================================
    # CUSTOMER LOANS
    # ========================================================

    "CUSTOMER_LOANS": """

    MATCH
    (c:Customer {
        customerId: $customer_id
    })
    -[:BORROWER_OF]->
    (l:Loan)

    RETURN
        c.customerId AS customerId,
        c.name AS customerName,
        l.loanId AS loanId,
        l.loanType AS loanType,
        l.principal AS principal,
        l.interestRate AS interestRate,
        l.tenureMonths AS tenureMonths,
        l.loanStatus AS status,
        l.sanctionDate AS sanctionDate

    ORDER BY
        l.principal DESC

    """,


    # ========================================================
    # CUSTOMER TRANSACTIONS
    # ========================================================

    "CUSTOMER_TRANSACTIONS": """

    MATCH
    (c:Customer {
        customerId: $customer_id
    })
    -[:HOLDS_ACCOUNT]->
    (a:BankAccount)
    -[:HAS_TRANSACTION]->
    (t:Transaction)

    RETURN
        c.customerId AS customerId,
        c.name AS customerName,
        a.accountId AS accountId,
        t.transactionId AS transactionId,
        t.transactionType AS transactionType,
        t.amount AS amount,
        t.direction AS direction,
        t.channel AS channel,
        t.transactionTimestamp AS timestamp

    ORDER BY
        t.transactionTimestamp DESC

    LIMIT 100

    """,


    # ========================================================
    # HIGH-RISK ACTIVE LOANS
    # ========================================================

    "HIGH_RISK_ACTIVE_LOANS": """

    MATCH
    (c:Customer)
    -[:BORROWER_OF]->
    (l:Loan)

    WHERE
        c.riskSegment = "HIGH"

        AND

        l.loanStatus = "ACTIVE"

    RETURN
        c.customerId AS customerId,
        c.name AS customerName,
        l.loanId AS loanId,
        l.loanType AS loanType,
        l.principal AS principal,
        l.interestRate AS interestRate

    ORDER BY
        l.principal DESC

    LIMIT 100

    """,


    # ========================================================
    # SHARED BENEFICIARIES
    # ========================================================

    "SHARED_BENEFICIARIES": """

    MATCH
    (c1:Customer)
    -[:HAS_BENEFICIARY]->
    (b:Beneficiary)
    <-[:HAS_BENEFICIARY]-
    (c2:Customer)

    WHERE
        c1.customerId
        <
        c2.customerId

    RETURN
        c1.customerId AS customer1,
        c1.name AS customer1Name,

        c2.customerId AS customer2,
        c2.name AS customer2Name,

        b.beneficiaryId
            AS sharedBeneficiary,

        b.beneficiaryType
            AS beneficiaryType

    LIMIT 100

    """,


    # ========================================================
    # SHARED ADDRESS
    # ========================================================

    "SHARED_ADDRESS": """

    MATCH
    (c1:Customer)
    -[:HAS_ADDRESS]->
    (a:Address)
    <-[:HAS_ADDRESS]-
    (c2:Customer)

    WHERE
        c1.customerId
        <
        c2.customerId

    RETURN
        c1.customerId AS customer1,
        c1.name AS customer1Name,

        c2.customerId AS customer2,
        c2.name AS customer2Name,

        a.addressId AS addressId,
        a.city AS city

    LIMIT 100

    """,


    # ========================================================
    # CONNECTION PATH
    # ========================================================

    "CUSTOMER_CONNECTION_PATH": """

    MATCH
    (c1:Customer {
        customerId: $customer_id
    }),

    (c2:Customer {
        customerId: $customer_id_2
    })

    MATCH path =
        shortestPath(
            (c1)-[*..6]-(c2)
        )

    RETURN
        [node IN nodes(path) |
            {
                labels: labels(node),
                customerId:
                    node.customerId,
                accountId:
                    node.accountId,
                beneficiaryId:
                    node.beneficiaryId,
                addressId:
                    node.addressId,
                loanId:
                    node.loanId
            }
        ] AS nodes,

        [relationship IN relationships(path) |
            type(relationship)
        ] AS relationships,

        length(path)
            AS pathLength

    LIMIT 1

    """
}


def retrieve_graph_context(
    routing_result: dict[str, Any],
) -> list[dict[str, Any]]:

    intent = routing_result[
        "intent"
    ]

    if intent not in QUERIES:
        return []

    parameters: dict[str, Any] = {
        "customer_id": routing_result.get("customer_id"),
        "customer_id_2": routing_result.get("customer_id_2"),
    }

    with driver.session(database=DATABASE) as session:
        result = session.run(
            cast(Any, QUERIES[intent]),
            **parameters,
        )
        return [
            record.data()
            for record in result
        ]


def close_driver():

    driver.close()
