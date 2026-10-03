import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    # ========================================================
    # APPLICATION
    # ========================================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Banking Semantic Intelligence API"
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        "1.0.0"
    )

    APP_ENV = os.getenv(
        "APP_ENV",
        "development"
    )


    # ========================================================
    # NEO4J
    # ========================================================

    NEO4J_URI = os.getenv(
        "NEO4J_URI",
        "bolt://localhost:7687"
    )

    NEO4J_USERNAME = os.getenv(
        "NEO4J_USERNAME",
        "neo4j"
    )

    NEO4J_PASSWORD = os.getenv(
        "NEO4J_PASSWORD"
    )

    NEO4J_DATABASE = os.getenv(
        "NEO4J_DATABASE",
        "neo4j"
    )


    # ========================================================
    # GOOGLE CLOUD
    # ========================================================

    GOOGLE_CLOUD_PROJECT = os.getenv(
        "GOOGLE_CLOUD_PROJECT"
    )

    GOOGLE_CLOUD_LOCATION = os.getenv(
        "GOOGLE_CLOUD_LOCATION",
        "global"
    )


settings = Settings()
