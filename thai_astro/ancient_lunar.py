"""ปฏิทินจันทรคติพุทธกาล (พ.ศ. 1-1180 / CE -542 ถึง 637)

ก่อน จ.ศ. 0 (CE 638) สูตรสุริยยาตร์ของไทยไม่ valid (epoch ของจ.ศ.)
ใช้ Meeus astronomical algorithm (Jean Meeus, "Astronomical Algorithms", 2nd ed)
ในการคำนวณดวงจันทร์ใหม่ → ดิถี → เดือนจันทรคติ

ความแม่นยำ: ±5-15 วัน (สูตรประมาณ ไม่นับ nutation/precession ละเอียด)
ใช้สำหรับศึกษาประวัติศาสตร์เท่านั้น — ไม่ใช่ปฏิทินทางการ
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .lunar import (
    LUNAR_MONTH_NAMES,
    ZODIAC_YEARS,
    ZODIAC_ANIMALS_EN,
    LunarDate,
)


SYNODIC_MONTH = 29.530588861  # Meeus precise value (วัน)


def jdn_to_jde(jdn: int) -> float:
    """JDN (integer) → JDE (ephemeris time, noon-based)"""
    return float(jdn) + 0.5


def meeus_new_moon_jde(k: int) -> float:
    """JDE ของดวงจันทร์ใหม่ครั้งที่ k นับจาก J2000 (Meeus Ch 49)
    k = 0 = ดวงจันทร์ใหม่วันที่ 2000-01-06 (JDE 2451550.09766)
    k บวก = อนาคต, k ลบ = อดีต

    สูตรเรียบง่าย (skip planetary corrections — error ±1-2 วัน):
        JDE = 2451550.09766 + 29.530588861*k + 0.00015437*T^2 - ...
    """
    T = k / 1236.85
    jde = (
        2451550.09766
        + 29.530588861 * k
        + 0.00015437 * T * T
        - 0.000000150 * T * T * T
        + 0.00000000073 * T * T * T * T
    )
    return jde


def find_k_for_jdn(jdn: int) -> int:
    """หา k ของดวงจันทร์ใหม่ก่อนหน้า JDN ที่กำหนด"""
    # estimate k
    k = int((jdn - 2451550.09766) / SYNODIC_MONTH)
    # walk back until new_moon_jde(k) <= jdn
    while meeus_new_moon_jde(k) > jdn:
        k -= 1
    # walk forward to find largest k such that new_moon_jde(k) <= jdn
    while meeus_new_moon_jde(k + 1) <= jdn:
        k += 1
    return k


def ancient_lunar_tithi(jdn: int) -> int:
    """ดิถี (0-29) ของวันที่ JDN ในยุคโบราณ"""
    k = find_k_for_jdn(jdn)
    new_moon = meeus_new_moon_jde(k)
    days_since_new = jdn + 0.5 - new_moon  # noon-based
    tithi = int(days_since_new * 30 / SYNODIC_MONTH)
    if tithi < 0:
        tithi = 0
    if tithi >= 30:
        tithi = 29
    return tithi


def ancient_lunar_month(jdn: int, ce_year_at_new_year: int) -> int:
    """เดือนจันทรคติ (1-12) — ประมาณการจากจำนวนเดือนตั้งแต่ต้นปีลูนาร์

    ต้นปีลูนาร์ของไทย (ก่อนเปลี่ยนเป็นสุริยคติใน ค.ศ. 1889) ≈ ขึ้น 1 ค่ำ เดือน 5
    ≈ ราว 11 เม.ย. - 14 เม.ย. ในแต่ละปี
    """
    # ประมาณ JDN ของวันที่ 14 เม.ย. ปีเดียวกัน (เถลิงศกประมาณ)
    # ใช้ Meeus jdn formula สำหรับ Julian/Gregorian
    # ปีก่อน 1582 = Julian calendar
    y = ce_year_at_new_year
    m, d = 4, 14
    # Julian Date for April 14 of year y
    if y < 1582:
        # Julian calendar
        a = (14 - m) // 12
        yy = y + 4800 - a
        mm = m + 12 * a - 3
        jdn_new_year = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083
    else:
        # Gregorian
        a = (14 - m) // 12
        yy = y + 4800 - a
        mm = m + 12 * a - 3
        jdn_new_year = (d + (153 * mm + 2) // 5 + 365 * yy
                        + yy // 4 - yy // 100 + yy // 400 - 32045)

    # ดวงจันทร์ใหม่ก่อน JDN ปัจจุบัน
    k_now = find_k_for_jdn(jdn)
    # ดวงจันทร์ใหม่ก่อน ขึ้นปีใหม่
    k_year = find_k_for_jdn(jdn_new_year)
    # จำนวนเดือนตั้งแต่ขึ้นปีใหม่ (เริ่มจาก เดือน 5 = อ้าย+4)
    months_in = k_now - k_year
    if months_in < 0:
        months_in += 12
    # เดือน 5 = index 5 → ขึ้นปีใหม่
    lunar_month = ((months_in + 4) % 12) + 1
    return lunar_month


def compute_ancient_lunar_date(jdn: int, ce_year: int) -> LunarDate:
    """คำนวณ LunarDate ในยุคก่อน จ.ศ. (พ.ศ. 1-1180)"""
    tithi = ancient_lunar_tithi(jdn)

    # phase
    if tithi < 15:
        waxing = True
        phase_name = "ขึ้น"
        day_in_phase = tithi + 1
    else:
        waxing = False
        phase_name = "แรม"
        day_in_phase = tithi - 14

    # month
    lunar_month = ancient_lunar_month(jdn, ce_year)
    lunar_month_name = LUNAR_MONTH_NAMES[lunar_month]

    # ปี: ใช้ ค.ศ. ปกติ (จ.ศ. = ค.ศ. - 638 อาจติดลบ)
    cs_year = ce_year - 638  # อาจติดลบ — ก่อน จ.ศ. 0
    be_year_lunar = ce_year + 543

    # นักษัตร: ใช้สูตร mod 12 — แต่ฐานปีอาจคลาดเคลื่อนได้
    # ปี ค.ศ. 1972 = ปีชวด (index 0) — ขยายไปอดีต
    z_idx = (ce_year - 1972) % 12
    z_name = ZODIAC_YEARS[z_idx]
    z_animal = ZODIAC_ANIMALS_EN[z_idx]

    pretty_short = (
        f"{phase_name} {day_in_phase} ค่ำ เดือน {lunar_month} ปี{z_name} (ประมาณ)"
    )
    pretty = (
        f"{phase_name} {day_in_phase} ค่ำ "
        f"เดือน {lunar_month} ({lunar_month_name}) "
        f"ปี{z_name} จ.ศ. {cs_year} — ประมาณการ Meeus ±5-15 วัน"
    )

    return LunarDate(
        tithi=tithi,
        waxing=waxing,
        phase_name=phase_name,
        day_in_phase=day_in_phase,
        day_label="ค่ำ",
        lunar_month=lunar_month,
        lunar_month_name=lunar_month_name,
        is_leap_month_year=False,  # ไม่คำนวณ adhikamasa ในยุคโบราณ
        zodiac_year_index=z_idx,
        zodiac_year_name=z_name,
        zodiac_animal_en=z_animal,
        cs_year=cs_year,
        be_year_lunar=be_year_lunar,
        pretty=pretty,
        pretty_short=pretty_short,
    )
