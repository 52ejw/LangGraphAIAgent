from graph import build_graph

# Conversation thread ID for maintaining state
THREAD_ID = "demo-session-3"


def run_turn(app, user_input: str):
    # Tells the agent which conversation the message belongs to 
    config = {
        "configurable": {
            "thread_id": THREAD_ID
        }
    }

    # Create starting information for this turn
    input_state = {
    "messages": [
        {
            "role": "user",
            "content": user_input
        }
    ],
    "topic": "",
    "plan": [],
    "current_step": 0,
    "research_results": [],
    "sources": [],
    "next_action": "",
    "error": None,
    "final_answer": None,
}

    # Run agent workflow
    result = app.invoke(input_state, config=config)

    # Display final asnwer 
    print("\n--- Agent response ---")
    print(result["final_answer"])
    print("-----------------------\n")

    return result


def main():
    app = build_graph()

    print("Research Assistant Agent (LangGraph demo)")
    print("Type a research topic/question. Type 'exit' to quit.\n")

    # Asks user for input until 'exit'
    while True:
        user_input = input("You: ").strip()

        # Allows user to exit program
        if user_input.lower() in ("exit", "quit"):
            break

        # Ignore empty messages
        if not user_input:
            continue

        # Sends messages to agent
        run_turn(app, user_input)

    # Display stored conversation state
    config = {
        "configurable": {
            "thread_id": THREAD_ID
        }
    }

    saved_state = app.get_state(config)

    # Displays messages stored during the conversation
    print("\n=== Persisted conversation ===")

    for message in saved_state.values.get("messages", []):
        print(
            f"[{message['role']}] {message['content'][:120]}"
        )


if __name__ == "__main__":
    main()