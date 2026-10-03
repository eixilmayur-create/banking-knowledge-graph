from pathlib import Path
import pandas as pd
import numpy as np
import random


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

random.seed(42)
np.random.seed(42)


# ============================================================
# LOAD CLEAN CRM CUSTOMERS
# ============================================================

customers = pd.read_csv(
    PROCESSED_DIR / "customers_clean.csv"
)


# ============================================================
# SAMPLE CUSTOMERS
# ============================================================

external = customers.sample(
    n=1500,
    random_state=42
).copy()

external.reset_index(
    drop=True,
    inplace=True
)


# ============================================================
# CREATE INDEPENDENT SOURCE IDS
# ============================================================

external["external_customer_id"] = [
    f"EXT{i:06d}"
    for i in range(1, len(external) + 1)
]


# Keep truth temporarily for evaluation.
external["original_crm_customer_id"] = (
    external["crm_customer_id"]
)


# ============================================================
# INTRODUCE REALISTIC DATA VARIATIONS
# ============================================================

def alter_name(name: object) -> str | None:

    if name is None or (isinstance(name, float) and pd.isna(name)):
        return None

    name = str(name)
    choice = random.randint(1, 5)

    if choice == 1:
        return name.upper()

    if choice == 2:
        return name.lower()

    if choice == 3:
        parts = name.split()

        if len(parts) >= 2:
            return f"{parts[0]} {parts[-1][0]}"

    if choice == 4:
        return name.replace(" ", "  ")

    return name


def alter_phone(phone: object) -> str | None:

    if phone is None or (isinstance(phone, float) and pd.isna(phone)):
        return None

    phone = str(phone)
    choice = random.randint(1, 5)

    if choice == 1:
        return "+91" + phone

    if choice == 2:
        return "91" + phone

    if choice == 3:
        return phone[:5] + " " + phone[5:]

    return phone


def alter_email(email: object) -> str | None:

    if email is None or (isinstance(email, float) and pd.isna(email)):
        return None

    email = str(email)
    choice = random.randint(1, 5)

    if choice == 1:
        return email.upper()

    if choice == 2:
        return " " + email + " "

    return email


external["full_name"] = (
    external["full_name"]
    .apply(alter_name)
)

external["phone"] = (
    external["phone"]
    .apply(alter_phone)
)

external["email"] = (
    external["email"]
    .apply(alter_email)
)


# ============================================================
# INTRODUCE MISSING VALUES
# ============================================================

for index in external.sample(
    100,
    random_state=10
).index:

    external.loc[index, "email"] = None


for index in external.sample(
    80,
    random_state=11
).index:

    external.loc[index, "phone"] = None


# ============================================================
# DROP CRM ID FROM MATCHING DATA
# ============================================================

matching_columns = [
    "external_customer_id",
    "full_name",
    "date_of_birth",
    "email",
    "phone",
    "pan_number",
    "city",
    "state",
]

external_matching = external[
    matching_columns
]


# ============================================================
# SAVE FILE
# ============================================================

output_file = (
    RAW_DIR /
    "external_customers.csv"
)

external_matching.to_csv(
    output_file,
    index=False
)


# Save ground truth separately
truth_file = (
    RAW_DIR /
    "external_customer_ground_truth.csv"
)

external[
    [
        "external_customer_id",
        "original_crm_customer_id"
    ]
].to_csv(
    truth_file,
    index=False
)


print("=" * 60)
print("EXTERNAL CUSTOMER SOURCE CREATED")
print("=" * 60)

print(
    f"External customer records: {len(external_matching)}"
)

print(
    f"\nSaved to:\n{output_file}"
)

print(
    f"\nGround truth:\n{truth_file}"
)
