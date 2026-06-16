from conversation_manager import ConversationManager
from ollama_client import OllamaClient

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"

with open("Prompts/system_prompt.txt", "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

conversation_manager = ConversationManager()

client = OllamaClient(
    model=MODEL,
    url=OLLAMA_URL
)


def chat(user_message):

    conversation_manager.add_user_message(
        user_message
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + conversation_manager.get_history()

    reply = client.chat(messages)

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