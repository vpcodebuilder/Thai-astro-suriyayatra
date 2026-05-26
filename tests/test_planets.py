"""ทดสอบ planets.py - สูตรสุริยยาตร์ Devtino"""
import unittest

from thai_astro.boonnak import build_desire
from thai_astro.planets import (
    compute_all, compute_sun, compute_moon, compute_power,
    Putchakoti, compact_angle, ZODIAC_ARCMIN, RASI_ARCMIN,
)


class TestPlanets(unittest.TestCase):
    def test_compact_angle(self):
        self.assertEqual(compact_angle(0), 0)
        self.assertEqual(compact_angle(21600), 0)
        self.assertEqual(compact_angle(21601), 1)
        self.assertEqual(compact_angle(-100), 21500)

    def test_putchakoti_quadrants(self):
        # Q1: 0..5399
        p = Putchakoti.find_quadrant(1000)
        self.assertEqual(p.p_sign, -1)
        # Q2: 5400..10799
        p = Putchakoti.find_quadrant(7000)
        self.assertEqual(p.p_sign, -1)
        # Q3: 10800..16199
        p = Putchakoti.find_quadrant(13000)
        self.assertEqual(p.p_sign, 1)
        # Q4: 16200..21599
        p = Putchakoti.find_quadrant(20000)
        self.assertEqual(p.p_sign, 1)

    def test_sun_in_valid_range(self):
        # อาทิตย์ต้องอยู่ในช่วง 0..21600 arcmin
        d = build_desire(2533, 5, 15, 8, 30)
        sun = compute_sun(d)
        self.assertTrue(0 <= sun.somput < ZODIAC_ARCMIN)
        # 15 พ.ค. อาทิตย์ควรอยู่ในราศีพฤษภ (rasi=1) หรือเมษ (rasi=0)
        self.assertIn(sun.zodiac.rasi, [0, 1, 2])

    def test_all_planets_computed(self):
        d = build_desire(2543, 1, 1, 12, 0)  # 1 ม.ค. 2000
        planets = compute_all(d)
        expected = {"อาทิตย์", "จันทร์", "อังคาร", "พุธ",
                    "พฤหัสบดี", "ศุกร์", "เสาร์", "ราหู", "เกตุ"}
        self.assertEqual(set(planets.keys()), expected)
        for p in planets.values():
            self.assertTrue(0 <= p.somput < ZODIAC_ARCMIN)
            self.assertTrue(0 <= p.zodiac.rasi <= 11)

    def test_rahu_ketu_independently_computed(self):
        # หมายเหตุ: ใน Devtino สุริยยาตร์ ราหู-เกตุ คำนวณจากสูตรต่างกัน
        # (ราหูจาก PowerPlanet, เกตุจาก HorakhunAtMidnight) จึงไม่ใช่
        # ตรงข้ามกันเป๊ะ 180° แค่ทั้งคู่ต้องเป็นค่าถูกต้อง 0..21600
        d = build_desire(2533, 5, 15, 8, 30)
        planets = compute_all(d)
        self.assertTrue(0 <= planets["ราหู"].somput < ZODIAC_ARCMIN)
        self.assertTrue(0 <= planets["เกตุ"].somput < ZODIAC_ARCMIN)
        # ทั้งคู่ retrograde
        self.assertTrue(planets["ราหู"].retrograde)
        self.assertTrue(planets["เกตุ"].retrograde)

    def test_sun_moves_about_one_degree_per_day(self):
        # อาทิตย์เคลื่อน ~ 60 arcmin/day = 1°/day
        d1 = build_desire(2533, 5, 15, 12, 0)
        d2 = build_desire(2533, 5, 16, 12, 0)
        sun1 = compute_sun(d1)
        sun2 = compute_sun(d2)
        diff = (sun2.somput - sun1.somput) % ZODIAC_ARCMIN
        self.assertTrue(50 < diff < 70, f"sun daily motion = {diff} arcmin")

    def test_moon_moves_about_13_degrees_per_day(self):
        # จันทร์เคลื่อน ~ 780 arcmin/day = 13°/day
        d1 = build_desire(2533, 5, 15, 12, 0)
        d2 = build_desire(2533, 5, 16, 12, 0)
        moon1 = compute_moon(d1)
        moon2 = compute_moon(d2)
        diff = (moon2.somput - moon1.somput) % ZODIAC_ARCMIN
        self.assertTrue(600 < diff < 900, f"moon daily motion = {diff} arcmin")


if __name__ == "__main__":
    unittest.main()
