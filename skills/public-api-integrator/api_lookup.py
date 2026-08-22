#!/usr/bin/env python3
"""
CLI Query Utility for Public APIs Integrator Skill.
Fast search, filtering, and inspection of 1,695+ public APIs for agentic workflows.
"""

import argparse
import json
import os
import random
import sys
from typing import List, Dict, Any, Optional

def load_index(custom_path: Optional[str] = None) -> Dict[str, Any]:
    candidates = []
    if custom_path:
        candidates.append(custom_path)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.extend([
        os.path.join(script_dir, "public_apis_index.json"),
        os.path.join(script_dir, "..", "..", "brain", "public_apis_index.json"),
        os.path.join(script_dir, "..", "brain", "public_apis_index.json"),
        os.path.join("f:\\top repo\\public-apis-master\\.agent\\brain\\public_apis_index.json"),
        os.path.join(os.path.expanduser("~"), ".gemini", "config", "brain", "public_apis_index.json"),
        os.path.join(os.path.expanduser("~"), ".gemini", "antigravity-ide", "brain", "public_apis_index.json"),
    ])

    for path in candidates:
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                continue

    print(f"Error: Unable to locate public_apis_index.json in any expected path.", file=sys.stderr)
    sys.exit(1)

def filter_apis(
    data: Dict[str, Any],
    query: Optional[str] = None,
    category: Optional[str] = None,
    auth: Optional[str] = None,
    no_auth: bool = False,
    cors: Optional[str] = None,
    https_only: bool = False,
    frontend_ready: bool = False
) -> List[Dict[str, Any]]:
    apis = data.get("apis", [])
    results = []

    q_lower = query.lower() if query else None
    cat_lower = category.lower() if category else None
    cors_lower = cors.lower() if cors else None

    for api in apis:
        # Category filter
        if cat_lower and cat_lower not in api.get("category", "").lower():
            continue

        # Auth filter
        if no_auth and api.get("auth") != "No":
            continue
        elif auth and auth.lower() != api.get("auth", "").lower():
            continue

        # CORS filter
        if cors_lower and api.get("cors", "").lower() != cors_lower:
            continue

        # HTTPS filter
        if https_only and not api.get("https", True):
            continue

        # Frontend ready preset: No Auth + CORS Yes + HTTPS True
        if frontend_ready:
            if api.get("auth") != "No" or api.get("cors") != "yes" or not api.get("https", True):
                continue

        # Free text search query
        if q_lower:
            name = api.get("name", "").lower()
            desc = api.get("description", "").lower()
            cat = api.get("category", "").lower()
            if q_lower not in name and q_lower not in desc and q_lower not in cat:
                continue

        results.append(api)

    return results

def format_table(apis: List[Dict[str, Any]], limit: int = 50) -> str:
    if not apis:
        return "No matching public APIs found."

    lines = []
    lines.append(f"\nFound {len(apis)} API(s) (Showing up to {limit}):\n")
    lines.append(f"{'#':<4} | {'API Name':<28} | {'Category':<18} | {'Auth':<8} | {'HTTPS':<6} | {'CORS':<8} | {'URL / Docs'}")
    lines.append("-" * 115)

    for idx, item in enumerate(apis[:limit], 1):
        name = (item['name'][:26] + '..') if len(item['name']) > 28 else item['name']
        category = (item['category'][:16] + '..') if len(item['category']) > 18 else item['category']
        auth = item['auth']
        https = "Yes" if item['https'] else "No"
        cors = item['cors']
        url = item['url']
        lines.append(f"{idx:<4} | {name:<28} | {category:<18} | {auth:<8} | {https:<6} | {cors:<8} | {url}")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Lookup and discover 1,695+ public APIs from the local indexed registry."
    )
    parser.add_argument("-q", "--query", help="Search keyword across API name, category, and description")
    parser.add_argument("-c", "--category", help="Filter by specific category name (e.g., Anime, Weather, Finance, Tools)")
    parser.add_argument("-a", "--auth", help="Filter by authentication type (No, apiKey, OAuth)")
    parser.add_argument("--no-auth", action="store_true", help="Shortcut for --auth No (free, zero-key endpoints)")
    parser.add_argument("--cors", choices=["yes", "no", "unknown"], help="Filter by CORS support status")
    parser.add_argument("--https", action="store_true", help="Require HTTPS support")
    parser.add_argument("--frontend-ready", action="store_true", help="Vibe-coding preset: Auth:No + CORS:yes + HTTPS:true")
    parser.add_argument("-l", "--limit", type=int, default=30, help="Maximum number of results to display (default: 30)")
    parser.add_argument("-r", "--random", type=int, default=0, help="Pick N random APIs matching the criteria")
    parser.add_argument("--categories", action="store_true", help="List all available categories and counts")
    parser.add_argument("--json", action="store_true", help="Output results in raw JSON format for tool consumption")
    parser.add_argument("--index-path", help="Custom path to public_apis_index.json")

    args = parser.parse_args()
    data = load_index(args.index_path)

    if args.categories:
        stats = data.get("stats", {}).get("categories", {})
        sorted_cats = sorted(stats.items(), key=lambda x: x[0])
        if args.json:
            print(json.dumps(dict(sorted_cats), indent=2))
        else:
            print(f"\nAvailable Categories ({len(sorted_cats)} total):\n")
            for cat, count in sorted_cats:
                print(f"  • {cat:<32} ({count} APIs)")
        return

    results = filter_apis(
        data=data,
        query=args.query,
        category=args.category,
        auth=args.auth,
        no_auth=args.no_auth,
        cors=args.cors,
        https_only=args.https,
        frontend_ready=args.frontend_ready
    )

    if args.random > 0 and results:
        results = random.sample(results, min(args.random, len(results)))

    if args.json:
        output_limit = args.limit if args.limit > 0 else len(results)
        print(json.dumps(results[:output_limit], indent=2, ensure_ascii=False))
    else:
        print(format_table(results, limit=args.limit))

if __name__ == "__main__":
    main()
