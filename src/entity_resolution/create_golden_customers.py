from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR = (
    PROJECT_ROOT /
    "outputs" /
    "entity_resolution"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


customers = pd.read_csv(
    PROCESSED_DIR /
    "crm_customers_er_ready.csv"
)


# ============================================================
# ASSIGN GOLDEN IDS
# ============================================================

customers = customers.sort_values(
    "crm_customer_id"
).reset_index(drop=True)


customers["golden_customer_id"] = [
    f"GC{i:07d}"
    for i in range(
        1,
        len(customers) + 1
    )
]


golden = customers[
    [
        "golden_customer_id",
        "crm_customer_id",
        "full_name",
        "date_of_birth",
        "email",
        "phone",
        "pan_number",
        "city",
        "state",
        "kyc_status",
        "risk_segment",
    ]
]


golden.to_csv(
    OUTPUT_DIR /
    "golden_customers.csv",
    index=False
)


print("=" * 60)
print("GOLDEN CUSTOMER MASTER CREATED")
print("=" * 60)

print(
    f"Golden customers: {len(golden)}"
)
