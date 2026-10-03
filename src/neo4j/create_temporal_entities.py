from pathlib import Path
import pandas as pd
import random


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CUSTOMER_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "neo4j"
    / "customers.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "neo4j"
)


random.seed(42)


customers = pd.read_csv(
    CUSTOMER_FILE
)


# ============================================================
# ORGANIZATIONS
# ============================================================

organizations: list[dict[str, str]] = []

for i in range(
    1,
    201
):

    organizations.append(
        {
            "organizationId":
                f"ORG{i:05d}",

            "organizationName":
                f"Organization {i}"
        }
    )


organizations_df = pd.DataFrame(
    organizations
)


organizations_df.to_csv(
    OUTPUT_DIR
    / "organizations.csv",
    index=False
)


# ============================================================
# CUSTOMER -> ORGANIZATION
# ============================================================

organization_ids = (
    organizations_df[
        "organizationId"
    ].tolist()
)


rows: list[dict[str, object]] = []


sample_customers = customers.sample(
    n=600,
    random_state=42
)


for _, customer in sample_customers.iterrows():

    start_year = random.randint(
        2016,
        2022
    )

    duration = random.randint(
        1,
        6
    )

    end_year = min(
        start_year + duration,
        2026
    )


    rows.append(
        {
            "customerId":
                customer[
                    "customerId"
                ],

            "organizationId":
                random.choice(
                    organization_ids
                ),

            "role":
                random.choice(
                    [
                        "DIRECTOR",
                        "OWNER",
                        "AUTHORIZED_SIGNATORY"
                    ]
                ),

            "validFrom":
                f"{start_year}-01-01",

            "validTo":
                f"{end_year}-12-31",

            "sourceSystem":
                "CORPORATE_REGISTRY",

            "confidence":
                0.98
        }
    )


relationship_df = pd.DataFrame(
    rows
)


relationship_df.to_csv(
    OUTPUT_DIR
    / "rel_customer_organization.csv",
    index=False
)


print(
    "Temporal organization data created."
)
