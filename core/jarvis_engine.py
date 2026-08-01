from pathlib import Path
from datetime import datetime 

from core.conversation_manager import ConversationManager
from core.ollama_client import OllamaClient

from memory.embedding_service import EmbeddingService
from memory.memory_manager import MemoryManager
from memory.retrieval import MemoryRetriever
from PySide6.QtCore import QObject, Signal


# How many previous journal entries to pull into the "Generate
# Tomorrow's Plan" prompt, in addition to today's entry. Kept small and
# bounded so the prompt stays a sane size for the local model even
# after months of journaling, rather than growing unboundedly with
# accumulated data.
PLAN_RECENT_JOURNAL_LIMIT = 7

# How many semantically-relevant long-term memories (preferences,
# work, reminders, etc.) to pull into the same prompt, via the same
# retrieval already used for chat.
PLAN_MEMORY_TOP_K = 8


class JarvisEngine(QObject):
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
    memory_updated = Signal()



    def __init__(
        self,
        model="llama3.2:latest",
        url="http://localhost:11434/api/chat"
    ):

        super().__init__()

        self.conversation_manager = ConversationManager()

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

        plan_prompt_file = base_dir / "prompts" / "next_day_plan_prompt.txt"

        with open(plan_prompt_file, "r", encoding="utf-8") as file:
            self.next_day_plan_prompt = file.read()

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

        # Last few turns *before* the current message, as plain text,
        # so the classifier can tell "your birthday" said about the
        # assistant apart from a fact about the user. This is context
        # only -- store_memory only ever extracts facts from
        # `user_message` itself.
        history_window = self.conversation_manager.get_history()[:-1][-6:]
        history_text = "\n".join(
            f"{turn['role'].capitalize()}: {turn['content']}"
            for turn in history_window
        )

        self.memory_manager.store_memory(
            user_message,
            history=history_text
        )

        retrieved_memories = self.memory_retriever.search(
            user_message
        )

        time_context = (
            "\nCurrent date and time: "
            f"{datetime.now().strftime('%A, %d %B %Y, %I:%M %p')}\n"
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
                "content": self.system_prompt + time_context + memory_context
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

        memory_id = self.memory_manager.store_journal(
            journal_text
        )
        if memory_id is not None:
            self.memory_updated.emit()
            return True 

        return False 

    # ==========================================================
    # Next-Day Plan API
    # ==========================================================

    def generate_next_day_plan(
        self,
        today_journal_draft="",
        recent_journal_limit=PLAN_RECENT_JOURNAL_LIMIT,
        memory_top_k=PLAN_MEMORY_TOP_K
    ):
        """
        Generates a plan for tomorrow for the Journal page's
        "Generate Tomorrow's Plan" section. Pure read + LLM call --
        stores nothing (see save_plan for that).

        Context assembled, in order:
          1. today_journal_draft -- whatever is currently typed in the
             journal editor. May be unsaved. If empty (e.g. the user
             already clicked "Save Journal", which clears the editor),
             falls back to the most recently saved journal entry.
          2. The `recent_journal_limit` previous journal entries,
             chronological, so the plan can react to an actual pattern
             across days instead of one entry in isolation.
          3. Long-term memories semantically relevant to today's entry
             (preferences, work, reminders, etc.), via the same
             MemoryRetriever already used by send_message -- not every
             memory ever stored, to keep the prompt a sane size and
             avoid slow or failing LLM calls as history grows over
             months.

        Raises ValueError if there is no journal content at all to
        plan from (nothing typed and nothing previously saved).
        """

        today_text = (today_journal_draft or "").strip()

        previous_journals = self.memory_manager.sqlite_store.get_memories_by_category(
            category="journal",
            limit=recent_journal_limit + 1
        )

        if not today_text:

            if not previous_journals:
                raise ValueError(
                    "No journal entry found yet. Write something in "
                    "today's journal first."
                )

            # Editor was empty (already saved and cleared) -- treat the
            # most recent saved entry as "today", and don't repeat it
            # again in the "previous entries" list below.
            today_text = previous_journals[0]["content"]
            previous_journals = previous_journals[1:]

        else:

            previous_journals = previous_journals[:recent_journal_limit]

        journal_history_text = ""

        if previous_journals:

            journal_history_text = (
                "\nPrevious journal entries (most recent first):\n"
            )

            for entry in previous_journals:
                journal_history_text += (
                    f"- [{entry['created_at']}] {entry['content']}\n"
                )

        # Semantic recall across all long-term memories relevant to
        # today's entry. Journal-category hits are excluded here since
        # recent journal history is already covered, chronologically,
        # above -- this avoids showing the same entry twice.
        relevant_memories = [
            memory
            for memory in self.memory_retriever.search(
                today_text,
                top_k=memory_top_k
            )
            if memory["category"] != "journal"
        ]

        memory_context = ""

        if relevant_memories:

            memory_context = "\nRelevant long-term memories:\n"

            for memory in relevant_memories:
                memory_context += (
                    f"- [{memory['category']}] {memory['content']}\n"
                )

        time_context = (
            "\nCurrent date and time: "
            f"{datetime.now().strftime('%A, %d %B %Y, %I:%M %p')}\n"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    self.next_day_plan_prompt
                    + time_context
                    + journal_history_text
                    + memory_context
                )
            },
            {
                "role": "user",
                "content": f"Today's journal entry:\n{today_text}"
            }
        ]

        plan = self.client.chat(messages)

        return plan

    def save_plan(self, plan_text):
        """
        Stores a generated plan using the existing memory system.

        Same pattern as save_journal: an explicit user action, so it
        bypasses the StoragePolicy classifier and writes directly.
        """

        plan_text = plan_text.strip()

        if not plan_text:
            return False

        memory_id = self.memory_manager.store_plan(
            plan_text
        )

        if memory_id is not None:
            self.memory_updated.emit()
            return True

        return False

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

    def delete_memory(self, memory_id):
        """
        Permanently deletes a single memory (used by the Memory
        Browser's per-item delete button). Removes it from both the
        structured store and the semantic store, so it can never
        resurface in the browser or in retrieved chat context.

        Returns True if the memory existed and was deleted.
        """

        deleted = self.memory_manager.delete_memory(memory_id)

        if deleted:
            self.memory_updated.emit()

        return deleted

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