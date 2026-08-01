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

# Words/phrases that indicate a fact is describing an absence of
# information rather than an actual fact (e.g. "The user's birthday is
# unknown."). Seen in testing: the model will sometimes fabricate a
# statement like this out of a bare question with zero real content,
# then mark it as a "correction" that overwrites a correct memory.
# The prompt tells it not to -- this is the code-level backstop.
NON_FACT_MARKERS = (
    "unknown", "unspecified", "not specified", "not mentioned",
    "not provided", "unclear", "not stated", "not sure", "not certain"
)

# A message this heuristic identifies as a bare question skips the LLM
# call entirely and is never classified. This is deterministic and
# catches cases prompting alone cannot reliably prevent: a small local
# model asked "don't store questions" will still sometimes invent an
# answer-shaped "fact" for a question it can't answer (see NON_FACT_MARKERS
# above for the real example that motivated this).
QUESTION_STARTERS = {
    "who", "what", "when", "where", "why", "how",
    "is", "are", "do", "does", "did", "can", "could",
    "would", "will", "should", "have", "has"
}

# If any of these appear in the message, it's treated as carrying real
# declarative content even if it also reads like a question, so it's
# still sent to the LLM rather than auto-skipped.
DECLARATION_OVERRIDE_CUES = (
    "remember", "actually", "correct", "note that", "fyi",
    "by the way", "also remember", "my birthday", "i am", "i'm"
)


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

    def _looks_like_bare_question(self, message: str) -> bool:
        """
        Deterministic pre-filter: catches bare questions before the LLM
        ever sees them, so there's nothing for it to hallucinate an
        answer-shaped "fact" out of. Skipped if the message also carries
        a clear declarative cue (e.g. "remember", "actually"), since
        those often mix a real correction into a question-like sentence.
        """
        text = message.strip().lower()

        if not text:
            return False

        if any(cue in text for cue in DECLARATION_OVERRIDE_CUES):
            return False

        words = text.split()
        first_word = words[0].strip(",.!?\"'") if words else ""

        ends_with_question_mark = text.endswith("?")
        starts_like_question = first_word in QUESTION_STARTERS

        return ends_with_question_mark or starts_like_question

    def _is_valid_fact(self, content: str) -> bool:
        """
        Rejects fragments, empty strings, facts not phrased as
        statements about the user, and facts that merely describe an
        absence of information. This is what catches the model storing
        a fact about itself, a meta-comment about the chat, a
        stripped-context fragment like "Python", or a fabricated
        "unknown" statement -- even if prompt-following fails, this
        filter still fires.
        """
        if not content:
            return False

        if len(content.split()) < MIN_FACT_WORDS:
            return False

        if not content.lower().startswith(REQUIRED_SUBJECT):
            return False

        lowered = content.lower()
        if any(marker in lowered for marker in NON_FACT_MARKERS):
            return False

        return True

    def classify(self, message: str, history: str = "") -> dict:
        """
        Runs the LLM classifier on a message.

        Args:
            message: the current user message to classify.
            history: recent conversation turns as plain text, used only
                to help the model resolve pronouns like "you"/"your"
                (e.g. distinguishing a fact about the assistant from a
                fact about the user). Never mined for facts itself —
                only `message` is classified.

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

        default = {"facts": []}

        # Deterministic fast-path: skip the LLM entirely for bare
        # questions. Cheaper, and immune to the model ignoring its
        # instructions -- there is no LLM call left to misbehave.
        if self._looks_like_bare_question(message):
            print(f"[StoragePolicy] bare question detected, skipping classification: {message!r}")
            return default

        prompt = CLASSIFIER_PROMPT.format(
            message=message,
            history=history if history.strip() else "(no prior context)"
        )

        messages = [
            {"role": "system", "content": "You output only valid JSON, nothing else."},
            {"role": "user", "content": prompt}
        ]

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
