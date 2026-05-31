"""ตรียางค์ (Drekkana / Triyangka) + ธาตุของราศี

ตรียางค์:
    ราศี 1 ราศี = 30° แบ่งเป็น 3 ช่อง × 10°
    - ปฐมตรียางค์ (0°-10°)   : ครองโดยดาวเกษตรของราศีนั้น
    - ทุติยตรียางค์ (10°-20°): ครองโดยดาวเกษตรของราศีตรีโกณที่ 5 (rashi + 4) mod 12
    - ตติยตรียางค์ (20°-30°) : ครองโดยดาวเกษตรของราศีตรีโกณที่ 9 (rashi + 8) mod 12

ตรียางค์พิษ 3 ชนิด:
    - 🐍 พิษนาค    : ปฐมตรียางค์ ของราศี เมษ(0), กันย์(5), ธนู(8), มีน(11)
    - 🦅 พิษครุฑ   : ทุติยตรียางค์ ของราศี พฤษภ(1), สิงห์(4), ตุล(6), กุมภ์(10)
    - 🐕 พิษสุนัข  : ตติยตรียางค์ ของราศี เมถุน(2), กรกฎ(3), พิจิก(7), มกร(9)

ระดับความหนัก (offset จากต้นช่อง 0-9.99°):
    - 🟡 เบา: 0.00-3.19° และ 6.40-9.59°
    - 🔴 หนัก: 3.20-6.39°

ธาตุของราศี:
    🔥 ไฟ: เมษ(0), สิงห์(4), ธนู(8)
    🌍 ดิน: พฤษภ(1), กันย์(5), มกร(9)
    💨 ลม: เมถุน(2), ตุล(6), กุมภ์(10)
    💧 น้ำ: กรกฎ(3), พิจิก(7), มีน(11)

References:
- horapayakorn.com — ตรียางค์ ปฐม/ทุติย/ตติย และดาวครอง
- mahaplee.blogspot.com — ตรียางค์พิษ พิษนาค/ครุฑ/สุนัข
- baankhunyai.com — ธาตุในโหราศาสตร์ไทย
- ตำราโหราศาสตร์ไทยมาตรฐาน
"""

from __future__ import annotations

from dataclasses import dataclass

from .planets import RASI_LORD, RASI_NAMES_TH


# ============================================================
# ธาตุของราศี (4 ธาตุ)
# ============================================================
# 0=ไฟ, 1=ดิน, 2=ลม, 3=น้ำ
ELEMENT_FIRE = "fire"
ELEMENT_EARTH = "earth"
ELEMENT_AIR = "air"
ELEMENT_WATER = "water"

RASHI_ELEMENT: dict[int, str] = {
    0:  ELEMENT_FIRE,    # เมษ
    1:  ELEMENT_EARTH,   # พฤษภ
    2:  ELEMENT_AIR,     # เมถุน
    3:  ELEMENT_WATER,   # กรกฎ
    4:  ELEMENT_FIRE,    # สิงห์
    5:  ELEMENT_EARTH,   # กันย์
    6:  ELEMENT_AIR,     # ตุล
    7:  ELEMENT_WATER,   # พิจิก
    8:  ELEMENT_FIRE,    # ธนู
    9:  ELEMENT_EARTH,   # มกร
    10: ELEMENT_AIR,     # กุมภ์
    11: ELEMENT_WATER,   # มีน
}

ELEMENT_INFO: dict[str, dict] = {
    ELEMENT_FIRE:  {"name_th": "ไฟ",  "icon": "🔥", "symbol": "▲",  "color": "#c0392b"},
    ELEMENT_EARTH: {"name_th": "ดิน", "icon": "🌍", "symbol": "■",  "color": "#7d5a35"},
    ELEMENT_AIR:   {"name_th": "ลม",  "icon": "💨", "symbol": "〰", "color": "#3498db"},
    ELEMENT_WATER: {"name_th": "น้ำ", "icon": "💧", "symbol": "▼",  "color": "#1a5490"},
}


def element_of(rashi: int) -> str:
    """คืน element key ('fire'/'earth'/'air'/'water')"""
    return RASHI_ELEMENT[rashi % 12]


# ============================================================
# ตรียางค์พิษ
# ============================================================
POISON_NAGA = "naga"      # พิษนาค
POISON_KRUT = "krut"      # พิษครุฑ
POISON_SUNAK = "sunak"    # พิษสุนัข

# (poison_type, decanate_index) keyed by rashi
# decanate_index: 0=ปฐม, 1=ทุติย, 2=ตติย
POISON_MAP: dict[int, tuple[str, int]] = {
    # พิษนาค — ปฐมตรียางค์ ของ เมษ, กันย์, ธนู, มีน
    0:  (POISON_NAGA, 0),
    5:  (POISON_NAGA, 0),
    8:  (POISON_NAGA, 0),
    11: (POISON_NAGA, 0),
    # พิษครุฑ — ทุติยตรียางค์ ของ พฤษภ, สิงห์, ตุล, กุมภ์
    1:  (POISON_KRUT, 1),
    4:  (POISON_KRUT, 1),
    6:  (POISON_KRUT, 1),
    10: (POISON_KRUT, 1),
    # พิษสุนัข — ตติยตรียางค์ ของ เมถุน, กรกฎ, พิจิก, มกร
    2:  (POISON_SUNAK, 2),
    3:  (POISON_SUNAK, 2),
    7:  (POISON_SUNAK, 2),
    9:  (POISON_SUNAK, 2),
}

POISON_INFO: dict[str, dict] = {
    POISON_NAGA: {
        "name_th": "พิษนาค",
        "icon": "🐍",
        "symbol": "นาค",
        "shadow_color": "#2d6a4f",   # เขียวเข้ม
        "meaning": "พิษยา กินยาผิด ติดสุรา ลมพิษ โรคสมอง ความดัน ส่วนบนของศีรษะ",
    },
    POISON_KRUT: {
        "name_th": "พิษครุฑ",
        "icon": "🦅",
        "symbol": "ครุฑ",
        "shadow_color": "#7d4f00",   # น้ำตาลทอง
        "meaning": "อุบัติเหตุฉับพลัน อวัยวะส่วนกลางของร่างกาย จากการทำงาน/การเดินทาง",
    },
    POISON_SUNAK: {
        "name_th": "พิษสุนัข",
        "icon": "🐕",
        "symbol": "สุนัข",
        "shadow_color": "#7a2d12",   # แดงเลือดหมู
        "meaning": "ศัตรู ใส่ความ อุบัติเหตุจากรถยนต์/ของมีคม การทะเลาะ",
    },
}


# ============================================================
# Core compute
# ============================================================
@dataclass(frozen=True)
class TriyangkaInfo:
    """ตรียางค์ที่ดาวหรือลัคนาตกในผัง."""

    rashi: int                  # 0-11
    rashi_name: str
    degree: int                 # 0-29 (องศาในราศี)
    arcminute: int              # 0-59
    decanate: int               # 0=ปฐม, 1=ทุติย, 2=ตติย
    decanate_name_th: str       # "ปฐมตรียางค์" / "ทุติยตรียางค์" / "ตติยตรียางค์"
    lord_planet: str            # ดาวครองตรียางค์นั้น (ชื่อไทย)
    is_poison: bool             # อยู่ในตรียางค์พิษไหม
    poison_type: str | None     # 'naga' / 'krut' / 'sunak' / None
    poison_name_th: str | None
    poison_icon: str | None
    poison_severity: str | None # 'light' / 'heavy' / None
    element: str                # 'fire' / 'earth' / 'air' / 'water'
    element_name_th: str
    element_icon: str


DECANATE_NAMES_TH = ["ปฐมตรียางค์", "ทุติยตรียางค์", "ตติยตรียางค์"]


def triyangka_lord(rashi: int, decanate: int) -> str:
    """คืนดาวเจ้าตรียางค์ที่ decanate (0/1/2) ของราศีนั้น

    - decanate 0 (ปฐม): เจ้าราศีเดิม
    - decanate 1 (ทุติย): เจ้าราศีตรีโกณที่ 5 = (rashi + 4) % 12
    - decanate 2 (ตติย): เจ้าราศีตรีโกณที่ 9 = (rashi + 8) % 12
    """
    if decanate not in (0, 1, 2):
        raise ValueError(f"decanate ต้องเป็น 0/1/2 ได้รับ {decanate}")
    target_rashi = (rashi + decanate * 4) % 12
    return RASI_LORD[target_rashi]


def decanate_of_degree(degree: int, arcminute: int = 0) -> int:
    """หาว่าองศาในราศี (0-29° + arcmin 0-59) อยู่ตรียางค์ใด (0/1/2)"""
    d = degree + arcminute / 60.0
    if d < 10:
        return 0
    if d < 20:
        return 1
    return 2


def degree_within_decanate(degree: int, arcminute: int = 0) -> float:
    """คืนองศาตั้งแต่ต้นช่องตรียางค์ (0.00 - 9.99)"""
    d = degree + arcminute / 60.0
    return d - decanate_of_degree(degree, arcminute) * 10


def poison_severity_at(offset_in_decanate: float) -> str:
    """พิษหนัก/เบา จาก offset 0-10 ภายในช่องตรียางค์

    - หนัก: 3.20-6.39° (กลางช่อง)
    - เบา: 0.00-3.19° หรือ 6.40-9.59° (ขอบช่อง)
    """
    if 3.20 <= offset_in_decanate <= 6.39:
        return "heavy"
    return "light"


def get_triyangka_info(rashi: int, degree: int, arcminute: int = 0) -> TriyangkaInfo:
    """คืนข้อมูลตรียางค์ครบสำหรับตำแหน่งใดๆ ในจักรราศี.

    Args:
        rashi: 0-11
        degree: 0-29 (องศาในราศี)
        arcminute: 0-59 (ลิปดา)
    """
    rashi = rashi % 12
    decanate = decanate_of_degree(degree, arcminute)
    lord = triyangka_lord(rashi, decanate)
    element = element_of(rashi)
    element_info = ELEMENT_INFO[element]

    is_poison = False
    poison_type: str | None = None
    poison_name: str | None = None
    poison_icon: str | None = None
    severity: str | None = None
    if rashi in POISON_MAP:
        ptype, pdec = POISON_MAP[rashi]
        if pdec == decanate:
            is_poison = True
            poison_type = ptype
            pinfo = POISON_INFO[ptype]
            poison_name = pinfo["name_th"]
            poison_icon = pinfo["icon"]
            offset = degree_within_decanate(degree, arcminute)
            severity = poison_severity_at(offset)

    return TriyangkaInfo(
        rashi=rashi,
        rashi_name=RASI_NAMES_TH[rashi],
        degree=degree,
        arcminute=arcminute,
        decanate=decanate,
        decanate_name_th=DECANATE_NAMES_TH[decanate],
        lord_planet=lord,
        is_poison=is_poison,
        poison_type=poison_type,
        poison_name_th=poison_name,
        poison_icon=poison_icon,
        poison_severity=severity,
        element=element,
        element_name_th=element_info["name_th"],
        element_icon=element_info["icon"],
    )


def all_decanate_lords() -> list[dict]:
    """คืน list ของ 36 ช่อง (12 ราศี × 3 ช่อง) พร้อมข้อมูลครบ.

    ใช้ render เลขดาวตรียางค์บนผัง SVG ของแต่ละช่อง
    """
    result: list[dict] = []
    for rashi in range(12):
        for dec in range(3):
            lord = triyangka_lord(rashi, dec)
            poison_type: str | None = None
            if rashi in POISON_MAP and POISON_MAP[rashi][1] == dec:
                poison_type = POISON_MAP[rashi][0]
            result.append({
                "rashi": rashi,
                "rashi_name": RASI_NAMES_TH[rashi],
                "decanate": dec,
                "decanate_name_th": DECANATE_NAMES_TH[dec],
                "lord": lord,
                "is_poison": poison_type is not None,
                "poison_type": poison_type,
                "poison_name_th": POISON_INFO[poison_type]["name_th"] if poison_type else None,
                "poison_icon": POISON_INFO[poison_type]["icon"] if poison_type else None,
            })
    return result


__all__ = [
    # constants
    "ELEMENT_FIRE", "ELEMENT_EARTH", "ELEMENT_AIR", "ELEMENT_WATER",
    "POISON_NAGA", "POISON_KRUT", "POISON_SUNAK",
    "RASHI_ELEMENT", "ELEMENT_INFO", "POISON_MAP", "POISON_INFO",
    "DECANATE_NAMES_TH",
    # functions
    "element_of", "triyangka_lord", "decanate_of_degree",
    "degree_within_decanate", "poison_severity_at",
    "get_triyangka_info", "all_decanate_lords",
    # dataclass
    "TriyangkaInfo",
]
