"""Tests สำหรับโมดูลหาฤกษ์ (Muhurta)"""
import unittest
from datetime import datetime

from thai_astro.kalayok import compute_kalayok, _one_based
from thai_astro.nakshatra import compute_from_moon_position, NAKSHATRA_NAMES, ROEK_GROUPS
from thai_astro.navamsa import compute_navamsa
from thai_astro.muhurta import compute_muhurta, scan_range
from thai_astro.muhurta_criteria import EVENTS, evaluate_special_criteria


class TestKalayok(unittest.TestCase):
    def test_one_based_remainder(self):
        # 7 % 7 = 0 → 7
        self.assertEqual(_one_based(7, 7), 7)
        self.assertEqual(_one_based(8, 7), 1)
        self.assertEqual(_one_based(0, 7), 7)

    def test_thongchai_factor(self):
        k = compute_kalayok(1341)
        # 1341 * 10 + 3 = 13413
        self.assertEqual(k.thongchai.factor, 13413)
        # 13413 % 7 = 1 → อาทิตย์
        self.assertEqual(k.thongchai.wan, 1)
        self.assertEqual(k.thongchai.wan_name, "อาทิตย์")

    def test_athibodi_factor(self):
        k = compute_kalayok(1341)
        # 1341 % 498 = 345
        self.assertEqual(k.athibodi.factor, 345)

    def test_ubat_factor(self):
        k = compute_kalayok(1341)
        # 1341 * 10 + 2 = 13412
        self.assertEqual(k.ubat.factor, 13412)

    def test_lokawinat_factor(self):
        k = compute_kalayok(1341)
        # 1341 + 1120 = 2461
        self.assertEqual(k.lokawinat.factor, 2461)

    def test_all_entries(self):
        k = compute_kalayok(1388)
        d = k.all_entries()
        self.assertEqual(set(d.keys()), {"thongchai", "athibodi", "ubat", "lokawinat"})


class TestNakshatra(unittest.TestCase):
    def test_27_names(self):
        self.assertEqual(len(NAKSHATRA_NAMES), 27)
        self.assertEqual(NAKSHATRA_NAMES[0], "อัศวินี")
        self.assertEqual(NAKSHATRA_NAMES[26], "เรวดี")

    def test_9_roek_groups(self):
        self.assertEqual(len(ROEK_GROUPS), 9)
        # มหัทธโน (index 1) is auspicious
        self.assertTrue(ROEK_GROUPS[1][1])
        # โจโร (index 2) is not
        self.assertFalse(ROEK_GROUPS[2][1])

    def test_first_nakshatra(self):
        # arcmin 0 → อัศวินี ปาทะ 1
        n = compute_from_moon_position(0)
        self.assertEqual(n.number, 1)
        self.assertEqual(n.name, "อัศวินี")
        self.assertEqual(n.pada, 1)
        self.assertEqual(n.roek_name, "ทลิทโทฤกษ์")
        self.assertFalse(n.is_auspicious)

    def test_pada_boundaries(self):
        # 200 arcmin → ปาทะ 2 (เริ่มปาทะ 2)
        n = compute_from_moon_position(200)
        self.assertEqual(n.pada, 2)
        # 799 → ยังอัศวินี ปาทะ 4
        n = compute_from_moon_position(799)
        self.assertEqual(n.number, 1)
        self.assertEqual(n.pada, 4)
        # 800 → ภรณี ปาทะ 1
        n = compute_from_moon_position(800)
        self.assertEqual(n.number, 2)
        self.assertEqual(n.name, "ภรณี")

    def test_wraparound(self):
        # 21600 = full circle → ควรกลับมาที่อัศวินี
        n = compute_from_moon_position(21600)
        self.assertEqual(n.number, 1)


class TestNavamsa(unittest.TestCase):
    def test_movable_sign_starts_self(self):
        # เมษ (rashi=0, movable) navamsa แรกควรเริ่มที่เมษ
        nv = compute_navamsa(0, 0, 0)
        self.assertEqual(nv.nav_rashi, 0)
        self.assertEqual(nv.nav_index, 1)
        self.assertTrue(nv.is_vargottama)

    def test_fixed_sign_offset_8(self):
        # พฤษภ (rashi=1, fixed) navamsa แรก = 1 + 8 = 9 = มกร
        nv = compute_navamsa(1, 0, 0)
        self.assertEqual(nv.nav_rashi, 9)

    def test_dual_sign_offset_4(self):
        # เมถุน (rashi=2, dual) navamsa แรก = 2 + 4 = 6 = ตุล
        nv = compute_navamsa(2, 0, 0)
        self.assertEqual(nv.nav_rashi, 6)

    def test_navamsa_advance(self):
        # เมษ 6° (= 360 arcmin) → navamsa index 2 → ราศีที่ 2 จากเมษ = พฤษภ
        nv = compute_navamsa(0, 6, 40)  # 6°40' = 400 arcmin → idx 2
        self.assertEqual(nv.nav_index, 3)
        self.assertEqual(nv.nav_rashi, 2)  # เมถุน (เมษ+2)

    def test_vargottama_in_middle(self):
        # เมษ 13°20' (800 arcmin = idx 4) → start เมษ → nav_rashi = เมษ+4 = สิงห์
        nv = compute_navamsa(0, 13, 20)
        self.assertEqual(nv.nav_index, 5)
        self.assertEqual(nv.nav_rashi, 4)


class TestMuhurta(unittest.TestCase):
    def test_compute_basic(self):
        mr = compute_muhurta(datetime(2026, 6, 7, 9, 30), "กรุงเทพมหานคร")
        self.assertEqual(mr.wan, 1)  # 2026-06-07 = Sunday
        self.assertEqual(mr.wan_planet, "อาทิตย์")
        self.assertIsNotNone(mr.nakshatra.name)
        self.assertIn(mr.verdict, ("ดีเยี่ยม", "ดี", "กลาง", "ระวัง", "ไม่เหมาะ"))

    def test_kalayok_in_result(self):
        mr = compute_muhurta(datetime(2026, 6, 7, 9, 30))
        self.assertGreater(mr.kalayok.cs_year, 1000)
        # match_wan keys = entry names
        self.assertEqual(
            set(mr.kalayok_matches["wan"].keys()),
            {"thongchai", "athibodi", "ubat", "lokawinat"},
        )

    def test_with_event(self):
        mr = compute_muhurta(datetime(2026, 6, 7, 9, 30), event_key="wedding")
        self.assertEqual(mr.event_key, "wedding")
        self.assertIn("score", mr.event_score)

    def test_invalid_event_ignored(self):
        # invalid event_key ใน compute_muhurta จะถูก event_score handle เป็น 0
        mr = compute_muhurta(datetime(2026, 6, 7, 9, 30), event_key="nope")
        self.assertEqual(mr.event_score["score"], 0)


class TestScan(unittest.TestCase):
    def test_scan_short_range(self):
        # 1 day, every 6 hours
        start = datetime(2026, 6, 7, 0, 0)
        end = datetime(2026, 6, 7, 23, 59)
        hits = scan_range(start, end, step_minutes=360, top_n=5, min_score=-99)
        self.assertGreater(len(hits), 0)
        # sorted desc by score
        scores = [h.score for h in hits]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_scan_over_max_days_raises(self):
        # default max_days=90, ใส่ช่วง 120 วัน → raise
        with self.assertRaises(ValueError):
            scan_range(
                datetime(2026, 1, 1), datetime(2026, 5, 1),
                step_minutes=180,
            )

    def test_scan_explicit_max_days(self):
        # custom max_days=30, ใส่ 45 วัน → raise
        with self.assertRaises(ValueError):
            scan_range(
                datetime(2026, 1, 1), datetime(2026, 2, 15),
                step_minutes=60, max_days=30,
            )


class TestEvents(unittest.TestCase):
    def test_events_present(self):
        # ขยายเป็น 20+ events หลายหมวด
        self.assertGreaterEqual(len(EVENTS), 20)
        for key in ("wedding", "housewarming", "ordination",
                    "foundation_stone", "office_opening", "name_change"):
            self.assertIn(key, EVENTS)

    def test_event_fields(self):
        ev = EVENTS["wedding"]
        self.assertEqual(ev.icon, "💍")
        self.assertTrue(ev.favored_planets)
        self.assertTrue(ev.favored_bhavas)


class TestSpecialCriteria(unittest.TestCase):
    def test_three_criteria(self):
        from thai_astro.chart import Chart
        chart = Chart.calculate(2026, 6, 7, 9, 30)
        results = evaluate_special_criteria(chart)
        self.assertEqual(len(results), 3)
        names = {r.name for r in results}
        self.assertEqual(names, {"กนกนารี", "กนกกุญชร", "จักขุมายา"})


if __name__ == "__main__":
    unittest.main()
