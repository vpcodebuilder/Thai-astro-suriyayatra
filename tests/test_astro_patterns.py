"""ทดสอบ astro_patterns.py"""
import unittest

from thai_astro.chart import Chart
from thai_astro.dignities import compute_all_dignities
from thai_astro.astro_patterns import (
    detect_astro_patterns,
    _consecutive_rasi_span,
    _arc_span_degrees,
    LAGNA_GROUP,
)


class TestHelpers(unittest.TestCase):
    def test_consecutive_span_basic(self):
        self.assertEqual(_consecutive_rasi_span({0, 1, 2, 3, 4}), 5)
        self.assertEqual(_consecutive_rasi_span({0, 2, 4}), 1)
        self.assertEqual(_consecutive_rasi_span(set()), 0)

    def test_consecutive_span_cyclic(self):
        # 11, 0, 1 ติดกัน (wrap)
        self.assertEqual(_consecutive_rasi_span({11, 0, 1}), 3)

    def test_consecutive_span_full(self):
        self.assertEqual(_consecutive_rasi_span(set(range(12))), 12)

    def test_arc_span_single(self):
        self.assertEqual(_arc_span_degrees([0]), 0)

    def test_arc_span_opposite(self):
        # ราศี 0 (เมษ 15°) กับ ราศี 6 (ตุลย์ 15°) = 180° เป๊ะ
        self.assertEqual(_arc_span_degrees([0, 6]), 180)

    def test_arc_span_cluster(self):
        # ราศี 0,1,2,3 → กิน 90°
        self.assertEqual(_arc_span_degrees([0, 1, 2, 3]), 90)


class TestDetectIntegration(unittest.TestCase):
    """รัน chart จริงเพื่อทดสอบไม่ crash + structure ถูกต้อง"""

    @classmethod
    def setUpClass(cls):
        cls.chart = Chart.calculate(1990, 5, 15, 8, 30)
        cls.dignities = compute_all_dignities(cls.chart.planets)
        cls.report = detect_astro_patterns(cls.chart, cls.dignities)

    def test_report_structure(self):
        self.assertTrue(hasattr(self.report, "matched"))
        self.assertTrue(hasattr(self.report, "near_misses"))
        self.assertIsInstance(self.report.matched, list)
        self.assertIsInstance(self.report.near_misses, list)

    def test_pattern_fields(self):
        for p in self.report.matched + self.report.near_misses:
            self.assertTrue(p.code)
            self.assertTrue(p.name)
            self.assertIn(p.category, {
                "รูปดวงไทย", "กลุ่มลัคนา", "เกณฑ์ลัคนา (ยศ-ทรัพย์)",
                "ปัญจมหาบุรุษ", "โยคสำคัญ", "จันทรโยค", "โยคเสีย",
            })
            self.assertIn(p.tone, {"good", "warning", "neutral"})

    def test_lagna_group_shown_only_when_ong_udom_both_match(self):
        # หมวด 2 (กลุ่มลัคนา) แสดงได้เฉพาะเมื่อเข้าทั้ง องค์เกณฑ์ + อุดมเกณฑ์
        lagna_matches = [
            p for p in self.report.matched
            if p.category == "กลุ่มลัคนา"
        ]
        ong = any(p.code == "TH-105" and p.matched for p in self.report.matched)
        udom = any(p.code == "TH-106" and p.matched for p in self.report.matched)
        expected = 1 if (ong and udom) else 0
        self.assertEqual(len(lagna_matches), expected)

    def test_near_misses_have_advice(self):
        for p in self.report.near_misses:
            self.assertTrue(p.advice, f"{p.code} ควรมี advice")

    def test_lagna_groups_cover_all_12_rasis(self):
        all_rasis = set()
        for s in LAGNA_GROUP.values():
            all_rasis |= s
        self.assertEqual(all_rasis, set(range(12)))


class TestMultipleCharts(unittest.TestCase):
    """ทดสอบ 3 ดวงต่าง ๆ ไม่ crash"""

    def test_charts(self):
        cases = [
            (1979, 9, 2, 14, 18),    # ดวงในตัวอย่าง CLAUDE.md
            (2000, 1, 1, 0, 0),
            (1975, 12, 31, 23, 59),
        ]
        for y, m, d, h, mi in cases:
            chart = Chart.calculate(y, m, d, h, mi)
            dignities = compute_all_dignities(chart.planets)
            report = detect_astro_patterns(chart, dignities)
            # ไม่ crash + report มี structure ปกติ
            self.assertIsNotNone(report.matched)


if __name__ == "__main__":
    unittest.main()
