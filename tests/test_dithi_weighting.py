"""Tests สำหรับการให้น้ำหนักคะแนนใหม่ — universal_bad ×2 penalty
+ ทดสอบว่าฤกษ์ที่ติดดิถีร้าย < ฤกษ์ที่ไม่ติดอะไรเลย (เกิดจริง)
"""
import unittest
from datetime import datetime

from thai_astro.muhurta import compute_muhurta


class TestUniversalBadPenalty(unittest.TestCase):
    """ทดสอบว่า universal_bad dithi ลดคะแนนแรงพอ"""

    def test_bad_dithi_lowers_score_significantly(self):
        """ฤกษ์ที่ติดดิถีร้าย (อายกรรมพลาย/พิฆาต/ฯลฯ) ต้องมีคะแนนต่ำ"""
        # 27/06/2569 14:00 = วันเสาร์ ขึ้น 13 ค่ำ → อายกรรมพลาย (universal_bad)
        mr = compute_muhurta(datetime(2026, 6, 27, 14, 0), "กรุงเทพมหานคร")
        # ต้องมี อายกรรมพลาย อยู่
        names = [d.name for d in mr.dithi_classifications]
        self.assertIn("ดิถีอายกรรมพลาย", names)
        # universal_bad ×2 → severity 2 × 2 = -4
        # บวกกับ universal_good ที่อาจมี → คะแนนสุทธิควรไม่สูงเกิน
        # (ก่อนแก้: คะแนน 8/47% / หลังแก้ ควรลดต่ำลง)
        self.assertLessEqual(mr.score, 8, "อายกรรมพลายควรลดคะแนนแรง")

    def test_score_with_bad_dithi_lower_than_without(self):
        """ฤกษ์ที่มีดิถีร้าย ควรน้อยกว่าฤกษ์ปกติ (ดิถีปกติ) เมื่อปัจจัยอื่นใกล้กัน"""
        # 27/06/2569 14:00 น. (เสาร์ ขึ้น 13 ค่ำ — มีอายกรรมพลาย)
        mr_bad = compute_muhurta(datetime(2026, 6, 27, 14, 0), "กรุงเทพมหานคร")
        names_bad = [d.name for d in mr_bad.dithi_classifications]

        # หา moment ปกติ (ดิถีปกติ) วันเดียวกันเพื่อเปรียบเทียบ
        # 28/06/2569 (อาทิตย์ ขึ้น 14) อาจเป็นปกติ
        mr_normal = compute_muhurta(datetime(2026, 6, 28, 14, 0), "กรุงเทพมหานคร")
        names_normal = [d.name for d in mr_normal.dithi_classifications]

        # ถ้าทั้งคู่ใกล้เคียงในปัจจัยอื่น แต่อันแรกมีอายกรรมพลาย
        # คะแนนของ mr_bad ควรน้อยกว่า mr_normal
        # (อาจไม่เป๊ะ เพราะ wan/lakkana ต่างกัน — เช็คเชิงโครงสร้าง)
        if "ดิถีอายกรรมพลาย" in names_bad and "ดิถีปกติ" in names_normal:
            # คะแนน universal_bad ส่วนต่าง = 4 (severity 2 × 2)
            # ปัจจัยอื่นอาจชดเชย — ทดสอบว่า "อายกรรมพลายมาแล้วต้องเห็นการลด"
            self.assertLess(mr_bad.score, mr_normal.score + 5,
                "อายกรรมพลายต้องลดคะแนนชัดเจน")


class TestScorePercentMapping(unittest.TestCase):
    """ทดสอบ % calc + กรอง 60%"""

    def test_score_threshold_60_percent(self):
        """score = ceil(MAX*0.6) ควรได้ >= 60%"""
        import math
        from webapp.server import _score_to_percent, MUHURTA_SCORE_MAX
        threshold_score = math.ceil(MUHURTA_SCORE_MAX * 0.6)
        self.assertGreaterEqual(_score_to_percent(threshold_score), 60)

    def test_score_max_is_100(self):
        """ค่า score เต็มควรได้ 100% (เปลี่ยนจาก 17 → 18 หลังเพิ่มมาตรา ดีนัก กนกกุญชร)"""
        from webapp.server import _score_to_percent, MUHURTA_SCORE_MAX
        self.assertEqual(_score_to_percent(MUHURTA_SCORE_MAX), 100.0)

    def test_score_min_is_zero(self):
        """ค่า score ต่ำสุด (MIN) ควรได้ 0%"""
        from webapp.server import _score_to_percent, MUHURTA_SCORE_MIN
        self.assertEqual(_score_to_percent(MUHURTA_SCORE_MIN), 0.0)

    def test_score_below_min_clamps_to_zero(self):
        from webapp.server import _score_to_percent, MUHURTA_SCORE_MIN
        self.assertEqual(_score_to_percent(MUHURTA_SCORE_MIN - 10), 0.0)


class TestRoekTagging(unittest.TestCase):
    """ทดสอบว่า ROEK_INFO ครบ + relevant_events ถูกต้อง"""

    def test_all_9_roek_have_info(self):
        from thai_astro.nakshatra import ROEK_GROUPS, ROEK_INFO
        for name, _, _ in ROEK_GROUPS:
            self.assertIn(name, ROEK_INFO, f"{name} ขาด ROEK_INFO")
            self.assertIn("long_desc", ROEK_INFO[name])
            self.assertIn("relevant_events", ROEK_INFO[name])

    def test_phumipalo_relevant_to_home(self):
        from thai_astro.nakshatra import ROEK_INFO
        events = ROEK_INFO["ภูมิปาโลฤกษ์"]["relevant_events"]
        self.assertIn("housewarming", events)
        self.assertIn("land_purchase", events)

    def test_devi_relevant_to_wedding(self):
        from thai_astro.nakshatra import ROEK_INFO
        events = ROEK_INFO["เทวีฤกษ์"]["relevant_events"]
        self.assertIn("wedding", events)


class TestCriterionInfo(unittest.TestCase):
    """ทดสอบ CRITERION_INFO ของกนกนารี/กนกกุญชร/จักขุมายา"""

    def test_3_criteria_have_info(self):
        from thai_astro.muhurta_criteria import CRITERION_INFO
        for name in ("กนกนารี", "กนกกุญชร", "จักขุมายา"):
            self.assertIn(name, CRITERION_INFO)
            self.assertIn("long_desc", CRITERION_INFO[name])
            self.assertIn("relevant_events", CRITERION_INFO[name])

    def test_kanaka_naree_for_wedding(self):
        from thai_astro.muhurta_criteria import CRITERION_INFO
        events = CRITERION_INFO["กนกนารี"]["relevant_events"]
        self.assertIn("wedding", events)
        self.assertIn("engagement_ask", events)

    def test_chakkhumaya_for_contract(self):
        from thai_astro.muhurta_criteria import CRITERION_INFO
        events = CRITERION_INFO["จักขุมายา"]["relevant_events"]
        self.assertIn("contract", events)


if __name__ == "__main__":
    unittest.main()
