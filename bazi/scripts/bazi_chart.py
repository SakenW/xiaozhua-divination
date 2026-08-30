#!/usr/bin/env python3
"""Deterministic Bazi chart calculator for XiaoZhua Divination."""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from lunar_python import Lunar, Solar
except ImportError as exc:  # pragma: no cover - exercised by agent runtime
    raise SystemExit(
        "Missing dependency: lunar_python. Install root requirements.txt first."
    ) from exc


GAN_ELEMENT = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

ZHI_ELEMENT = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

PILLAR_LABELS = ("year", "month", "day", "time")
PILLAR_NAMES = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "time": "时柱",
}


@dataclass(frozen=True)
class NormalizedInput:
    original_datetime: str
    effective_dt: datetime
    date_type: str
    is_leap_month: bool
    timezone: str
    gender: str
    sect: int
    true_solar_time: bool
    longitude: float | None
    standard_longitude: float
    longitude_correction_minutes: float
    equation_of_time_minutes: float
    total_correction_minutes: float


def parse_gender(value: str) -> tuple[str, int]:
    normalized = value.strip().lower()
    if normalized in {"male", "m", "man", "男", "乾造"}:
        return "male", 1
    if normalized in {"female", "f", "woman", "女", "坤造"}:
        return "female", 0
    raise ValueError("gender must be male/female or 男/女")


def parse_date_parts(date_text: str) -> tuple[int, int, int]:
    try:
        year, month, day = [int(part) for part in date_text.split("-")]
    except ValueError as exc:
        raise ValueError("date must be YYYY-MM-DD") from exc
    return year, month, day


def parse_time_parts(time_text: str) -> tuple[int, int]:
    try:
        parts = time_text.split(":")
        if len(parts) != 2:
            raise ValueError
        hour, minute = [int(part) for part in parts]
        datetime(2000, 1, 1, hour, minute)
    except ValueError as exc:
        raise ValueError("time must be HH:MM") from exc
    return hour, minute


def parse_solar_datetime(date_text: str, time_text: str) -> datetime:
    year, month, day = parse_date_parts(date_text)
    hour, minute = parse_time_parts(time_text)
    return datetime(year, month, day, hour, minute)


def standard_longitude_for_timezone(tz_name: str, at_dt: datetime) -> float:
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown timezone: {tz_name}") from exc
    aware = at_dt.replace(tzinfo=tz)
    offset = aware.utcoffset()
    if offset is None:
        return 120.0
    longitude = offset.total_seconds() / 3600 * 15
    return ((longitude + 180) % 360) - 180


def validate_longitude(name: str, value: float | None) -> None:
    if value is None:
        return
    if not math.isfinite(value) or not -180 <= value <= 180:
        raise ValueError(f"{name} must be a finite number in [-180, 180]")


def solar_to_datetime(solar: Any) -> datetime:
    return datetime(
        solar.getYear(),
        solar.getMonth(),
        solar.getDay(),
        solar.getHour(),
        solar.getMinute(),
        solar.getSecond(),
    )


def datetime_to_solar(dt: datetime) -> Solar:
    return Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def equation_of_time_minutes(dt: datetime) -> float:
    """Approximate apparent-solar correction in minutes.

    NOAA-style compact formula, accurate enough for minute-level Bazi time
    correction without adding an astronomy dependency.
    """
    day_of_year = dt.timetuple().tm_yday
    angle = 2 * 3.141592653589793 * (day_of_year - 81) / 364
    return (
        9.87 * math.sin(2 * angle)
        - 7.53 * math.cos(angle)
        - 1.5 * math.sin(angle)
    )


def build_solar_from_input(args: argparse.Namespace) -> tuple[str, Solar]:
    hour, minute = parse_time_parts(args.time)
    if args.date_type == "lunar":
        year, month, day = parse_date_parts(args.date)
        lunar_month = -month if args.leap_month else month
        lunar = Lunar.fromYmdHms(
            year,
            lunar_month,
            day,
            hour,
            minute,
            0,
        )
        return f"{args.date} {args.time}:00", lunar.getSolar()
    raw_dt = parse_solar_datetime(args.date, args.time)
    return raw_dt.strftime("%Y-%m-%d %H:%M:%S"), datetime_to_solar(raw_dt)


def normalize_input(args: argparse.Namespace) -> tuple[NormalizedInput, Solar]:
    gender, _ = parse_gender(args.gender)
    validate_longitude("--longitude", args.longitude)
    validate_longitude("--standard-longitude", args.standard_longitude)
    original_datetime, solar = build_solar_from_input(args)
    effective_dt = solar_to_datetime(solar)
    standard_longitude = args.standard_longitude
    if standard_longitude is None:
        standard_longitude = standard_longitude_for_timezone(args.timezone, effective_dt)

    longitude_correction = 0.0
    eot_correction = 0.0
    total_correction = 0.0

    if args.true_solar_time:
        if args.longitude is None:
            raise ValueError("--longitude is required when --true-solar-time is enabled")
        longitude_delta = ((args.longitude - standard_longitude + 180) % 360) - 180
        longitude_correction = longitude_delta * 4
        eot_correction = equation_of_time_minutes(effective_dt)
        total_correction = longitude_correction + eot_correction
        effective_dt = effective_dt + timedelta(minutes=total_correction)
        solar = datetime_to_solar(effective_dt)

    return (
        NormalizedInput(
            original_datetime=original_datetime,
            effective_dt=effective_dt,
            date_type=args.date_type,
            is_leap_month=args.leap_month,
            timezone=args.timezone,
            gender=gender,
            sect=args.sect,
            true_solar_time=args.true_solar_time,
            longitude=args.longitude,
            standard_longitude=standard_longitude,
            longitude_correction_minutes=longitude_correction,
            equation_of_time_minutes=eot_correction,
            total_correction_minutes=total_correction,
        ),
        solar,
    )


def pillar_payload(eight_char: Any, label: str) -> dict[str, Any]:
    title = label.capitalize() if label != "time" else "Time"
    ganzhi = getattr(eight_char, f"get{title}")()
    gan = getattr(eight_char, f"get{title}Gan")()
    zhi = getattr(eight_char, f"get{title}Zhi")()
    return {
        "label": PILLAR_NAMES[label],
        "ganzhi": ganzhi,
        "gan": gan,
        "zhi": zhi,
        "gan_element": GAN_ELEMENT.get(gan),
        "zhi_element": ZHI_ELEMENT.get(zhi),
        "ten_god_gan": getattr(eight_char, f"get{title}ShiShenGan")(),
        "ten_god_hidden": getattr(eight_char, f"get{title}ShiShenZhi")(),
        "hidden_gan": getattr(eight_char, f"get{title}HideGan")(),
        "wuxing": getattr(eight_char, f"get{title}WuXing")(),
        "nayin": getattr(eight_char, f"get{title}NaYin")(),
        "di_shi": getattr(eight_char, f"get{title}DiShi")(),
        "xun": getattr(eight_char, f"get{title}Xun")(),
        "xun_kong": getattr(eight_char, f"get{title}XunKong")(),
    }


def dayun_payload(eight_char: Any, gender_code: int, limit: int) -> dict[str, Any]:
    yun = eight_char.getYun(gender_code)
    items = []
    dayuns = [dayun for dayun in yun.getDaYun() if dayun.getGanZhi()]
    for dayun in dayuns[:limit]:
        items.append(
            {
                "index": dayun.getIndex(),
                "ganzhi": dayun.getGanZhi(),
                "start_year": dayun.getStartYear(),
                "end_year": dayun.getEndYear(),
                "start_age": dayun.getStartAge(),
                "end_age": dayun.getEndAge(),
                "xun": dayun.getXun(),
                "xun_kong": dayun.getXunKong(),
            }
        )
    return {
        "forward": yun.isForward(),
        "start_after": {
            "years": yun.getStartYear(),
            "months": yun.getStartMonth(),
            "days": yun.getStartDay(),
            "hours": yun.getStartHour(),
            "solar_date": yun.getStartSolar().toYmdHms(),
        },
        "items": items,
    }


def calculate(args: argparse.Namespace) -> dict[str, Any]:
    if not 1 <= args.dayun_limit <= 10:
        raise ValueError("--dayun-limit must be in [1, 10]")
    normalized, solar = normalize_input(args)
    _, gender_code = parse_gender(args.gender)
    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()
    eight_char.setSect(args.sect)

    pillars = {label: pillar_payload(eight_char, label) for label in PILLAR_LABELS}
    return {
        "meta": {
            "schema": "xiaozhua.bazi.v1",
            "engine": "lunar_python",
            "sect": args.sect,
            "sect_note": "1 = 晚子时(23:00-23:59)日柱按次日; 2 = 晚子时日柱按当日",
        },
        "input": {
            "date": args.date,
            "time": args.time,
            "date_type": normalized.date_type,
            "is_leap_month": normalized.is_leap_month,
            "gender": normalized.gender,
            "timezone": normalized.timezone,
            "true_solar_time": normalized.true_solar_time,
            "longitude": normalized.longitude,
            "standard_longitude": normalized.standard_longitude,
        },
        "normalized": {
            "original_datetime": normalized.original_datetime,
            "effective_solar_datetime": normalized.effective_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "time_correction": {
                "longitude_minutes": round(normalized.longitude_correction_minutes, 2),
                "equation_of_time_minutes": round(normalized.equation_of_time_minutes, 2),
                "total_minutes": round(normalized.total_correction_minutes, 2),
            },
            "solar": solar.toYmdHms(),
            "lunar": lunar.toString(),
            "ganzhi": {
                "year": pillars["year"]["ganzhi"],
                "month": pillars["month"]["ganzhi"],
                "day": pillars["day"]["ganzhi"],
                "time": pillars["time"]["ganzhi"],
            },
        },
        "bazi": {
            "display": eight_char.toString(),
            "day_master": {
                "gan": pillars["day"]["gan"],
                "element": pillars["day"]["gan_element"],
            },
            "pillars": pillars,
            "ming_gong": eight_char.getMingGong(),
            "ming_gong_nayin": eight_char.getMingGongNaYin(),
            "shen_gong": eight_char.getShenGong(),
            "shen_gong_nayin": eight_char.getShenGongNaYin(),
            "tai_yuan": eight_char.getTaiYuan(),
            "tai_yuan_nayin": eight_char.getTaiYuanNaYin(),
            "tai_xi": eight_char.getTaiXi(),
            "tai_xi_nayin": eight_char.getTaiXiNaYin(),
        },
        "luck": dayun_payload(eight_char, gender_code, args.dayun_limit),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    bazi = payload["bazi"]
    lines = [
        "# 八字排盘",
        "",
        f"- 四柱：{bazi['display']}",
        f"- 日主：{bazi['day_master']['gan']}（{bazi['day_master']['element']}）",
        f"- 公历时间：{payload['normalized']['solar']}",
        f"- 农历：{payload['normalized']['lunar']}",
        f"- 起运：{payload['luck']['start_after']['solar_date']}",
        "",
        "## 四柱明细",
        "",
        "| 柱 | 干支 | 天干十神 | 藏干 | 藏干十神 | 纳音 | 旬空 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label in PILLAR_LABELS:
        item = bazi["pillars"][label]
        lines.append(
            "| {label} | {ganzhi} | {ten_god_gan} | {hidden} | {hidden_gods} | {nayin} | {xun_kong} |".format(
                label=item["label"],
                ganzhi=item["ganzhi"],
                ten_god_gan=item["ten_god_gan"],
                hidden="/".join(item["hidden_gan"]),
                hidden_gods="/".join(item["ten_god_hidden"]),
                nayin=item["nayin"],
                xun_kong=item["xun_kong"],
            )
        )
    lines.extend(["", "## 大运", "", "| 大运 | 年龄 | 年份 | 旬空 |", "| --- | --- | --- | --- |"])
    for item in payload["luck"]["items"]:
        if not item["ganzhi"]:
            continue
        lines.append(
            f"| {item['ganzhi']} | {item['start_age']}-{item['end_age']} | "
            f"{item['start_year']}-{item['end_year']} | {item['xun_kong']} |"
        )
    lines.append("")
    lines.append("> 固定排盘以脚本输出为准；格局、喜忌和事件校验请继续按 bazi/SKILL.md 的解读流程完成。")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="小爪命理屋八字排盘脚本")
    parser.add_argument("--date", required=True, help="出生日期 YYYY-MM-DD")
    parser.add_argument("--time", required=True, help="出生时间 HH:MM")
    parser.add_argument("--gender", required=True, help="male/female 或 男/女")
    parser.add_argument("--date-type", choices=["solar", "lunar"], default="solar")
    parser.add_argument("--leap-month", action="store_true", help="农历闰月输入时启用")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--true-solar-time", action="store_true", help="按经度做真太阳时校正")
    parser.add_argument("--longitude", type=float, help="出生地经度；启用真太阳时必填")
    parser.add_argument("--standard-longitude", type=float, help="标准时区经度；默认由 timezone 推算")
    parser.add_argument("--sect", type=int, choices=[1, 2], default=1)
    parser.add_argument("--dayun-limit", type=int, default=10)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = calculate(args)
    except Exception as exc:
        print(f"bazi_chart.py: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
