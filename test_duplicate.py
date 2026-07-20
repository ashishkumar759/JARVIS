from memory.embedding_service import EmbeddingService
from core.ollama_client import OllamaClient
from memory.memory_manager import MemoryManager


def main():
    print("=" * 60)
    print("JARVIS Duplicate Detection Test")
    print("=" * 60)

    # Initialize components
    embedding_service = EmbeddingService()
    client = OllamaClient(
        model="llama3.2:latest",
        url = "http://localhost:11434/api/chat"
    )
    memory_manager = MemoryManager(embedding_service, client)

    test_message = "My favorite programming language is Python."

    print("\nFirst storage attempt...")
    memory_id_1 = memory_manager.store_memory(test_message)

    if memory_id_1:
        print(f"✓ Memory stored with ID: {memory_id_1}")
    else:
        print("✗ Memory was not stored.")

    print("\nSecond storage attempt (same message)...")
    memory_id_2 = memory_manager.store_memory(test_message)

    if memory_id_2:
        print(f"✗ Duplicate stored with ID: {memory_id_2}")
    else:
        print("✓ Duplicate correctly detected and skipped.")

    print("\nCurrent SQLite Memories:\n")

    memories = memory_manager.sqlite_store.get_all_memories()

    for memory in memories:
        print(memory)

    print("\nValidation Complete.")


if __name__ == "__main__":
    main()