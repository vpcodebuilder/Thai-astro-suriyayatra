"""tests สำหรับ horathaynu/core/relations.py + interpreter.py + api.py
(ใช้ตัวอย่าง อ.กานดา: วันพุธ ยาม 4, counts=[5,3,1,6,4,4,6,1,3,5,7])
"""

from __future__ import annotations

import unittest

from thai_astro.horathaynu.api import predict
from thai_astro.horathaynu.core.caster import cast_chain
from thai_astro.horathaynu.core.relations import chain_for

WED = 3
ASKED_YAM = 4
COUNTS = [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7]


class RelationsTest(unittest.TestCase):
    def test_chain_focus_lagna(self):
        # ลัคนาที่พฤษภ → เกษตร = ศุกร์ → ศุกร์ที่ตุล (ภพอริ=6)
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS)
        chain = chain_for(chart, "lagna")
        self.assertEqual(chain.focus, "lagna")
        self.assertEqual(chain.focus_sign, 1)   # พฤษภ
        self.assertEqual(chain.focus_house, 1)  # ตนุ
        self.assertEqual(chain.step1.lord, "venus")
        self.assertEqual(chain.step1.lord_house, 6)  # อริ
        # ศุกร์ที่ตุล → เกษตร = ศุกร์ซ้ำ → step2 None
        self.assertIsNone(chain.step2)

    def test_chain_focus_sun_two_step(self):
        # อาทิตย์อยู่กันย์ (ภพ 5 ปุตตะ) → เกษตร = พุธ → พุธอยู่เมษ (ภพ 12)
        # → เกษตรของเมษ = อังคาร → อังคารอยู่พิจิก (ภพ 7)
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS)
        chain = chain_for(chart, "sun")
        self.assertEqual(chain.step1.lord, "mercury")
        self.assertEqual(chain.step1.lord_house, 12)  # วินาศ
        self.assertIsNotNone(chain.step2)
        self.assertEqual(chain.step2.lord, "mars")
        self.assertEqual(chain.step2.lord_house, 7)  # ปัตนิ

    def test_chain_with_loop_returns_no_step2(self):
        # mars อยู่พิจิก → เกษตร = mars เอง → loop → step2 None
        chart = cast_chain(WED, ASKED_YAM, counts=COUNTS)
        chain = chain_for(chart, "mars")
        self.assertEqual(chain.step1.lord, "mars")
        self.assertIsNone(chain.step2)


class PredictTest(unittest.TestCase):
    def test_predict_basic(self):
        result = predict(WED, ASKED_YAM, counts=COUNTS)
        self.assertEqual(result["focus"], "lagna")
        self.assertEqual(result["chart"]["ascendant_sign"], 1)  # พฤษภ
        self.assertIn("opening", result)
        self.assertGreater(len(result["predictions"]), 0)
        # ดาว 6 (ศุกร์) อยู่ ภพ 6 (อริ)
        self.assertEqual(result["chart"]["placements"]["venus"]["house"], 6)

    def test_predict_with_focus_override(self):
        result = predict(WED, ASKED_YAM, counts=COUNTS, focus_override="moon")
        self.assertEqual(result["focus"], "moon")

    def test_predict_with_question_love(self):
        # question='love' → focus_house 7 (ปัตนิ) → จันทร์ + อังคารอยู่ที่นั่น
        result = predict(WED, ASKED_YAM, counts=COUNTS, question="love")
        self.assertIn(result["focus"], ["moon", "mars"])

    def test_predict_opening(self):
        result = predict(WED, ASKED_YAM, counts=COUNTS)
        self.assertIn("พุธ", result["opening"])
        self.assertIn("10:30", result["opening"])

    def test_predict_without_counts_now_works(self):
        # ping-pong walking implement แล้ว → predict ใช้งานได้โดยไม่ต้องส่ง counts
        result = predict(WED, ASKED_YAM)
        self.assertEqual(result["chart"]["ascendant_sign"], 1)  # พฤษภ
        self.assertEqual(result["chart"]["placements"]["venus"]["house"], 6)  # อริ


if __name__ == "__main__":
    unittest.main()
