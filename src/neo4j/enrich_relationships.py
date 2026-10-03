from pathlib import Path
from datetime import datetime
import random
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "neo4j"
)

OUTPUT_DIR = (
    INPUT_DIR
    / "enriched"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


random.seed(42)

ingested_at = datetime.now().strftime(
    "%Y-%m-%dT%H:%M:%S"
)


# ============================================================
# CUSTOMER -> ACCOUNT
# ============================================================

customer_account = pd.read_csv(
    INPUT_DIR
    / "rel_customer_account.csv"
)

customer_account["sourceSystem"] = "CORE_BANKING"
customer_account["confidence"] = 1.00
customer_account["validFrom"] = "2020-01-01"
customer_account["validTo"] = None
customer_account["ingestedAt"] = ingested_at
customer_account["recordVersion"] = 1

customer_account.to_csv(
    OUTPUT_DIR
    / "rel_customer_account_enriched.csv",
    index=False
)


# ============================================================
# CUSTOMER -> LOAN
# ============================================================

customer_loan = pd.read_csv(
    INPUT_DIR
    / "rel_customer_loan.csv"
)

customer_loan["sourceSystem"] = "LOAN_ORIGINATION"
customer_loan["confidence"] = 1.00
customer_loan["validFrom"] = "2021-01-01"
customer_loan["validTo"] = None
customer_loan["ingestedAt"] = ingested_at
customer_loan["recordVersion"] = 1

customer_loan.to_csv(
    OUTPUT_DIR
    / "rel_customer_loan_enriched.csv",
    index=False
)


# ============================================================
# CUSTOMER -> ADDRESS
# ============================================================

customer_address = pd.read_csv(
    INPUT_DIR
    / "rel_customer_address.csv"
)

customer_address["sourceSystem"] = [
    random.choice(
        [
            "CRM",
            "KYC",
            "DIGITAL_BANKING"
        ]
    )
    for _ in range(
        len(customer_address)
    )
]

customer_address["confidence"] = [
    round(
        random.uniform(
            0.80,
            1.00
        ),
        2
    )
    for _ in range(
        len(customer_address)
    )
]

customer_address["validFrom"] = "2023-01-01"
customer_address["validTo"] = None
customer_address["ingestedAt"] = ingested_at
customer_address["recordVersion"] = 1

customer_address.to_csv(
    OUTPUT_DIR
    / "rel_customer_address_enriched.csv",
    index=False
)


# ============================================================
# CUSTOMER -> BENEFICIARY
# ============================================================

customer_beneficiary = pd.read_csv(
    INPUT_DIR
    / "rel_customer_beneficiary.csv"
)

customer_beneficiary["sourceSystem"] = "PAYMENTS"

customer_beneficiary["confidence"] = [
    round(
        random.uniform(
            0.85,
            1.00
        ),
        2
    )
    for _ in range(
        len(customer_beneficiary)
    )
]

customer_beneficiary["validFrom"] = "2024-01-01"
customer_beneficiary["validTo"] = None
customer_beneficiary["ingestedAt"] = ingested_at
customer_beneficiary["recordVersion"] = 1

customer_beneficiary.to_csv(
    OUTPUT_DIR
    / "rel_customer_beneficiary_enriched.csv",
    index=False
)


print("=" * 65)
print("RELATIONSHIP ENRICHMENT COMPLETE")
print("=" * 65)

print(
    f"Files saved to:\n{OUTPUT_DIR}"
)
