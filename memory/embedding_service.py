import os

# Must be set before sentence_transformers/huggingface_hub is imported —
# these libraries read the env var once at import time to decide whether
# they're allowed to make any network calls at all. This is the
# belt-and-suspenders guard (Option A): even if the local path below were
# ever wrong or missing, this stops it from silently falling back to a
# network fetch.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from pathlib import Path
from sentence_transformers import SentenceTransformer

# Anchored to this file's location, same pattern chroma_store.py uses --
# resolves correctly no matter what directory the app is launched from,
# and survives the project folder being moved or renamed.
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = BASE_DIR.parent / "models" / "all-MiniLM-L6-v2"


class EmbeddingService:
    def __init__(self, model_name=None):
        model_path = str(model_name) if model_name else str(DEFAULT_MODEL_PATH)
        self.model = SentenceTransformer(model_path)

    def embed(self, text: str):
        return self.model.encode(text).tolist()