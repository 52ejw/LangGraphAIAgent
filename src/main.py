from graph import build_graph

THREAD_ID = "demo-session-1"


def run_turn(app, user_input: str):
    config = {
        "configurable": {
            "thread_id": THREAD_ID
        }
    }


    input_state = {
    "messages": [
        {
            "role": "user",
            "content": user_input
        }
    ],
    "next_action": ""
}

    result = app.invoke(input_state, config=config)

    print("\n--- Agent response ---")
    print(result["final_answer"])
    print("-----------------------\n")

    return result


def main():
    app = build_graph()

    print("Research Assistant Agent (LangGraph demo)")
    print("Type a research topic/question. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            break

        if not user_input:
            continue

        run_turn(app, user_input)

    # Display stored conversation state
    config = {
        "configurable": {
            "thread_id": THREAD_ID
        }
    }

    saved_state = app.get_state(config)

    print("\n=== Persisted conversation ===")

    for message in saved_state.values.get("messages", []):
        print(
            f"[{message['role']}] {message['content'][:120]}"
        )


if __name__ == "__main__":
    main()