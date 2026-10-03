from pathlib import Path
from typing import Any
import pandas as pd
import re
import unicodedata


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def normalize_string(value: Any) -> str | None:

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    value = str(value).strip().lower()

    value = unicodedata.normalize(
        "NFKD",
        value
    )

    value = re.sub(
        r"[^a-z0-9]",
        "",
        value
    )

    return value


def normalize_phone(value: Any) -> str | None:

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    value = re.sub(
        r"\D",
        "",
        str(value)
    )

    # Keep last 10 digits for Indian phone numbers
    if len(value) >= 10:
        value = value[-10:]

    return value


# ============================================================
# CRM
# ============================================================

crm = pd.read_csv(
    PROCESSED_DIR / "customers_clean.csv"
)

crm["name_norm"] = (
    crm["full_name"]
    .apply(normalize_string)
)

crm["email_norm"] = (
    crm["email"]
    .apply(normalize_string)
)

crm["phone_norm"] = (
    crm["phone"]
    .apply(normalize_phone)
)

crm["pan_norm"] = (
    crm["pan_number"]
    .apply(normalize_string)
)


# ============================================================
# EXTERNAL
# ============================================================

external = pd.read_csv(
    RAW_DIR / "external_customers.csv"
)

external["name_norm"] = (
    external["full_name"]
    .apply(normalize_string)
)

external["email_norm"] = (
    external["email"]
    .apply(normalize_string)
)

external["phone_norm"] = (
    external["phone"]
    .apply(normalize_phone)
)

external["pan_norm"] = (
    external["pan_number"]
    .apply(normalize_string)
)


# ============================================================
# SAVE
# ============================================================

crm.to_csv(
    PROCESSED_DIR /
    "crm_customers_er_ready.csv",
    index=False
)

external.to_csv(
    PROCESSED_DIR /
    "external_customers_er_ready.csv",
    index=False
)


print(
    "Entity-resolution normalization complete."
)
