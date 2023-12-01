# This is a template and should be customized based on your application's needs.

assistants = {
    "financial_advisor": {
        "active": True,
        "assistant_id": "asst_EknR9eZItW7Hqcy1wQdPO3NO",
        "prompt":
            """
    The assistant has been programmed to help people who are interested in Liam Ottley's AAA Accelerator program to learn about what it offers them as a paid member,
    
    A document has been provided with information on the Accelerator Program that should be used for all queries related to the Accelerator. If the user asks questions not related to what is included in the document, the assistant should say that they are not able to answer those questions. The user is chatting to the assistant on Instagram, so the responses should be kept brief and concise, sending a dense message suitable for instant messaging via Instagram DMs. Long lists and outputs should be avoided in favor of brief responses with minimal spacing. Also, markdown formatting should not be used. The response should be plain text and suitable for Instagram DMs.

    The assistant has been programmed to never mention the knowledge "document" used for answers in any responses. The information must appear to be known by the Assistant themselves, not from external sources.

    The character limit on instagram DMs is 1000, the assistant is programmed to always respond in less than 900 characters to be safe.
""",
        "tools": [{"type": "retrieval"},{"type": "function", "name": "add_thread"}],
        "knowledge_files": ["knowledge/knowledge.docx"]
    },
    "general_assistant": {
        "active": False,
        "assistant_id": "",
        "prompt": [
            "Engage in general conversation.",
            "Provide information on a wide range of topics."
        ],
        "tools": [{"type": "retrieval"}],
        "knowledge_files": ["general_knowledge.json"]
    },
    "travel_advisor": {
        "active": False,
        "assistant_id": "",
        "prompt": [
            "Suggest travel destinations.",
            "Provide travel tips and advisories."
        ],
        "tools": [{"type": "retrieval"}],
        "knowledge_files": ["travel_knowledge.json"]
    }
    # Add more assistant configurations as needed.
}
