import requests


class OllamaClient:

    def __init__(self, model, url):
        self.model = model
        self.url = url

    def chat(self, messages):

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        return response.json()["message"]["content"]