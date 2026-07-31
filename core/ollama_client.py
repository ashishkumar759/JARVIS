import requests


class OllamaClient:

    def __init__(self, model, url):
        self.model = model
        self.url = url

    def chat(self, messages, format=None, options=None):
        """
        Args:
            messages: chat history in Ollama's message format.
            format: optional, e.g. "json" to force the model to return
                valid JSON only. Used by StoragePolicy classification;
                left as None for normal conversational replies so this
                is fully backward compatible.
            options: optional dict of Ollama generation options, e.g.
                {"temperature": 0} for deterministic output.
        """

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        if format is not None:
            payload["format"] = format

        if options is not None:
            payload["options"] = options

        response = requests.post(
            self.url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        return response.json()["message"]["content"]