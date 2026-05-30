"""ตรรกะเรือนสัมพันธ์ — 2 ชั้น

ตามแนวทาง อ.ประทีป อัครา:
1. focus → ดาวเกษตรของราศี focus → ดาวเกษตรนั้นไปสถิตภพใด
2. ดาวเกษตรนั้น (ในข้อ 1) อยู่ราศีใด → ดาวเกษตรของราศีนั้น → ไปสถิตภพใด

ผลลัพธ์เป็น dataclass ที่ interpreter เอาไปประกอบเป็นประโยค
"""

from __future__ import annotations

from dataclasses import dataclass

from thai_astro.horathaynu.core.caster import Chart
from thai_astro.horathaynu.data.lordship import lord_of


@dataclass(frozen=True)
class RelationStep:
    """ผลของเรือนสัมพันธ์ 1 ชั้น"""
    lord: str           # ดาวเกษตร (planet_key)
    lord_sign: int      # ราศีที่ดาวเกษตรอยู่
    lord_house: int     # ภพที่ดาวเกษตรอยู่


@dataclass(frozen=True)
class RelationChain:
    """เรือนสัมพันธ์ครบ 2 ชั้น"""
    focus: str          # planet_key ของจุดพยากรณ์ ('lagna', 'sun', ...)
    focus_sign: int     # ราศีของจุดพยากรณ์
    focus_house: int    # ภพของจุดพยากรณ์
    step1: RelationStep
    step2: RelationStep | None  # None ถ้าดาวเกษตรเดียวกับชั้นแรก (วน loop)


def _step_from(sign: int, chart: Chart) -> RelationStep | None:
    """หาดาวเกษตรของราศี → ตำแหน่งของดาวเกษตรนั้น

    คืน None ถ้าดาวเกษตรไม่ได้อยู่ใน chart (ตำราบางสำนักไม่ขับครบ)
    """
    lord = lord_of(sign)
    if lord not in chart.placements:
        return None
    p = chart.placements[lord]
    return RelationStep(lord=lord, lord_sign=p.sign, lord_house=p.house)


def chain_for(chart: Chart, focus: str) -> RelationChain:
    """คำนวณเรือนสัมพันธ์ 2 ชั้นจากจุดพยากรณ์"""
    if focus not in chart.placements:
        raise ValueError(f"focus '{focus}' ไม่อยู่ใน chart")

    focus_p = chart.placements[focus]
    step1 = _step_from(focus_p.sign, chart)
    if step1 is None:
        raise ValueError(
            f"ดาวเกษตรของราศี {focus_p.sign} (ของ {focus}) "
            "ไม่ปรากฏใน chart"
        )

    step2 = _step_from(step1.lord_sign, chart)
    # ถ้าชั้น 2 ได้ดาวเกษตรเดียวกับชั้น 1 → ไม่ต้องอ่านซ้ำ
    if step2 is not None and step2.lord == step1.lord:
        step2 = None

    return RelationChain(
        focus=focus,
        focus_sign=focus_p.sign,
        focus_house=focus_p.house,
        step1=step1,
        step2=step2,
    )
