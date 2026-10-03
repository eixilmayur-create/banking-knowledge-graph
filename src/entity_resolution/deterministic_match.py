from pathlib import Path
from typing import Any
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


crm = pd.read_csv(
    PROCESSED_DIR /
    "crm_customers_er_ready.csv"
)

external = pd.read_csv(
    PROCESSED_DIR /
    "external_customers_er_ready.csv"
)


matches: list[dict[str, Any]] = []


# ============================================================
# CREATE LOOKUP INDEXES
# ============================================================

pan_lookup: dict[str, list[str]] = {}

phone_lookup: dict[str, list[str]] = {}

email_lookup: dict[str, list[str]] = {}


for _, row in crm.iterrows():

    customer_id = str(row["crm_customer_id"])

    pan_value = row["pan_norm"]
    phone_value = row["phone_norm"]
    email_value = row["email_norm"]

    if pd.notna(pan_value):

        key = str(pan_value)
        pan_lookup.setdefault(key, []).append(customer_id)

    if pd.notna(phone_value):

        key = str(phone_value)
        phone_lookup.setdefault(key, []).append(customer_id)

    if pd.notna(email_value):

        key = str(email_value)
        email_lookup.setdefault(key, []).append(customer_id)


# ============================================================
# DETERMISTIC MATCHING
# ============================================================

for _, row in external.iterrows():

    external_id = str(row["external_customer_id"])

    candidate_scores: dict[str, int] = {}


    # PAN match
    pan = row["pan_norm"]

    if pd.notna(pan):

        for customer_id in pan_lookup.get(str(pan), []):

            candidate_scores[customer_id] = (
                candidate_scores.get(customer_id, 0) + 50
            )


    # Phone match
    phone = row["phone_norm"]

    if pd.notna(phone):

        for customer_id in phone_lookup.get(str(phone), []):

            candidate_scores[customer_id] = (
                candidate_scores.get(customer_id, 0) + 30
            )


    # Email match
    email = row["email_norm"]

    if pd.notna(email):

        for customer_id in email_lookup.get(str(email), []):

            candidate_scores[customer_id] = (
                candidate_scores.get(customer_id, 0) + 20
            )


    # ========================================================
    # SELECT BEST CANDIDATE
    # ========================================================

    if candidate_scores:

        best_customer = max(
            candidate_scores,
            key=lambda customer_id: candidate_scores[customer_id],
        )
        score = candidate_scores[best_customer]

        matches.append(
            {
                "external_customer_id": external_id,
                "crm_customer_id": best_customer,
                "deterministic_score": score,
                "match_method": "DETERMINISTIC",
            }
        )


results = pd.DataFrame(
    matches
)

output_file = (
    OUTPUT_DIR /
    "deterministic_matches.csv"
)

results.to_csv(
    output_file,
    index=False
)


print("=" * 60)
print("DETERMINISTIC MATCHING COMPLETE")
print("=" * 60)

print(
    f"Matches found: {len(results)}"
)

print(
    f"\nSaved to:\n{output_file}"
)
