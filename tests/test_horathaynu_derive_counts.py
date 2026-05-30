"""tests สำหรับ ping-pong walking ใน derive_counts (ฉบับ อ.กานดา)

3 ตัวอย่างจริงจาก user:
- Wed ยาม 4 (day): counts = [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7]
- Tue night ยาม 6: counts = [2, 6, 3, 3, 6, 2, 5, 1, 4, 7, 3]
- Mon night ยาม 8: counts = [2, 2, 5, 1, 4, 7, 3, 6, 2, 2, 6]
"""

from __future__ import annotations

import unittest

from thai_astro.horathaynu.core.bhava import bhava_name
from thai_astro.horathaynu.core.caster import cast_chain
from thai_astro.horathaynu.data.yam_table import derive_counts


class PingPongWalkTest(unittest.TestCase):
    def test_wed_day_yam_4(self):
        """พุธ ยาม 4 — กลางตาราง เด้ง 1 ฝั่ง (ขวา)"""
        counts = derive_counts(day=3, yam_index=4)
        self.assertEqual(counts, [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7])

    def test_tue_night_yam_6(self):
        """อังคาร คืน ยาม 6 (global=14) — ใกล้ปลายขวา เด้ง 1 ฝั่ง"""
        counts = derive_counts(day=2, yam_index=14)
        self.assertEqual(counts, [2, 6, 3, 3, 6, 2, 5, 1, 4, 7, 3])

    def test_mon_night_yam_8(self):
        """จันทร์ คืน ยาม 8 (global=16) — สุดขวา เด้งทั้ง 2 ฝั่ง"""
        counts = derive_counts(day=1, yam_index=16)
        self.assertEqual(counts, [2, 2, 5, 1, 4, 7, 3, 6, 2, 2, 6])

    def test_with_override(self):
        """override ค่าบางตัว"""
        counts = derive_counts(day=3, yam_index=4, overrides={0: 99})
        self.assertEqual(counts[0], 99)
        # ตัวอื่นยังคำนวณตามปกติ
        self.assertEqual(counts[1:], [3, 1, 6, 4, 4, 6, 1, 3, 5, 7])


RASHI_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]


class ChartFromAutoCountsTest(unittest.TestCase):
    """verify ผังคำนวณอัตโนมัติตรงกับ user-confirmed positions"""

    def test_tue_night_yam_6_lagna_at_aries(self):
        """ลัคนาต้องอยู่ราศีเมษ (ตามที่ user ยืนยัน)"""
        chart = cast_chain(day=2, yam_index=14)
        self.assertEqual(chart.placements["lagna"].sign, 0)  # เมษ

    def test_tue_night_yam_6_full_positions(self):
        """ตำแหน่งดาวทั้งหมดต้องตรง user-confirmed"""
        chart = cast_chain(day=2, yam_index=14)
        expected = {
            "jupiter": 4,   # ดาว 5 = สิงห์
            "venus":   5,   # ดาว 6 = กันย์
            "saturn":  9,   # ดาว 7 = มกร
            "rahu":    9,   # ดาว 8 = มกร
            "lagna":   0,   # ลัคนา = เมษ
            "ketu":    6,   # ดาว 9 = ตุลย์
            "uranus":  8,   # ดาว 0 = ธนู
        }
        for planet, sign in expected.items():
            with self.subTest(planet=planet):
                self.assertEqual(chart.placements[planet].sign, sign,
                                 f"{planet}: expect {RASHI_TH[sign]} "
                                 f"got {RASHI_TH[chart.placements[planet].sign]}")

    def test_wed_yam_4_still_works(self):
        """ตัวอย่าง Wed ยาม 4 (เดิม) ต้องไม่เสีย"""
        chart = cast_chain(day=3, yam_index=4)
        # ลัคนาที่พฤษภ
        self.assertEqual(chart.placements["lagna"].sign, 1)
        # ศุกร์ที่ตุล (ภพ 6 อริ)
        self.assertEqual(chart.placements["venus"].sign, 6)
        self.assertEqual(chart.placements["venus"].house, 6)


if __name__ == "__main__":
    unittest.main()
