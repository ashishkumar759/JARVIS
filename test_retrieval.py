from memory.embedding_service import EmbeddingService
from memory.retrieval import MemoryRetriever

embedding_service = EmbeddingService()

retriever = MemoryRetriever(
    embedding_service=embedding_service
)

results = retriever.search(
    "What coffee do I like?"
)

print("\nRetrieved Memories:\n")

if not results:
    print("No memories found.")
else:
    for memory in results:
        print(memory)