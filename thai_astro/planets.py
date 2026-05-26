"""โมดูลคำนวณตำแหน่งดาวเคราะห์ทั้ง 9 ตามวิธีสุริยยาตร์

Port จาก Devtino.Astrology/Somput/* (Sun, Moon, MinorPlanet, Rahu, Ketu)
ทุกตำแหน่งคำนวณเป็นหน่วย "อาร์คมินิต" (arcminute) โดย:
    21600 arcminutes = 360° (1 รอบจักรราศี)
    1800 arcminutes = 30° (1 ราศี)
    60 arcminutes = 1°

คำศัพท์:
- มัธยม (Mattayom)   = mean longitude
- สมผุส (Somput)     = true longitude
- ภุชพล (Phutchapon) = equation of center (สำหรับอาทิตย์/จันทร์)
- มันโทจจ์ (Mandocca/Uja) = apogee
- ฉายา (Chaya)       = ตารางย่อยของ sine 4 ค่า
- ขันธ์ (Kan)         = ตารางย่อยของ sine สำหรับอาทิตย์/จันทร์
- กำลังพระเคราะห์ (PowerPlanet) = ค่าตั้งต้นของดาวรอง
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .boonnak import Desire


# ============================================================
# ค่าคงที่จักรราศี
# ============================================================
ZODIAC_ARCMIN = 21600           # 360° เป็น arcminute
RASI_ARCMIN = 1800              # 30° เป็น arcminute
RASI_NAMES_TH = [
    "เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
    "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน",
]

# ตารางฉายา (Chaya) สำหรับดาวรอง 4 ค่า (Devtino.Astrology/Somput/Orbital/Chaya.cs)
CHAYA = [0, 244, 427, 488]

# ตารางขันธ์ (Kan) — ตาราง sine ของอาทิตย์/จันทร์ 7 ค่า
KAN_SUN = [0, 35, 67, 94, 116, 129, 134]
KAN_MOON = [0, 77, 148, 209, 256, 286, 296]

# ดาวเจ้าเรือนแต่ละราศี (โหราศาสตร์ไทย)
RASI_LORD = {
    0: "อังคาร",   1: "ศุกร์",   2: "พุธ",       3: "จันทร์",
    4: "อาทิตย์",  5: "พุธ",     6: "ศุกร์",     7: "อังคาร",
    8: "พฤหัสบดี", 9: "เสาร์",  10: "เสาร์",    11: "พฤหัสบดี",
}

# ลำดับแสดงผล
PLANET_ORDER = [
    "อาทิตย์", "จันทร์", "อังคาร", "พุธ",
    "พฤหัสบดี", "ศุกร์", "เสาร์", "ราหู", "เกตุ",
]


# ============================================================
# Utility: compact_angle, zodiac conversion
# ============================================================

def compact_angle(value: int) -> int:
    """ทำให้ค่าอยู่ในช่วง [0, 21600) (port ของ Zodiac.CompactAngleFromArcminutes)"""
    return value % ZODIAC_ARCMIN


@dataclass
class Zodiac:
    """ตำแหน่งในจักรราศี"""
    arcminute_total: int             # 0..21599
    rasi: int                        # 0..11 (เมษ..มีน)
    degree: int                      # 0..29 (ในราศี)
    arcminute: int                   # 0..59
    arcsecond: int = 0

    @classmethod
    def from_arcminutes(cls, value: int) -> "Zodiac":
        v = value % ZODIAC_ARCMIN
        rasi = v // RASI_ARCMIN
        rem = v % RASI_ARCMIN
        degree = rem // 60
        arcminute = rem % 60
        return cls(arcminute_total=v, rasi=rasi, degree=degree, arcminute=arcminute)

    @property
    def rasi_name(self) -> str:
        return RASI_NAMES_TH[self.rasi]

    def format(self) -> str:
        return f"{self.rasi_name} {self.degree:02d}°{self.arcminute:02d}'"

    @property
    def longitude_degrees(self) -> float:
        """ตำแหน่งเป็นองศาสมบูรณ์ 0..360"""
        return self.arcminute_total / 60.0


# ============================================================
# Putchakoti (ภุชโกฏิ) - หาควอแดรนต์ของมุม
# ============================================================

@dataclass
class Putchakoti:
    """ข้อมูลภุชโกฏิจากมุม (port จาก Putchakoti.cs)"""
    p_value: int
    p_sign: int           # +1 หรือ -1
    p_rasi: int
    k_value: int
    k_sign: int           # +1 หรือ -1
    k_rasi: int

    @classmethod
    def find_quadrant(cls, corner: int) -> "Putchakoti":
        """แบ่ง 21600 arcmin ออกเป็น 4 ควอแดรนต์ แล้วคำนวณ P, K ตามทิศ"""
        if corner < 0:
            corner += ZODIAC_ARCMIN
        q = corner // 5400 + 1  # 1..4

        if q == 1:
            p_val = corner
            p_sgn = -1
            k_val = 5400 - corner
            k_sgn = 1
        elif q == 2:
            p_val = 10800 - corner
            p_sgn = -1
            k_val = corner - 5400
            k_sgn = -1
        elif q == 3:
            p_val = corner - 10800
            p_sgn = 1
            k_val = 16200 - corner
            k_sgn = -1
        else:  # q == 4
            p_val = 21600 - corner
            p_sgn = 1
            k_val = corner - 16200
            k_sgn = 1

        return cls(
            p_value=p_val, p_sign=p_sgn, p_rasi=p_val // RASI_ARCMIN,
            k_value=k_val, k_sign=k_sgn, k_rasi=k_val // RASI_ARCMIN,
        )


# ============================================================
# Planet result
# ============================================================

@dataclass
class Planet:
    """ผลลัพธ์ดาวเคราะห์หนึ่งดวง"""
    name: str
    mattayom: int                    # arcminute
    somput: int                      # arcminute (ตำแหน่งจริง)
    zodiac: Zodiac
    retrograde: bool = False
    # debug fields
    extra: Dict[str, int] = field(default_factory=dict)

    @property
    def rasi(self) -> int:
        return self.zodiac.rasi

    @property
    def degree_in_rasi(self) -> float:
        return self.somput % RASI_ARCMIN / 60.0

    @property
    def longitude(self) -> float:
        return self.somput / 60.0

    def format_dms(self) -> str:
        return self.zodiac.format()


# ============================================================
# Sun (อาทิตย์)
# ============================================================

def sun_mattayom(desire: Desire) -> int:
    """มัธยมอาทิตย์ (port จาก Sun.GetMattayomMinutes)

    หาร KammatchaphonDesire ออกเป็น (ราศี, องศา, นาที) ด้วยตัวหาร 24350, 811, 14
    แล้วประกอบเป็น arcminute พร้อมหัก offset 3 นาที
    """
    K = desire.kammatchaphon
    rasi_q, rasi_r = divmod(K, 24350)
    deg_q, deg_r = divmod(rasi_r, 811)
    min_q, _min_r = divmod(deg_r, 14)
    value = rasi_q * 1800 + deg_q * 60 + (min_q - 3)
    return compact_angle(value)


def compute_sun(desire: Desire) -> Planet:
    mattayom = sun_mattayom(desire)
    # มัธยมรวิ (ปรับ -23 arcmin สำหรับใช้กับดาวอื่น)
    mattayom_rawi = compact_angle(mattayom - 23)
    # มุม A: มัธยม - มันโทจจ์อาทิตย์ (= 4800 arcmin = 80°)
    corner = compact_angle(mattayom - 4800)
    p = Putchakoti.find_quadrant(corner)

    # ขันธ์
    kan_value = p.p_value // 900
    # ภุชพล (Phutchapon) - interpolate ตาราง Kan
    frac = p.p_value / 900.0 - kan_value
    phutchapon = int(math.floor(
        frac * (KAN_SUN[kan_value + 1] - KAN_SUN[kan_value]) + KAN_SUN[kan_value]
    ))

    somput = compact_angle(mattayom + phutchapon * p.p_sign)
    return Planet(
        name="อาทิตย์",
        mattayom=mattayom,
        somput=somput,
        zodiac=Zodiac.from_arcminutes(somput),
        extra={"mattayom_rawi": mattayom_rawi, "phutchapon": phutchapon},
    )


# ============================================================
# Moon (จันทร์)
# ============================================================

def compute_moon(desire: Desire) -> Planet:
    """มัธยม + สมผุสของจันทร์ (port จาก Moon.cs)

    Mattayom = DithiDesire × 720 + floor(1.04 × UjaponRemainderDesire) − 40 + SunMattayom
    MattayomUja = floor(((UjaponDesire + time/24) / 3232) × 21600) + 2
    Corner = Mattayom − MattayomUja
    """
    sun_m = sun_mattayom(desire)

    raw = (
        desire.dithi * 720
        + int(math.floor(1.04 * desire.ujapon_remainder))
        - 40
        + sun_m
    )
    mattayom = compact_angle(raw)

    # มัธยมอุจจ์
    uja_value = (desire.ujapon + desire.time_hours / 24.0) / 3232.0 * 21600
    mattayom_uja = compact_angle(int(math.floor(uja_value)) + 2)

    corner = compact_angle(mattayom - mattayom_uja)
    p = Putchakoti.find_quadrant(corner)

    kan_value = p.p_value // 900
    frac = p.p_value / 900.0 - kan_value
    phutchapon = int(math.floor(
        frac * (KAN_MOON[kan_value + 1] - KAN_MOON[kan_value]) + KAN_MOON[kan_value]
    ))

    somput = compact_angle(mattayom + phutchapon * p.p_sign)
    return Planet(
        name="จันทร์",
        mattayom=mattayom,
        somput=somput,
        zodiac=Zodiac.from_arcminutes(somput),
        extra={"mattayom_uja": mattayom_uja, "phutchapon": phutchapon},
    )


# ============================================================
# PowerPlanet (กำลังพระเคราะห์) - ตัวตั้งสำหรับดาวรอง
# ============================================================

@dataclass
class PowerPlanet:
    mattayom_rawi: int       # อาทิตย์ - 23
    appa: int                # ปีอัปป
    value_minutes: int       # = Appa × 21600 + MattayomRawi


def compute_power(desire: Desire) -> PowerPlanet:
    """port จาก PowerPlanet.cs

    appaFactor = (KammatchaphonDesire < 364) ? 611 : 610
    Appa = ThaiMinorEra.Year - appaFactor
    """
    sun_m = sun_mattayom(desire)
    mattayom_rawi = compact_angle(sun_m - 23)
    appa_factor = 611 if desire.kammatchaphon < 364 else 610
    appa = desire.thai_minor_era - appa_factor
    value_minutes = appa * 21600 + mattayom_rawi
    return PowerPlanet(
        mattayom_rawi=mattayom_rawi,
        appa=appa,
        value_minutes=value_minutes,
    )


# ============================================================
# MinorPlanet (ดาวรอง: พุธ, ศุกร์, อังคาร, พฤหัส, เสาร์, ยูเรนัส)
# ============================================================

# ข้อมูลดาวรอง: { ฐานบนเศษ, ฐานบนส่วน, ฐานล่างเศษ, ฐานล่างส่วน,
#                 มัธยมคงที่, โกฏิคงที่, มนทเฉท, สิงฆผล_factor }
MINOR_PLANET_DATA = {
    "พุธ":       (7, 46, 4, 1, 10642, 13200, 6000, 21.0),
    "ศุกร์":     (5, 3, 10, 243, 10944, 4800, 19200, 11.0),
    "อังคาร":   (1, 2, 16, 505, 5420, 7620, 2700, 4 / 15.0),
    "พฤหัสบดี": (1, 12, 1, 1032, 14297, 10320, 5520, 3 / 7.0),
    "เสาร์":    (1, 30, 6, 10000, 11944, 14820, 3780, 7 / 6.0),
}
# ยูเรนัสไม่อยู่ในสุริยยาตร์ดั้งเดิม แต่ Devtino ใส่ไว้
MINOR_PLANET_DATA_URANUS = (1, 84, 1, 7224, 16277, 7440, 38640, 3 / 7.0)


def _interpolate_chaya(value: int, rasi: int) -> float:
    """interpolate ค่า chaya สำหรับ rasi (0..3)"""
    return (value / 1800.0 - rasi) * (CHAYA[rasi + 1] - CHAYA[rasi]) + CHAYA[rasi]


def compute_minor_planet(name: str, desire: Desire, power: PowerPlanet) -> Planet:
    """port จาก MinorPlanet.Compute()

    ขั้นตอนหลัก:
    1. ฐานบน, ฐานล่าง จากกำลังพระเคราะห์
    2. มัธยม = ฐานบน ± ฐานล่าง + ค่าคงที่[4]
    3. มุม A = (มัธยม หรือ มัธยมรวิ) − ค่าคงที่[5]
    4. หา Putchakoti (manda quadrant) -> มนทผล (Phon)
    5. มันทสมผุส และ มุม A ใหม่
    6. หา Putchakoti อีกครั้ง (sighra) -> มหาผล (Mahaphon)
    7. สมผุส = มันทสมผุส + มหาผล × PSign
    """
    if name == "ยูเรนัส":
        data = MINOR_PLANET_DATA_URANUS
    else:
        data = MINOR_PLANET_DATA[name]

    is_inner = name in ("พุธ", "ศุกร์")

    # ฐานบน / ฐานล่าง
    base_up = power.value_minutes * data[0] / data[1]
    base_down = power.value_minutes * data[2] / data[3]
    base_up_floor = int(math.floor(base_up))
    base_down_floor = int(math.floor(base_down))

    # มัธยม
    if name == "ศุกร์":
        mattayom_raw = base_up_floor - base_down_floor + int(data[4])
    else:
        mattayom_raw = base_up_floor + base_down_floor + int(data[4])
    mattayom = compact_angle(mattayom_raw)

    # มุม A
    if is_inner:
        corner = compact_angle(power.mattayom_rawi - int(data[5]))
    else:
        corner = compact_angle(mattayom - int(data[5]))

    p = Putchakoti.find_quadrant(corner)

    # มนทภุช (ฟิลิปดา)
    montaputcha = int(math.floor(_interpolate_chaya(p.p_value, p.p_rasi) * 60))
    # มนทโกฏิ
    montakoti = int(math.floor(_interpolate_chaya(p.k_value, p.k_rasi) + 0.5))
    # โกฏิผล
    kotipon = montakoti // 2
    # มนทเฉท
    montachet = int(data[6]) + kotipon * p.k_sign
    # ผล (Phon)
    if montachet == 0:
        phon = 0
    else:
        phon = int(math.floor(montaputcha * 60 / montachet))

    # มันทสมผุส และ มุม A ใหม่
    if is_inner:
        montasomput = compact_angle(power.mattayom_rawi + phon * p.p_sign)
        corner2 = compact_angle(montasomput - mattayom)
    else:
        montasomput = compact_angle(mattayom + phon * p.p_sign)
        corner2 = compact_angle(montasomput - power.mattayom_rawi)

    p2 = Putchakoti.find_quadrant(corner2)

    sinkaputcha = int(math.floor(_interpolate_chaya(p2.p_value, p2.p_rasi) * 60))
    sinkakoti = int(math.floor(_interpolate_chaya(p2.k_value, p2.k_rasi) + 0.5))
    sinkaphon = int(math.floor(int(math.floor((sinkaputcha / 60.0) + 0.5)) / 3.0))

    # มนทพยาต
    if is_inner:
        montapayat = int(math.floor(60 * data[7]))
    else:
        montapayat = int(math.floor(montachet * data[7]))

    somputpayat = sinkaphon + montapayat
    sinkasomputchet = somputpayat + sinkakoti * p2.k_sign

    if sinkasomputchet == 0:
        mahaphon = 0
    else:
        mahaphon = int(math.floor(sinkaputcha * 60 / sinkasomputchet))

    somput = compact_angle(montasomput + mahaphon * p2.p_sign)

    return Planet(
        name=name,
        mattayom=mattayom,
        somput=somput,
        zodiac=Zodiac.from_arcminutes(somput),
        extra={
            "phon": phon,
            "mahaphon": mahaphon,
            "montasomput": montasomput,
        },
    )


# ============================================================
# Rahu (ราหู)
# ============================================================

def compute_rahu(power: PowerPlanet) -> Planet:
    """port จาก Rahu.cs

    BaseUp = ValueMinutes / 20
    BaseDown = ValueMinutes / 265
    Mattayom = floor(BaseUp) + floor(BaseDown)
    Somput = 15150 − Mattayom
    """
    base_up = power.value_minutes // 20
    base_down = power.value_minutes // 265
    mattayom = compact_angle(base_up + base_down)
    somput = compact_angle(15150 - mattayom)
    return Planet(
        name="ราหู",
        mattayom=mattayom,
        somput=somput,
        zodiac=Zodiac.from_arcminutes(somput),
        retrograde=True,
    )


# ============================================================
# Ketu (เกตุ)
# ============================================================

def compute_ketu(desire: Desire) -> Planet:
    """port จาก Ketu.cs

    fraction = (HorakhunAtMidnight − 344) / 679
    Pon = remainder (compacted)
    Mattayom = floor((Pon + time/24) × 21600 / 679)
    Somput = 21600 − Mattayom
    """
    v = desire.horakhun_at_midnight - 344
    pon = compact_angle(v % 679)
    mattayom = compact_angle(
        int(math.floor((pon + desire.time_hours / 24.0) * 21600 / 679.0))
    )
    somput = compact_angle(21600 - mattayom)
    return Planet(
        name="เกตุ",
        mattayom=mattayom,
        somput=somput,
        zodiac=Zodiac.from_arcminutes(somput),
        retrograde=True,
    )


# ============================================================
# Compute all planets
# ============================================================

def compute_all(desire: Desire) -> Dict[str, Planet]:
    """คำนวณดาวทั้ง 9 ดวง (ไม่รวมยูเรนัส) ตามมาตรฐานโหราศาสตร์ไทย"""
    power = compute_power(desire)
    return {
        "อาทิตย์": compute_sun(desire),
        "จันทร์": compute_moon(desire),
        "อังคาร": compute_minor_planet("อังคาร", desire, power),
        "พุธ": compute_minor_planet("พุธ", desire, power),
        "พฤหัสบดี": compute_minor_planet("พฤหัสบดี", desire, power),
        "ศุกร์": compute_minor_planet("ศุกร์", desire, power),
        "เสาร์": compute_minor_planet("เสาร์", desire, power),
        "ราหู": compute_rahu(power),
        "เกตุ": compute_ketu(desire),
    }
