from memory.retrieval import MemoryRetriever

retriever = MemoryRetriever()

results = retriever.search(
    "What coffee do I like?"
)

print("\nRetrieved Memories:\n")

if not results:
    print("No memories found.")
else:
    for memory in results:
        print(memory)