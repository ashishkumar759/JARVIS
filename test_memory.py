from memory.memory_manager import MemoryManager

manager = MemoryManager()

memory_id = manager.store_memory(
    "Ashish likes black coffee.",
    "preference"
)

print(f"Memory stored with ID: {memory_id}")

print("\nStored Memories:")
for memory in manager.get_all_memories():
    print(memory)

manager.close()
results = manager.chroma_store.search("What drink does Ashish like?")
print(results)