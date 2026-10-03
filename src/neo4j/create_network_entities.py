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
# ADDRESS NODES
# ============================================================

cities = [
    "Mumbai",
    "Pune",
    "Nagpur",
    "Delhi",
    "Gurugram",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
]


addresses: list[dict[str, str]] = []

for i in range(1, 301):

    addresses.append(
        {
            "addressId": f"ADDR{i:05d}",
            "city": random.choice(cities),
            "postalCode": str(
                random.randint(
                    100000,
                    999999
                )
            )
        }
    )


address_df = pd.DataFrame(
    addresses
)

address_df.to_csv(
    OUTPUT_DIR / "addresses.csv",
    index=False
)


# ============================================================
# CUSTOMER -> ADDRESS
# ============================================================

address_ids = address_df[
    "addressId"
].tolist()


customer_address_rows: list[dict[str, object]] = []

for _, row in customers.iterrows():

    customer_address_rows.append(
        {
            "customerId":
                row["customerId"],

            "addressId":
                random.choice(
                    address_ids
                )
        }
    )


pd.DataFrame(
    customer_address_rows
).to_csv(
    OUTPUT_DIR
    / "rel_customer_address.csv",
    index=False
)


# ============================================================
# BENEFICIARY NODES
# ============================================================

beneficiaries: list[dict[str, str]] = []

for i in range(1, 501):

    beneficiaries.append(
        {
            "beneficiaryId":
                f"BEN{i:05d}",

            "beneficiaryType":
                random.choice(
                    [
                        "PERSON",
                        "BUSINESS"
                    ]
                )
        }
    )


beneficiary_df = pd.DataFrame(
    beneficiaries
)

beneficiary_df.to_csv(
    OUTPUT_DIR / "beneficiaries.csv",
    index=False
)


# ============================================================
# CUSTOMER -> BENEFICIARY
# ============================================================

beneficiary_ids = beneficiary_df[
    "beneficiaryId"
].tolist()


customer_beneficiary_rows: list[dict[str, object]] = []

for _, row in customers.iterrows():

    selected = random.sample(
        beneficiary_ids,
        random.randint(1, 3)
    )

    for beneficiary_id in selected:

        customer_beneficiary_rows.append(
            {
                "customerId":
                    row["customerId"],

                "beneficiaryId":
                    beneficiary_id
            }
        )


pd.DataFrame(
    customer_beneficiary_rows
).to_csv(
    OUTPUT_DIR
    / "rel_customer_beneficiary.csv",
    index=False
)


print(
    "Network entity datasets created successfully."
)
