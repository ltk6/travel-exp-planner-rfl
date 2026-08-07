"""N1: Unified multi-channel embedding API."""

from .pipeline import (
    embed,
    embed_batch,
    light_embed,
    light_embed_batch,
)
from .schemas import N1EmbedInput

__all__ = [
    "embed",
    "light_embed",
    "embed_batch",
    "light_embed_batch",
    "N1EmbedInput",
]