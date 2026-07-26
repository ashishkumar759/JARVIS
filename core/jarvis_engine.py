from pathlib import Path

from core.conversation_manager import ConversationManager
from core.ollama_client import OllamaClient

from memory.embedding_service import EmbeddingService
from memory.memory_manager import MemoryManager
from memory.retrieval import MemoryRetriever


class JarvisEngine:
    """
    Single interface between the UI and the JARVIS backend.

    The UI should ONLY communicate with this class.
    No UI page should directly import or use:
        - OllamaClient
        - MemoryManager
        - MemoryRetriever
        - SQLiteStore
        - ChromaStore
    """

    def __init__(
        self,
        model="llama3.2:latest",
        url="http://localhost:11434/api/chat"
    ):

        # -----------------------------
        # Core Components
        # -----------------------------

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

        # -----------------------------
        # Load System Prompt
        # -----------------------------

        base_dir = Path(__file__).resolve().parent.parent
        prompt_file = base_dir / "prompts" / "system_prompt.txt"

        with open(prompt_file, "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    # ==========================================================
    # Chat API
    # ==========================================================

    def send_message(self, user_message):
        """
        Primary API used by the Chat UI.
        """

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
                "The following memories are authoritative facts stored "
                "by your memory system. "
                "Use them while answering the user.\n\n"
                "Retrieved Memories:\n"
            )

            for memory in retrieved_memories:
                memory_context += (
                    f"- {memory['content']}\n"
                )

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

    # ==========================================================
    # Memory API
    # ==========================================================
    
    # ==========================================================
# Journal API
# ==========================================================

    def save_journal(self, journal_text):
        """
        Store a journal entry using the existing memory system.
        """

        journal_text = journal_text.strip()

        if not journal_text:
            return False

        self.memory_manager.store_memory(
            journal_text
        )

        return True


    def chat(self, user_message):
        """
        Backward-compatible wrapper.
        Existing CLI code can continue using chat().
        """
        return self.send_message(user_message)
       


    def search_memories(self, query):

        return self.memory_retriever.search(query)

    def get_all_memories(self):

        return self.memory_manager.sqlite_store.get_all_memories()

    # ==========================================================
    # Conversation API
    # ==========================================================

    def get_chat_history(self):

        return self.conversation_manager.get_history()

    def clear_chat_history(self):

        self.conversation_manager.clear_history()

    # ==========================================================
# Settings API
# ==========================================================

    def get_settings(self):

        return {
            "model": self.client.model,
            "embedding_model": "all-MiniLM-L6-v2",
            "memory_backend": "SQLite + ChromaDB",
            "llm_backend": "Ollama",
            "status": "Connected"
        }