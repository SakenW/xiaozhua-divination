#!/usr/bin/env python3
"""Focused unit-style checks for the bundled Bazi calculator."""
from __future__ import annotations

import unittest

from bazi_chart import build_parser, calculate


def args_for(*extra: str):
    return build_parser().parse_args(
        ["--date", "2026-04-06", "--time", "12:00", "--gender", "male", *extra]
    )


class BaziChartSelfCheck(unittest.TestCase):
    def test_valid_lunar_day_is_not_rejected_as_solar_date(self) -> None:
        payload = calculate(
            args_for("--date", "2024-02-30", "--date-type", "lunar")
        )
        self.assertEqual("2024-04-08 12:00:00", payload["normalized"]["solar"])

    def test_sect_day_is_authoritative_in_both_json_views(self) -> None:
        expected = {1: "辛亥", 2: "庚戌"}
        for sect, day_ganzhi in expected.items():
            with self.subTest(sect=sect):
                payload = calculate(
                    args_for("--time", "23:30", "--sect", str(sect))
                )
                self.assertEqual(
                    day_ganzhi, payload["bazi"]["pillars"]["day"]["ganzhi"]
                )
                self.assertEqual(
                    day_ganzhi, payload["normalized"]["ganzhi"]["day"]
                )

    def test_rejects_invalid_coordinate_and_dayun_limits(self) -> None:
        for args in (
            args_for("--longitude", "181"),
            args_for("--standard-longitude", "nan"),
            args_for("--dayun-limit", "0"),
            args_for("--dayun-limit", "11"),
        ):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    calculate(args)

        payload = calculate(args_for("--dayun-limit", "1"))
        self.assertEqual(1, len(payload["luck"]["items"]))
        self.assertTrue(payload["luck"]["items"][0]["ganzhi"])


if __name__ == "__main__":
    unittest.main()
