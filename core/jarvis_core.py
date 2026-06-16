import requests
from conversation_manager import ConversationManager

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL = "llama3.2:latest"

with open("Prompts/system_prompt.txt","r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

conversation_manager = ConversationManager()


def chat(user_message):
    conversation_manager.add_user_message(
    user_message
  )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + conversation_manager.get_history(),
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    reply = response.json()["message"]["content"]

    conversation_manager.add_assistant_message(
       reply
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