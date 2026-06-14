"""ยืนยันตารางตำแหน่งดาวมาตรฐานไทย 10 ตำแหน่ง ตรงตำรา (astropattern.md)

ราศี index:
  0=เมษ 1=พฤษภ 2=เมถุน 3=กรกฎ 4=สิงห์ 5=กันย์
  6=ตุล 7=พิจิก 8=ธนู 9=มกร 10=กุมภ์ 11=มีน
"""
import unittest

from thai_astro.dignities import (
    EXALTATION_RASI, DEBILITATION_RASI, SWAKSHETRA, PRA_RASIS,
    MAHACHAK, JULACHAK, RAJA_YOKE, TEVI_YOKE, UJ_PHIMUKH, UJ_VILAS,
    compute_dignity,
)


class TestExaltation(unittest.TestCase):
    """ตารางตำแหน่งอุจจ์ — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   0,    # เมษ
        "จันทร์":    1,    # พฤษภ
        "อังคาร":   9,    # มกร
        "พุธ":       5,    # กันย์
        "พฤหัสบดี": 3,    # กรกฎ
        "ศุกร์":    11,    # มีน
        "เสาร์":    6,    # ตุล
        "ราหู":     1,    # พฤษภ
        "เกตุ":     7,    # พิจิก
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(EXALTATION_RASI[p], r, f"อุจจ์ {p}")


class TestDebilitation(unittest.TestCase):
    """ตารางตำแหน่งนิจ — astropattern.md (= +6 ราศีจากอุจจ์)"""
    EXPECTED = {
        "อาทิตย์":   6,    # ตุล
        "จันทร์":    7,    # พิจิก
        "อังคาร":   3,    # กรกฎ
        "พุธ":       11,   # มีน
        "พฤหัสบดี": 9,    # มกร
        "ศุกร์":    5,    # กันย์
        "เสาร์":    0,    # เมษ
        "ราหู":     7,    # พิจิก
        "เกตุ":     1,    # พฤษภ
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(DEBILITATION_RASI[p], r, f"นิจ {p}")


class TestSwakshetra(unittest.TestCase):
    """ตารางตำแหน่งเกษตร — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   {4},          # สิงห์
        "จันทร์":    {3},          # กรกฎ
        "อังคาร":   {0, 7},        # เมษ, พิจิก
        "พุธ":       {2, 5},       # เมถุน, กันย์
        "พฤหัสบดี": {8, 11},      # ธนู, มีน
        "ศุกร์":     {1, 6},       # พฤษภ, ตุล
        "เสาร์":    {9, 10},       # มกร, กุมภ์
    }
    def test_all(self):
        for p, rs in self.EXPECTED.items():
            self.assertEqual(SWAKSHETRA[p], rs, f"เกษตร {p}")


class TestPra(unittest.TestCase):
    """ตารางตำแหน่งประ — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   {10},          # กุมภ์
        "จันทร์":    {9},           # มกร
        "อังคาร":   {1, 6},        # พฤษภ, ตุล
        "พุธ":       {8, 11},       # ธนู, มีน
        "พฤหัสบดี": {2, 5},       # เมถุน, กันย์
        "ศุกร์":     {0, 7},       # เมษ, พิจิก
        "เสาร์":    {3, 4},        # กรกฎ, สิงห์
    }
    def test_all(self):
        for p, rs in self.EXPECTED.items():
            self.assertEqual(PRA_RASIS[p], rs, f"ประ {p}")


class TestMahachak(unittest.TestCase):
    """ตารางมหาจักร — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   1,    # พฤษภ
        "จันทร์":    2,    # เมถุน
        "อังคาร":   10,   # กุมภ์
        "พุธ":       6,    # ตุล
        "พฤหัสบดี": 4,    # สิงห์
        "ศุกร์":     0,    # เมษ
        "เสาร์":    7,    # พิจิก
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(MAHACHAK[p], r, f"มหาจักร {p}")


class TestJulachak(unittest.TestCase):
    """ตารางจุลจักร — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   2,    # เมถุน
        "จันทร์":    3,    # กรกฎ
        "อังคาร":   11,   # มีน
        "พุธ":       7,    # พิจิก
        "พฤหัสบดี": 5,    # กันย์
        "ศุกร์":     1,    # พฤษภ
        "เสาร์":    8,    # ธนู
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(JULACHAK[p], r, f"จุลจักร {p}")


class TestRajaYoke(unittest.TestCase):
    """ตารางราชาโชค — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   3,    # กรกฎ
        "จันทร์":    4,    # สิงห์
        "อังคาร":   0,    # เมษ
        "พุธ":       8,    # ธนู
        "พฤหัสบดี": 6,    # ตุล
        "ศุกร์":     2,    # เมถุน
        "เสาร์":    9,    # มกร
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(RAJA_YOKE[p], r, f"ราชาโชค {p}")


class TestTeviYoke(unittest.TestCase):
    """ตารางเทวีโชค — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   4,    # สิงห์
        "จันทร์":    5,    # กันย์
        "อังคาร":   1,    # พฤษภ
        "พุธ":       9,    # มกร
        "พฤหัสบดี": 7,    # พิจิก
        "ศุกร์":     3,    # กรกฎ
        "เสาร์":    10,   # กุมภ์
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(TEVI_YOKE[p], r, f"เทวีโชค {p}")


class TestUjPhimukh(unittest.TestCase):
    """ตารางอุจจาภิมุข — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   5,    # กันย์
        "จันทร์":    6,    # ตุล
        "อังคาร":   2,    # เมถุน
        "พุธ":       10,   # กุมภ์
        "พฤหัสบดี": 8,    # ธนู
        "ศุกร์":     4,    # สิงห์
        "เสาร์":    11,   # มีน
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(UJ_PHIMUKH[p], r, f"อุจจาภิมุข {p}")


class TestUjVilas(unittest.TestCase):
    """ตารางอุจจาวิลาส — astropattern.md"""
    EXPECTED = {
        "อาทิตย์":   6,    # ตุล
        "จันทร์":    7,    # พิจิก
        "อังคาร":   3,    # กรกฎ
        "พุธ":       11,   # มีน
        "พฤหัสบดี": 9,    # มกร
        "ศุกร์":     5,    # กันย์
        "เสาร์":    0,    # เมษ
    }
    def test_all(self):
        for p, r in self.EXPECTED.items():
            self.assertEqual(UJ_VILAS[p], r, f"อุจจาวิลาส {p}")


class TestPriorityResolution(unittest.TestCase):
    """ลำดับกำลัง — เมื่อราศีเดียวกันอยู่หลายตาราง เลือก dignity ที่แรงสุด"""

    def test_sun_aries_exalted(self):
        """อาทิตย์ ราศีเมษ = อุจจ์ (highest)"""
        self.assertEqual(compute_dignity("อาทิตย์", 0).dignity, "อุจน์")

    def test_sun_leo_devi_over_kshetra(self):
        """อาทิตย์ สิงห์ = เทวีโชค (priority 5 > เกษตร priority 6)"""
        self.assertEqual(compute_dignity("อาทิตย์", 4).dignity, "เทวีโชค")

    def test_saturn_aquarius_devi_over_kshetra(self):
        """เสาร์ กุมภ์ = เทวีโชค (เพราะอยู่หลายตาราง)"""
        self.assertEqual(compute_dignity("เสาร์", 10).dignity, "เทวีโชค")

    def test_mars_aries_raja(self):
        """อังคาร เมษ = ราชาโชค (priority สูงกว่าเกษตร)"""
        self.assertEqual(compute_dignity("อังคาร", 0).dignity, "ราชาโชค")

    def test_sun_capricorn_satru_not_pra(self):
        """อาทิตย์ มกร — ไม่อยู่ในตารางใด → fallback ศัตรู (ไม่ใช่ ประ!)
        ประ ของอาทิตย์ = กุมภ์ ไม่ใช่ มกร"""
        d = compute_dignity("อาทิตย์", 9)
        self.assertEqual(d.dignity, "ศัตรู")
        self.assertNotEqual(d.dignity, "ประ")
        self.assertNotIn("ประ", d.label)

    def test_jupiter_taurus_satru_not_pra(self):
        """พฤหัสบดี พฤษภ — fallback ศัตรู ไม่ใช่ ประ
        ประ ของพฤหัสบดี = เมถุน/กันย์ ไม่ใช่ พฤษภ"""
        d = compute_dignity("พฤหัสบดี", 1)
        self.assertEqual(d.dignity, "ศัตรู")
        self.assertNotEqual(d.dignity, "ประ")
        self.assertNotIn("ประ", d.label)

    def test_sun_aquarius_pra(self):
        """อาทิตย์ กุมภ์ = ประ จริง ๆ (ตามตาราง)"""
        self.assertEqual(compute_dignity("อาทิตย์", 10).dignity, "ประ")

    def test_jupiter_gemini_pra(self):
        """พฤหัสบดี เมถุน = ประ"""
        self.assertEqual(compute_dignity("พฤหัสบดี", 2).dignity, "ประ")


class TestSatruLabelClean(unittest.TestCase):
    """label ศัตรู ห้ามมีคำว่า 'ประ' (กันสับสน)"""
    def test_all_planets_in_satru_position(self):
        # rasis ที่จะตกศัตรู ของแต่ละดาว
        cases = [
            ("อาทิตย์", 9),    # มกร
            ("พฤหัสบดี", 1),  # พฤษภ
        ]
        for planet, rasi in cases:
            d = compute_dignity(planet, rasi)
            if d.dignity == "ศัตรู":
                self.assertNotIn("ประ", d.label,
                    f"{planet} ราศี {rasi} label='{d.label}' ห้ามมี 'ประ'")


if __name__ == "__main__":
    unittest.main()
