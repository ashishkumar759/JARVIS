from core.jarvis_engine import JarvisEngine


def main():

    engine = JarvisEngine()

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

            answer = engine.chat(user_input)

            print()
            print("JARVIS:", answer)
            print()

        except Exception as e:

            print()
            print("ERROR:", e)
            print()


if __name__ == "__main__":
    main()