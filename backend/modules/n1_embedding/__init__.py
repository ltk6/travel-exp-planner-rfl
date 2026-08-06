"""N1: Unified multi-channel embedding API."""

from .pipeline import (
    embed,
    embed_batch,
    light_embed,
    light_embed_batch,
)

__all__ = [
    "embed",
    "light_embed",
    "embed_batch",
    "light_embed_batch",
]