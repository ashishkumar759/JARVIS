from memory.storage_policy import StoragePolicy

policy = StoragePolicy()

messages = [
    "I like black coffee.",
    "Hello!",
    "My birthday is 7 July.",
    "What's the weather today?",
    "I work at OpenAI.",
    "I have an RTX 3050 laptop."
]

for message in messages:
    print(f"\nMessage: {message}")
    print("Store:", policy.should_store(message))

    if policy.should_store(message):
        print("Category:", policy.categorize(message))