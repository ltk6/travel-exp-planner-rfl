"""
embed_locations.py
==================
Embeds all locations using N1 (real BGE-M3 if available).

Outputs:
  - locations_with_vectors.json
  
Supports incremental saving. If the script is interrupted, running it again
will resume from where it left off.
"""

from __future__ import annotations
import sys, json, time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Read input locations
INPUT_PATH = PROJECT_ROOT / "backend/n3_database/seeds/locations.json"
OUTPUT_PATH = PROJECT_ROOT / "backend/n3_database/seeds/locations_with_vectors.json"
BATCH_SIZE = 5

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)

from backend.services.n1_embedding import embed_batch

print("[N1] Using REAL BGE-M3 embeddings")

# ─────────────────────────────────────────────────────────────
# WRITE OUTPUTS
# ─────────────────────────────────────────────────────────────

def _write_json(locations: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

def _read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def run() -> list[dict]:
    print("\n" + "="*60)
    print(f"Embedding {len(LOCATIONS)} locations")
    print("Mode: N1 REAL (returns 4-vector dict) INCREMENTAL")
    print("="*60 + "\n")

    # Load existing progress
    existing = _read_json(OUTPUT_PATH)
    existing_map = {loc["location_id"]: loc for loc in existing}
    
    # Identify missing
    missing_locs = []
    for loc in LOCATIONS:
        if loc["location_id"] not in existing_map:
            missing_locs.append(loc)

    print(f"Found {len(existing_map)} already embedded.")
    print(f"Need to embed {len(missing_locs)} new locations.")

    if not missing_locs:
        print("All locations are already embedded. Exiting.")
        return existing

    t0 = time.time()
    
    for i in range(0, len(missing_locs), BATCH_SIZE):
        batch = missing_locs[i:i+BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1}/{(len(missing_locs) + BATCH_SIZE - 1)//BATCH_SIZE} (size: {len(batch)})...")
        
        inputs = []
        for loc in batch:
            meta = loc["metadata"]
            inputs.append({
                "text": meta.get("description", ""),
                "tags": meta.get("tags", []),
            })
            
        results = embed_batch(inputs)
        
        for loc, res in zip(batch, results):
            name = loc["metadata"]["name"]
            vec = res["vectors"]
            print(f" -> {name:<35} dim={len(vec['text'])}")
            
            existing_map[loc["location_id"]] = {
                "location_id": loc["location_id"],
                "vectors": vec,
                "metadata": loc["metadata"],
                "geo": loc.get("geo", {}),
            }
            
        # Re-sort to match original order
        final_list = []
        for loc in LOCATIONS:
            if loc["location_id"] in existing_map:
                final_list.append(existing_map[loc["location_id"]])
                
        _write_json(final_list, OUTPUT_PATH)
        print(f" -> Saved checkpoint to {OUTPUT_PATH.name}")

    ms = (time.time() - t0) * 1000
    print(f"\nCompleted {len(missing_locs)} embeddings in {ms:.0f}ms")
    print("=" * 60 + "\n")

    return list(existing_map.values())


if __name__ == "__main__":
    run()