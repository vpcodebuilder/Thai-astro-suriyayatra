"""Calendar conversion: จันทรคติ ⇄ สุริยคติ (ไทย)

Forward:   สุริยคติ → จันทรคติ  (ใช้ lunar.compute_lunar_date)
Reverse:   จันทรคติ → สุริยคติ  (search-based: iterate วันใน window แล้ว match)

ขอบเขต Phase 1:
    - รองรับ พ.ศ. 1181-3000 (CE 638-2457) — ช่วงที่สูตรสุริยยาตร์ valid
    - คืน multiple matches ถ้าปีอธิกมาส (formula ปัจจุบันคืน 1 match แต่ flag bool ไว้)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from .boonnak import build_desire
from .lunar import LunarDate, compute_lunar_date
from .ancient_lunar import compute_ancient_lunar_date
from .calendar import gregorian_to_jdn


# ขอบเขตของสูตรสุริยยาตร์: จ.ศ. 0 = ค.ศ. 638 = พ.ศ. 1181
SURIYAYAT_MIN_BE = 1181


# วันในสัปดาห์ภาษาไทย (Python: Mon=0 ... Sun=6)
WEEKDAY_NAME_TH = {
    0: "จันทร์", 1: "อังคาร", 2: "พุธ", 3: "พฤหัสบดี",
    4: "ศุกร์", 5: "เสาร์", 6: "อาทิตย์",
}

THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


@dataclass
class SolarLunarPair:
    """คู่ผลลัพธ์ของวันสุริยคติ + จันทรคติ"""
    # สุริยคติ
    ce_year: int
    be_year: int
    month: int
    day: int
    weekday_idx: int            # 0=Mon ... 6=Sun
    weekday_th: str             # "จันทร์", "อังคาร" ฯลฯ
    julian_day: int             # JDN

    # จันทรคติ
    lunar: LunarDate

    # display strings
    solar_pretty: str           # "วันพุธที่ 22 พฤษภาคม พ.ศ. 2567"
    solar_iso: str              # "2024-05-22"


def _to_solar_pair(d: date) -> Optional[SolarLunarPair]:
    """สร้าง SolarLunarPair จาก datetime.date (ภายใน)
    - ถ้า พ.ศ. >= 1181 (CE 638): ใช้สูตรสุริยยาตร์ปกติ
    - ถ้า พ.ศ. < 1181 (พุทธกาล): ใช้ Meeus algorithm (ประมาณ ±5-15 วัน)
    """
    be_year = d.year + 543
    weekday_idx = d.weekday()
    weekday_th = WEEKDAY_NAME_TH[weekday_idx]
    solar_pretty = (
        f"วัน{weekday_th}ที่ {d.day} {THAI_MONTHS[d.month]} พ.ศ. {be_year}"
    )

    if be_year >= SURIYAYAT_MIN_BE:
        # สูตรสุริยยาตร์ปกติ
        try:
            desire = build_desire(be_year, d.month, d.day)
        except Exception:
            return None
        lunar = compute_lunar_date(desire, sun_rasi=0)
        jdn = desire.julian_date
    else:
        # พุทธกาล — ใช้ Meeus algorithm
        try:
            jdn = gregorian_to_jdn(d.year, d.month, d.day)
            lunar = compute_ancient_lunar_date(jdn, d.year)
        except Exception:
            return None

    return SolarLunarPair(
        ce_year=d.year,
        be_year=be_year,
        month=d.month,
        day=d.day,
        weekday_idx=weekday_idx,
        weekday_th=weekday_th,
        julian_day=jdn,
        lunar=lunar,
        solar_pretty=solar_pretty,
        solar_iso=d.isoformat(),
    )


def solar_to_lunar(be_year: int, month: int, day: int) -> SolarLunarPair:
    """แปลงสุริยคติ → จันทรคติ
    รองรับ:
        - พ.ศ. 1181-3000: สูตรสุริยยาตร์ (แม่นยำ)
        - พ.ศ. 1-1180: Meeus algorithm (ประมาณ ±5-15 วัน)

    Raises:
        ValueError: ถ้าวันที่ไม่ valid
    """
    ce_year = be_year - 543
    # Python date accepts year 1-9999
    if ce_year < 1:
        raise ValueError(f"พ.ศ. {be_year} อยู่นอกขอบเขต (ก่อน ค.ศ. 1 = พ.ศ. 544)")
    try:
        d = date(ce_year, month, day)
    except ValueError as e:
        raise ValueError(f"วันที่ไม่ถูกต้อง: {e}")

    pair = _to_solar_pair(d)
    if pair is None:
        raise ValueError(f"คำนวณวันที่ {d} ไม่สำเร็จ (อาจอยู่นอกขอบเขตสูตร)")
    return pair


def lunar_to_solar(
    be_year: int,
    lunar_month: int,
    waxing: bool,
    day_in_phase: int,
    is_intercalary_month: bool = False,
) -> List[SolarLunarPair]:
    """แปลงจันทรคติ → สุริยคติ

    Algorithm:
        Iterate ทุกวันในช่วง 2 ปีรอบ ๆ ปีที่ระบุ → match ตาม
        (be_year_lunar, lunar_month, waxing, day_in_phase, is_intercalary_month)

    คืน list (อาจมีมากกว่า 1 ถ้าปีอธิกมาสและ formula รองรับ — ปัจจุบันมักได้ 1)

    Args:
        be_year: ปี พ.ศ. จันทรคติ (544-3000)
        lunar_month: เดือนจันทรคติ 1-12
        waxing: True = ขึ้น, False = แรม
        day_in_phase: 1-15 (ขึ้น) หรือ 1-15 (แรม)
        is_intercalary_month: True = "เดือน 8 หลัง" (เฉพาะปีอธิกมาส, เดือน 8 เท่านั้น)

    Raises:
        ValueError: input invalid หรือ search ไม่เจอ
    """
    if not (544 <= be_year <= 3000):
        raise ValueError(
            f"ปี พ.ศ. {be_year} อยู่นอกขอบเขต (รองรับ 544-3000 — "
            f"พุทธกาล 544-1180 ใช้ Meeus ประมาณ)"
        )
    if not (1 <= lunar_month <= 12):
        raise ValueError(f"เดือนจันทรคติต้องอยู่ในช่วง 1-12 (ได้ {lunar_month})")
    if not (1 <= day_in_phase <= 15):
        raise ValueError(f"ค่ำต้องอยู่ในช่วง 1-15 (ได้ {day_in_phase})")
    if is_intercalary_month and lunar_month != 8:
        raise ValueError(
            f'"เดือน 8 หลัง" (intercalary) มีเฉพาะเดือน 8 เท่านั้น '
            f'(ได้เดือน {lunar_month})'
        )

    ce_year = be_year - 543

    # window: ครอบคลุม ม.ค. ปีก่อน ถึง มิ.ย. ปีถัดไป (กันขอบ + อธิกมาส)
    start = date(ce_year - 1, 1, 1)
    end = date(ce_year + 1, 12, 31)

    matches: List[SolarLunarPair] = []
    cur = start
    while cur <= end:
        pair = _to_solar_pair(cur)
        cur += timedelta(days=1)
        if pair is None:
            continue
        lun = pair.lunar
        if (lun.be_year_lunar == be_year
                and lun.lunar_month == lunar_month
                and lun.waxing == waxing
                and lun.day_in_phase == day_in_phase
                and lun.is_intercalary_month == is_intercalary_month):
            matches.append(pair)

    if not matches:
        month_label = f"เดือน {lunar_month}" + (" หลัง" if is_intercalary_month else "")
        hint = ""
        if is_intercalary_month:
            hint = (
                f' — "เดือน 8 หลัง" มีเฉพาะในปีอธิกมาส '
                f'(ปี พ.ศ. {be_year} อาจไม่ใช่ปีอธิกมาส)'
            )
        raise ValueError(
            f"ไม่พบวันสุริยคติที่ตรงกับ "
            f"{('ขึ้น' if waxing else 'แรม')} {day_in_phase} ค่ำ "
            f"{month_label} ปี พ.ศ. {be_year}{hint}"
        )
    return matches


def round_trip_check(be_year: int, month: int, day: int) -> bool:
    """ตรวจ round-trip: solar → lunar → solar ได้วันเดิมไหม"""
    pair = solar_to_lunar(be_year, month, day)
    lun = pair.lunar
    matches = lunar_to_solar(
        lun.be_year_lunar, lun.lunar_month, lun.waxing, lun.day_in_phase
    )
    return any(
        m.be_year == be_year and m.month == month and m.day == day
        for m in matches
    )
