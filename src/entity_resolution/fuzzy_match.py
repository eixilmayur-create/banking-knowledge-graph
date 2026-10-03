from pathlib import Path
from typing import Any
import pandas as pd
from rapidfuzz.fuzz import ratio


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


results: list[dict[str, Any]] = []


# ============================================================
# BLOCK CRM BY CITY
# ============================================================

crm_blocks = {
    city: group
    for city, group
    in crm.groupby("city")
}


# ============================================================
# MATCH EACH EXTERNAL CUSTOMER
# ============================================================

for _, ext in external.iterrows():

    city = ext["city"]

    candidate_group = crm_blocks.get(
        city
    )

    if candidate_group is None:
        continue


    best_score = 0
    best_customer = None


    for _, candidate in candidate_group.iterrows():

        name_score = ratio(
            str(ext["name_norm"]),
            str(candidate["name_norm"])
        )

        dob_score = (
            100
            if ext["date_of_birth"]
            == candidate["date_of_birth"]
            else 0
        )

        pan_score = (
            100
            if (
                pd.notna(ext["pan_norm"])
                and ext["pan_norm"]
                == candidate["pan_norm"]
            )
            else 0
        )


        combined_score = (
            name_score * 0.40
            + dob_score * 0.20
            + pan_score * 0.40
        )


        if combined_score > best_score:

            best_score = combined_score

            best_customer = candidate[
                "crm_customer_id"
            ]


    results.append(
        {
            "external_customer_id":
                ext["external_customer_id"],

            "crm_customer_id":
                best_customer,

            "fuzzy_score":
                round(best_score, 2)
        }
    )


result_df = pd.DataFrame(
    results
)


result_df.to_csv(
    OUTPUT_DIR /
    "fuzzy_matches.csv",
    index=False
)


print("=" * 60)
print("FUZZY MATCHING COMPLETE")
print("=" * 60)

print(
    f"Records evaluated: {len(result_df)}"
)
