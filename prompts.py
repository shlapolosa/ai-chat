# This is a template and should be customized based on your application's needs.

assistants = {
    "financial_advisor": {
        "active": False,
        "assistant_id": "",
        "prompt": [
            "Provide financial advice based on current market trends.",
            "Answer queries related to investments and savings."
        ],
        "tools": ["finance_tool"],
        "knowledge_files": ["finance_knowledge.json"]
    },
    "general_assistant": {
        "active": False,
        "assistant_id": "",
        "prompt": [
            "Engage in general conversation.",
            "Provide information on a wide range of topics."
        ],
        "tools": ["general_knowledge_tool"],
        "knowledge_files": ["general_knowledge.json"]
    },
    "travel_advisor": {
        "active": False,
        "assistant_id": "",
        "prompt": [
            "Suggest travel destinations.",
            "Provide travel tips and advisories."
        ],
        "tools": ["travel_tool"],
        "knowledge_files": ["travel_knowledge.json"]
    }
    # Add more assistant configurations as needed.
}
