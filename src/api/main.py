import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)

from src.api.database import (
    verify_connection,
    close_driver,
)

from src.config.logging_config import (
    configure_logging,
)

from src.api.customer_service import (
    get_customer,
    get_customer_accounts,
    get_customer_loans,
    get_customer_transactions,
)

from src.api.graphrag_service import (
    ask_graphrag,
)

from src.api.models import (
    GraphRAGRequest,
    GraphRAGResponse,
    HealthResponse,
)


configure_logging()

logger = logging.getLogger(
    __name__
)

logger.info(
    "Starting Banking Knowledge Graph API"
)


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    logger.info(
        "Starting Banking Knowledge Graph API..."
    )

    verify_connection()

    logger.info(
        "Neo4j connectivity verified"
    )

    yield

    logger.info(
        "Closing Neo4j connection"
    )

    close_driver()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title=(
        "Banking Knowledge Graph API"
    ),

    description=(
        "API layer for Banking Customer 360, "
        "Neo4j graph retrieval and GraphRAG."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["System"]
)
def root() -> dict[str, str]:

    return {
        "message":
            "Banking Knowledge Graph API",

        "version":
            "1.0.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"]
)
def health() -> dict[str, str]:

    try:

        verify_connection()

        return {
            "status":
                "healthy",

            "neo4j":
                "connected"
        }

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Neo4j unavailable: "
                f"{error}"
            )
        )


# ============================================================
# CUSTOMER 360
# ============================================================

@app.get(
    "/customer/{customer_id}",
    tags=["Customer"]
)
def customer_360(
    customer_id: str,
) -> Any:

    customer = get_customer(
        customer_id
    )

    if customer is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Customer not found."
            )
        )

    return customer


# ============================================================
# CUSTOMER ACCOUNTS
# ============================================================

@app.get(
    "/customer/{customer_id}/accounts",
    tags=["Customer"]
)
def customer_accounts(
    customer_id: str,
) -> dict[str, Any]:

    return {
        "customerId":
            customer_id,

        "accounts":
            get_customer_accounts(
                customer_id
            )
    }


# ============================================================
# CUSTOMER LOANS
# ============================================================

@app.get(
    "/customer/{customer_id}/loans",
    tags=["Customer"]
)
def customer_loans(
    customer_id: str,
) -> dict[str, Any]:

    return {
        "customerId":
            customer_id,

        "loans":
            get_customer_loans(
                customer_id
            )
    }


# ============================================================
# CUSTOMER TRANSACTIONS
# ============================================================

@app.get(
    "/customer/{customer_id}/transactions",
    tags=["Customer"]
)
def customer_transactions(
    customer_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=200
    ),
) -> dict[str, Any]:

    return {
        "customerId":
            customer_id,

        "transactions":
            get_customer_transactions(
                customer_id,
                limit
            )
    }


# ============================================================
# GRAPHRAG
# ============================================================

@app.post(
    "/graphrag/ask",
    response_model=GraphRAGResponse,
    tags=["GraphRAG"]
)
def graphrag(
    request: GraphRAGRequest,
) -> dict[str, Any]:

    try:

        return ask_graphrag(
            request.question
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"GraphRAG request failed: "
                f"{error}"
            )
        )
