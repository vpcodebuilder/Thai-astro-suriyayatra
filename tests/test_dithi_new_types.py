"""Tests สำหรับ dithi ประเภทใหม่ (รอบ Session 2026-06-13):
    - ดิถีทักทิน (ทัคธทิน) — universal_bad, severity 2
    - ดิถียมขันธ์ — universal_bad, severity 3
    - ฤกษ์ปัญจมหาเศรษฐี (เศรษฐี) — มงคลทรัพย์, severity 3, business+ceremony

ตารางอ้างอิงจาก astroneemo.net และ horoscope.trueid.net
"""
import unittest

from thai_astro.dithi_classifier import (
    DITHI_INFO,
    DITHI_THAKTHIN,
    DITHI_YAMKHAN,
    DITHI_PANJA_SETTHI,
    classify_dithi,
    is_relevant_for,
    should_show_for_event,
)


class TestThakthinTable(unittest.TestCase):
    """ตารางดิถีทักทิน (astroneemo.net)"""

    def test_table_values(self):
        # อาทิตย์ 1, จันทร์ 4, อังคาร 6, พุธ 9, พฤหัสบดี 5, ศุกร์ 3, เสาร์ 7
        expected = {1: [1], 2: [4], 3: [6], 4: [9], 5: [5], 6: [3], 7: [7]}
        self.assertEqual(DITHI_THAKTHIN, expected)

    def test_thakthin_classification_field(self):
        dc = DITHI_INFO["ทักทิน"]
        self.assertFalse(dc.is_auspicious)
        self.assertEqual(dc.severity, 2)
        self.assertEqual(dc.relevant_categories, ("universal_bad",))
        self.assertIn("universal_bad", dc.relevant_categories)

    def test_thakthin_hits_sunday_phase_1(self):
        # วันอาทิตย์ (wan=1) ขึ้น 1 ค่ำ → ต้องเจอ "ทักทิน"
        matches = classify_dithi(wan=1, day_in_phase=1, is_waxing=True)
        names = [m.name for m in matches]
        self.assertIn("ดิถีทักทิน", names)

    def test_thakthin_hits_sunday_phase_1_waning(self):
        # ข้างแรมก็ต้องเจอ
        matches = classify_dithi(wan=1, day_in_phase=1, is_waxing=False)
        names = [m.name for m in matches]
        self.assertIn("ดิถีทักทิน", names)

    def test_thakthin_does_not_hit_off_day(self):
        # วันอาทิตย์ ขึ้น 5 ค่ำ → ไม่เจอทักทิน
        matches = classify_dithi(wan=1, day_in_phase=5, is_waxing=True)
        names = [m.name for m in matches]
        self.assertNotIn("ดิถีทักทิน", names)

    def test_thakthin_all_seven_days(self):
        # ทุกวันในสัปดาห์ ตามตาราง
        cases = [(1, 1), (2, 4), (3, 6), (4, 9), (5, 5), (6, 3), (7, 7)]
        for wan, dip in cases:
            with self.subTest(wan=wan, dip=dip):
                matches = classify_dithi(wan=wan, day_in_phase=dip, is_waxing=True)
                names = [m.name for m in matches]
                self.assertIn("ดิถีทักทิน", names)


class TestYamkhanTable(unittest.TestCase):
    """ตารางดิถียมขันธ์ (astroneemo.net)"""

    def test_table_values(self):
        # อา 12, จ 11, อ 7, พุธ 3, พฤ 6, ศ 8, ส 9
        expected = {1: [12], 2: [11], 3: [7], 4: [3], 5: [6], 6: [8], 7: [9]}
        self.assertEqual(DITHI_YAMKHAN, expected)

    def test_yamkhan_classification_field(self):
        dc = DITHI_INFO["ยมขันธ์"]
        self.assertFalse(dc.is_auspicious)
        self.assertEqual(dc.severity, 3)    # ร้ายแรงสุด — ไฟ
        self.assertEqual(dc.relevant_categories, ("universal_bad",))

    def test_yamkhan_hits_sunday_phase_12(self):
        matches = classify_dithi(wan=1, day_in_phase=12, is_waxing=True)
        names = [m.name for m in matches]
        self.assertIn("ดิถียมขันธ์", names)

    def test_yamkhan_hits_wednesday_phase_3(self):
        # พุธ ขึ้น 3 ค่ำ
        matches = classify_dithi(wan=4, day_in_phase=3, is_waxing=True)
        names = [m.name for m in matches]
        self.assertIn("ดิถียมขันธ์", names)

    def test_yamkhan_all_seven_days(self):
        cases = [(1, 12), (2, 11), (3, 7), (4, 3), (5, 6), (6, 8), (7, 9)]
        for wan, dip in cases:
            with self.subTest(wan=wan, dip=dip):
                matches = classify_dithi(wan=wan, day_in_phase=dip, is_waxing=False)
                names = [m.name for m in matches]
                self.assertIn("ดิถียมขันธ์", names)


class TestPanjaSetthiTable(unittest.TestCase):
    """ตารางฤกษ์ปัญจมหาเศรษฐี (trueid.net)"""

    def test_table_values(self):
        # อา/จันทร์: ไม่มี
        # อ 3,8,13 / พุธ 2,7,12 / พฤ 5,10,15 / ศ 1,6,11 / ส 4,9,14
        expected = {
            1: [],
            2: [],
            3: [3, 8, 13],
            4: [2, 7, 12],
            5: [5, 10, 15],
            6: [1, 6, 11],
            7: [4, 9, 14],
        }
        self.assertEqual(DITHI_PANJA_SETTHI, expected)

    def test_setthi_classification_field(self):
        dc = DITHI_INFO["เศรษฐี"]
        self.assertTrue(dc.is_auspicious)
        self.assertEqual(dc.severity, 3)
        self.assertEqual(dc.relevant_categories, ("business", "ceremony"))

    def test_nanda_friday(self):
        # นันทมหาเศรษฐี — ศุกร์ ขึ้น 1, 6, 11 ค่ำ
        for dip in (1, 6, 11):
            with self.subTest(dip=dip):
                matches = classify_dithi(wan=6, day_in_phase=dip, is_waxing=True)
                names = [m.name for m in matches]
                self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_bhadra_wednesday(self):
        # ภัทรมหาเศรษฐี — พุธ ขึ้น 2, 7, 12 ค่ำ
        for dip in (2, 7, 12):
            matches = classify_dithi(wan=4, day_in_phase=dip, is_waxing=True)
            names = [m.name for m in matches]
            self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_chaya_tuesday(self):
        # ชัยมหาเศรษฐี — อังคาร 3, 8, 13
        for dip in (3, 8, 13):
            matches = classify_dithi(wan=3, day_in_phase=dip, is_waxing=False)
            names = [m.name for m in matches]
            self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_mitra_saturday(self):
        # มิตรมหาเศรษฐี — เสาร์ 4, 9, 14
        for dip in (4, 9, 14):
            matches = classify_dithi(wan=7, day_in_phase=dip, is_waxing=True)
            names = [m.name for m in matches]
            self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_purana_thursday(self):
        # ปุรณมหาเศรษฐี — พฤหัสบดี 5, 10, 15
        for dip in (5, 10, 15):
            matches = classify_dithi(wan=5, day_in_phase=dip, is_waxing=False)
            names = [m.name for m in matches]
            self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_no_setthi_on_sunday(self):
        # อาทิตย์ไม่มีฤกษ์เศรษฐีตามตำรา
        for dip in range(1, 16):
            matches = classify_dithi(wan=1, day_in_phase=dip, is_waxing=True)
            names = [m.name for m in matches]
            self.assertNotIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_no_setthi_on_monday(self):
        # จันทร์ไม่มีฤกษ์เศรษฐี
        for dip in range(1, 16):
            matches = classify_dithi(wan=2, day_in_phase=dip, is_waxing=True)
            names = [m.name for m in matches]
            self.assertNotIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_setthi_off_dip_no_hit(self):
        # ศุกร์ ขึ้น 5 ค่ำ → ไม่เจอเศรษฐี (เพราะศุกร์ใช้ 1,6,11)
        matches = classify_dithi(wan=6, day_in_phase=5, is_waxing=True)
        names = [m.name for m in matches]
        self.assertNotIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_setthi_is_relevant_for_business(self):
        dc = DITHI_INFO["เศรษฐี"]
        self.assertTrue(is_relevant_for(dc, "business", event_key="shop_opening"))
        self.assertTrue(is_relevant_for(dc, "ceremony", event_key=None))
        self.assertFalse(is_relevant_for(dc, "religion", event_key="ordination"))


class TestNewTypesIntegration(unittest.TestCase):
    """ทดสอบรวมว่าระบบยังทำงานไม่มี regression"""

    def test_dithi_info_has_new_keys(self):
        for key in ("ทักทิน", "ยมขันธ์", "เศรษฐี"):
            self.assertIn(key, DITHI_INFO, f"missing key: {key}")

    def test_no_overlap_thakthin_yamkhan(self):
        # ทักทินกับยมขันธ์ไม่ควรชนกันในวันเดียวกัน — เช็คทุก wan/dip
        for wan in range(1, 8):
            tk = set(DITHI_THAKTHIN.get(wan, []))
            yk = set(DITHI_YAMKHAN.get(wan, []))
            self.assertEqual(tk & yk, set(),
                             f"wan {wan} has overlap between ทักทิน/ยมขันธ์")

    def test_known_setthi_vs_thakthin_overlap_documented(self):
        # ตำราจริงมีจุดเดียวที่ ฤกษ์เศรษฐี ตรงกับ ทักทิน:
        #   พฤหัสบดี (wan=5) ขึ้น/แรม 5 ค่ำ
        #     - ทักทิน: พฤหัสบดี 5 ค่ำ (astroneemo.net)
        #     - ปุรณมหาเศรษฐี: พฤหัสบดี 5,10,15 ค่ำ (trueid.net)
        # ระบบจัดการได้: classifier จะคืน 2 entries — UI ตัดสินตาม severity
        matches = classify_dithi(wan=5, day_in_phase=5, is_waxing=True)
        names = [m.name for m in matches]
        self.assertIn("ดิถีทักทิน", names)
        self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_known_setthi_vs_yamkhan_overlap_documented(self):
        # ตำราจริงมีจุดที่ ฤกษ์เศรษฐี ตรงกับ ยมขันธ์:
        #   เสาร์ (wan=7) 9 ค่ำ
        #     - ยมขันธ์: เสาร์ 9 ค่ำ (astroneemo.net)
        #     - มิตรมหาเศรษฐี: เสาร์ 4,9,14 ค่ำ (trueid.net)
        # classifier คืนทั้งคู่ — UI ตัดสินตาม severity
        matches = classify_dithi(wan=7, day_in_phase=9, is_waxing=True)
        names = [m.name for m in matches]
        self.assertIn("ดิถียมขันธ์", names)
        self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_classify_friday_phase_1_includes_setthi(self):
        # วันศุกร์ ขึ้น 1 ค่ำ — เป็นฤกษ์เศรษฐี (นันทะ)
        matches = classify_dithi(wan=6, day_in_phase=1, is_waxing=True)
        names = [m.name for m in matches]
        self.assertIn("ฤกษ์ปัญจมหาเศรษฐี", names)

    def test_classify_keeps_existing_dithi_working(self):
        # smoke: existing classifications still work
        matches = classify_dithi(wan=1, day_in_phase=5, is_waxing=True)
        names = [m.name for m in matches]
        # วันอาทิตย์ ขึ้น 5 ค่ำ ในตารางเดิม = อมฤตโชค
        self.assertIn("ดิถีอมฤตโชค", names)


if __name__ == "__main__":
    unittest.main()
