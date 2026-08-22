#!/usr/bin/env python3
"""
Public APIs Indexer & Normalizer for Antigravity Agent Workstation.
Parses public-apis Markdown database into high-performance structured JSON.
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Any

LINK_RE = re.compile(r'\[(.*?)\]\((.*?)\)')
HEADER_RE = re.compile(r'^###\s+(.+)$')

def normalize_auth(raw_auth: str) -> str:
    cleaned = raw_auth.strip('` ').strip()
    if not cleaned or cleaned.lower() == 'no' or cleaned.lower() == 'none':
        return "No"
    if "oauth" in cleaned.lower():
        return "OAuth"
    if "apikey" in cleaned.lower() or "api key" in cleaned.lower() or "x-mashape-key" in cleaned.lower() or "user-agent" in cleaned.lower():
        return "apiKey"
    return cleaned

def normalize_https(raw_https: str) -> bool:
    cleaned = raw_https.strip().lower()
    return cleaned == 'yes' or cleaned == 'true'

def normalize_cors(raw_cors: str) -> str:
    cleaned = raw_cors.strip().lower()
    if cleaned in ['yes', 'no', 'unknown']:
        return cleaned
    if cleaned == 'true':
        return 'yes'
    if cleaned == 'false':
        return 'no'
    return 'unknown'

def parse_markdown(readme_path: str) -> Dict[str, Any]:
    if not os.path.exists(readme_path):
        raise FileNotFoundError(f"Markdown file not found at {readme_path}")

    with open(readme_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    current_category = None
    apis = []
    category_stats = {}

    for line in lines:
        line_str = line.strip()
        
        # Check for category header (e.g. "### Animals")
        header_match = HEADER_RE.match(line_str)
        if header_match:
            current_category = header_match.group(1).strip()
            continue

        # Skip non-table rows or table headers/dividers
        if not line_str.startswith('|') or line_str.startswith('|---') or line_str.startswith('|:---') or 'API | Description' in line_str:
            continue

        if not current_category:
            continue

        # Split columns
        cols = [c.strip() for c in line_str.split('|')[1:-1]]
        if len(cols) < 5:
            continue

        raw_api, raw_desc, raw_auth, raw_https, raw_cors = cols[0], cols[1], cols[2], cols[3], cols[4]

        # Extract name & URL
        link_match = LINK_RE.search(raw_api)
        if link_match:
            name = link_match.group(1).strip()
            url = link_match.group(2).strip()
        else:
            name = raw_api.strip()
            url = ""

        # Build normalized entry
        api_entry = {
            "name": name,
            "category": current_category,
            "description": raw_desc.strip(),
            "auth": normalize_auth(raw_auth),
            "https": normalize_https(raw_https),
            "cors": normalize_cors(raw_cors),
            "url": url
        }

        apis.append(api_entry)
        category_stats[current_category] = category_stats.get(current_category, 0) + 1

    by_category = {}
    for api in apis:
        cat = api["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(api)

    auth_stats = {}
    cors_stats = {}
    for api in apis:
        auth_stats[api["auth"]] = auth_stats.get(api["auth"], 0) + 1
        cors_stats[api["cors"]] = cors_stats.get(api["cors"], 0) + 1

    return {
        "metadata": {
            "total_apis": len(apis),
            "total_categories": len(category_stats),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source": "public-apis/public-apis"
        },
        "stats": {
            "categories": category_stats,
            "auth_distribution": auth_stats,
            "cors_distribution": cors_stats
        },
        "apis": apis,
        "by_category": by_category
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "README.md"),
        os.path.join(base_dir, "public-apis-master", "README.md"),
        os.path.join("f:\\top repo\\public-apis-master\\public-apis-master\\README.md"),
        os.path.join("f:\\top repo\\public-apis-master\\README.md"),
    ]

    readme_path = None
    for candidate in candidates:
        if os.path.exists(candidate):
            readme_path = candidate
            break

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        readme_path = sys.argv[1]

    if not readme_path:
        print("Error: Could not locate README.md")
        sys.exit(1)

    print(f"[*] Parsing public-apis database from: {readme_path}")
    data = parse_markdown(readme_path)

    # Destination paths
    output_paths = [
        os.path.join(base_dir, ".agent", "brain", "public_apis_index.json"),
        os.path.join("f:\\top repo\\public-apis-master\\.agent\\brain\\public_apis_index.json"),
        os.path.join(os.path.expanduser("~"), ".gemini", "config", "brain", "public_apis_index.json"),
        os.path.join(os.path.expanduser("~"), ".gemini", "antigravity-ide", "brain", "public_apis_index.json"),
    ]

    for out_path in output_paths:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[+] Successfully generated index at: {out_path}")

    print("\n--- Summary Report ---")
    print(f"Total APIs Indexed: {data['metadata']['total_apis']}")
    print(f"Total Categories: {data['metadata']['total_categories']}")
    print("\nTop 10 Categories:")
    sorted_cats = sorted(data['stats']['categories'].items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats[:10]:
        print(f"  - {cat}: {count} APIs")
    
    print("\nAuth Distribution:")
    for auth_type, count in data['stats']['auth_distribution'].items():
        print(f"  - {auth_type}: {count}")

    print("\nCORS Distribution:")
    for cors_type, count in data['stats']['cors_distribution'].items():
        print(f"  - {cors_type}: {count}")

if __name__ == "__main__":
    main()
