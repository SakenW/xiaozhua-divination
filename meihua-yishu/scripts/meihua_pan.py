#!/usr/bin/env python3
"""Meihua Yishu casting script for XiaoZhua Divination."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from lunar_python import Solar
except ImportError as exc:  # pragma: no cover - exercised by agent runtime
    raise SystemExit(
        "Missing dependency: lunar_python. Install root requirements.txt first."
    ) from exc


TRIGRAMS = {
    1: {"name": "乾", "symbol": "☰", "element": "金", "image": "天", "lines": [1, 1, 1]},
    2: {"name": "兑", "symbol": "☱", "element": "金", "image": "泽", "lines": [1, 1, 0]},
    3: {"name": "离", "symbol": "☲", "element": "火", "image": "火", "lines": [1, 0, 1]},
    4: {"name": "震", "symbol": "☳", "element": "木", "image": "雷", "lines": [1, 0, 0]},
    5: {"name": "巽", "symbol": "☴", "element": "木", "image": "风", "lines": [0, 1, 1]},
    6: {"name": "坎", "symbol": "☵", "element": "水", "image": "水", "lines": [0, 1, 0]},
    7: {"name": "艮", "symbol": "☶", "element": "土", "image": "山", "lines": [0, 0, 1]},
    8: {"name": "坤", "symbol": "☷", "element": "土", "image": "地", "lines": [0, 0, 0]},
}

HEXAGRAMS = {
    ("乾", "乾"): "乾为天",
    ("坤", "坤"): "坤为地",
    ("坎", "震"): "水雷屯",
    ("艮", "坎"): "山水蒙",
    ("坎", "乾"): "水天需",
    ("乾", "坎"): "天水讼",
    ("坤", "坎"): "地水师",
    ("坎", "坤"): "水地比",
    ("巽", "乾"): "风天小畜",
    ("乾", "兑"): "天泽履",
    ("坤", "乾"): "地天泰",
    ("乾", "坤"): "天地否",
    ("乾", "离"): "天火同人",
    ("离", "乾"): "火天大有",
    ("坤", "艮"): "地山谦",
    ("震", "坤"): "雷地豫",
    ("兑", "震"): "泽雷随",
    ("艮", "巽"): "山风蛊",
    ("坤", "兑"): "地泽临",
    ("巽", "坤"): "风地观",
    ("离", "震"): "火雷噬嗑",
    ("艮", "离"): "山火贲",
    ("艮", "坤"): "山地剥",
    ("坤", "震"): "地雷复",
    ("乾", "震"): "天雷无妄",
    ("艮", "乾"): "山天大畜",
    ("艮", "震"): "山雷颐",
    ("兑", "巽"): "泽风大过",
    ("坎", "坎"): "坎为水",
    ("离", "离"): "离为火",
    ("兑", "艮"): "泽山咸",
    ("震", "巽"): "雷风恒",
    ("乾", "艮"): "天山遯",
    ("震", "乾"): "雷天大壮",
    ("离", "坤"): "火地晋",
    ("坤", "离"): "地火明夷",
    ("巽", "离"): "风火家人",
    ("离", "兑"): "火泽睽",
    ("坎", "艮"): "水山蹇",
    ("震", "坎"): "雷水解",
    ("艮", "兑"): "山泽损",
    ("巽", "震"): "风雷益",
    ("兑", "乾"): "泽天夬",
    ("乾", "巽"): "天风姤",
    ("兑", "坤"): "泽地萃",
    ("坤", "巽"): "地风升",
    ("兑", "坎"): "泽水困",
    ("坎", "巽"): "水风井",
    ("兑", "离"): "泽火革",
    ("离", "巽"): "火风鼎",
    ("震", "震"): "震为雷",
    ("艮", "艮"): "艮为山",
    ("巽", "艮"): "风山渐",
    ("震", "兑"): "雷泽归妹",
    ("震", "离"): "雷火丰",
    ("离", "艮"): "火山旅",
    ("巽", "巽"): "巽为风",
    ("兑", "兑"): "兑为泽",
    ("巽", "坎"): "风水涣",
    ("坎", "兑"): "水泽节",
    ("巽", "兑"): "风泽中孚",
    ("震", "艮"): "雷山小过",
    ("坎", "离"): "水火既济",
    ("离", "坎"): "火水未济",
}

ZHI_NUM = {
    "子": 1,
    "丑": 2,
    "寅": 3,
    "卯": 4,
    "辰": 5,
    "巳": 6,
    "午": 7,
    "未": 8,
    "申": 9,
    "酉": 10,
    "戌": 11,
    "亥": 12,
}

GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def mod_to_trigram(value: int) -> int:
    remainder = value % 8
    return 8 if remainder == 0 else remainder


def mod_to_yao(value: int) -> int:
    remainder = value % 6
    return 6 if remainder == 0 else remainder


def parse_dt(value: str, timezone_name: str) -> datetime:
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown timezone: {timezone_name}") from exc
    if value == "now":
        return datetime.now(timezone).replace(tzinfo=None)
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError("time must be 'now', YYYY-MM-DD HH:MM, or YYYY-MM-DDTHH:MM")


def trigram_by_lines(lines: list[int]) -> dict[str, Any]:
    for idx, trigram in TRIGRAMS.items():
        if trigram["lines"] == lines:
            return {"index": idx, **trigram}
    raise ValueError(f"unknown trigram lines: {lines}")


def hexagram(upper_idx: int, lower_idx: int) -> dict[str, Any]:
    upper = TRIGRAMS[upper_idx]
    lower = TRIGRAMS[lower_idx]
    name = HEXAGRAMS.get((upper["name"], lower["name"]), f"{upper['name']}上{lower['name']}下")
    lines = lower["lines"] + upper["lines"]
    return {
        "name": name,
        "upper": {"index": upper_idx, **upper},
        "lower": {"index": lower_idx, **lower},
        "lines": lines,
    }


def changed_hexagram(base: dict[str, Any], moving_yao: int) -> dict[str, Any]:
    lines = list(base["lines"])
    idx = moving_yao - 1
    lines[idx] = 0 if lines[idx] else 1
    lower = trigram_by_lines(lines[:3])
    upper = trigram_by_lines(lines[3:])
    return hexagram(upper["index"], lower["index"])


def mutual_hexagram(base: dict[str, Any]) -> dict[str, Any]:
    lines = base["lines"]
    lower = trigram_by_lines(lines[1:4])
    upper = trigram_by_lines(lines[2:5])
    return hexagram(upper["index"], lower["index"])


def relation(subject: str, other: str) -> str:
    if subject == other:
        return "同气"
    if GENERATES[subject] == other:
        return "体生用"
    if GENERATES[other] == subject:
        return "用生体"
    if CONTROLS[subject] == other:
        return "体克用"
    if CONTROLS[other] == subject:
        return "用克体"
    return "无明显生克"


def time_cast(dt: datetime, timezone_name: str) -> tuple[int, int, int, dict[str, Any]]:
    lunar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0).getLunar()
    year_zhi = lunar.getYearZhi()
    hour_zhi = lunar.getTimeZhi()
    year_num = ZHI_NUM[year_zhi]
    hour_num = ZHI_NUM[hour_zhi]
    month = abs(lunar.getMonth())
    day = lunar.getDay()
    upper_source = year_num + month + day
    lower_source = upper_source + hour_num
    return (
        mod_to_trigram(upper_source),
        mod_to_trigram(lower_source),
        mod_to_yao(lower_source),
        {
            "solar": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone_name,
            "lunar": lunar.toString(),
            "year_zhi": year_zhi,
            "hour_zhi": hour_zhi,
            "formula": {
                "upper": f"({year_num}+{month}+{day}) mod 8",
                "lower": f"({year_num}+{month}+{day}+{hour_num}) mod 8",
                "moving_yao": f"({year_num}+{month}+{day}+{hour_num}) mod 6",
            },
        },
    )


def number_cast(numbers: list[int]) -> tuple[int, int, int, dict[str, Any]]:
    if len(numbers) == 2:
        upper_source, lower_source = numbers
        moving_source = sum(numbers)
    elif len(numbers) == 3:
        upper_source, lower_source, moving_source = numbers
    else:
        raise ValueError("--numbers expects two or three comma-separated positive integers")
    if any(n <= 0 for n in numbers):
        raise ValueError("--numbers only accepts positive integers")
    return (
        mod_to_trigram(upper_source),
        mod_to_trigram(lower_source),
        mod_to_yao(moving_source),
        {"numbers": numbers, "formula": "upper/lower/moving use mod 8, mod 8, mod 6"},
    )


def seed_cast(seed: str) -> tuple[int, int, int, dict[str, Any]]:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    upper_source = int.from_bytes(digest[:4], "big")
    lower_source = int.from_bytes(digest[4:8], "big")
    moving_source = int.from_bytes(digest[8:12], "big")
    return (
        mod_to_trigram(upper_source),
        mod_to_trigram(lower_source),
        mod_to_yao(moving_source),
        {"seed": seed, "sha256": hashlib.sha256(seed.encode("utf-8")).hexdigest()},
    )


def ti_yong(base: dict[str, Any], moving_yao: int) -> dict[str, Any]:
    moving_part = "lower" if moving_yao <= 3 else "upper"
    ti_part = "upper" if moving_part == "lower" else "lower"
    yong_part = moving_part
    ti = base[ti_part]
    yong = base[yong_part]
    return {
        "moving_part": "下卦" if moving_part == "lower" else "上卦",
        "ti_part": "上卦" if ti_part == "upper" else "下卦",
        "yong_part": "上卦" if yong_part == "upper" else "下卦",
        "ti": ti,
        "yong": yong,
        "relation": relation(ti["element"], yong["element"]),
    }


def cast(args: argparse.Namespace) -> dict[str, Any]:
    if args.method == "time":
        upper_idx, lower_idx, moving_yao, source = time_cast(parse_dt(args.time, args.timezone), args.timezone)
    elif args.method == "number":
        if not args.numbers:
            raise ValueError("--numbers is required for number casting")
        numbers = [int(item.strip()) for item in args.numbers.split(",") if item.strip()]
        upper_idx, lower_idx, moving_yao, source = number_cast(numbers)
    else:
        seed = args.seed or args.question
        if not seed:
            raise ValueError("--seed or --question is required for seed casting")
        upper_idx, lower_idx, moving_yao, source = seed_cast(seed)

    base = hexagram(upper_idx, lower_idx)
    changed = changed_hexagram(base, moving_yao)
    mutual = mutual_hexagram(base)
    return {
        "meta": {"schema": "xiaozhua.meihua.v1"},
        "input": {
            "method": args.method,
            "question": args.question,
            "timezone": args.timezone,
        },
        "source": source,
        "chart": {
            "base": base,
            "changed": changed,
            "mutual": mutual,
            "moving_yao": moving_yao,
            "ti_yong": ti_yong(base, moving_yao),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    chart = payload["chart"]
    ti_yong_data = chart["ti_yong"]
    lines = [
        "# 梅花易数起卦",
        "",
        f"- 本卦：{chart['base']['name']}（上{chart['base']['upper']['name']}下{chart['base']['lower']['name']}）",
        f"- 互卦：{chart['mutual']['name']}",
        f"- 变卦：{chart['changed']['name']}",
        f"- 动爻：第 {chart['moving_yao']} 爻",
        f"- 体用：{ti_yong_data['ti_part']}为体（{ti_yong_data['ti']['name']}，{ti_yong_data['ti']['element']}），"
        f"{ti_yong_data['yong_part']}为用（{ti_yong_data['yong']['name']}，{ti_yong_data['yong']['element']}）",
        f"- 生克：{ti_yong_data['relation']}",
        "",
        "> 起卦结果只提供象数结构；断事需继续结合问题背景、体用旺衰、动变和现实信息。",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="小爪命理屋梅花易数起卦脚本")
    parser.add_argument("--method", choices=["time", "number", "seed"], default="time")
    parser.add_argument("--time", default="now", help="'now', YYYY-MM-DD HH:MM, or YYYY-MM-DDTHH:MM")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="IANA timezone used for --time now and explicit local times")
    parser.add_argument("--numbers", help="数字起卦：两个或三个正整数，如 12,34,56")
    parser.add_argument("--seed", help="seed 起卦：可复现的任意文本")
    parser.add_argument("--question", default="", help="所问之事，用于记录或 seed 起卦")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = cast(args)
    except Exception as exc:
        print(f"meihua_pan.py: {exc}", file=sys.stderr)
        return 2
    if args.format == "markdown":
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
