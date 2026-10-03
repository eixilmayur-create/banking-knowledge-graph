from query_router import route_question


questions = [

    "Show me all accounts for customer GC0000001",

    "What loans does customer GC0000025 have?",

    "Show transactions for GC0000100",

    "How are GC0000001 and GC0000050 connected?",

    "Which high-risk customers have active loans?"
]


for question in questions:

    result = route_question(
        question
    )

    print("\nQUESTION:")
    print(question)

    print("ROUTING:")
    print(result)
