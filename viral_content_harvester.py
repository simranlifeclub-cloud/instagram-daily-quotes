#!/usr/bin/env python3
"""
Viral Content Harvester & Remastering Engine for @simranlifeclub

Niche Pillars:
1. Life Coaching & Mental Resets
2. Anxiety, Overthinking & Stress Relief
3. Work-Life Balance & Burnout Prevention
4. Relationship Management, Boundaries & Self-Love
5. Quiet Discipline, Focus & Inner Strength

Reverse-engineers proven high-retention viral formats from YouTube Shorts & Instagram Reels,
remasters them with SimranLifeClub's peaceful aesthetic tone, and injects them into quotes_database.json.
"""

import os
import sys
import json
import random
import argparse
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes_database.json")

# Proven Viral Hook & Structural Archetypes (2x–10x Median Engagement Outliers)
VIRAL_ARCHETYPES = {
    "ANXIETY_RELIEF": {
        "pillar": "Anxiety & Overthinking",
        "hook_formats": [
            "If your mind won't shut up tonight,",
            "Read this before you overthink again:",
            "Anxiety tells you everything is urgent.",
            "You are not stressed because you have too much to do.",
        ],
        "psychology": "Pattern-interrupt that validates somatic overwhelm, followed by an immediate permission to drop the weight."
    },
    "WORK_LIFE_BALANCE": {
        "pillar": "Work-Life Balance & Burnout",
        "hook_formats": [
            "Your company will replace you in 5 days.",
            "Rest is not a reward you have to earn.",
            "Never sacrifice your physical health",
            "Stop calling your burnout 'hustle'.",
        ],
        "psychology": "Direct reality-check separating self-worth from corporate productivity."
    },
    "RELATIONSHIPS_BOUNDARIES": {
        "pillar": "Relationship Management & Healthy Boundaries",
        "hook_formats": [
            "Stop explaining yourself to people",
            "Not everyone deserves access to you.",
            "Maturity is learning to walk away quietly",
            "If it costs you your inner peace,",
        ],
        "psychology": "Validates quiet detachment over toxic confrontation; reinforces self-respect."
    },
    "LIFE_COACH_CLARITY": {
        "pillar": "Life Coaching & Mental Clarity",
        "hook_formats": [
            "3 harsh truths that will save you 5 years:",
            "The life you want is hiding behind",
            "Nobody is coming to save you.",
            "The quietest season of your life",
        ],
        "psychology": "Direct coaching advice delivering an instant epiphany or perspective shift."
    },
    "QUIET_DISCIPLINE": {
        "pillar": "Discipline & Inner Resilience",
        "hook_formats": [
            "Motivation is an emotion. Discipline is a standard.",
            "Win the morning in silence.",
            "Consistency in the shadows",
            "You don't need a new plan. You need commitment.",
        ],
        "psychology": "Anti-hype, grounded stoic focus on daily execution."
    }
}


def load_quotes_database() -> List[Dict[str, Any]]:
    if not os.path.exists(QUOTES_FILE):
        return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_quotes_database(quotes: List[Dict[str, Any]]) -> None:
    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)


def get_next_quote_id(quotes: List[Dict[str, Any]]) -> int:
    numeric_ids = [q["id"] for q in quotes if isinstance(q.get("id"), int)]
    return max(numeric_ids, default=0) + 1


def add_remastered_quote(quote_data: Dict[str, Any]) -> int:
    """Validates and appends a remastered quote to the main database."""
    quotes = load_quotes_database()
    new_id = get_next_quote_id(quotes)
    quote_data["id"] = new_id

    # Validate required fields
    required = ["slot", "category", "hero_lines", "subtext", "caption"]
    for field in required:
        if field not in quote_data:
            raise ValueError(f"Missing required quote field: '{field}'")

    if "quote_text" not in quote_data:
        quote_data["quote_text"] = " ".join(quote_data["hero_lines"]) + " " + quote_data["subtext"]

    quotes.append(quote_data)
    save_quotes_database(quotes)
    print(f"✅ [SUCCESS] Injected Quote #{new_id} [{quote_data.get('language', 'en').upper()} - {quote_data['category']}] into database!")
    return new_id


def list_niche_pillars():
    print("\n" + "=" * 65)
    print("🌟 SIMRAN LIFE CLUB — VIRAL PILLARS & HOOK ARCHETYPES")
    print("=" * 65)
    for key, data in VIRAL_ARCHETYPES.items():
        print(f"\n📌 {data['pillar']} [{key}]")
        print(f"   🧠 Psychology: {data['psychology']}")
        print("   🎯 Top Outlier Hooks:")
        for h in data["hook_formats"]:
            print(f"      • \"{h}\"")
    print("\n" + "=" * 65 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Viral Content Harvester & Remastering CLI")
    parser.add_argument("--list-pillars", action="store_true", help="List content pillars and viral hook frameworks")
    args = parser.parse_args()

    if args.list_pillars:
        list_niche_pillars()
    else:
        list_niche_pillars()
        print("Use add_remastered_quote() or run with --list-pillars to inspect frameworks.")
