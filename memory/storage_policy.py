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
            "general"
        }

 
 
class StoragePolicy:
    """
    Decides whether a message should become long-term memory
    and assigns a category, using an LLM call instead of keyword matching.
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
 
    def classify(self, message: str) -> dict:
        """
        Runs the LLM classifier on a message.
 
        Returns a dict:
            {
                "should_store": bool,
                "fact": str,
                "category": str,
                "is_correction": bool
            }
 
        Fails safe: on any parsing/network error, returns should_store=False
        rather than raising, so a bad classification never crashes the chat loop.
        """
 
        prompt = CLASSIFIER_PROMPT.format(message=message)

 
        messages = [
            {"role": "system", "content": "You output only valid JSON, nothing else."},
            {"role": "user", "content": prompt}
        ]
 
        default = {
            "should_store": False,
            "fact": "",
            "category": "general",
            "is_correction": False
        }
 
        try:
            raw = self.client.chat(messages)
            raw = self._extract_json(raw)

            parsed = json.loads(raw)
 
            category = str(
                parsed.get("category", "general")
            ).strip().lower()

            if category not in VALID_CATEGORIES:
                category = "general"

            fact = str(parsed.get("fact", "")).strip()

            return {
                "should_store": bool(parsed.get("should_store", False)),
                "fact": fact,
                "category": category,
                "is_correction": bool(parsed.get("is_correction", False))
            }
 
        except Exception as e:
            print(f"[StoragePolicy] classification failed, defaulting to no-store: {e}")
            return default