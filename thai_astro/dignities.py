"""ตำแหน่งกำลังของดาว + เกณฑ์/โยคในดวงชะตา (Planet dignities & Yogas)

ครอบคลุม:
    1. ตำแหน่งดาวรายดวง (Dignities)
       - เกษตร (Swakshetra)     ดาวอยู่ในราศีของตัวเอง
       - อุจน์/มหาอุจ (Ucha)     ดาวอยู่ในราศีที่ตนได้กำลังสูงสุด
       - นิจ (Nicha)              ดาวอยู่ในราศีตรงข้ามอุจน์ = กำลังต่ำสุด
       - มหาจักร (Mūlatrikoṇa)   ดาวอยู่ในราศีหลักของตน (subset ของเกษตร)
       - มิตร / ศัตรู / สมพล      ตามผังมิตรศัตรูพื้นฐาน
       - ประ (Pra)                ดาวอยู่ในราศีศัตรู — กำลังอ่อน

    2. เกณฑ์/โยคในชะตา (Yogas) — จัดให้สอดคล้องตำราไทย:
       - ปทุมเกณฑ์ (Padma)        ดาวสำคัญ ≥ 4 ดวงอยู่ในเกณฑ์ (ภพ 1,4,7,10)
       - องค์เกณฑ์                ดาวเป็นเกษตร/อุจน์ ≥ 3 ดวง (ดาวมีกำลัง)
       - อุดมเกณฑ์                ดาวอุจน์ ≥ 2 ดวง (อุดมความสามารถ)
       - มหาภูตเกณฑ์              ดาวอย่างน้อย 3 ดวงอยู่ในตรีโกณ (ภพ 1,5,9)
       - นิจภังคราชโยค            ดาวนิจ แต่เจ้าราศีที่ดาวนั้นอยู่ได้ตำแหน่งดี
                                  → ความนิจ "แตก" กลายเป็นโชค
       - วิปริตราชโยค             (จัดที่ bhava_lord_prophecy แล้ว)

ตำราอ้างอิง:
    - อ.เทพย์ สาริกบุตร, "คัมภีร์โหราศาสตร์ภาคต้น"
    - พล.ต.ประยูร พลอารีย์, "ตำราโหราศาสตร์ไทยมาตรฐาน"
    - ตำรา B.V. Raman, Phaladeepika (มหาเทวะ)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .planets import RASI_NAMES_TH, RASI_LORD


# ============================================================
# ราศีของอุจน์ / นิจ / เกษตร
# (sidereal Thai = ใช้ราศีตามดาวจริง ไม่ใช่ tropical)
# index 0..11 = เมษ..มีน
# ============================================================
EXALTATION_RASI: Dict[str, int] = {
    "อาทิตย์":   0,    # เมษ
    "จันทร์":    1,    # พฤษภ
    "อังคาร":   9,    # มกร
    "พุธ":       5,    # กันย์
    "พฤหัสบดี": 3,    # กรกฎ
    "ศุกร์":    11,    # มีน
    "เสาร์":    6,    # ตุลย์
    "ราหู":     1,    # พฤษภ (บางตำราว่ามิถุน)
    "เกตุ":     7,    # พิจิก
}

DEBILITATION_RASI: Dict[str, int] = {
    name: (rasi + 6) % 12 for name, rasi in EXALTATION_RASI.items()
}

# เกษตร: ราศีที่ดาวครอง (อาจมี 1 หรือ 2 ราศี)
SWAKSHETRA: Dict[str, Set[int]] = {
    "อาทิตย์":   {4},          # สิงห์
    "จันทร์":    {3},          # กรกฎ
    "อังคาร":   {0, 7},        # เมษ, พิจิก
    "พุธ":       {2, 5},       # เมถุน, กันย์
    "พฤหัสบดี": {8, 11},      # ธนู, มีน
    "ศุกร์":     {1, 6},       # พฤษภ, ตุลย์
    "เสาร์":    {9},           # มกร (กุมภ์ยกให้ราหูตามเลขเกษตร 8)
    "ราหู":     {10},          # กุมภ์
    "เกตุ":     set(),
}

# มหาจักร (Mūlatrikoṇa) — ราศีหลักของดาว (ดีกว่าเกษตรเฉย ๆ)
MULATRIKONA: Dict[str, int] = {
    "อาทิตย์":   4,    # สิงห์
    "จันทร์":    1,    # พฤษภ (Devanagari = vrishabha)
    "อังคาร":   0,    # เมษ
    "พุธ":       5,    # กันย์
    "พฤหัสบดี": 8,    # ธนู
    "ศุกร์":     6,    # ตุลย์
    "เสาร์":    10,   # กุมภ์
}

# ผังมิตรศัตรูพื้นฐาน (Naisargika)
# {ดาว: {"friends": set, "enemies": set, "neutral": set}}
PLANET_RELATIONS: Dict[str, Dict[str, Set[str]]] = {
    "อาทิตย์": {
        "friends": {"จันทร์", "อังคาร", "พฤหัสบดี"},
        "enemies": {"ศุกร์", "เสาร์", "ราหู"},
        "neutral": {"พุธ", "เกตุ"},
    },
    "จันทร์": {
        "friends": {"อาทิตย์", "พุธ"},
        "enemies": {"ราหู", "เกตุ"},
        "neutral": {"อังคาร", "พฤหัสบดี", "ศุกร์", "เสาร์"},
    },
    "อังคาร": {
        "friends": {"อาทิตย์", "จันทร์", "พฤหัสบดี"},
        "enemies": {"พุธ", "ราหู"},
        "neutral": {"ศุกร์", "เสาร์", "เกตุ"},
    },
    "พุธ": {
        "friends": {"อาทิตย์", "ศุกร์"},
        "enemies": {"จันทร์"},
        "neutral": {"อังคาร", "พฤหัสบดี", "เสาร์", "ราหู", "เกตุ"},
    },
    "พฤหัสบดี": {
        "friends": {"อาทิตย์", "จันทร์", "อังคาร"},
        "enemies": {"พุธ", "ศุกร์", "ราหู"},
        "neutral": {"เสาร์", "เกตุ"},
    },
    "ศุกร์": {
        "friends": {"พุธ", "เสาร์", "ราหู"},
        "enemies": {"อาทิตย์", "จันทร์"},
        "neutral": {"อังคาร", "พฤหัสบดี", "เกตุ"},
    },
    "เสาร์": {
        "friends": {"พุธ", "ศุกร์", "ราหู"},
        "enemies": {"อาทิตย์", "จันทร์", "อังคาร"},
        "neutral": {"พฤหัสบดี", "เกตุ"},
    },
    "ราหู": {
        "friends": {"ศุกร์", "เสาร์"},
        "enemies": {"อาทิตย์", "จันทร์", "อังคาร"},
        "neutral": {"พุธ", "พฤหัสบดี", "เกตุ"},
    },
    "เกตุ": {
        "friends": {"อังคาร", "ศุกร์", "เสาร์"},
        "enemies": {"อาทิตย์", "จันทร์"},
        "neutral": {"พุธ", "พฤหัสบดี", "ราหู"},
    },
}


# ============================================================
# ระดับกำลัง (Strength)
# ============================================================
DIGNITY_STRENGTH = {
    "อุจน์":   3,    # สูงสุด — มหาอุจ
    "เกษตร":  2,    # อยู่บ้านตัวเอง
    "มูล":    2,    # มูลตรีโกณ
    "มิตร":    1,    # ราศีของเพื่อน
    "สมพล":    0,    # กลาง
    "ศัตรู":   -1,   # ราศีของศัตรู (เป็นประ)
    "ประ":     -1,   # ราศีศัตรู
    "นิจ":     -3,   # ต่ำสุด — มหานิจ
}

DIGNITY_LABEL_TH = {
    "อุจน์":   "อุจน์ (มหาอุจ)",
    "เกษตร":  "เกษตร",
    "มูล":    "มูลตรีโกณ",
    "มิตร":    "มิตร",
    "สมพล":    "สมพล",
    "ศัตรู":   "ศัตรู (เป็นประ)",
    "ประ":     "ประ",
    "นิจ":     "นิจ (มหานิจ)",
}


# ============================================================
# Public API
# ============================================================
@dataclass
class PlanetDignity:
    planet: str
    rasi: int                # 0-11
    rasi_name: str
    dignity: str             # "อุจน์" | "เกษตร" | "มูล" | "มิตร" | "สมพล" | "ศัตรู" | "นิจ"
    label: str               # ภาษาไทยพร้อมขยาย
    strength: int            # -3..+3
    is_strong: bool          # อุจน์ / เกษตร / มูล
    is_weak: bool            # นิจ / ศัตรู
    is_exalted: bool         # อุจน์ โดยเฉพาะ
    is_debilitated: bool     # นิจ โดยเฉพาะ


def compute_dignity(planet: str, rasi: int) -> PlanetDignity:
    """คำนวณตำแหน่ง 1 ดาว"""
    # ลำดับเช็ค: อุจน์ → นิจ → มูล → เกษตร → มิตร/ศัตรู/สมพล
    if planet in EXALTATION_RASI and EXALTATION_RASI[planet] == rasi:
        dignity = "อุจน์"
    elif planet in DEBILITATION_RASI and DEBILITATION_RASI[planet] == rasi:
        dignity = "นิจ"
    elif planet in MULATRIKONA and MULATRIKONA[planet] == rasi:
        dignity = "มูล"
    elif planet in SWAKSHETRA and rasi in SWAKSHETRA[planet]:
        dignity = "เกษตร"
    else:
        # ดูจากเจ้าราศี
        rasi_lord = RASI_LORD[rasi]
        if rasi_lord == planet:
            dignity = "เกษตร"  # safety net
        else:
            relations = PLANET_RELATIONS.get(planet, {})
            if rasi_lord in relations.get("friends", set()):
                dignity = "มิตร"
            elif rasi_lord in relations.get("enemies", set()):
                dignity = "ประ"
            else:
                dignity = "สมพล"

    strength = DIGNITY_STRENGTH[dignity]
    label = DIGNITY_LABEL_TH[dignity]
    return PlanetDignity(
        planet=planet,
        rasi=rasi,
        rasi_name=RASI_NAMES_TH[rasi],
        dignity=dignity,
        label=label,
        strength=strength,
        is_strong=dignity in ("อุจน์", "เกษตร", "มูล"),
        is_weak=dignity in ("นิจ", "ประ", "ศัตรู"),
        is_exalted=dignity == "อุจน์",
        is_debilitated=dignity == "นิจ",
    )


def compute_all_dignities(planets: Dict[str, "object"]) -> Dict[str, PlanetDignity]:
    """คำนวณตำแหน่งทุกดาว"""
    out = {}
    for name, p in planets.items():
        out[name] = compute_dignity(name, p.zodiac.rasi)
    return out


# ============================================================
# Yoga detection
# ============================================================
@dataclass
class Yoga:
    name: str               # "ปทุมเกณฑ์"
    description: str        # คำอธิบายสั้น
    effect: str             # ผล (ดี/พลิกดวง)
    planets_involved: List[str]   # ดาวที่ทำให้เกิดโยคนี้
    severity: int           # 1-3 (3 = โยคใหญ่)


KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}

MAIN_PLANETS = {
    "อาทิตย์", "จันทร์", "อังคาร", "พุธ",
    "พฤหัสบดี", "ศุกร์", "เสาร์",
}


def _rasi_to_house(rasi: int, asc_rasi: int) -> int:
    return ((rasi - asc_rasi) % 12) + 1


def detect_yogas(
    asc_rasi: int,
    planets: Dict[str, "object"],
    dignities: Dict[str, PlanetDignity],
) -> List[Yoga]:
    """ตรวจหาเกณฑ์/โยคในชะตา"""
    yogas: List[Yoga] = []

    # นับดาวอุจน์/เกษตร/มูล
    exalted = [n for n, d in dignities.items() if d.is_exalted]
    own_or_strong = [
        n for n, d in dignities.items()
        if d.is_strong and n in MAIN_PLANETS
    ]
    debilitated = [n for n, d in dignities.items() if d.is_debilitated]

    # ดาวในเกณฑ์ (1,4,7,10) และตรีโกณ (1,5,9)
    in_kendra = []
    in_trikona = []
    in_dusthana = []
    for n in MAIN_PLANETS:
        if n not in planets:
            continue
        house = _rasi_to_house(planets[n].zodiac.rasi, asc_rasi)
        if house in KENDRA_HOUSES:
            in_kendra.append(n)
        if house in TRIKONA_HOUSES:
            in_trikona.append(n)
        if house in DUSTHANA_HOUSES:
            in_dusthana.append(n)

    # === ปทุมเกณฑ์ (Padma) ===
    # ดาวหลัก ≥ 4 ดวง อยู่ในเกณฑ์
    if len(in_kendra) >= 4:
        yogas.append(Yoga(
            name="ปทุมเกณฑ์",
            description=f"ดาวหลัก {len(in_kendra)} ดวงอยู่ในเกณฑ์ (ภพ 1, 4, 7, 10)",
            effect="ดวงใหญ่ มีอำนาจวาสนา เป็นที่นับหน้าถือตา ฐานะมั่นคง",
            planets_involved=in_kendra,
            severity=3,
        ))

    # === มหาภูตเกณฑ์ ===
    # ดาวหลัก ≥ 3 ดวง อยู่ในตรีโกณ
    if len(in_trikona) >= 3:
        yogas.append(Yoga(
            name="มหาภูตเกณฑ์",
            description=f"ดาวหลัก {len(in_trikona)} ดวงอยู่ในตรีโกณ (ภพ 1, 5, 9)",
            effect="บุญเก่าหนุนชีวิต ดวงสมหวังในเรื่องสำคัญ คนชอบช่วยเหลือ",
            planets_involved=in_trikona,
            severity=2,
        ))

    # === อุดมเกณฑ์ ===
    # ดาวอุจน์ ≥ 2 ดวง
    if len(exalted) >= 2:
        yogas.append(Yoga(
            name="อุดมเกณฑ์",
            description=f"มีดาวได้ตำแหน่งอุจน์ {len(exalted)} ดวง ({', '.join(exalted)})",
            effect="ดวงอุดมความสามารถ ดาวมีกำลังสูง พลิกเรื่องร้ายเป็นดีได้บ่อย",
            planets_involved=exalted,
            severity=3,
        ))

    # === องค์เกณฑ์ ===
    # ดาวอย่างน้อย 3 ดวงเป็นเกษตร/อุจน์/มูล
    if len(own_or_strong) >= 3:
        yogas.append(Yoga(
            name="องค์เกณฑ์",
            description=f"ดาวมีกำลัง {len(own_or_strong)} ดวง ({', '.join(own_or_strong)})",
            effect="ดวงพื้นฐานแข็งแรง พึ่งตนเองได้ดี โอกาสมาเองโดยไม่ต้องเหนื่อยมาก",
            planets_involved=own_or_strong,
            severity=2,
        ))

    # === นิจภังคราชโยค ===
    # ดาวเป็นนิจ แต่เจ้าราศีที่ดาวนั้นสถิตอยู่ ได้ตำแหน่งดี
    # → ความนิจถูกหัก กลายเป็นโชค
    for d_planet in debilitated:
        p = planets[d_planet]
        host_rasi = p.zodiac.rasi
        host_lord = RASI_LORD[host_rasi]
        host_dignity = dignities.get(host_lord)
        if host_dignity and host_dignity.is_strong:
            yogas.append(Yoga(
                name="นิจภังคราชโยค",
                description=(
                    f"ดาว{d_planet}เป็นนิจในราศี{p.zodiac.rasi_name} "
                    f"แต่{host_lord}เจ้าราศีอยู่ในตำแหน่ง{host_dignity.dignity} "
                    f"(ราศี{host_dignity.rasi_name})"
                ),
                effect=(
                    f"เรื่องที่ควรร้ายของ{d_planet}จะ \"พลิกกลายเป็นดี\" "
                    f"เริ่มต้นจากจุดต่ำแล้วลุกขึ้นได้สูงกว่าเดิม"
                ),
                planets_involved=[d_planet, host_lord],
                severity=3,
            ))

    # === ดาวอุจน์รายดวง (น้อยกว่าโยค แต่ก็เป็นกำลังใจ) ===
    # บันทึกเป็นโยคเล็ก ๆ ถ้ายังไม่มีอุดมเกณฑ์
    if exalted and len(exalted) < 2:
        for p in exalted:
            yogas.append(Yoga(
                name=f"{p}ได้อุจน์",
                description=f"ดาว{p}อยู่ในราศี{RASI_NAMES_TH[EXALTATION_RASI[p]]} (ราศีอุจน์)",
                effect=f"เรื่องของ{p}จะเด่นมากในชีวิต — กำลังสูงสุดของดาวดวงนี้",
                planets_involved=[p],
                severity=2,
            ))

    return yogas


def yoga_modifier_for_planet(planet: str, yogas: List[Yoga]) -> Optional[str]:
    """ถ้าดาวนี้มีส่วนในโยคใด คืนข้อความเสริม"""
    relevant = [y for y in yogas if planet in y.planets_involved]
    if not relevant:
        return None
    # เลือกโยคที่ severity สูงสุด
    relevant.sort(key=lambda y: -y.severity)
    return relevant[0].name
