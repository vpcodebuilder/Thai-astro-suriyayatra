"""Phase 2 — Dignity scoring สำหรับโหรทายหนู

หลักการเดียวกับ `thai_astro/dignities.py` (สุริยยาตร์) แต่ปรับให้ใช้กับ
key ดาวภาษาอังกฤษของ horathaynu (sun/moon/mars/...) และคืน suffix สั้น
สำหรับผนวกเข้าคำทำนาย

Output ของ `compute_sig_dignity()`:
    SigDignity(
        planet="venus",
        rashi=1,
        dignity="เกษตร",        # อุจน์/เกษตร/มูล/มิตร/สมพล/ประ/นิจ
        label="เกษตร",           # ป้ายไทยพร้อมขยาย
        strength=2,              # -3..+3
        suffix=" — ดาวศุกร์...",
    )
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# ===========================================================================
# ตำแหน่งดาว — port จาก thai_astro/dignities.py แต่ใช้ key อังกฤษ
# ===========================================================================

# ราศี: 0=เมษ 1=พฤษภ 2=เมถุน 3=กรกฎ 4=สิงห์ 5=กันย์
#       6=ตุล  7=พิจิก 8=ธนู  9=มกร  10=กุมภ์ 11=มีน

# ดาวอุจน์ — ราศีที่ดาวแสดงพลังสูงสุด
EXALTATION: dict[str, int] = {
    "sun":     0,    # เมษ
    "moon":    1,    # พฤษภ
    "mars":    9,    # มกร
    "mercury": 5,    # กันย์
    "jupiter": 3,    # กรกฎ
    "venus":   11,   # มีน
    "saturn":  6,    # ตุล
    "rahu":    1,    # พฤษภ (บางตำราว่ามิถุน)
    "ketu":    7,    # พิจิก (ตรงข้ามราหู)
}

# ดาวนิจ — ตรงข้ามอุจน์ 180°
DEBILITATION: dict[str, int] = {
    name: (rasi + 6) % 12 for name, rasi in EXALTATION.items()
}

# เกษตร — ราศีที่ดาวครอง (Session 13: กุมภ์=ราหู)
SWAKSHETRA: dict[str, set[int]] = {
    "sun":     {4},          # สิงห์
    "moon":    {3},          # กรกฎ
    "mars":    {0, 7},       # เมษ, พิจิก
    "mercury": {2, 5},       # เมถุน, กันย์
    "jupiter": {8, 11},      # ธนู, มีน
    "venus":   {1, 6},       # พฤษภ, ตุล
    "saturn":  {9},          # มกร
    "rahu":    {10},         # กุมภ์
    "ketu":    set(),
    "uranus":  set(),
    "lagna":   set(),
}

# มูลตรีโกณ
MULATRIKONA: dict[str, int] = {
    "sun":     4,    # สิงห์ (0-19°)
    "moon":    1,    # พฤษภ
    "mars":    0,    # เมษ
    "mercury": 5,    # กันย์
    "jupiter": 8,    # ธนู
    "venus":   6,    # ตุล
    "saturn":  10,   # กุมภ์
}

# ความสัมพันธ์มิตร/ศัตรู — ระหว่างดาวเจ้าราศี
PLANET_RELATIONS: dict[str, dict[str, set[str]]] = {
    "sun": {
        "friends":  {"moon", "mars", "jupiter"},
        "enemies":  {"venus", "saturn", "rahu"},
        "neutral":  {"mercury", "ketu", "uranus"},
    },
    "moon": {
        "friends":  {"sun", "mercury"},
        "enemies":  {"rahu", "ketu"},
        "neutral":  {"mars", "jupiter", "venus", "saturn", "uranus"},
    },
    "mars": {
        "friends":  {"sun", "moon", "jupiter"},
        "enemies":  {"mercury", "rahu"},
        "neutral":  {"venus", "saturn", "ketu", "uranus"},
    },
    "mercury": {
        "friends":  {"sun", "venus"},
        "enemies":  {"moon"},
        "neutral":  {"mars", "jupiter", "saturn", "rahu", "ketu", "uranus"},
    },
    "jupiter": {
        "friends":  {"sun", "moon", "mars"},
        "enemies":  {"mercury", "venus", "rahu"},
        "neutral":  {"saturn", "ketu", "uranus"},
    },
    "venus": {
        "friends":  {"mercury", "saturn", "rahu"},
        "enemies":  {"sun", "moon"},
        "neutral":  {"mars", "jupiter", "ketu", "uranus"},
    },
    "saturn": {
        "friends":  {"mercury", "venus", "rahu"},
        "enemies":  {"sun", "moon", "mars"},
        "neutral":  {"jupiter", "ketu", "uranus"},
    },
    "rahu": {
        "friends":  {"venus", "saturn"},
        "enemies":  {"sun", "moon", "mars"},
        "neutral":  {"mercury", "jupiter", "ketu", "uranus"},
    },
    "ketu": {
        "friends":  {"mars", "venus", "saturn"},
        "enemies":  {"sun", "moon"},
        "neutral":  {"mercury", "jupiter", "rahu", "uranus"},
    },
    "uranus": {
        "friends":  {"saturn", "mercury"},
        "enemies":  set(),
        "neutral":  {"sun", "moon", "mars", "jupiter", "venus", "rahu", "ketu"},
    },
}

DIGNITY_STRENGTH: dict[str, int] = {
    "อุจน์":   3,
    "เกษตร":  2,
    "มูล":    2,
    "มิตร":    1,
    "สมพล":    0,
    "ประ":     -1,
    "ศัตรู":   -1,
    "นิจ":     -3,
}

DIGNITY_LABEL: dict[str, str] = {
    "อุจน์":   "อุจน์ (มหาอุจ)",
    "เกษตร":  "เกษตร (บ้านตัวเอง)",
    "มูล":    "มูลตรีโกณ",
    "มิตร":    "ราศีมิตร",
    "สมพล":    "สมพล (กลาง)",
    "ประ":     "ประ (ราศีศัตรู)",
    "ศัตรู":   "ราศีศัตรู",
    "นิจ":     "นิจ (มหานิจ)",
}

# Suffix สำหรับผนวกเข้าคำทำนาย (Phase 2)
DIGNITY_SUFFIX: dict[str, str] = {
    "อุจน์":  " — {p}ได้ {d} พลังเต็มที่ ส่งผลแรงในเรื่องนี้",
    "มูล":    " — {p}อยู่ {d} พลังหนุนเรื่องนี้อย่างมั่นคง",
    "เกษตร": " — {p}อยู่ {d} (บ้านตัวเอง) แสดงพลังเต็ม เรื่องนี้พึ่งตัวเองได้",
    "มิตร":   " — {p}อยู่ {d} มีคนหนุนหลังเรื่องนี้",
    "ประ":    " — {p}ตก {d} เรื่องนี้ติดขัด ต้องอาศัยความพยายามมากกว่าปกติ",
    "ศัตรู":  " — {p}อยู่ {d} มีอุปสรรคในเรื่องนี้",
    "นิจ":    " — {p}ตก {d} อ่อนกำลังที่สุด เรื่องนี้เสี่ยงผิดพลาดสูง",
    "สมพล":   "",  # ไม่เสริม
}


@dataclass(frozen=True)
class SigDignity:
    planet: str
    rashi: int
    dignity: str
    label: str
    strength: int
    suffix: str
    is_strong: bool   # อุจน์/เกษตร/มูล
    is_weak: bool     # นิจ/ประ/ศัตรู


def _planet_th(planet_key: str) -> str:
    return {
        "sun":     "อาทิตย์",
        "moon":    "จันทร์",
        "mars":    "อังคาร",
        "mercury": "พุธ",
        "jupiter": "พฤหัสบดี",
        "venus":   "ศุกร์",
        "saturn":  "เสาร์",
        "rahu":    "ราหู",
        "ketu":    "เกตุ",
        "uranus":  "มฤตยู",
        "lagna":   "ลัคนา",
    }.get(planet_key, planet_key)


def compute_sig_dignity(planet: str, rashi: int) -> SigDignity:
    """คำนวณตำแหน่งกำลังของดาว significator ในราศี.

    ลำดับเช็ค: อุจน์ → นิจ → มูล → เกษตร → ดูเจ้าราศี (มิตร/ศัตรู/สมพล)
    """
    if planet == "lagna":
        # ลัคนาไม่นับ dignity เพราะไม่ใช่ดาวจริง
        return SigDignity(
            planet=planet, rashi=rashi, dignity="สมพล",
            label="(ลัคนา)", strength=0, suffix="",
            is_strong=False, is_weak=False,
        )

    if planet in EXALTATION and EXALTATION[planet] == rashi:
        dignity = "อุจน์"
    elif planet in DEBILITATION and DEBILITATION[planet] == rashi:
        dignity = "นิจ"
    elif planet in MULATRIKONA and MULATRIKONA[planet] == rashi:
        dignity = "มูล"
    elif planet in SWAKSHETRA and rashi in SWAKSHETRA[planet]:
        dignity = "เกษตร"
    else:
        # ดูจากเจ้าราศี
        from thai_astro.horathaynu.data.lordship import lord_of
        rashi_lord = lord_of(rashi)
        if rashi_lord == planet:
            dignity = "เกษตร"  # safety net
        else:
            rels = PLANET_RELATIONS.get(planet, {})
            if rashi_lord in rels.get("friends", set()):
                dignity = "มิตร"
            elif rashi_lord in rels.get("enemies", set()):
                dignity = "ประ"
            else:
                dignity = "สมพล"

    strength = DIGNITY_STRENGTH[dignity]
    label = DIGNITY_LABEL[dignity]
    suffix_tmpl = DIGNITY_SUFFIX.get(dignity, "")
    suffix = suffix_tmpl.format(p=_planet_th(planet), d=label) if suffix_tmpl else ""

    return SigDignity(
        planet=planet,
        rashi=rashi,
        dignity=dignity,
        label=label,
        strength=strength,
        suffix=suffix,
        is_strong=(dignity in {"อุจน์", "เกษตร", "มูล"}),
        is_weak=(dignity in {"นิจ", "ประ", "ศัตรู"}),
    )


__all__ = [
    "SigDignity",
    "compute_sig_dignity",
    "EXALTATION",
    "DEBILITATION",
    "SWAKSHETRA",
    "PLANET_RELATIONS",
]
