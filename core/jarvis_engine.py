from pathlib import Path

from core.conversation_manager import ConversationManager
from core.ollama_client import OllamaClient

from memory.embedding_service import EmbeddingService
from memory.memory_manager import MemoryManager
from memory.retrieval import MemoryRetriever


class JarvisEngine:

    def __init__(
        self,
        model="llama3.2:latest",
        url="http://localhost:11434/api/chat"
    ):

        self.conversation_manager = ConversationManager()

        self.embedding_service = EmbeddingService()

        self.client = OllamaClient(
            model=model,
            url=url
        )

        self.memory_manager = MemoryManager(
            embedding_service=self.embedding_service,
            client=self.client
        )

        self.memory_retriever = MemoryRetriever(
            embedding_service=self.embedding_service
        )

        base_dir = Path(__file__).resolve().parent.parent
        prompt_file = base_dir / "prompts" / "system_prompt.txt"

        with open(prompt_file, "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    def chat(self, user_message):

        self.conversation_manager.add_user_message(
            user_message
        )

        self.memory_manager.store_memory(
            user_message
        )

        retrieved_memories = self.memory_retriever.search(
            user_message
        )

        memory_context = ""

        if retrieved_memories:

            memory_context = (
                "\nYou have access to the user's long-term memory. "
                "The following memories are authoritative facts stored by your memory system. "
                "Use them while answering the user. "
                "If a memory directly answers the user's question, use it confidently.\n\n"
                "Retrieved Memories:\n"
            )

            for memory in retrieved_memories:
                memory_context += f"- {memory['content']}\n"

        messages = [
            {
                "role": "system",
                "content": self.system_prompt + memory_context
            }
        ] + self.conversation_manager.get_history()

        reply = self.client.chat(messages)

        self.conversation_manager.add_assistant_message(
            reply
        )

        return reply