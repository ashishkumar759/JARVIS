from core.conversation_manager import ConversationManager
from core.ollama_client import OllamaClient
from memory.retrieval import MemoryRetriever
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "system_prompt.txt"

with open(PROMPT_FILE, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

conversation_manager = ConversationManager()
memory_retriever = MemoryRetriever()

client = OllamaClient(
    model=MODEL,
    url=OLLAMA_URL
)


def chat(user_message):

    conversation_manager.add_user_message(
        user_message
    )
    retrieved_memories = memory_retriever.search(user_message)
    
    memory_context = ""

    if retrieved_memories:
        memory_context = "\nRelevant memories:\n"

        for memory in retrieved_memories:
            memory_context += f"- {memory['content']}\n"

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + memory_context
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