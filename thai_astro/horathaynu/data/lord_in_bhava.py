"""ภพผสมภพ (Lord-in-Bhava) — ชั้นที่ 2 ของการพยากรณ์โหรทายหนู

หลักการ: เจ้าเรือนของ "ภพหลักของคำถาม" ไปสถิตในภพไหน
    → ภพ X (เรื่องที่ถาม) จะเกิดผ่านเรื่องของภพ Y

ตัวอย่าง: คำถามเรื่องงาน → primary_bhava=10 (กัมมะ)
    - เจ้าเรือนกัมมะของผังนี้คือ "เสาร์" (ถ้าภพ 10 = ราศีกุมภ์/มกร)
    - ถ้าเสาร์อยู่ภพ 6 (อริ) → "งานมีศัตรู/อุปสรรค"
    - ถ้าเสาร์อยู่ภพ 11 (ลาภะ) → "งานนำลาภและรายได้"

Implementation note:
    Phase 4 ใช้ตาราง 144 entries ที่ port จาก `thai_astro/bhava_lord_prophecy.py`
    (มี SPECIAL_BHAVA_PAIRS 80+ override + template generic 60+)
    เราไม่ duplicate ตาราง — แต่ wrap function `text_for_pair()` ของเดิม
    เพราะตาราง 144 entries เหมือนกันระหว่าง natal กับ prashna
    เพียงแต่ตีความต่างกัน (ตลอดชีวิต vs เรื่องที่ถามตอนนี้)
"""

from __future__ import annotations

from dataclasses import dataclass

from thai_astro.bhava_lord_prophecy import (
    BHAVA_NAMES,
    text_for_pair as _text_for_pair_natal,
    _classify_pair,
)
from thai_astro.horathaynu.core.caster import Chart
from thai_astro.horathaynu.data.lordship import lord_of, RASHI_NAME_TH
from thai_astro.horathaynu.data.planet_meanings import PLANET_NAME_TH


@dataclass(frozen=True)
class LordInBhavaResult:
    """ผลลัพธ์ชั้นที่ 2 — เจ้าเรือนของภพหลักไปสถิตภพไหน."""

    primary_bhava: int                # ภพหลักของคำถาม
    primary_bhava_name: str
    lord_planet_key: str              # ดาวเจ้าเรือนภพหลัก (key เช่น "saturn")
    lord_planet_th: str               # ชื่อไทย
    lord_rashi_index: int             # ราศีที่ดาวอยู่
    lord_rashi_name: str
    located_bhava: int                # ดาวเจ้าเรือนอยู่ภพไหน
    located_bhava_name: str
    is_same_bhava: bool               # เจ้าเรือนภพ X อยู่ภพ X เอง?
    text: str                         # คำทำนาย
    tone: str                         # good / warning / neutral


def _sign_of_bhava(asc_sign: int, bhava: int) -> int:
    """หาราศีของภพที่ N นับจากลัคนา.

    ภพ 1 = ราศีของลัคนา
    ภพ 2 = ราศีถัดไป (zodiac forward = "วนซ้าย" ในผังไทย)
    """
    return (asc_sign + bhava - 1) % 12


def predict_for_primary_bhava(
    chart: Chart, primary_bhava: int
) -> LordInBhavaResult | None:
    """ทำนายชั้นที่ 2 จาก primary_bhava + chart.

    ขั้นตอน:
        a) primary_bhava → ราศีของภพนั้นในผังนี้
        b) ราศี → ดาวเกษตร (lord_of)
        c) หาดาวเกษตรนั้นใน chart.placements → ภพที่อยู่จริง
        d) text_for_pair(primary_bhava, located_bhava)

    คืน None ถ้า primary_bhava นอกช่วง 1-12 หรือดาวเกษตรไม่อยู่ในผัง
    """
    if not (1 <= primary_bhava <= 12):
        return None

    # (a) ราศีของภพหลัก
    primary_sign = _sign_of_bhava(chart.ascendant_sign, primary_bhava)
    # (b) ดาวเกษตรของราศีนั้น
    lord_key = lord_of(primary_sign)
    # (c) หาตำแหน่งจริงของดาวเจ้าเรือนใน chart
    if lord_key not in chart.placements:
        return None
    lord_placement = chart.placements[lord_key]
    located_bhava = lord_placement.house
    located_rashi_index = lord_placement.sign

    # (d) ข้อความ
    text = _text_for_pair_natal(primary_bhava, located_bhava)
    tone, _ = _classify_pair(primary_bhava, located_bhava)

    return LordInBhavaResult(
        primary_bhava=primary_bhava,
        primary_bhava_name=BHAVA_NAMES[primary_bhava - 1],
        lord_planet_key=lord_key,
        lord_planet_th=PLANET_NAME_TH.get(lord_key, lord_key),
        lord_rashi_index=located_rashi_index,
        lord_rashi_name=RASHI_NAME_TH.get(located_rashi_index, ""),
        located_bhava=located_bhava,
        located_bhava_name=BHAVA_NAMES[located_bhava - 1],
        is_same_bhava=(primary_bhava == located_bhava),
        text=text,
        tone=tone,
    )


__all__ = ["LordInBhavaResult", "predict_for_primary_bhava"]
