"""นวางค์จักร์ (Navamsa) — การแบ่งจักรราศีย่อย 9 ส่วน/ราศี

แต่ละราศี (30°) แบ่ง 9 ส่วน × 3°20' (= 200 arcmin) เรียกว่า "navamsa"
รวมจักรราศี = 12 × 9 = 108 navamsa (เท่ากับจำนวนตำแหน่งสำคัญทางอินเดีย)

กฎ Parashara (สูตรไทยใช้ตามนี้):
    - Movable signs (เมษ/กรกฎ/ตุล/มกร = 0,3,6,9): navamsa แรกเริ่มที่ราศีตัวเอง
    - Fixed signs (พฤษภ/สิงห์/พิจิก/กุมภ์ = 1,4,7,10): navamsa แรกเริ่มที่ราศี 9 จากตัวเอง
    - Dual signs (เมถุน/กันย์/ธนู/มีน = 2,5,8,11): navamsa แรกเริ่มที่ราศี 5 จากตัวเอง

Vargottama: ดาวที่อยู่ในราศีเดียวกันทั้ง rashi และ navamsa → กำลังแข็ง (Yoga)

ตำราอ้างอิง:
    - horasaadrevision.com (id=19689) — วิธีคำนวณนวางค์
    - Parashara Hora Shastra (ฉบับอินเดีย, แปลไทยโดย อ.จรัญ พิกุล)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


ARCMIN_PER_NAVAMSA = 200      # 3°20'
NAVAMSA_PER_RASI = 9
TOTAL_NAVAMSA = 108


@dataclass(frozen=True)
class NavamsaPosition:
    """ตำแหน่งในนวางค์จักร์"""
    nav_rashi: int          # 0-11 (ราศีในวงนวางค์)
    nav_index: int          # 1-9 (ลำดับนวางค์ในราศีเดิม)
    is_vargottama: bool     # True ถ้า nav_rashi == rashi เดิม


def compute_navamsa(rashi: int, degree: int, arcmin: int = 0) -> NavamsaPosition:
    """คำนวณนวางค์จาก (rashi, degree, arcmin)

    Args:
        rashi: 0-11 (เมษ=0)
        degree: 0-29 (องศาในราศี)
        arcmin: 0-59 (ลิปดา)

    Returns:
        NavamsaPosition
    """
    total = degree * 60 + arcmin
    nav_index_0 = total // ARCMIN_PER_NAVAMSA   # 0-8
    nav_index_0 = max(0, min(8, nav_index_0))

    if rashi in (0, 3, 6, 9):       # movable (จร)
        start = rashi
    elif rashi in (1, 4, 7, 10):    # fixed (สถิร)
        start = (rashi + 8) % 12
    else:                            # dual (อุภัย) (2, 5, 8, 11)
        start = (rashi + 4) % 12

    nav_rashi = (start + nav_index_0) % 12

    return NavamsaPosition(
        nav_rashi=nav_rashi,
        nav_index=nav_index_0 + 1,
        is_vargottama=(nav_rashi == rashi),
    )


def chart_to_navamsa_view(chart) -> Dict[str, NavamsaPosition]:
    """แปลงดาวทุกดวงในดวงเป็น navamsa position

    คืน dict {planet_name: NavamsaPosition}
    """
    result: Dict[str, NavamsaPosition] = {}
    for name, planet in chart.planets.items():
        z = planet.zodiac
        result[name] = compute_navamsa(z.rasi, z.degree, z.arcminute)
    # รวมลัคนา
    asc_z = chart.ascendant.zodiac
    result["ลัคนา"] = compute_navamsa(asc_z.rasi, asc_z.degree, asc_z.arcminute)
    return result


def navamsa_rashi_to_planets(nav_view: Dict[str, NavamsaPosition]) -> Dict[int, list]:
    """กลับ index — รายราศีในวงนวางค์ คืนรายชื่อดาวที่ตกราศีนั้น"""
    out: Dict[int, list] = {i: [] for i in range(12)}
    for name, pos in nav_view.items():
        out[pos.nav_rashi].append(name)
    return out
