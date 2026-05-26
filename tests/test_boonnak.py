"""ทดสอบ boonnak.py"""
import unittest

from thai_astro.boonnak import (
    thaloengsok, horakhun_thaloengsok, surathin, build_desire,
    be_to_cs, ce_to_be,
)


class TestBoonnak(unittest.TestCase):
    def test_era_conversions(self):
        self.assertEqual(be_to_cs(2533), 1352)   # พ.ศ. 2533 = จ.ศ. 1352
        self.assertEqual(ce_to_be(1990), 2533)
        self.assertEqual(ce_to_be(2000), 2543)

    def test_thaloengsok_modern(self):
        # จ.ศ. 1352 (พ.ศ. 2533, ค.ศ. 1990) เถลิงศกควรอยู่กลางเมษายน
        t = thaloengsok(1352)
        self.assertEqual(t.month, 4)
        self.assertTrue(13 <= t.day <= 17, f"day={t.day}")

    def test_horakhun_increases(self):
        h1 = horakhun_thaloengsok(1352)
        h2 = horakhun_thaloengsok(1353)
        # ปีถัดไป หรคุณต้องมากกว่าประมาณ 365 วัน
        diff = h2 - h1
        self.assertTrue(364 <= diff <= 367, f"diff={diff}")

    def test_surathin_after_thaloengsok(self):
        # 15 พ.ค. 1990 = พ.ศ. 2533 หลังเถลิงศก (ราว 14 เม.ย.)
        sr = surathin(2533, 5, 15)
        # ราว 30 วันหลังเถลิงศก
        self.assertTrue(25 <= sr.total_days <= 35, f"days={sr.total_days}")
        # ใช้ จ.ศ. 1352 (ปีของวันเกิด)
        self.assertEqual(sr.thaloengsok_cs_year, 1352)

    def test_surathin_before_thaloengsok(self):
        # 1 ม.ค. 1990 = พ.ศ. 2533 ก่อนเถลิงศก -> ใช้ จ.ศ. 1351
        sr = surathin(2533, 1, 1)
        self.assertEqual(sr.thaloengsok_cs_year, 1351)
        # อยู่หลังเถลิงศกของ จ.ศ. 1351 (เม.ย. 1989) ราว 8 เดือน = ~260 วัน
        self.assertTrue(240 <= sr.total_days <= 280, f"days={sr.total_days}")

    def test_build_desire_basic(self):
        d = build_desire(2533, 5, 15, 8, 30)
        self.assertEqual(d.be_year, 2533)
        self.assertEqual(d.thai_minor_era, 1352)
        # หรคุณต้องเป็นจำนวนเต็มบวก
        self.assertTrue(d.horakhun > 0)
        # Kammatchaphon < 292207
        self.assertTrue(0 <= d.kammatchaphon < 292207)
        # Ujapon < 3232
        self.assertTrue(0 <= d.ujapon < 3232)


if __name__ == "__main__":
    unittest.main()
