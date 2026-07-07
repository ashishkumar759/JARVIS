from memory.memory_manager import MemoryManager

manager = MemoryManager()

messages = [
    "Hello!",
    "I like black coffee.",
    "My birthday is 7 July.",
    "What's the weather today?"
]

for message in messages:
    print(f"\nMessage: {message}")

    memory_id = manager.store_memory(message)

    if memory_id:
        print(f"Stored with ID: {memory_id}")
    else:
        print("Not stored.")