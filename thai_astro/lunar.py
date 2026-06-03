"""ปฏิทินจันทรคติไทย (Thai Lunar Calendar)

คำนวณ:
    - ดิถี → ขึ้น/แรม X ค่ำ
    - เดือนทางจันทรคติ (1-12: อ้าย ยี่ สาม ... สิบสอง)
    - ปีอธิกมาส / ปีปกติมาส (port จาก ThaiLunarYear.cs ของ Devtino)
    - ปีนักษัตร (ชวด ฉลู ขาล ... กุน)
    - จ.ศ. ของปีจันทรคติ

ตำราอ้างอิง:
    - สูตรอธิกมาส: Loy Chunpongthong (อนุรักษ์สูตรเก่าโบราณ)
    - ปฏิทินจันทรคติไทย: หอสมุดแห่งชาติ
    - ตำราโหราศาสตร์ไทยทั่วไป (อ.เทพย์ สาริกบุตร)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


# ============================================================
# ชื่อเดือนทางจันทรคติ (Thai Lunar Months)
# index 0 = unused, 1-12 = เดือน 1-12
# ============================================================
LUNAR_MONTH_NAMES = [
    "",
    "อ้าย", "ยี่", "สาม", "สี่", "ห้า", "หก",
    "เจ็ด", "แปด", "เก้า", "สิบ", "สิบเอ็ด", "สิบสอง",
]


# ============================================================
# ปีนักษัตร (12 Thai Zodiac Years)
# Index 0 = ปีชวด (เริ่มที่ ค.ศ. 1972, 1984, 1996 ...)
# ============================================================
ZODIAC_YEARS = [
    "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง",
    "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน",
]
# Animal English names
ZODIAC_ANIMALS_EN = [
    "rat", "ox", "tiger", "rabbit", "dragon", "snake",
    "horse", "goat", "monkey", "rooster", "dog", "pig",
]


# ============================================================
# Public dataclass
# ============================================================
@dataclass
class LunarDate:
    """วันทางจันทรคติไทย"""
    tithi: int                  # ดิถีดิบ (0-29)
    waxing: bool                # True = ขึ้น (waxing), False = แรม (waning)
    phase_name: str             # "ขึ้น" หรือ "แรม"
    day_in_phase: int           # 1-15
    day_label: str              # "ค่ำ" (เสมอ)

    lunar_month: int            # 1-12
    lunar_month_name: str       # "อ้าย", "ยี่", ... , "สิบสอง"
    is_leap_month_year: bool    # ปีอธิกมาส (มีเดือน 8 หนสอง)

    zodiac_year_index: int      # 0-11
    zodiac_year_name: str       # "มะแม"
    zodiac_animal_en: str       # "goat"

    cs_year: int                # จ.ศ. (Thai Minor Era)
    be_year_lunar: int          # พ.ศ. (สำหรับปีจันทรคติ)

    pretty: str                 # "ขึ้น 11 ค่ำ เดือน 9 (เก้า) ปีมะแม จ.ศ. 1341"
    pretty_short: str           # "ขึ้น 11 ค่ำ เดือน 9 ปีมะแม"

    is_intercalary_month: bool = False  # เดือน 8 หลัง (8/8) — เฉพาะปีอธิกมาส


# ============================================================
# Computation
# ============================================================
def tithi_to_phase_day(tithi: int) -> Tuple[bool, str, int]:
    """แปลงดิถีดิบ (0-29) เป็น (waxing, phase_name, day_in_phase)
        dithi 0-14  → ขึ้น 1-15 ค่ำ
        dithi 15-29 → แรม 1-15 ค่ำ
    """
    if tithi < 0:
        tithi = 0
    if tithi >= 30:
        tithi = tithi % 30
    if tithi < 15:
        return True, "ขึ้น", tithi + 1
    else:
        return False, "แรม", tithi - 14


SYNODIC_MONTH = 29.530588  # ค่าเฉลี่ยของเดือนทางจันทรคติ (วัน)


# cache mas at thaloengsok per cs_year — รัน build_desire เพียงครั้งแรกแล้วเก็บไว้
_MAS_THALOENGSOK_CACHE: dict[int, int] = {}


def _mas_at_thaloengsok(thaloengsok) -> int:
    """หา mas (synodic month count) ณ วันเถลิงศก
    Cache ตาม cs_year — กัน recursion / double-compute
    """
    cs = thaloengsok.cs_year
    if cs in _MAS_THALOENGSOK_CACHE:
        return _MAS_THALOENGSOK_CACHE[cs]
    from .boonnak import build_desire
    d = build_desire(thaloengsok.be_year, thaloengsok.month, thaloengsok.day)
    _MAS_THALOENGSOK_CACHE[cs] = d.mas
    return d.mas


def lunar_month_from_surathin(surathin_days: int) -> int:
    """[DEPRECATED] approximate formula — keep for backward compat
    ใช้ floor(surathin/29.53) — มี off-by-1 day ในบางจุด
    สูตรใหม่ใน compute_lunar_date() ใช้ desire.mas - mas_at_thaloengsok แทน
    """
    months = int((surathin_days + 7) / SYNODIC_MONTH)
    return ((months + 4) % 12) + 1


def sun_rasi_to_lunar_month_approx(sun_rasi: int) -> int:
    """ประมาณการเดือนจันทรคติจากราศีอาทิตย์ (เลิกใช้ — มี error สูง)
    คงไว้เป็น backup
    """
    return ((sun_rasi + 4) % 12) + 1


def _lookup_db_year_type(cs_year: int) -> str | None:
    """หาประเภทปีจาก DB (adhikamasa_years)
    คืน 'adhikamasa' | 'adhikavara' | 'both' | 'normal' หรือ None ถ้าไม่มี
    Best-effort: ถ้า DB ไม่พร้อม/error → None (caller จะ fallback formula)
    """
    try:
        # Late import เพื่อเลี่ยง circular dep และ optional DB
        from webapp.db import SessionLocal
        from webapp.models import AdhikamasaYear
        s = SessionLocal()
        try:
            row = s.query(AdhikamasaYear).filter_by(cs_year=cs_year).first()
            return row.type if row else None
        finally:
            s.close()
    except Exception:
        return None


def is_leap_month_year(cs_year: int) -> bool:
    """ปีอธิกมาสหรือไม่
    ลำดับการตัดสิน:
        1. ถ้ามี entry ใน adhikamasa_years (DB) → ใช้ค่านั้น (authoritative)
        2. ถ้าไม่มี → fallback formula port จาก ThaiLunarYear.cs ของ Devtino
            GrateYear = cs_year + 560
            value = (GrateYear - 0.45222) % 2.7118886
            IsLeapMonth = (value < 1)
    """
    db_type = _lookup_db_year_type(cs_year)
    if db_type is not None:
        return db_type in ("adhikamasa", "both")

    # fallback algorithm
    grate_year = cs_year + 560
    value = (grate_year - 0.45222) % 2.7118886
    return value < 1.0


def zodiac_year_index(ce_year_at_lunar_year_start: int) -> int:
    """0-11 ของปีนักษัตร
        ปี ค.ศ. 1972 = ปีชวด (index 0)
        ปี ค.ศ. 1979 = ปีมะแม (index 7)
        ปี ค.ศ. 1980 = ปีวอก (index 8)
    """
    return (ce_year_at_lunar_year_start - 1972) % 12


def compute_lunar_date(
    desire,
    sun_rasi: int,
) -> LunarDate:
    """คำนวณวันทางจันทรคติจาก Desire + ราศีของอาทิตย์
    desire: Desire (จาก thai_astro.boonnak)
    sun_rasi: ราศีของอาทิตย์ (0-11) — ใช้เป็น context (ไม่ใช้ในสูตรใหม่)
    """
    tithi = desire.dithi
    waxing, phase_name, day_in_phase = tithi_to_phase_day(tithi)

    # ปี: ใช้ จ.ศ. ของเถลิงศกที่ใช้ (ปีจันทรคติเริ่มที่เถลิงศก)
    cs_year = desire.surathin.thaloengsok_cs_year
    ce_year_lunar = cs_year + 638  # CE ของเถลิงศก
    be_year_lunar = ce_year_lunar + 543

    leap = is_leap_month_year(cs_year)

    # ============================================================
    # สูตรเดือนจันทรคติ v2 (2026-06-03)
    # ใช้ desire.mas (synodic month count from Devtino formula) แทน
    # floor(surathin/29.53) approximation
    #
    # mas_diff = mas ของวันที่ - mas ณ วันเถลิงศก (ใช้ helper cache)
    # mas เพิ่มที่ "ขึ้น 1 ค่ำ" ของแต่ละเดือน
    #
    # ปีปกติ (12 เดือน): map mas_diff 0..11 → เดือน 5,6,7,8,9,10,11,12,1,2,3,4
    # ปีอธิกมาส (13 เดือน, แทรกเดือน 8 หลัง):
    #   mas_diff 0..12 → เดือน 5,6,7,8(ต้น),8(หลัง intercalary),9,10,11,12,1,2,3,4
    # ============================================================
    mas_thal = _mas_at_thaloengsok(desire.surathin.thaloengsok)
    mas_diff = desire.mas - mas_thal

    is_intercalary = False
    if not leap:
        # ปีปกติ: ((mas_diff + 4) % 12) + 1
        # mas_diff 0 → 5, 1 → 6, ..., 7 → 12, 8 → 1, 9 → 2, 10 → 3, 11 → 4
        idx = mas_diff % 12
        lunar_month = ((idx + 4) % 12) + 1
    else:
        # ปีอธิกมาส
        if mas_diff <= 0:
            lunar_month = 5  # ต้นปี
        elif mas_diff < 4:
            lunar_month = 5 + mas_diff   # 6, 7, 8 (first)
        elif mas_diff == 4:
            lunar_month = 8              # second 8 (หลัง / intercalary)
            is_intercalary = True
        else:
            # mas_diff 5+ : shift back by 1 จากตำแหน่งปกติ
            # (เพราะแทรกเดือน 8 หลังเข้ามาแล้ว)
            idx = (mas_diff - 1) % 12
            lunar_month = ((idx + 4) % 12) + 1

    lunar_month_name = LUNAR_MONTH_NAMES[lunar_month]
    intercalary_suffix = " หลัง" if is_intercalary else ""

    z_idx = zodiac_year_index(ce_year_lunar)
    z_name = ZODIAC_YEARS[z_idx]
    z_animal = ZODIAC_ANIMALS_EN[z_idx]

    # pretty strings
    pretty_short = (
        f"{phase_name} {day_in_phase} ค่ำ เดือน {lunar_month}{intercalary_suffix} ปี{z_name}"
    )
    leap_tag = " (อธิกมาส)" if leap else ""
    pretty = (
        f"{phase_name} {day_in_phase} ค่ำ "
        f"เดือน {lunar_month}{intercalary_suffix} ({lunar_month_name}){leap_tag} "
        f"ปี{z_name} จ.ศ. {cs_year}"
    )

    return LunarDate(
        tithi=tithi,
        waxing=waxing,
        phase_name=phase_name,
        day_in_phase=day_in_phase,
        day_label="ค่ำ",
        lunar_month=lunar_month,
        lunar_month_name=lunar_month_name,
        is_leap_month_year=leap,
        is_intercalary_month=is_intercalary,
        zodiac_year_index=z_idx,
        zodiac_year_name=z_name,
        zodiac_animal_en=z_animal,
        cs_year=cs_year,
        be_year_lunar=be_year_lunar,
        pretty=pretty,
        pretty_short=pretty_short,
    )
