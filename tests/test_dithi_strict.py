"""Tests สำหรับ dithi_classifier — strict_event_only filtering

ตรวจสอบว่าดิถีที่เป็นเฉพาะกิจกรรม (strict_event_only=True) ถูก filter
ออกจากกิจกรรมที่ไม่เกี่ยวข้อง และยังคงแสดงเมื่อกิจกรรมตรง
"""
import unittest

from thai_astro.dithi_classifier import (
    DITHI_INFO, classify_dithi, is_relevant_for, should_show_for_event,
)


class TestStrictEventOnly(unittest.TestCase):
    """ทดสอบ strict_event_only filter"""

    # ===== ดิถีเรียงหมอน (เฉพาะแต่งงาน) =====
    def test_riang_mon_strict_field(self):
        dc = DITHI_INFO["เรียงหมอน"]
        self.assertTrue(dc.strict_event_only)
        self.assertEqual(
            dc.relevant_events,
            ("wedding", "engagement_ask", "wedding_registration"),
        )

    def test_riang_mon_shows_for_wedding(self):
        dc = DITHI_INFO["เรียงหมอน"]
        # แต่งงาน → แสดง
        self.assertTrue(should_show_for_event(dc, "ceremony", "wedding"))
        self.assertTrue(should_show_for_event(dc, "ceremony", "engagement_ask"))
        self.assertTrue(should_show_for_event(dc, "ceremony", "wedding_registration"))

    def test_riang_mon_hidden_for_others(self):
        dc = DITHI_INFO["เรียงหมอน"]
        # ขึ้นบ้าน, ซื้อที่ดิน, เปิดร้าน → ไม่แสดง
        self.assertFalse(should_show_for_event(dc, "home", "housewarming"))
        self.assertFalse(should_show_for_event(dc, "home", "land_purchase"))
        self.assertFalse(should_show_for_event(dc, "business", "shop_opening"))
        self.assertFalse(should_show_for_event(dc, "religion", "ordination"))

    # ===== ห้ามขึ้นบ้านใหม่วันเสาร์ =====
    def test_taboo_saturday_house_strict(self):
        dc = DITHI_INFO["ห้ามวันเสาร์_บ้าน"]
        self.assertTrue(dc.strict_event_only)

    def test_taboo_saturday_house_shows_for_housewarming(self):
        dc = DITHI_INFO["ห้ามวันเสาร์_บ้าน"]
        self.assertTrue(should_show_for_event(dc, "home", "housewarming"))
        self.assertTrue(should_show_for_event(dc, "home", "move_house"))

    def test_taboo_saturday_house_hidden_for_land(self):
        """ซื้อที่ดิน ไม่ใช่ขึ้นบ้านใหม่ → ห้ามวันเสาร์ ไม่ควรแสดง"""
        dc = DITHI_INFO["ห้ามวันเสาร์_บ้าน"]
        self.assertFalse(should_show_for_event(dc, "home", "land_purchase"))
        self.assertFalse(should_show_for_event(dc, "home", "foundation_stone"))
        self.assertFalse(should_show_for_event(dc, "ceremony", "wedding"))

    # ===== ห้ามแต่งงานวันพุธ =====
    def test_taboo_wed_wedding_shows_only_for_wedding(self):
        dc = DITHI_INFO["ห้ามวันพุธ_แต่งงาน"]
        self.assertTrue(should_show_for_event(dc, "ceremony", "wedding"))
        self.assertTrue(should_show_for_event(dc, "ceremony", "engagement_ask"))
        # ตั้งชื่อบุตร (ceremony) ไม่ใช่งานแต่ง → ไม่แสดง
        self.assertFalse(should_show_for_event(dc, "ceremony", "baby_naming"))

    # ===== สงฆ์ 14 =====
    def test_song14_shows_only_for_ordination(self):
        dc = DITHI_INFO["สงฆ์14"]
        self.assertTrue(should_show_for_event(dc, "religion", "ordination"))
        # ทำบุญ ทอดกฐิน — ไม่ใช่บวช → ไม่แสดง
        self.assertFalse(should_show_for_event(dc, "religion", "merit"))
        self.assertFalse(should_show_for_event(dc, "religion", "kathin"))
        self.assertFalse(should_show_for_event(dc, "ceremony", "wedding"))

    # ===== นารี 11 =====
    def test_naree11_shows_for_wedding_only(self):
        dc = DITHI_INFO["นารี11"]
        self.assertTrue(should_show_for_event(dc, "ceremony", "wedding"))
        self.assertTrue(should_show_for_event(dc, "ceremony", "engagement_ask"))
        self.assertTrue(should_show_for_event(dc, "ceremony", "baby_naming"))
        # ขึ้นบ้านใหม่, ออกรถ → ไม่แสดง
        self.assertFalse(should_show_for_event(dc, "home", "housewarming"))
        self.assertFalse(should_show_for_event(dc, "travel", "vehicle"))


class TestUniversalAlwaysShows(unittest.TestCase):
    """ดิถี universal ต้องแสดงเสมอ ไม่ว่ากิจกรรมไหน"""

    def test_amritachok_shows_everywhere(self):
        dc = DITHI_INFO["อมฤตโชค"]
        for ek in ["wedding", "housewarming", "vehicle", "ordination", "investment"]:
            self.assertTrue(should_show_for_event(dc, "", ek),
                f"อมฤตโชค ต้องแสดงสำหรับ {ek}")

    def test_phromprasit_shows_everywhere(self):
        dc = DITHI_INFO["พรหมประสิทธิ์"]
        for ek in ["wedding", "housewarming", "merit", "ordination"]:
            self.assertTrue(should_show_for_event(dc, "", ek))

    def test_universal_bad_always_shows(self):
        for key in ["อัคนิโรธ", "มหาสูญ", "พิฆาต", "ทรธึก",
                    "อายกรรมพลาย", "กทิงวันแท้", "กทิงวันไม่เต็ม"]:
            dc = DITHI_INFO[key]
            for ek in ["wedding", "housewarming", "ordination"]:
                self.assertTrue(should_show_for_event(dc, "", ek),
                    f"{key} ต้องแสดงเสมอ ({ek})")


class TestInformationalDithiAlwaysShows(unittest.TestCase):
    """ดิถีมงคลเฉพาะหมวด (ไม่ strict) เช่น มหาสิทธิโชค ชัยโชค ราชาโชค
    ต้องแสดงเสมอ — ในกิจกรรมที่ตรง = specific_match,
    ในกิจกรรมที่ไม่ตรง = specific_other (informational)
    """

    def test_chai_chok_shows_in_business_and_other(self):
        dc = DITHI_INFO["ชัยโชค"]
        self.assertFalse(dc.strict_event_only)
        self.assertTrue(should_show_for_event(dc, "business", "contract"))
        # ใน wedding ก็ยังแสดง (informational)
        self.assertTrue(should_show_for_event(dc, "ceremony", "wedding"))

    def test_mahasiddhichok_shows_in_home_and_others(self):
        dc = DITHI_INFO["มหาสิทธิโชค"]
        self.assertFalse(dc.strict_event_only)
        self.assertTrue(should_show_for_event(dc, "home", "housewarming"))


class TestNeutralAlwaysShows(unittest.TestCase):
    """ดิถีปกติ (severity=0) ควรแสดงเสมอ"""

    def test_pakti_shows_everywhere(self):
        dc = DITHI_INFO["ปกติ"]
        self.assertEqual(dc.severity, 0)
        for ek in ["wedding", "housewarming", "vehicle"]:
            self.assertTrue(should_show_for_event(dc, "", ek))


class TestEndToEndClassification(unittest.TestCase):
    """ทดสอบทั้ง pipeline: classify_dithi + filter
    จำลองการเรียกจริงจาก server
    """

    @staticmethod
    def _filter(matches, event_cat, event_key):
        return [
            dc for dc in matches
            if should_show_for_event(dc, event_cat, event_key)
        ]

    def test_saturday_land_purchase_no_house_taboo(self):
        """ซื้อที่ดิน วันเสาร์ ขึ้น 4 ค่ำ
        ไม่ควรเห็น 'ห้ามขึ้นบ้านใหม่วันเสาร์'
        แต่ควรเห็น universal_bad (มหาสูญ ฯลฯ) ตามจริง
        """
        matches = classify_dithi(7, 4, True, lunar_month=8)  # เสาร์ ขึ้น 4
        filtered = self._filter(matches, "home", "land_purchase")
        names = [dc.name for dc in filtered]
        self.assertNotIn("ห้ามขึ้นบ้านใหม่วันเสาร์", names,
            "ซื้อที่ดิน ไม่ควรมี ห้ามขึ้นบ้านใหม่")

    def test_saturday_housewarming_has_house_taboo(self):
        """ขึ้นบ้านใหม่ วันเสาร์ → ต้องเห็น ห้ามขึ้นบ้านใหม่วันเสาร์"""
        matches = classify_dithi(7, 4, True, lunar_month=8)
        filtered = self._filter(matches, "home", "housewarming")
        names = [dc.name for dc in filtered]
        self.assertIn("ห้ามขึ้นบ้านใหม่วันเสาร์", names)

    def test_wedding_7th_day_has_riang_mon_and_taboo(self):
        """แต่งงาน ขึ้น 7 ค่ำ
        ควรเห็น: เรียงหมอน (✓ มงคล) + แต่งงาน7 (✗ ห้าม)
        """
        matches = classify_dithi(2, 7, True, lunar_month=8)  # จันทร์ ขึ้น 7
        filtered = self._filter(matches, "ceremony", "wedding")
        names = [dc.name for dc in filtered]
        self.assertIn("ดิถีเรียงหมอน", names)
        self.assertIn("ห้ามแต่งงาน (7 ค่ำ)", names)

    def test_housewarming_7th_day_no_riang_mon_no_taboo(self):
        """ขึ้นบ้าน ขึ้น 7 ค่ำ
        ไม่ควรเห็น เรียงหมอน หรือ ห้ามแต่งงาน 7
        """
        matches = classify_dithi(2, 7, True, lunar_month=8)
        filtered = self._filter(matches, "home", "housewarming")
        names = [dc.name for dc in filtered]
        self.assertNotIn("ดิถีเรียงหมอน", names)
        self.assertNotIn("ห้ามแต่งงาน (7 ค่ำ)", names)

    def test_ordination_14th_has_song(self):
        """บวช ขึ้น 14 ค่ำ → ต้องเห็น สงฆ์ 14"""
        matches = classify_dithi(3, 14, True, lunar_month=8)
        filtered = self._filter(matches, "religion", "ordination")
        names = [dc.name for dc in filtered]
        self.assertIn("ห้ามบวช (สงฆ์ 14)", names)

    def test_merit_14th_no_song(self):
        """ทำบุญ ขึ้น 14 ค่ำ → ไม่ควรเห็น สงฆ์ 14 (เพราะไม่ใช่บวช)"""
        matches = classify_dithi(3, 14, True, lunar_month=8)
        filtered = self._filter(matches, "religion", "merit")
        names = [dc.name for dc in filtered]
        self.assertNotIn("ห้ามบวช (สงฆ์ 14)", names)


if __name__ == "__main__":
    unittest.main()
