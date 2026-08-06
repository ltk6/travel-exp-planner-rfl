import os
import json
import time
import random
import statistics
import urllib.request
import urllib.error
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

num_requests_per_endpoint = 5
concurrency = 1 

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root_dir, '.env')
    
    api_key = ""
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("INTERNAL_API_KEY="):
                    api_key = line.strip().split("=")[1].strip('"\'')
                    break
                    
    if not api_key:
        print("ERROR: INTERNAL_API_KEY not found in .env")
        sys.exit(1)
    
    # Load real locations from seeds to use as test cases
    seed_path = os.path.join(root_dir, 'backend', 'n3_database', 'seeds', 'locations.json')
    locations_pool = []
    if os.path.exists(seed_path):
        with open(seed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            locations_pool = data[:20]  # Take first 20 as sample
    else:
        print(f"ERROR: Could not find {seed_path}")
        sys.exit(1)

    queries = [
        "I want to explore nice cafes and local food.",
        "Looking for adventurous outdoor activities and trekking.",
        "Where can I find historical sites and cultural experiences?",
        "Best spots for photography and scenic views.",
        "Relaxing places for a peaceful weekend trip."
    ]

    feedbacks = [
        "Actually, I prefer indoor activities.",
        "Can we make it more adventurous?",
        "I want something suitable for families.",
        "Make it cheaper.",
        "Focus on local street food."
    ]

    base_url = "http://127.0.0.1:8000"
    headers = {
        "Content-Type": "application/json",
        "X-Internal-Key": api_key
    }

    
    print(f"Starting end-to-end baseline load check against ALL endpoints...")
    print(f"Base URL: {base_url}")
    
    # Define endpoints to test
    endpoints = {
        "health_liveness": {"path": "/health", "method": "GET", "requires_payload": False},
        "health_deep": {"path": "/health/deep", "method": "GET", "requires_payload": False},
        "explore": {"path": "/explore", "method": "POST", "requires_payload": True, "type": "empty"},
        "locations": {"path": "/locations", "method": "POST", "requires_payload": True, "type": "locations"},
        "activities": {"path": "/activities", "method": "POST", "requires_payload": True, "type": "activities"},
        "feedback_locations": {"path": "/feedback/locations", "method": "POST", "requires_payload": True, "type": "feedback_locations"},
        "feedback_activities": {"path": "/feedback/activities", "method": "POST", "requires_payload": True, "type": "feedback_activities"}
    }
    
    results = {}
    
    def percentile(data, percent):
        if not data: return 0
        k = (len(data) - 1) * percent
        f = int(k)
        c = int(k) + 1 if int(k) + 1 < len(data) else f
        return data[f] if f == c else data[f] + (data[c] - data[f]) * (k - f)

    def generate_payload(endpoint_type, req_idx):
        loc = random.choice(locations_pool)
        query = random.choice(queries) + f" (Variant {req_idx})"
        fb = random.choice(feedbacks) + f" (Variant {req_idx})"
        
        if endpoint_type == "empty":
            return {}
        elif endpoint_type == "locations":
            return {"text": query, "top_k_locations": 3}
        elif endpoint_type == "activities":
            return {
                "text": query,
                "location": {
                    "location_id": loc["location_id"],
                    "metadata": loc.get("metadata", {})
                },
                "top_k_activities": 3
            }
        elif endpoint_type == "feedback_locations":
            return {"text": query, "feedback": fb, "top_k_locations": 3}
        elif endpoint_type == "feedback_activities":
            return {
                "text": query,
                "location": {
                    "location_id": loc["location_id"],
                    "metadata": loc.get("metadata", {})
                },
                "feedback": fb,
                "top_k_activities": 3
            }
        return {}

    for ep_name, ep_config in endpoints.items():
        print(f"\n--- Testing Endpoint: {ep_name} ({ep_config['path']}) ---")
        
        test_cases = []
        for i in range(num_requests_per_endpoint):
            pl = generate_payload(ep_config.get("type", "empty"), i) if ep_config["requires_payload"] else None
            test_cases.append((i + 1, pl))
            
        ep_latencies = {
            "client_total": [],
            "N1": [], "N2": [], "N3": [], "N4": [],
            "N5": [], "N6": [], "N17": [],
            "n5_tokens": []
        }
        ep_errors = 0
        ep_logs = []
        
        def make_request(req_num, payload):
            url = base_url + ep_config["path"]
            data_bytes = json.dumps(payload).encode('utf-8') if payload is not None else None
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=ep_config["method"])
            
            start_time = time.time()
            status_code = None
            error_msg = None
            stage_lats = {}
            n5_tok = 0
            
            try:
                with urllib.request.urlopen(req, timeout=45) as response:
                    status_code = response.getcode()
                    
                    # Extract ALL module latencies from the header injected by N18
                    lats_header = response.getheader("X-Stage-Latencies")
                    if lats_header:
                        try:
                            stage_lats = json.loads(lats_header)
                        except: pass
                    
                    resp_body = response.read()
                    try:
                        data = json.loads(resp_body)
                        n5_tok = data.get("meta", {}).get("usage", {}).get("total_tokens", 0)
                    except Exception:
                        pass
            except urllib.error.HTTPError as e:
                status_code = e.code
                error_msg = str(e)
                lats_header = e.getheader("X-Stage-Latencies")
                if lats_header:
                    try:
                        stage_lats = json.loads(lats_header)
                    except: pass
            except Exception as e:
                error_msg = str(e)
                
            client_total_ms = int((time.time() - start_time) * 1000)
            return req_num, status_code, client_total_ms, stage_lats, n5_tok, error_msg

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(make_request, req_num, payload): req_num for req_num, payload in test_cases}
            
            for future in as_completed(futures):
                req_num, status_code, client_ms, stage_lats, n5_tok, error_msg = future.result()
                
                if status_code == 200:
                    ep_latencies["client_total"].append(client_ms)
                    for mod in ["N1", "N2", "N3", "N4", "N5", "N6", "N17"]:
                        if mod in stage_lats and stage_lats[mod] >= 0:
                            ep_latencies[mod].append(stage_lats[mod])
                            
                    if n5_tok > 0: ep_latencies["n5_tokens"].append(n5_tok)
                    
                    stage_str = " | ".join([f"{k}: {v}ms" for k, v in stage_lats.items() if v >= 0])
                    print(f"  Req {req_num:02d} OK | Client: {client_ms}ms" + (f" | {stage_str}" if stage_str else ""))
                else:
                    ep_errors += 1
                    print(f"  Req {req_num:02d} FAILED - {error_msg} | Client: {client_ms}ms")
                    
                ep_logs.append({
                    "request_num": req_num,
                    "status_code": status_code,
                    "error": error_msg,
                    "metrics_ms": {
                        "client_total": client_ms,
                        **stage_lats
                    },
                    "tokens": {
                        "n5_total": n5_tok
                    }
                })
                time.sleep(0.5)
                
        compiled_metrics = {}
        for key, data_list in ep_latencies.items():
            if data_list:
                data_list.sort()
                compiled_metrics[key] = {
                    "p50": round(percentile(data_list, 0.50), 1),
                    "p95": round(percentile(data_list, 0.95), 1),
                    "mean": round(statistics.mean(data_list), 1),
                    "max": max(data_list)
                }
            
        results[ep_name] = {
            "total_requests": num_requests_per_endpoint,
            "successful_requests": len(ep_latencies["client_total"]),
            "errors": ep_errors,
            "metrics": compiled_metrics,
            "raw_logs": sorted(ep_logs, key=lambda x: x["request_num"])
        }

    # Final Export
    stats = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "description": "Comprehensive End-to-End Baseline Load Check (All N18 Endpoints)",
        "config": {
            "num_requests_per_endpoint": num_requests_per_endpoint,
            "concurrency": concurrency
        },
        "endpoints_results": results
    }
     
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    out_file = os.path.join(results_dir, "results.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print(f"\n==========================================")
    print(f" Baseline Results Exported: {out_file}")
    for ep, data in results.items():
        suc = data['successful_requests']
        errs = data['errors']
        p95 = data.get('metrics', {}).get('client_total', {}).get('p95', 0)
        print(f" - {ep}: {suc}/{num_requests_per_endpoint} OK | P95 Latency: {p95}ms")

if __name__ == "__main__":
    main()
