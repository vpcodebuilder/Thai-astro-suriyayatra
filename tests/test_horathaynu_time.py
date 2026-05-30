"""tests สำหรับ horathaynu/core/time_to_yam.py"""

from __future__ import annotations

import unittest
from datetime import date, datetime, time

from thai_astro.horathaynu.core.time_to_yam import (
    YAM_COUNT,
    date_time_to_day_yam,
    datetime_to_day_yam,
    time_to_yam,
    yam_range,
)


class TimeToYamTest(unittest.TestCase):
    def test_yam_1_at_sunrise(self):
        self.assertEqual(time_to_yam(time(6, 0)), 1)

    def test_yam_1_within_range(self):
        self.assertEqual(time_to_yam(time(7, 29)), 1)

    def test_yam_2_boundary(self):
        self.assertEqual(time_to_yam(time(7, 30)), 2)

    def test_yam_8_last_daytime(self):
        # 16:30-18:00
        self.assertEqual(time_to_yam(time(16, 30)), 8)
        self.assertEqual(time_to_yam(time(17, 59)), 8)

    def test_yam_9_first_nighttime(self):
        self.assertEqual(time_to_yam(time(18, 0)), 9)

    def test_yam_16_pre_dawn(self):
        # 04:30-06:00
        self.assertEqual(time_to_yam(time(4, 30)), 16)
        self.assertEqual(time_to_yam(time(5, 59)), 16)

    def test_yam_13_after_midnight(self):
        # 00:00-01:30
        self.assertEqual(time_to_yam(time(0, 0)), 13)
        self.assertEqual(time_to_yam(time(1, 29)), 13)


class YamRangeTest(unittest.TestCase):
    def test_range_yam_1(self):
        start, end = yam_range(1)
        self.assertEqual(start, time(6, 0))
        self.assertEqual(end, time(7, 30))

    def test_range_yam_16(self):
        start, end = yam_range(16)
        self.assertEqual(start, time(4, 30))
        self.assertEqual(end, time(6, 0))

    def test_invalid_yam(self):
        with self.assertRaises(ValueError):
            yam_range(0)
        with self.assertRaises(ValueError):
            yam_range(17)


class DayYamTest(unittest.TestCase):
    def test_sunday_morning_is_day_0(self):
        # 2026-05-31 = Sunday (Python weekday=6 → Thai day=0)
        d, y = date_time_to_day_yam(date(2026, 5, 31), time(8, 0))
        self.assertEqual(d, 0)
        self.assertEqual(y, 2)

    def test_after_midnight_belongs_to_previous_day(self):
        # 2026-05-31 02:59 (Sun pre-dawn) → ถือเป็นวันเสาร์, ยาม 14 (01:30-03:00)
        d, y = date_time_to_day_yam(date(2026, 5, 31), time(2, 59))
        self.assertEqual(d, 6)  # เสาร์
        self.assertEqual(y, 14)

    def test_just_before_sunrise(self):
        # 2026-05-31 05:59 → ยังเป็นวันเสาร์ ยาม 16
        d, y = date_time_to_day_yam(date(2026, 5, 31), time(5, 59))
        self.assertEqual(d, 6)
        self.assertEqual(y, 16)

    def test_sunrise_belongs_to_today(self):
        # 2026-05-31 06:00 → กลายเป็นวันอาทิตย์ ยาม 1
        d, y = date_time_to_day_yam(date(2026, 5, 31), time(6, 0))
        self.assertEqual(d, 0)
        self.assertEqual(y, 1)

    def test_friday_yam_11(self):
        # 2026-05-29 = Friday, 21:30 → ยาม 11 (21:00-22:30)
        dt = datetime(2026, 5, 29, 21, 30)
        d, y = datetime_to_day_yam(dt)
        self.assertEqual(d, 5)  # ศุกร์
        self.assertEqual(y, 11)


if __name__ == "__main__":
    unittest.main()
