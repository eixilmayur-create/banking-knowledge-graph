from typing import Any

import requests
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Banking Semantic Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# API HELPERS
# ============================================================

def api_get(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> Any | None:

    try:

        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=30,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        st.error(
            f"API request failed: {error}"
        )

        return None


def api_post(
    endpoint: str,
    payload: dict[str, Any] | None = None,
) -> Any | None:

    try:

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        st.error(
            f"API request failed: {error}"
        )

        return None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🏦 Banking KG"
)

st.sidebar.caption(
    "Semantic Intelligence Platform"
)


page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customer 360",
        "GraphRAG Assistant",
        "GraphRAG Test Lab",
    ]
)


st.sidebar.divider()


health = api_get(
    "/health"
)


if health:

    st.sidebar.success(
        "Neo4j Connected"
    )

else:

    st.sidebar.error(
        "Backend Offline"
    )


st.sidebar.caption(
    "Neo4j • RDF • OWL • SHACL • "
    "Gemini • GraphRAG • FastAPI"
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title(
        "Banking Semantic Intelligence Platform"
    )

    st.caption(
        "Knowledge Graph + Ontology + "
        "Graph Analytics + Gemini GraphRAG"
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.metric(
            "Knowledge Graph",
            "Online"
            if health
            else "Offline",
        )


    with col2:

        st.metric(
            "Graph Database",
            "Neo4j",
        )


    with col3:

        st.metric(
            "AI Layer",
            "Gemini",
        )


    with col4:

        st.metric(
            "API",
            "FastAPI",
        )


    st.divider()


    st.subheader(
        "Platform Architecture"
    )


    st.code(
        """
Multi-Source Banking Data
          │
          ▼
Profiling & Cleaning
          │
          ▼
Entity Resolution
          │
          ▼
Golden Customer
          │
          ▼
Ontology / RDF / OWL
          │
          ▼
SHACL + SPARQL
          │
          ▼
GraphDB / Neo4j
          │
          ▼
Graph Analytics
          │
          ▼
Semantic Mapping
          │
          ▼
Embeddings + Gemini
          │
          ▼
GraphRAG
          │
          ▼
FastAPI
          │
          ▼
Web Application
        """,
        language="text",
    )


    st.subheader(
        "Capabilities"
    )


    c1, c2, c3 = st.columns(
        3
    )


    with c1:

        st.info(
            """
**Customer 360**

Explore customer accounts,
loans, cards and transactions.
"""
        )


    with c2:

        st.info(
            """
**Graph Intelligence**

Traverse connected entities,
shared relationships and paths.
"""
        )


    with c3:

        st.info(
            """
**AI GraphRAG**

Ask natural-language questions
grounded in Knowledge Graph evidence.
"""
        )


# ============================================================
# CUSTOMER 360
# ============================================================

elif page == "Customer 360":

    st.title(
        "Customer 360"
    )

    st.caption(
        "Unified customer view powered by Neo4j"
    )


    customer_id = st.text_input(
        "Customer ID",
        value="GC0000001",
        placeholder="GC0000001",
    )


    if st.button(
        "Load Customer",
        type="primary",
    ):

        customer = api_get(
            f"/customer/{customer_id}"
        )


        if not customer:

            st.warning(
                "Customer not found."
            )

        else:

            st.success(
                f"Customer loaded: "
                f"{customer_id}"
            )


            # =================================================
            # PROFILE
            # =================================================

            st.subheader(
                "Customer Profile"
            )


            c1, c2, c3, c4 = st.columns(
                4
            )


            with c1:

                st.metric(
                    "Customer",
                    customer.get(
                        "name",
                        "Unknown",
                    ),
                )


            with c2:

                st.metric(
                    "Risk Segment",
                    customer.get(
                        "riskSegment",
                        "N/A",
                    ),
                )


            with c3:

                st.metric(
                    "KYC Status",
                    customer.get(
                        "kycStatus",
                        "N/A",
                    ),
                )


            with c4:

                st.metric(
                    "Transactions",
                    customer.get(
                        "transactionCount",
                        0,
                    ),
                )


            st.divider()


            # =================================================
            # ACCOUNTS
            # =================================================

            tabs = st.tabs(
                [
                    "Accounts",
                    "Loans",
                    "Transactions",
                    "Raw Graph Data",
                ]
            )


            with tabs[0]:

                accounts = api_get(
                    f"/customer/"
                    f"{customer_id}/accounts"
                )

                if accounts:

                    account_rows: list[dict[str, Any]] = accounts.get(
                        "accounts",
                        []
                    )

                    if account_rows:

                        st.dataframe(  # type: ignore[reportUnknownMemberType]
                            pd.DataFrame(
                                account_rows
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                    else:

                        st.info(
                            "No accounts found."
                        )


            # =================================================
            # LOANS
            # =================================================

            with tabs[1]:

                loans = api_get(
                    f"/customer/"
                    f"{customer_id}/loans"
                )

                if loans:

                    loan_rows: list[dict[str, Any]] = loans.get(
                        "loans",
                        []
                    )

                    if loan_rows:

                        st.dataframe(  # type: ignore[reportUnknownMemberType]
                            pd.DataFrame(
                                loan_rows
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                    else:

                        st.info(
                            "No loans found."
                        )


            # =================================================
            # TRANSACTIONS
            # =================================================

            with tabs[2]:

                transactions = api_get(
                    f"/customer/"
                    f"{customer_id}/transactions",
                    params={
                        "limit": 50
                    }
                )

                if transactions:

                    rows: list[dict[str, Any]] = transactions.get(
                        "transactions",
                        []
                    )

                    if rows:

                        transaction_df: pd.DataFrame = (
                            pd.DataFrame(
                                rows
                            )
                        )

                        st.dataframe(  # type: ignore[reportUnknownMemberType]
                            transaction_df,
                            use_container_width=True,
                            hide_index=True,
                        )

                        if (
                            "amount"
                            in transaction_df.columns
                        ):

                            st.subheader(
                                "Transaction Amounts"
                            )

                            st.bar_chart(  # type: ignore[reportUnknownMemberType]
                                transaction_df[
                                    "amount"
                                ]
                            )

                    else:

                        st.info(
                            "No transactions found."
                        )


            # =================================================
            # RAW DATA
            # =================================================

            with tabs[3]:

                st.json(
                    customer
                )


# ============================================================
# GRAPHRAG ASSISTANT
# ============================================================

elif page == "GraphRAG Assistant":

    st.title(
        "GraphRAG Assistant"
    )

    st.caption(
        "Ask questions grounded in "
        "Neo4j Knowledge Graph evidence"
    )


    # ========================================================
    # EXAMPLE QUESTIONS
    # ========================================================

    st.subheader(
        "Try an example"
    )


    examples = [

        "Show me all accounts for "
        "customer GC0000001",

        "What loans does customer "
        "GC0000025 have?",

        "Show transactions for "
        "GC0000100",

        "Give me a complete overview "
        "of customer GC0000001",

        "Which high-risk customers "
        "have active loans?",

        "Which customers share "
        "beneficiaries?",

        "Which customers share "
        "an address?",

        "How are GC0000001 and "
        "GC0000050 connected?",
    ]


    selected_example = st.selectbox(
        "Example questions",
        ["Select a question..."]
        + examples
    )


    if (
        selected_example
        != "Select a question..."
    ):

        st.session_state[
            "selected_question"
        ] = selected_example


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    if "messages" not in st.session_state:

        st.session_state["messages"] = []


    messages: list[dict[str, Any]] = st.session_state.get(
        "messages",
        []
    )

    for message in messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


            if message.get(
                "intent"
            ):

                st.caption(
                    f"Intent: "
                    f"{message['intent']}"
                )


            if message.get(
                "evidence"
            ):

                with st.expander(
                    "Graph Evidence"
                ):

                    st.json(
                        message[
                            "evidence"
                        ]
                    )


    # ========================================================
    # INPUT
    # ========================================================

    default_question = (
        st.session_state.pop(
            "selected_question",
            None
        )
    )


    if default_question:

        question = default_question

    else:

        question = st.chat_input(
            "Ask the Banking Knowledge Graph..."
        )


    if question:

        messages.append(
            {
                "role":
                    "user",

                "content":
                    question,
            }
        )
        st.session_state["messages"] = messages


        with st.chat_message(
            "user"
        ):

            st.markdown(
                question
            )


        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Searching the Knowledge Graph..."
            ):

                result = api_post(
                    "/graphrag/ask",
                    {
                        "question":
                            question
                    }
                )


            if result:

                answer = result.get(
                    "answer",
                    "No answer returned."
                )

                intent = result.get(
                    "intent",
                    "UNKNOWN"
                )

                evidence = result.get(
                    "evidence",
                    []
                )


                st.markdown(
                    answer
                )


                st.caption(
                    f"Detected intent: "
                    f"`{intent}`"
                )


                with st.expander(
                    "View Graph Evidence"
                ):

                    if evidence:

                        st.json(
                            evidence
                        )

                    else:

                        st.info(
                            "No graph evidence returned."
                        )


                messages.append(
                    {
                        "role":
                            "assistant",

                        "content":
                            answer,

                        "intent":
                            intent,

                        "evidence":
                            evidence,
                    }
                )
                st.session_state["messages"] = messages


    if st.button(
        "Clear Chat"
    ):

        st.session_state["messages"] = []

        st.rerun()


# ============================================================
# TEST LAB
# ============================================================

elif page == "GraphRAG Test Lab":

    st.title(
        "GraphRAG Test Lab"
    )

    st.caption(
        "Evaluate intent routing and "
        "GraphRAG behavior across multiple questions."
    )


    test_cases = [

        (
            "Show accounts for customer GC0000001",
            "CUSTOMER_ACCOUNTS"
        ),

        (
            "List bank accounts owned by GC0000001",
            "CUSTOMER_ACCOUNTS"
        ),

        (
            "What loans does GC0000025 have?",
            "CUSTOMER_LOANS"
        ),

        (
            "Show borrowing details for GC0000025",
            "CUSTOMER_LOANS"
        ),

        (
            "Show transactions for GC0000100",
            "CUSTOMER_TRANSACTIONS"
        ),

        (
            "What transactions belong to GC0000100?",
            "CUSTOMER_TRANSACTIONS"
        ),

        (
            "Give me complete information "
            "for GC0000001",
            "CUSTOMER_360"
        ),

        (
            "Show customer 360 for GC0000001",
            "CUSTOMER_360"
        ),

        (
            "Which high-risk customers "
            "have active loans?",
            "HIGH_RISK_ACTIVE_LOANS"
        ),

        (
            "List active loans belonging "
            "to high risk customers",
            "HIGH_RISK_ACTIVE_LOANS"
        ),

        (
            "Which customers share beneficiaries?",
            "SHARED_BENEFICIARIES"
        ),

        (
            "Find customers connected to "
            "the same beneficiary",
            "SHARED_BENEFICIARIES"
        ),

        (
            "Which customers share an address?",
            "SHARED_ADDRESS"
        ),

        (
            "Find people linked through "
            "a common address",
            "SHARED_ADDRESS"
        ),

        (
            "How are GC0000001 and "
            "GC0000050 connected?",
            "CUSTOMER_CONNECTION_PATH"
        ),

        (
            "Find the connection between "
            "GC0000001 and GC0000050",
            "CUSTOMER_CONNECTION_PATH"
        ),

        (
            "What loans does GC9999999 have?",
            "CUSTOMER_LOANS"
        ),

        (
            "Show me today's stock market price",
            "UNKNOWN"
        ),

        (
            "What is the weather in Delhi?",
            "UNKNOWN"
        ),

        (
            "Write a poem about banking",
            "UNKNOWN"
        ),
    ]


    st.metric(
        "Test Cases",
        len(test_cases)
    )


    if st.button(
        "Run All Tests",
        type="primary",
    ):

        results: list[dict[str, Any]] = []

        progress = st.progress(
            0
        )


        for index, (
            question,
            expected_intent
        ) in enumerate(
            test_cases
        ):

            result = api_post(
                "/graphrag/ask",
                {
                    "question":
                        question
                }
            )


            actual_intent = (
                result.get(
                    "intent",
                    "ERROR"
                )
                if result
                else "ERROR"
            )


            evidence_count = (
                len(
                    result.get(
                        "evidence",
                        []
                    )
                )
                if result
                else 0
            )


            passed = (
                expected_intent
                == actual_intent
            )


            results.append(
                {
                    "Question":
                        question,

                    "Expected":
                        expected_intent,

                    "Actual":
                        actual_intent,

                    "Evidence":
                        evidence_count,

                    "Result":
                        "PASS"
                        if passed
                        else "FAIL",
                }
            )


            progress.progress(
                (
                    index + 1
                )
                / len(
                    test_cases
                )
            )


        results_df: pd.DataFrame = pd.DataFrame(
            results
        )


        passed_count = len(
            results_df[
                results_df[
                    "Result"
                ] == "PASS"
            ]
        )


        accuracy = (
            passed_count
            / len(results_df)
            * 100
        )


        c1, c2, c3 = st.columns(
            3
        )


        with c1:

            st.metric(
                "Tests Passed",
                passed_count,
            )


        with c2:

            st.metric(
                "Tests Failed",
                len(results_df)
                - passed_count,
            )


        with c3:

            st.metric(
                "Routing Accuracy",
                f"{accuracy:.1f}%",
            )


        st.dataframe(  # type: ignore[reportUnknownMemberType]
            results_df,
            use_container_width=True,
            hide_index=True,
        )


        failed: pd.DataFrame = results_df[
            results_df[
                "Result"
            ] == "FAIL"
        ]


        if not failed.empty:

            st.subheader(
                "Failed Tests"
            )

            st.dataframe(  # type: ignore[reportUnknownMemberType]
                failed,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.success(
                "All routing tests passed."
            )
