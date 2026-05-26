"""ทดสอบ Module 1: calendar"""
import unittest

from thai_astro.calendar import (
    gregorian_to_jdn, jdn_to_gregorian,
    ce_to_buddhist, ce_to_chulasakarat, ce_to_mahasakarat,
    JDN_CS_EPOCH,
)


class TestCalendar(unittest.TestCase):
    def test_jdn_jan_1_2000(self):
        # 1 ม.ค. ค.ศ. 2000 = JDN 2451545
        self.assertEqual(gregorian_to_jdn(2000, 1, 1), 2451545)

    def test_jdn_cs_epoch_constant(self):
        # JDN_CS_EPOCH = 1954167 ตรงกับ 21 มี.ค. ค.ศ. 638 ตามปฏิทินจูเลียน
        # (ในยุคนั้นยังไม่มีปฏิทินเกรกอเรียน) ส่วนใน proleptic Gregorian
        # วันที่นั้นเท่ากับ 24 มี.ค. 638 (ต่างกัน 3 วัน)
        self.assertEqual(JDN_CS_EPOCH, 1954167)
        self.assertEqual(gregorian_to_jdn(638, 3, 24), JDN_CS_EPOCH)

    def test_jdn_roundtrip(self):
        for y, m, d in [(2000, 1, 1), (1990, 5, 15), (1, 1, 1), (2024, 2, 29)]:
            jdn = gregorian_to_jdn(y, m, d)
            self.assertEqual(jdn_to_gregorian(jdn), (y, m, d))

    def test_buddhist_year(self):
        self.assertEqual(ce_to_buddhist(2000), 2543)
        self.assertEqual(ce_to_buddhist(1990), 2533)

    def test_chulasakarat(self):
        self.assertEqual(ce_to_chulasakarat(2000), 1362)

    def test_mahasakarat(self):
        self.assertEqual(ce_to_mahasakarat(2000), 1922)


if __name__ == "__main__":
    unittest.main()
