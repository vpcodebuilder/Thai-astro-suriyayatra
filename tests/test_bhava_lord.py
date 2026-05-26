"""Test เจ้าเรือนครองภพ (bhava_lord_prophecy)"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from thai_astro.bhava_lord_prophecy import (
    BHAVA_NAMES,
    SPECIAL_BHAVA_PAIRS,
    text_for_pair,
    _classify_pair,
    predict_natal_lords,
    generate_bhava_lord_summary,
)
from thai_astro.chart import Chart


class TestClassification(unittest.TestCase):
    def test_good_to_good(self):
        # ภพ 2 (good) → ภพ 9 (good)
        tone, _ = _classify_pair(2, 9)
        self.assertEqual(tone, "good")

    def test_good_to_dusthana(self):
        # ภพ 2 ตกภพ 8
        tone, _ = _classify_pair(2, 8)
        self.assertEqual(tone, "warning")

    def test_viparita_raja_yoga(self):
        # ภพทุกข์ตกภพทุกข์ = ดี (วิปริต)
        tone, _ = _classify_pair(6, 12)
        self.assertEqual(tone, "good")
        tone, _ = _classify_pair(8, 12)
        self.assertEqual(tone, "good")


class TestTextLookup(unittest.TestCase):
    def test_special_pair_used(self):
        # 2-9 มีใน SPECIAL
        self.assertIn((2, 9), SPECIAL_BHAVA_PAIRS)
        text = text_for_pair(2, 9)
        self.assertIn("บุญ", text)

    def test_generic_fallback(self):
        # คู่ที่ไม่ได้ใส่ใน SPECIAL ก็ยังคืนค่ามาได้
        text = text_for_pair(3, 4)
        self.assertTrue(len(text) > 10)
        self.assertIn("เจ้าเรือน", text)


class TestPredictNatal(unittest.TestCase):
    def test_chart_lakkana_phichik_lords(self):
        # ลัคนาพิจิก: เจ้าเรือนกดุมภะ (ภพ 2) = พฤหัสบดี (เจ้าราศีธนู)
        # ใช้วันที่ใดก็ได้ที่ออกลัคนาพิจิก แต่ที่นี่ทดสอบกับวันใดก็ได้ แล้วเช็คโครงสร้าง
        chart = Chart.calculate(1990, 5, 15, 8, 30, province="กรุงเทพมหานคร")
        preds = predict_natal_lords(chart.ascendant.zodiac.rasi, chart.planets)
        # มี 12 ภพ (อาจน้อยกว่าถ้าดาวบางดวงไม่อยู่ในชาร์ต — แต่ปกติครบ 9 ดาวคลุม 12 ราศี)
        bhavas_covered = {p.lord_bhava for p in preds}
        self.assertEqual(bhavas_covered, set(range(1, 13)))

        # คุณสมบัติทั่วไป
        for p in preds:
            self.assertEqual(p.lord_bhava_name, BHAVA_NAMES[p.lord_bhava - 1])
            self.assertEqual(p.located_bhava_name, BHAVA_NAMES[p.located_bhava - 1])
            self.assertIn(p.tone, {"good", "warning", "neutral"})
            self.assertTrue(p.prediction)
            self.assertEqual(p.source, "natal")

    def test_summary_structure(self):
        chart = Chart.calculate(1990, 5, 15, 8, 30, province="กรุงเทพมหานคร")
        preds = predict_natal_lords(chart.ascendant.zodiac.rasi, chart.planets)
        s = generate_bhava_lord_summary(preds)
        self.assertIn("headline", s)
        self.assertIn("counts", s)
        self.assertEqual(
            s["counts"]["good"] + s["counts"]["warning"] + len([p for p in preds if p.tone == "neutral"]),
            s["counts"]["total"],
        )


if __name__ == "__main__":
    unittest.main()
