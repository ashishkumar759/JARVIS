import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL = "llama3.2:latest"

SYSTEM_PROMPT = """
You are JARVIS.

You are the personal AI assistant of Ashish.

You are calm, intelligent, concise and helpful.

You remember the current conversation during runtime.

You explain things clearly and avoid unnecessary complexity.
"""

conversation_history = []


def chat(user_message):
    conversation_history.append(
        {"role": "user", "content": user_message}
    )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + conversation_history,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    reply = response.json()["message"]["content"]

    conversation_history.append(
        {"role": "assistant", "content": reply}
    )

    return reply


print("JARVIS Online")
print("Type 'quit' to exit.")
print()

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "quit":
        print("JARVIS: Goodbye Ashish.")
        break

    if not user_input:
        continue

    try:
        answer = chat(user_input)
        print()
        print("JARVIS:", answer)
        print()

    except Exception as e:
        print()
        print("ERROR:", e)
        print()