"""ทดสอบ chart.py + display + prediction"""
import unittest

from thai_astro.chart import Chart
from thai_astro.display import render_chart
from thai_astro.prediction import predict
from thai_astro.planets import RASI_LORD


class TestChart(unittest.TestCase):
    def setUp(self):
        # 15 พ.ค. 1990 (พ.ศ. 2533) 08:30 ที่กรุงเทพฯ
        self.chart = Chart.calculate(1990, 5, 15, 8, 30)

    def test_basic_fields(self):
        self.assertEqual(self.chart.ce_year, 1990)
        self.assertEqual(self.chart.be_year, 2533)
        self.assertEqual(len(self.chart.planets), 9)

    def test_ascendant_valid(self):
        asc = self.chart.ascendant
        self.assertTrue(0 <= asc.zodiac.rasi <= 11)
        self.assertTrue(0 <= asc.degree_in_rasi < 30)

    def test_house_1_is_ascendant_rasi(self):
        self.assertEqual(self.chart.house_rasis[0], self.chart.ascendant.zodiac.rasi)

    def test_house_lords(self):
        asc_rasi = self.chart.ascendant.zodiac.rasi
        self.assertEqual(self.chart.house_lords[1], RASI_LORD[asc_rasi])

    def test_chart_lord_eq_house_1_lord(self):
        self.assertEqual(self.chart.chart_lord, self.chart.house_lords[1])

    def test_all_planets_in_houses(self):
        total = sum(len(v) for v in self.chart.house_planets.values())
        self.assertEqual(total, 9)

    def test_render_chart(self):
        text = render_chart(self.chart)
        self.assertIn("ลัคนา", text)
        self.assertIn("เจ้าชะตา", text)
        self.assertIn("หรคุณ", text)

    def test_predict(self):
        text = predict(self.chart)
        self.assertIn("คำพยากรณ์", text)


if __name__ == "__main__":
    unittest.main()
