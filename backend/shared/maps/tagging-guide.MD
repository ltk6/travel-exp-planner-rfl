# Shared Tagging Guide: Ontology & Vector Space Strategy

This guide defines the tagging strategy across the platform, specifically for mapping User Intents (N1/N6) and Location Profiles (N4/N5) into the shared `tags.py` ontology.

## 0. Pipeline Architecture

Tags form the semantic bridge between user inputs and locations.

```text
User Input (Text + Questionnaire)
        │
        ▼
   N1 / N6 Processing
  ┌─────────────────────────────────────────────────────┐
  │  1. Map answers to predefined tag keys              │
  │  2. Look up expansion strings from ALL_TAGS         │
  │  3. Join expansions into a single semantic string   │
  └─────────────────────────────────────────────────────┘
        │
        ▼
   BGE-M3 Embedding Model (Single Vector)
        │
        ▼
   Cosine Similarity (User Vector ↔ Location Vector)
        │
        ▼
   N4 Ranking / N5 Generation
```

**Critical Implication**: Because all tags are concatenated into a single string before embedding, every tag competes for influence. BGE-M3 averages the semantic content. Adding too many tags dilutes the vector, pushing it toward the center of the embedding space and resulting in weak, generic matches.

---

## 1. Fundamental Laws of Tagging

### Law 1: Dilution is Real
The more tags assigned, the weaker the signal. A location with 25 tags will score "okay" against everything and "great" against nothing.
- **Weak (Too Many):** `["beach", "mountain", "city", "history", "adventure", "peaceful", "romantic", "vibrant", "budget", "luxury", "family", "solo"]`
- **Strong (Focused):** `["beach", "snorkeling", "island", "peaceful", "couple", "seafood"]`

### Law 2: Category Balance
The categories with the most tags will dominate the vector. If you assign 8 activity tags and 1 vibe tag, the vector will be heavily activity-oriented, even if the location is primarily known for its atmosphere.

### Law 3: Expansions Drive the Match
The tag key (e.g., `"trekking"`) is just an identifier. The vector is shaped by its expansion (e.g., `"multi-day trekking mountain trail jungle endurance rewarding"`). Select tags based on the semantic weight of their expansions.

### Law 4: Shared Vocabulary
User intent and location profiles must expand through the exact same `ALL_TAGS` dictionary to ensure cosine distances are meaningful.

---

## 2. Location Tagging Rules

### 2.1 Total Tag Budget

| Tier | Total Tags | When to Use |
|------|-----------|-------------|
| Focused | **8–12** | Destination with a clear primary identity (e.g. Bai Sao beach, Langbiang peak) |
| Standard | **13–18** | Multi-experience destination (e.g. Nha Trang, Hoi An) |
| Complex | **19–24** | Major hub with diverse offerings (e.g. Da Nang, Phu Quoc) |
| Maximum | **25** | Hard cap. Above this, discrimination collapses. |

> **Default to Focused.** Err on the side of fewer, precise tags.

### 2.2 Per-Category Allocation

| Category | Min | Soft Max | Hard Max | Notes |
|----------|-----|----------|----------|-------|
| **Terrain/Water/Ecosystem** | 1 | 3 | 4 | Physical setting. Always include at least 1. |
| **Climate/Season** | 0 | 2 | 3 | Only if a genuine draw (e.g., cool highland, cloud sea). |
| **Culture/Heritage** | 0 | 3 | 4 | Only if prominently featured. |
| **Urban/Settlement** | 0 | 2 | 3 | For notable built environments. |
| **Activities (All)** | 1 | 4 | 6 | **Highest impact.** Prefer actual, available activities. |
| **Food/Drink** | 0 | 2 | 3 | Only if food is a specific draw. |
| **Vibe/Mood** | 1 | 2 | 3 | Emotional alignment. Always include 1–2. |
| **Trip Profile** | 0 | 2 | 3 | Only if distinctively suited (e.g., "honeymoon"). |
| **Budget/Style** | 0 | 1 | 2 | Dominant accommodation style. Don't mix luxury and budget. |
| **Special Interest** | 0 | 2 | 3 | Genuine niche destinations (e.g., "eco travel"). |

### 2.3 The "Specific Draw" Test
Before adding a tag, ask: *Would a reasonable traveler choose this location primarily because of this attribute?*
- **Yes:** Tag it.
- **Maybe/Incidental:** Skip it. (e.g., Do not tag "mountain" for Hoi An).

### 2.4 Avoid Semantic Duplication
Avoid pairing tags that overlap heavily in the embedding space:
- `peaceful` + `slow travel` (Near-identical)
- `luxury` + `resort` + `boutique` (Redundant premium cluster)
- `romantic` + `honeymoon` + `couple` (Extreme redundancy)
- `trekking` + `hiking` (Pick one based on difficulty)

### 2.5 Location Examples

**Côn Đảo** (13 tags - Standard Tier)
```python
tags = [
    "island", "beach", "coral reef",           # Terrain / Water
    "national park", "wildlife",               # Ecosystem
    "scuba diving", "snorkeling",              # Activities
    "war history", "spiritual",                # Culture
    "off the beaten path", "peaceful",         # Vibe
    "eco travel"                               # Special
]
```

**Bà Nà Hills** (9 tags - Focused Tier)
```python
tags = [
    "mountain", "cool climate",                # Terrain / Season
    "theme park", "cable car", "photography",  # Activities
    "colonial heritage",                       # Culture
    "instagrammable", "modern",                # Vibe
    "family"                                   # Trip Profile
]
```

**Chợ Nổi Cái Răng** (9 tags - Focused Tier)
```python
tags = [
    "delta", "river",                          # Terrain / Water
    "floating market",                         # Urban
    "food tour", "street food", "tropical fruit", # Food / Activities
    "authentic", "immersive",                  # Vibe
    "day trip"                                 # Trip Profile
]
```

---

## 3. Questionnaire & User Intent Tagging

User intent vectors must be **precise and sparse**. The retrieval model finds close neighbors; it does not average everything mentioned.

### 3.1 User Tag Budget

| Questionnaire Type | Recommended Tag Count |
|--------------------|-----------------------|
| Short (3–5 questions)| **4–8 tags** |
| Standard (6–10 questions)| **8–14 tags** |
| Long (10+ questions) | **12–18 tags** (Never exceed 20) |

### 3.2 Question-to-Tag Mapping

| Question Target | Category | Max Tags |
|-----------------|----------|----------|
| Landscape preference | TERRAIN/WATER | 1–2 |
| Desired activities | ACTIVITIES | 2–3 (Crucial) |
| Desired vibe | VIBE | 1–2 (Tie-breakers) |
| Travel companions | TRIP PROFILE | 1 |
| Trip duration | TRIP PROFILE | 1 |
| Budget | BUDGET | 1 |
| Dietary needs | FOOD | 1 |
| Must-haves | SPECIAL INT. | 0–2 |

### 3.3 Activities Drive Retrieval
Activity tags (`scuba diving`, `trekking`) are highly specific and strongly separate locations in the embedding space. Allocate the most questionnaire logic to capturing these preferences.

### 3.4 Vibe is the Tie-Breaker
When locations offer similar activities (e.g., two diving beaches), vibe tags (`peaceful` vs. `vibrant`) determine the ranking.

### 3.5 Handle Negative Preferences via Absence
The current single-vector space cannot subtract concepts. 
- If a user explicitly avoids crowds, do not inject an "anti-crowd" tag. 
- Instead, omit social/vibrant tags and rely on `peaceful`. 
- Hard filtering (omitting locations outright) is handled by N4 logic, not embeddings.

### 3.6 No Unstated Inferences
If a user wants to "trek in the mountains", derive `trekking` and `mountain`. Do not inject `camping` or `cool climate` unless explicitly stated, as this contaminates the vector with assumptions. (Exception: Basic Trip Profile derivations like "Partner" -> `couple`).

### 3.7 User Profile Example

**Input:** Beach/island, snorkeling, kayaking, peaceful/romantic, traveling with partner for 3 days, mid-range budget, loves seafood.

```python
user_tags = [
    "beach", "island",           # Terrain
    "snorkeling", "kayaking",    # Activities
    "peaceful", "romantic",      # Vibe
    "couple", "weekend trip",    # Trip Profile
    "mid range",                 # Budget
    "seafood"                    # Food
]
```
*Result:* Strongly matches Bãi Sao or Côn Đảo. Ignores Ha Giang or Ba Na Hills.

---

## 4. Common Tagging Mistakes

1. **The "Completeness" Trap:** Tagging every technically true attribute (20+ tags) creates a generic vector. Tag only the *primary draws*.
2. **Regional Tagging:** Tagging specific attributes (e.g., `war history`) to generic resorts just because they are in the same province. Tag intrinsic local attributes only.
3. **Symmetric Over-Tagging:** Tagging both `luxury` and `budget` averages out to zero. Pick the dominant profile.
4. **Missing Vibe Tags:** Vibe tags carry emotional differentiation. A location with only terrain and activities feels mechanical to the vector space.
5. **Copying Location Tags to Users:** Derive user tags purely from stated intent, not by copying tags from locations they liked in the past.

---

## 5. Future Architecture Considerations

Certain binary requirements (e.g., `halal`, `wheelchair accessible`, `pet friendly`, `day trip`) are currently handled via embedding semantics but will eventually be migrated to strict boolean filters within the N4 matching engine for absolute precision.