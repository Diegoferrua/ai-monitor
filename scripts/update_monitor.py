#!/usr/bin/env python3
"""
Ingestion helper script for AI Monitor.
Saves daily monitoring payload to data/{date}.json and updates data/manifest.json.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def update_monitor(date: str, payload: dict, base_dir: Path | None = None) -> Path:
    """
    Save the given payload into data/{date}.json and update manifest.json.

    Args:
        date: The date string in YYYY-MM-DD format.
        payload: Dictionary containing 'date', 'papers', 'launches', 'news'.
        base_dir: Path to the ai-monitor root directory.

    Returns:
        Path to the saved date JSON file.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent

    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Ensure payload has the date attribute matching
    if "date" not in payload:
        payload["date"] = date

    # Ensure papers subcategories exist
    if "papers" not in payload or not isinstance(payload["papers"], dict):
        payload["papers"] = {}
    default_categories = ["LLMs", "Vision/Multimodal", "Agents & Reasoning", "Infrastructure & Optimization"]
    for cat in default_categories:
        if cat not in payload["papers"]:
            payload["papers"][cat] = []

    if "launches" not in payload or not isinstance(payload["launches"], list):
        payload["launches"] = []

    if "news" not in payload or not isinstance(payload["news"], list):
        payload["news"] = []

    # Quality Gate: Deduplication against recent days
    recent_dates = []
    manifest_file = data_dir / "manifest.json"
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                recent_dates = [d for d in manifest_data.get("dates", []) if d != date][:7]
        except Exception:
            recent_dates = []

    existing_titles = set()
    existing_urls = set()
    for past_date in recent_dates:
        past_file = data_dir / f"{past_date}.json"
        if past_file.exists():
            try:
                with open(past_file, "r", encoding="utf-8") as f:
                    past_data = json.load(f)
                    for cat_papers in past_data.get("papers", {}).values():
                        for p in cat_papers:
                            if "title" in p:
                                existing_titles.add(p["title"].strip().lower())
                            for link in p.get("links", []):
                                if "url" in link and "arxiv" in link["url"]:
                                    existing_urls.add(link["url"].strip().lower())
            except Exception:
                pass

    # Filter out duplicates from incoming papers
    filtered_papers = {}
    dedup_count = 0
    for cat, p_list in payload["papers"].items():
        unique_list = []
        for p in p_list:
            t_norm = p.get("title", "").strip().lower()
            u_links = [l.get("url", "").strip().lower() for l in p.get("links", []) if "arxiv" in l.get("url", "")]
            is_dup = (t_norm in existing_titles) or any(u in existing_urls for u in u_links)
            if is_dup:
                dedup_count += 1
                print(f"[Quality Gate] Dropped duplicate paper from {cat}: {p.get('title')}")
            else:
                unique_list.append(p)
                if t_norm:
                    existing_titles.add(t_norm)
        filtered_papers[cat] = unique_list
    payload["papers"] = filtered_papers

    if dedup_count > 0:
        print(f"[Quality Gate] Deduplication complete: {dedup_count} repeated items removed.")
    date_file = data_dir / f"{date}.json"
    with open(date_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Update manifest.json
    manifest_file = data_dir / "manifest.json"
    manifest = {"dates": [], "updated_at": ""}
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {"dates": [], "updated_at": ""}

    dates_list = manifest.get("dates", [])
    if date not in dates_list:
        dates_list.insert(0, date)

    manifest["dates"] = dates_list
    manifest["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully saved {date_file} and updated {manifest_file}")
    return date_file


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest daily AI Monitor payload and update manifest."
    )
    parser.add_argument(
        "--date",
        "-d",
        required=True,
        help="Date string in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Path to JSON file containing the payload",
    )
    parser.add_argument(
        "--json",
        "-j",
        help="Raw JSON payload string",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    payload_data = None
    if args.json:
        payload_data = json.loads(args.json)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            payload_data = json.load(f)
    elif not sys.stdin.isatty():
        raw_input = sys.stdin.read().strip()
        if raw_input:
            payload_data = json.loads(raw_input)

    if payload_data is None:
        print("Error: No payload provided via --json, --file, or stdin.", file=sys.stderr)
        sys.exit(1)

    update_monitor(args.date, payload_data)


if __name__ == "__main__":
    main()
