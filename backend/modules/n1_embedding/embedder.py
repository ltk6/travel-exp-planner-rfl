"""N1: SentenceTransformer model loading and vector encoding."""

from __future__ import annotations
from typing import List, Optional

from config import setup_logging
from .config import EMBEDDING_MODEL_NAME, LIGHT_EMBEDDING_MODEL_NAME
logger = setup_logging("N1.embedder")


_MODEL = None
_LIGHT_MODEL = None

def get_model():
    """Return the globally loaded model, initializing it if necessary."""
    global _MODEL
    if _MODEL is None:
        try:
            # Log first so the user knows what's taking time
            logger.info(f"N1 — Initializing Embedding Engine (Model: {EMBEDDING_MODEL_NAME})...")
            
            # Heavy imports happen here
            import torch
            from sentence_transformers import SentenceTransformer
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"N1 — Loading weights onto {device} (this may take a few seconds)...")
            
            _MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
            logger.info(f"N1 — Embedding Model ready on {_MODEL.device}")
        except ImportError:
            logger.error("N1 — sentence-transformers or torch not installed")
            raise RuntimeError("sentence-transformers or torch not installed")
        except Exception as e:
            logger.error(f"N1 — Failed to load embedding model: {e}")
            raise RuntimeError(f"Failed to load embedding model: {e}")
    return _MODEL

def get_light_model():
    """Return the globally loaded light model, initializing it if necessary."""
    global _LIGHT_MODEL
    if _LIGHT_MODEL is None:
        try:
            # Log first so the user knows what's taking time
            logger.info(f"N1 — Initializing Light Embedding Engine (Model: {LIGHT_EMBEDDING_MODEL_NAME})...")
            
            # Heavy imports happen here
            import torch
            from sentence_transformers import SentenceTransformer
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"N1 — Loading weights onto {device} (this may take a few seconds)...")
            
            _LIGHT_MODEL = SentenceTransformer(LIGHT_EMBEDDING_MODEL_NAME, device=device)
            logger.info(f"N1 — Light Embedding Model ready on {_LIGHT_MODEL.device}")
        except ImportError:
            logger.error("N1 — sentence-transformers or torch not installed")
            raise RuntimeError("sentence-transformers or torch not installed")
        except Exception as e:
            logger.error(f"N1 — Failed to load light embedding model: {e}")
            raise RuntimeError(f"Failed to load light embedding model: {e}")
    return _LIGHT_MODEL

# Pre-load at module level to avoid lazy-loading delays during user requests
get_model()
get_light_model()


def embed_strings(strings: List[str]) -> List[Optional[List[float]]]:
    """
    Converts strings into normalized vectors.
    Return None for empty strings.
    """
    if not strings:
        return []

    model = get_model()

    # Separate non-empty strings, track original positions
    valid = [(i, t) for i, t in enumerate(strings) if t and t.strip()]
    if not valid:
        return [None] * len(strings)

    indices, to_encode = zip(*valid)
    vectors = model.encode(
        list(to_encode),
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    ).tolist()

    # Reconstruct with None for empty slots
    output: List[Optional[List[float]]] = [None] * len(strings)
    for idx, vec in zip(indices, vectors):
        output[idx] = vec

    return output


def light_embed_strings(strings: List[str]) -> List[Optional[List[float]]]:
    """
    Converts strings into normalized vectors using the light model.
    Return None for empty strings.
    """
    if not strings:
        return []

    model = get_light_model()

    # Separate non-empty strings, track original positions
    valid = [(i, t) for i, t in enumerate(strings) if t and t.strip()]
    if not valid:
        return [None] * len(strings)

    indices, to_encode = zip(*valid)
    
    # The prefix (e.g. 'query: ' or 'passage: ') should be added before calling this function.

    vectors = model.encode(
        list(to_encode),
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    ).tolist()

    # Reconstruct with None for empty slots
    output: List[Optional[List[float]]] = [None] * len(strings)
    for idx, vec in zip(indices, vectors):
        output[idx] = vec

    return output