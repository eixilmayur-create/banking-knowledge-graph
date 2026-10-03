from src.api.database import execute_query


# ============================================================
# CUSTOMER 360
# ============================================================

def get_customer(
    customer_id: str
):

    query = """
    MATCH (c:Customer {
        customerId: $customer_id
    })

    OPTIONAL MATCH
    (c)-[:HOLDS_ACCOUNT]->(a:BankAccount)

    OPTIONAL MATCH
    (c)-[:BORROWER_OF]->(l:Loan)

    OPTIONAL MATCH
    (a)-[:HAS_CARD]->(card:Card)

    OPTIONAL MATCH
    (a)-[:HAS_TRANSACTION]->(t:Transaction)

    RETURN

        c.customerId AS customerId,
        c.name AS name,
        c.city AS city,
        c.state AS state,
        c.kycStatus AS kycStatus,
        c.riskSegment AS riskSegment,

        collect(
            DISTINCT {
                accountId: a.accountId,
                accountType: a.accountType,
                balance: a.balance,
                status: a.accountStatus
            }
        ) AS accounts,

        collect(
            DISTINCT {
                loanId: l.loanId,
                loanType: l.loanType,
                principal: l.principal,
                status: l.loanStatus
            }
        ) AS loans,

        collect(
            DISTINCT card.cardId
        ) AS cards,

        count(
            DISTINCT t
        ) AS transactionCount
    """

    rows = execute_query(
        query,
        {
            "customer_id":
                customer_id
        }
    )

    if not rows:
        return None

    return rows[0]


# ============================================================
# CUSTOMER ACCOUNTS
# ============================================================

def get_customer_accounts(
    customer_id: str
):

    query = """
    MATCH
    (c:Customer {
        customerId: $customer_id
    })
    -[:HOLDS_ACCOUNT]->
    (a:BankAccount)

    RETURN
        a.accountId AS accountId,
        a.accountType AS accountType,
        a.accountStatus AS status,
        a.balance AS balance,
        a.currency AS currency,
        a.openDate AS openDate

    ORDER BY a.accountId
    """

    return execute_query(
        query,
        {
            "customer_id":
                customer_id
        }
    )


# ============================================================
# CUSTOMER LOANS
# ============================================================

def get_customer_loans(
    customer_id: str
):

    query = """
    MATCH
    (c:Customer {
        customerId: $customer_id
    })
    -[:BORROWER_OF]->
    (l:Loan)

    RETURN
        l.loanId AS loanId,
        l.loanType AS loanType,
        l.principal AS principal,
        l.interestRate AS interestRate,
        l.tenureMonths AS tenureMonths,
        l.loanStatus AS status,
        l.sanctionDate AS sanctionDate

    ORDER BY l.principal DESC
    """

    return execute_query(
        query,
        {
            "customer_id":
                customer_id
        }
    )


# ============================================================
# CUSTOMER TRANSACTIONS
# ============================================================

def get_customer_transactions(
    customer_id: str,
    limit: int = 50
):

    query = """
    MATCH
    (c:Customer {
        customerId: $customer_id
    })
    -[:HOLDS_ACCOUNT]->
    (a:BankAccount)
    -[:HAS_TRANSACTION]->
    (t:Transaction)

    RETURN
        a.accountId AS accountId,
        t.transactionId AS transactionId,
        t.transactionType AS transactionType,
        t.direction AS direction,
        t.amount AS amount,
        t.channel AS channel,
        t.transactionTimestamp AS timestamp

    ORDER BY
        t.transactionTimestamp DESC

    LIMIT $limit
    """

    return execute_query(
        query,
        {
            "customer_id":
                customer_id,

            "limit":
                limit
        }
    )
