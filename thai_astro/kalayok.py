"""กาลโยค (Kalayok) — เกณฑ์ปีตาม จ.ศ.

ประกอบด้วย 4 เกณฑ์หลัก:
    - ธงชัย (Thongchai) — มงคล
    - อธิบดี (Athibodi) — มงคล (ผู้ใหญ่/ตำแหน่ง)
    - อุบาทว์ (Ubat) — อัปมงคล
    - โลกาวินาศ (Lokawinat) — อัปมงคล (วินาศ)

แต่ละเกณฑ์ระบุ: วัน (Wan 1-7), ยาม (Yarm 1-8), ราศี (Rasi 0-11),
ดิถี (Dithi 0-29), ฤกษ์/นักษัตร (Roek 1-27)

Port จาก: Devtino.Astrology/Kalayok/*.cs (Thongchai.cs, Athibodi.cs,
Ubat.cs, Lokawinat.cs, Criterion.cs)

หมายเหตุ: Wan/Yarm/Roek เป็นแบบ 1-based (ถ้า mod=0 → คืนค่า divisor)
        Rasi/Dithi เป็นแบบ raw modulo (0-based)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ============================================================
# Factor constants (port จาก Common/Factor.cs)
# ============================================================
F_WAN = 7
F_YARM = 8
F_RASI = 12
F_DITHI = 30
F_ROEK = 27


# Wan name (1=อาทิตย์ ... 7=เสาร์)
WAN_NAMES = [
    "", "อาทิตย์", "จันทร์", "อังคาร", "พุธ",
    "พฤหัสบดี", "ศุกร์", "เสาร์",
]


def _one_based(value: int, divisor: int) -> int:
    """remainder = value % divisor; ถ้า 0 คืน divisor (1-based)"""
    r = value % divisor
    return r if r != 0 else divisor


@dataclass(frozen=True)
class KalayokEntry:
    """1 เกณฑ์ — มี 5 component"""
    name: str               # ชื่อเกณฑ์ ("ธงชัย" ฯลฯ)
    is_auspicious: bool     # True = มงคล, False = อัปมงคล
    factor: int             # ค่า Value ที่คำนวณได้
    wan: int                # 1-7 (วัน)
    yarm: int               # 1-8 (ยาม)
    rasi: int               # 0-11 (ราศี)
    dithi: int              # 0-29 (ดิถี)
    roek: int               # 1-27 (ฤกษ์/นักษัตร)

    @property
    def wan_name(self) -> str:
        return WAN_NAMES[self.wan] if 1 <= self.wan <= 7 else "?"


def _build(name: str, auspicious: bool, factor: int) -> KalayokEntry:
    return KalayokEntry(
        name=name,
        is_auspicious=auspicious,
        factor=factor,
        wan=_one_based(factor, F_WAN),
        yarm=_one_based(factor, F_YARM),
        rasi=factor % F_RASI,
        dithi=factor % F_DITHI,
        roek=_one_based(factor, F_ROEK),
    )


# ============================================================
# 4 เกณฑ์
# ============================================================
def thongchai(cs_year: int) -> KalayokEntry:
    """ธงชัย — Factor = จ.ศ. × 10 + 3"""
    return _build("ธงชัย", True, cs_year * 10 + 3)


def athibodi(cs_year: int) -> KalayokEntry:
    """อธิบดี — Factor = จ.ศ. mod 498"""
    return _build("อธิบดี", True, cs_year % 498)


def ubat(cs_year: int) -> KalayokEntry:
    """อุบาทว์ — Factor = จ.ศ. × 10 + 2"""
    return _build("อุบาทว์", False, cs_year * 10 + 2)


def lokawinat(cs_year: int) -> KalayokEntry:
    """โลกาวินาศ — Factor = จ.ศ. + 1120"""
    return _build("โลกาวินาศ", False, cs_year + 1120)


@dataclass(frozen=True)
class KalayokYear:
    """กาลโยคทั้งปี — ครบ 4 เกณฑ์"""
    cs_year: int
    thongchai: KalayokEntry
    athibodi: KalayokEntry
    ubat: KalayokEntry
    lokawinat: KalayokEntry

    def all_entries(self) -> Dict[str, KalayokEntry]:
        return {
            "thongchai": self.thongchai,
            "athibodi": self.athibodi,
            "ubat": self.ubat,
            "lokawinat": self.lokawinat,
        }


def compute_kalayok(cs_year: int) -> KalayokYear:
    """คำนวณกาลโยคทั้งปีจาก จ.ศ."""
    return KalayokYear(
        cs_year=cs_year,
        thongchai=thongchai(cs_year),
        athibodi=athibodi(cs_year),
        ubat=ubat(cs_year),
        lokawinat=lokawinat(cs_year),
    )


# ============================================================
# Match utilities — เช็คว่า moment ที่ให้ตกเกณฑ์ไหน
# ============================================================
def match_wan(year: KalayokYear, wan: int) -> Dict[str, bool]:
    """คืน dict ของ {ชื่อเกณฑ์: ตกหรือไม่} สำหรับวันที่ตรงเกณฑ์"""
    return {
        name: entry.wan == wan
        for name, entry in year.all_entries().items()
    }


def match_rasi(year: KalayokYear, rasi: int) -> Dict[str, bool]:
    return {
        name: entry.rasi == rasi
        for name, entry in year.all_entries().items()
    }


def match_dithi(year: KalayokYear, dithi: int) -> Dict[str, bool]:
    return {
        name: entry.dithi == dithi
        for name, entry in year.all_entries().items()
    }


def match_roek(year: KalayokYear, roek: int) -> Dict[str, bool]:
    return {
        name: entry.roek == roek
        for name, entry in year.all_entries().items()
    }
