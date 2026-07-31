import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "storage_policy_prompt.txt"

with open(PROMPT_FILE, "r", encoding="utf-8") as file:
    CLASSIFIER_PROMPT = file.read()

VALID_CATEGORIES = {
            "personal",
            "preference",
            "work",
            "device",
            "reminder",
            "general",
            "journal"
        }

# Safety-net rules applied to whatever the LLM returns, independent of
# how well it followed the prompt. These exist because a small local
# model will not reliably obey instructions 100% of the time — the
# validation below is what actually prevents garbage from reaching
# the database, not the prompt wording alone.
REQUIRED_SUBJECT = "the user"
MIN_FACT_WORDS = 3


class StoragePolicy:
    """
    Decides whether a message should become long-term memory
    and assigns a category, using an LLM call instead of keyword matching.

    A single message can yield zero, one, or multiple facts. This matters
    because a message often mixes storable and non-storable content
    (e.g. "I like black coffee, what's the weather?") — asking the model
    for one fact per message forces it to either drop the real fact or
    contaminate it with the unrelated part of the sentence.
    """

    def __init__(self, client):
        """
        Args:
            client: an OllamaClient instance (reused from core.ollama_client)
        """
        self.client = client

    def _extract_json(self, text: str) -> str:
        """
        Extract the first JSON object from the model response.
        Handles markdown code fences and extra explanatory text.
        """
        text = text.strip()

        # Remove markdown code fences
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        # Find first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found.")

        return text[start:end + 1]

    def _is_valid_fact(self, content: str) -> bool:
        """
        Rejects fragments, empty strings, and facts not phrased as
        statements about the user. This is what catches the model
        storing a fact about itself, a meta-comment about the chat,
        or a stripped-context fragment like "Python" — even if the
        prompt-following fails, this filter still fires.
        """
        if not content:
            return False

        if len(content.split()) < MIN_FACT_WORDS:
            return False

        if not content.lower().startswith(REQUIRED_SUBJECT):
            return False

        return True

    def classify(self, message: str) -> dict:
        """
        Runs the LLM classifier on a message.

        Returns a dict:
            {
                "facts": [
                    {
                        "content": str,
                        "category": str,
                        "is_correction": bool
                    },
                    ...
                ]
            }

        The list may be empty if nothing in the message is worth storing.

        Fails safe: on any parsing/network error, returns an empty facts
        list rather than raising, so a bad classification never crashes
        the chat loop.
        """

        prompt = CLASSIFIER_PROMPT.format(message=message)

        messages = [
            {"role": "system", "content": "You output only valid JSON, nothing else."},
            {"role": "user", "content": prompt}
        ]

        default = {"facts": []}

        try:
            # format="json" + temperature=0: constrains the model to emit
            # valid JSON and makes classification deterministic. Without
            # this, a chatty local model will sometimes wrap the JSON in
            # prose or vary its answer for the same input.
            raw = self.client.chat(
                messages,
                format="json",
                options={"temperature": 0}
            )
            print("[DEBUG] RAW CLASSIFIER OUTPUT:", repr(raw))

            raw = self._extract_json(raw)
            parsed = json.loads(raw)

            raw_facts = parsed.get("facts", [])
            if not isinstance(raw_facts, list):
                raw_facts = []

            cleaned_facts = []

            for item in raw_facts:
                if not isinstance(item, dict):
                    continue

                content = str(item.get("content", "")).strip()
                category = str(item.get("category", "general")).strip().lower()
                is_correction = bool(item.get("is_correction", False))

                if category not in VALID_CATEGORIES:
                    category = "general"

                if not self._is_valid_fact(content):
                    print(f"[StoragePolicy] rejected low-quality fact: {content!r}")
                    continue

                cleaned_facts.append({
                    "content": content,
                    "category": category,
                    "is_correction": is_correction
                })

            return {"facts": cleaned_facts}

        except Exception as e:
            print(f"[StoragePolicy] classification failed, defaulting to no-store: {e}")
            return default
