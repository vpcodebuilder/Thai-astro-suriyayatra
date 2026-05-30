"""tests สำหรับ horathaynu/core/caster.py (chain walking ฉบับ อ.กานดา)

ตัวอย่างหลัก: วันพุธ ยาม 4 (asked_time 10:32) — ลัคนาตกพฤษภ
counts ทั้ง 11: [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7]
"""

from __future__ import annotations

import unittest

from thai_astro.horathaynu.core.bhava import bhava_name, bhava_of, sign_of_bhava
from thai_astro.horathaynu.core.caster import PLACEMENT_ORDER, cast_chain, walk
from thai_astro.horathaynu.data.yam_table import YAM_TABLE_DAY, derive_counts

# วันพุธ ยาม 4 — ตัวอย่างหลักของอ.กานดา
WED = 3
ASKED_YAM = 4
COUNTS_WED4 = [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7]

# ตำแหน่งคาดหวังจากผังหน้า 8 (verify ด้วยมือ)
# index in PLACEMENT_ORDER → (sign 0-11, bhava 1-12)
EXPECTED = {
    "sun":     (5,  5),   # กันย์ ภพปุตตะ
    "moon":    (7,  7),   # พิจิก ภพปัตนิ
    "mars":    (7,  7),   # พิจิก ภพปัตนิ (กับจันทร์)
    "mercury": (0,  12),  # เมษ ภพวินาศ
    "jupiter": (3,  3),   # กรกฎ ภพสหัชชะ
    "venus":   (6,  6),   # ตุล ภพอริ ← เจ้าเรือนลัคนา ต้องตรงนี้
    "saturn":  (11, 11),  # มีน ภพลาภะ
    "rahu":    (11, 11),  # มีน ภพลาภะ
    "lagna":   (1,  1),   # พฤษภ ภพตนุ
    "ketu":    (5,  5),   # กันย์ ภพปุตตะ
    "uranus":  (11, 11),  # มีน ภพลาภะ
}


class WalkTest(unittest.TestCase):
    def test_walk_count_1_stays(self):
        self.assertEqual(walk(1, 1), 1)

    def test_walk_forward(self):
        # พฤษภ(1) นับ 5 → cell 5 = กันย์(5)
        self.assertEqual(walk(1, 5), 5)

    def test_walk_wraps(self):
        # มีน(11) นับ 3 → cell 3 = พฤษภ(1)
        self.assertEqual(walk(11, 3), 1)

    def test_walk_full_circle(self):
        self.assertEqual(walk(0, 13), 0)


class CastChainTest(unittest.TestCase):
    def test_lagna_at_pheusop(self):
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS_WED4)
        self.assertEqual(chart.placements["lagna"].sign, 1)  # พฤษภ
        self.assertEqual(chart.placements["lagna"].house, 1)  # ภพตนุ
        self.assertEqual(chart.ascendant_sign, 1)

    def test_all_placements_match_kanda_chart(self):
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS_WED4)
        for planet, (expected_sign, expected_bhava) in EXPECTED.items():
            with self.subTest(planet=planet):
                p = chart.placements[placement_key := planet]
                self.assertEqual(p.sign, expected_sign,
                                 f"{planet} sign: expect {expected_sign} got {p.sign}")
                self.assertEqual(p.house, expected_bhava,
                                 f"{planet} bhava: expect {expected_bhava} got {p.house}")

    def test_venus_in_aria_house(self):
        """เจ้าเรือนลัคนา (พฤษภ) = ศุกร์ ต้องอยู่ภพ 6 อริ — ตรงหน้า 8"""
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS_WED4)
        self.assertEqual(chart.placements["venus"].house, 6)
        self.assertEqual(bhava_name(6), "อริ")

    def test_chain_starts_at_taurus(self):
        # ดาว 1 count 5 → walk(1, 5) = กันย์
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS_WED4)
        self.assertEqual(chart.placements["sun"].sign, 5)  # กันย์

    def test_counts_stored_in_chart(self):
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS_WED4)
        self.assertEqual(chart.counts, COUNTS_WED4)

    def test_counts_length_validation(self):
        with self.assertRaises(ValueError):
            cast_chain(WED, ASKED_YAM, counts=[1, 2, 3])  # ผิด length

    def test_invalid_day(self):
        with self.assertRaises(ValueError):
            cast_chain(7, 4, counts=COUNTS_WED4)


class DeriveCountsTest(unittest.TestCase):
    def test_first_5_counts_for_wed_yam_4(self):
        # ดาว 1-5 derive ได้ → counts = yam (4,5,6,7,8) ของวันพุธกลางวัน
        # Wed day seq = (4, 2, 7, 5, 3, 1, 6, 4)
        # yam 4-8 → 5, 3, 1, 6, 4
        overrides = {i: 0 for i in range(5, 11)}  # mock ตัวที่เหลือ
        counts = derive_counts(WED, ASKED_YAM, n_stars=11, overrides=overrides)
        self.assertEqual(counts[:5], [5, 3, 1, 6, 4])

    def test_full_counts_for_wed_yam_4(self):
        # ping-pong walking ตอนนี้ derive ครบทั้ง 11 ตัวแล้ว
        counts = derive_counts(WED, ASKED_YAM, n_stars=11)
        self.assertEqual(counts, [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7])

    def test_wed_day_table_correct(self):
        # Wed (day=3) → (4, 2, 7, 5, 3, 1, 6, 4)
        self.assertEqual(YAM_TABLE_DAY[3], (4, 2, 7, 5, 3, 1, 6, 4))

    def test_sun_day_table_is_heart(self):
        # อาทิตย์ = (1, 6, 4, 2, 7, 5, 3, 1)
        self.assertEqual(YAM_TABLE_DAY[0], (1, 6, 4, 2, 7, 5, 3, 1))


class BhavaTest(unittest.TestCase):
    def test_lagna_at_taurus_bhavas(self):
        # ตัวอย่างที่ user ยืนยัน: พฤษภ → ตนุ, เมถุน → กดุมภะ, ..., เมษ → วินาศ
        self.assertEqual(bhava_of(1, 1), 1)   # พฤษภ = ตนุ
        self.assertEqual(bhava_of(2, 1), 2)   # เมถุน = กดุมภะ
        self.assertEqual(bhava_of(0, 1), 12)  # เมษ = วินาศ
        self.assertEqual(bhava_of(6, 1), 6)   # ตุล = อริ

    def test_sign_of_bhava_inverse(self):
        for asc in range(12):
            for b in range(1, 13):
                sign = sign_of_bhava(b, asc)
                self.assertEqual(bhava_of(sign, asc), b)


if __name__ == "__main__":
    unittest.main()
