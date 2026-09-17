import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL_NAME

_model_instance = None

def get_embedding_model() -> SentenceTransformer:
    global _model_instance
    if _model_instance is None:
        _model_instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model_instance

def generate_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generates normalized embedding vectors for a list of text strings.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype(np.float32)
