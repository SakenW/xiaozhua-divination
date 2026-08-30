#!/usr/bin/env python3
"""Deterministic/local tarot draw helper for XiaoZhua divination."""
from __future__ import annotations

import argparse
import json
import random
import secrets
import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Card:
    name: str
    arcana: str
    suit: str | None = None
    rank: str | None = None


MAJOR_ARCANA = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
]

SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
RANKS = [
    "Ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "Page",
    "Knight",
    "Queen",
    "King",
]

SPREADS = {
    "single": ["Focus"],
    "three": ["Past / background", "Present / core", "Future / advice"],
    "choice": ["Option A", "Option B", "Guidance"],
    "relationship": [
        "Your feelings / perspective",
        "Their observable role / interaction",
        "Foundation / bond",
        "Current challenge / obstacle",
        "Direction to explore",
    ],
    "celtic": [
        "Present situation",
        "Crossing card",
        "Foundation",
        "Recent past",
        "Conscious goal",
        "Near future",
        "Your attitude",
        "External environment",
        "Hopes and fears",
        "Final outcome",
    ],
}


def build_deck() -> list[Card]:
    deck = [Card(name=name, arcana="Major") for name in MAJOR_ARCANA]
    for suit in SUITS:
        for rank in RANKS:
            deck.append(
                Card(name=f"{rank} of {suit}", arcana="Minor", suit=suit, rank=rank)
            )
    return deck


def make_rng(seed: str | None) -> random.Random:
    if seed is None:
        return secrets.SystemRandom()
    return random.Random(seed)


def draw_cards(spread: str, seed: str | None) -> dict[str, Any]:
    positions = SPREADS[spread]
    rng = make_rng(seed)
    deck = build_deck()
    rng.shuffle(deck)

    cards = []
    for index, (position, card) in enumerate(zip(positions, deck), start=1):
        orientation = rng.choice(["upright", "reversed"])
        cards.append(
            {
                "index": index,
                "position": position,
                "card": card.name,
                "arcana": card.arcana,
                "suit": card.suit,
                "rank": card.rank,
                "orientation": orientation,
            }
        )

    return {
        "tool": "run_tarot",
        "schema_version": 1,
        "spread": spread,
        "question": None,
        "seed": seed,
        "cards": cards,
        "notes": [
            "Cards are drawn without replacement from a 78-card Rider-Waite-Smith deck.",
            "Each card orientation is selected independently after shuffling.",
            "Tarot output is symbolic reflection and not professional medical, legal, or financial advice.",
        ],
    }


def render_markdown(reading: dict[str, Any]) -> str:
    title = reading["spread"].replace("_", " ").title()
    lines = [f"# Tarot Draw - {title}", ""]
    if reading.get("question"):
        lines.extend([f"Question: {reading['question']}", ""])
    if reading.get("seed") is not None:
        lines.extend([f"Seed: `{reading['seed']}`", ""])
    lines.extend(
        [
            "| # | Position | Card | Arcana | Suit | Orientation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for card in reading["cards"]:
        suit = card["suit"] or ""
        lines.append(
            f"| {card['index']} | {card['position']} | {card['card']} | "
            f"{card['arcana']} | {suit} | {card['orientation']} |"
        )
    lines.extend(
        ["", "_Symbolic reflection only; final choices remain with the querent._"]
    )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw a local tarot spread as JSON or markdown."
    )
    parser.add_argument(
        "--spread",
        choices=sorted(SPREADS),
        default="three",
        help="spread to draw: single, three, choice, relationship, or celtic",
    )
    parser.add_argument(
        "--question", default=None, help="optional question/theme to echo in output"
    )
    parser.add_argument("--seed", default=None, help="optional seed for reproducible output")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="output format; JSON is the default",
    )
    parser.add_argument(
        "--list-spreads", action="store_true", help="print supported spreads and exit"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.list_spreads:
        print(
            json.dumps(
                {name: positions for name, positions in SPREADS.items()},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    reading = draw_cards(args.spread, args.seed)
    reading["question"] = args.question

    if args.format == "markdown":
        sys.stdout.write(render_markdown(reading))
    else:
        print(json.dumps(reading, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
