"""
preferences.py — Rule-based inference of user activity preferences.

Receives user_input from N6 (tags + text + img_desc) and returns preference scores
on 3 physical axes in [0, 1]:
    - intensity: preference for excitement / adventure
    - physical:  preference for physical activity level
    - social:    preference for social / crowd interaction

Approach: lookup table from tags (highest weight) + keyword scan over text+img_desc (bonus).
Deterministic — the same input always produces the same output.

Returns None for any axis with no signal → scoring skips that axis (neutral treatment).

All tag keys in _TAG_WEIGHTS MUST exist in backend.shared.maps.ALL_ACTIVITY_TAGS.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional

from backend.shared.maps import ALL_ACTIVITY_TAGS


_ALL_TAG_KEYS = set(ALL_ACTIVITY_TAGS.keys())

# =============================================================================
# TAG → PREFERENCE AXIS WEIGHTS
# All keys must be present in ALL_TAGS
# Values: ±1.0 = strong signal, ±0.5 = moderate, ±0.3 = mild.
# Positive = user wants this axis high; negative = user wants it low.
# =============================================================================

_TAG_WEIGHTS: Dict[str, Dict[str, float]] = {
    # ── High intensity / physical ────────────────────────────────────────────
    "adventure":       {"intensity":  1.0, "physical":  0.8},
    "trekking":        {"intensity":  0.8, "physical":  1.0},
    "motorbiking":     {"intensity":  0.8, "physical":  0.5},
    "cycling":         {"intensity":  0.3, "physical":  0.8},
    "surfing":         {"intensity":  0.8, "physical":  0.8},
    "scuba diving":    {"intensity":  0.5, "physical":  0.5},
    "kayaking":        {"intensity":  0.5, "physical":  0.7},
    "camping":         {"intensity":  0.4, "physical":  0.5},
    "canyoning":       {"intensity":  0.9, "physical":  0.9},
    "rock climbing":   {"intensity":  0.9, "physical":  1.0},
    "caving":          {"intensity":  0.6, "physical":  0.6},
    "rafting":         {"intensity":  0.8, "physical":  0.7},
    "kitesurfing":     {"intensity":  0.9, "physical":  0.8},
    "trail running":   {"intensity":  0.7, "physical":  1.0},

    # ── Relaxation / low intensity ───────────────────────────────────────────
    "peaceful":        {"intensity": -0.8, "physical": -0.5, "social": -0.3},
    "cozy":            {"intensity": -0.5, "physical": -0.3, "social": -0.2},
    "spa":             {"intensity": -0.8, "physical": -0.8},
    "boat cruise":     {"intensity": -0.3, "physical": -0.5},
    "slow travel":     {"intensity": -0.5, "physical": -0.4},
    "yoga retreat":    {"intensity": -0.5, "physical":  0.2, "social": -0.3},
    "wellness retreat":{"intensity": -0.6, "physical": -0.3},
    "chill":           {"intensity": -0.6, "physical": -0.4},
    "picnic":          {"intensity": -0.4, "physical": -0.2, "social":  0.2},

    # ── Social axis ───────────────────────────────────────────────────────────
    "family":          {"social":  0.8, "intensity": -0.3},
    "group":           {"social":  1.0},
    "friends trip":    {"social":  0.8},
    "vibrant":         {"social":  0.8, "intensity":  0.3},
    "couple":          {"social": -0.2},
    "solo":            {"social": -1.0},
    "romantic":        {"social": -0.3, "intensity": -0.3},
    "homestay":        {"social":  0.3, "intensity": -0.2},
    "off the beaten path": {"intensity":  0.3, "social": -0.3},

    # ── Soft activities ───────────────────────────────────────────────────────
    "photography":     {"physical":  0.2},
    "cooking class":   {"social":    0.3, "physical": -0.2},
    "nightlife":       {"social":    0.8, "intensity":  0.4},
}

# =============================================================================
# KEYWORD WEIGHTS  (text + img_desc, weighted at 0.5× tag weight)
# =============================================================================

_KEYWORD_WEIGHTS: Dict[str, Dict[str, float]] = {
    # Vietnamese
    "mạo hiểm":  {"intensity":  0.5},
    "kịch tính": {"intensity":  0.5},
    "thử thách": {"intensity":  0.4, "physical":  0.4},
    "leo núi":   {"intensity":  0.5, "physical":  0.6},
    "vận động":  {"physical":   0.5},
    "thể thao":  {"physical":   0.5, "intensity":  0.3},
    "thư giãn":  {"intensity": -0.6, "physical": -0.3},
    "yên tĩnh":  {"intensity": -0.5, "social":   -0.3},
    "yên bình":  {"intensity": -0.5, "social":   -0.3},
    "nghỉ ngơi": {"intensity": -0.5, "physical": -0.3},
    "đông vui":  {"social":     0.5},
    "bạn bè":    {"social":     0.4},
    "gia đình":  {"social":     0.5, "intensity": -0.2},
    "một mình":  {"social":    -0.8},
    "lãng mạn":  {"social":    -0.3, "intensity": -0.2},
    "cắm trại":  {"intensity":  0.3, "physical":  0.4},
    "leo vách":  {"intensity":  0.8, "physical":  1.0},

    # English (img_desc from N2 is usually English)
    "adventure":  {"intensity":  0.5},
    "exciting":   {"intensity":  0.4},
    "hiking":     {"intensity":  0.4, "physical":  0.5},
    "climbing":   {"intensity":  0.5, "physical":  0.6},
    "active":     {"physical":   0.4},
    "peaceful":   {"intensity": -0.5, "social":   -0.2},
    "quiet":      {"intensity": -0.4, "social":   -0.3},
    "relaxing":   {"intensity": -0.5, "physical": -0.3},
    "family":     {"social":     0.4},
    "crowd":      {"social":     0.4},
    "bustling":   {"social":     0.5},
    "solo":       {"social":    -0.5},
    "extreme":    {"intensity":  0.8, "physical":  0.7},
    "strenuous":  {"physical":   0.8, "intensity":  0.5},
}

_AXES = ("intensity", "physical", "social")

# Axes with total absolute signal below this threshold → return None (no preference)
NEUTRAL_THRESHOLD = 0.10


def _sigmoid(x: float) -> float:
    """Map raw signal ℝ → [0, 1]. x=0 → 0.5, x=±2 → ~0.88/0.12."""
    return 1.0 / (1.0 + math.exp(-x))


def infer_user_preferences(user_input: Dict) -> Dict[str, Optional[float]]:
    """
    Analyse user_input → preference scores on 3 axes: intensity / physical / social.

    Args:
        user_input: {"text": str?, "img_desc": str?, "tags": [str]?}

    Returns:
        {"intensity": float|None, "physical": float|None, "social": float|None}
        - float in [0,1]: 1.0 = strongly prefers high value, 0.0 = strongly opposed.
        - None: no clear signal → scoring will skip this axis (neutral, not penalised).
    """
    raw = {axis: 0.0 for axis in _AXES}
    signal_count = {axis: 0 for axis in _AXES}

    # 1. Tags (highest weight — direct lookup)
    tags = [t.lower().strip() for t in (user_input.get("tags") or [])]
    for tag in tags:
        axis_weights = _TAG_WEIGHTS.get(tag)
        if not axis_weights:
            continue
        for axis, w in axis_weights.items():
            raw[axis]          += w
            signal_count[axis] += 1

    # 2. Keywords in text + img_desc (0.5× tag weight)
    haystack = " ".join(filter(None, [
        (user_input.get("text")     or "").lower(),
        (user_input.get("img_desc") or "").lower(),
    ]))
    if haystack:
        for kw, axis_weights in _KEYWORD_WEIGHTS.items():
            if kw in haystack:
                for axis, w in axis_weights.items():
                    raw[axis]          += 0.5 * w
                    signal_count[axis] += 1

    # 3. Sigmoid + threshold: axes with little/no signal → None
    result: Dict[str, Optional[float]] = {}
    for axis in _AXES:
        if signal_count[axis] == 0 or abs(raw[axis]) < NEUTRAL_THRESHOLD:
            result[axis] = None
        else:
            result[axis] = round(_sigmoid(raw[axis]), 3)

    return result
