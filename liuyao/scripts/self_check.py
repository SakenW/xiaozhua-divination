#!/usr/bin/env python3
"""Focused unit-style checks for the bundled Liuyao calculator."""
from __future__ import annotations

import unittest

from liuyao_pan import LiuYaoPan, liuyao_pan


class LiuYaoPanSelfCheck(unittest.TestCase):
    def test_lichun_uses_input_hour_and_minute(self) -> None:
        self.assertEqual(
            ("乙", "巳"), LiuYaoPan.get_year_gan_zhi(2026, 2, 4, 4, 1)
        )
        self.assertEqual(
            ("丙", "午"), LiuYaoPan.get_year_gan_zhi(2026, 2, 4, 4, 3)
        )
        self.assertEqual(
            ("己", "丑"), LiuYaoPan.get_month_gan_zhi(2026, 2, 4, 4, 1)
        )
        self.assertEqual(
            ("庚", "寅"), LiuYaoPan.get_month_gan_zhi(2026, 2, 4, 4, 3)
        )

    def test_number_casting_rejects_surplus_values(self) -> None:
        with self.assertRaises(ValueError):
            LiuYaoPan.number_to_gua([1, 2, 3, 4])

    def test_documented_time_casting_example_is_reproducible(self) -> None:
        payload = liuyao_pan("2026-04-06 10:55", question="事业")
        self.assertEqual("雷泽归妹", payload["本卦"])
        self.assertEqual("地泽临", payload["变卦"])
        self.assertEqual(4, payload["动爻"])
        self.assertEqual("丙午  壬辰  庚戌  辛巳", payload["四柱"])


if __name__ == "__main__":
    unittest.main()
