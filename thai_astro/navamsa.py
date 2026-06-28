"""นวางค์จักร (Navamsa / D9) — การแบ่งจักรราศีย่อย 9 ส่วน/ราศี

แต่ละราศี (30°) แบ่ง 9 ส่วน × 3°20' (= 200 arcmin) เรียกว่า "navamsa"
รวมจักรราศี = 12 × 9 = 108 navamsa

กฎ Parashara (สูตรไทยใช้ตามนี้):
    - Movable signs (เมษ/กรกฎ/ตุล/มกร = 0,3,6,9): navamsa แรกเริ่มที่ราศีตัวเอง
    - Fixed signs (พฤษภ/สิงห์/พิจิก/กุมภ์ = 1,4,7,10): navamsa แรกเริ่มที่ราศี 9 จากตัวเอง
    - Dual signs (เมถุน/กันย์/ธนู/มีน = 2,5,8,11): navamsa แรกเริ่มที่ราศี 5 จากตัวเอง

Vargottama: ดาวที่อยู่ในราศีเดียวกันทั้ง rashi และ navamsa → กำลังแข็ง 3 เท่า
Uttamanamsa (วรโคตรนวางค์): movable ลูก 1, fixed ลูก 5, dual ลูก 9 → กำลังพิเศษสูงสุด

ตำราอ้างอิง:
    - อ.สิงห์โต สุริยาอาลักษณ์ — นวางค์จักรและการพยากรณ์
    - อ.บุศรินทร์ ปัทมาคม — ดวงนวางค์จักรประกอบดวงชาตา
    - Parashara Hora Shastra
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


ARCMIN_PER_NAVAMSA = 200      # 3°20'
NAVAMSA_PER_RASI = 9
TOTAL_NAVAMSA = 108


# ============================================================
# ประเภทนวางค์ (เทวะ / นะระ / รากษส)
# nav_index 1-9 → 3 กลุ่ม
# ============================================================
# ลูกนวางค์ 1,4,7 → เทวะ; 2,5,8 → นะระ; 3,6,9 → รากษส
NAVAMSA_TYPE_MAP: Dict[int, str] = {
    1: "เทวะ", 4: "เทวะ", 7: "เทวะ",
    2: "นะระ", 5: "นะระ", 8: "นะระ",
    3: "รากษส", 6: "รากษส", 9: "รากษส",
}

NAVAMSA_TYPE_INFO: Dict[str, dict] = {
    "เทวะ": {
        "icon": "✨",
        "meaning": "เทพเจ้า — ทรัพย์สมบัติ ความเมตตา อำนาจ ความมั่งคั่ง",
        "lagna_meaning": "ใจบุญ เคร่งศาสนา มีทรัพย์สินและอำนาจ",
        "color_class": "navamsa-type-deva",
    },
    "นะระ": {
        "icon": "🧑",
        "meaning": "มนุษย์ — ใจดี มีชื่อเสียง อยู่ดีกินดี มีความสุข",
        "lagna_meaning": "ใจดี มีชื่อเสียงดี อยู่ดีกินดีสุขสบาย",
        "color_class": "navamsa-type-nara",
    },
    "รากษส": {
        "icon": "👹",
        "meaning": "ยักษ์/ปีศาจ — ลักษณะโหดร้าย ความรุนแรง เห็นแก่ตัว",
        "lagna_meaning": "นิสัยแข็งกร้าว เอาตัวรอดเก่ง อาจมีชื่อเสียงทางลบ",
        "color_class": "navamsa-type-rakshas",
    },
}


# ============================================================
# Uttamanamsa (วรโคตรนวางค์) — กำลังพิเศษสูงสุด
# movable ลูก 1, fixed ลูก 5, dual ลูก 9
# ============================================================
# rashi type: movable(0)=เมษ/กรกฎ/ตุล/มกร, fixed(1)=พฤษภ/สิงห์/พิจิก/กุมภ์, dual(2)=เมถุน/กันย์/ธนู/มีน
RASI_TYPE_MAP: Dict[int, int] = {
    0: 0, 3: 0, 6: 0, 9: 0,    # movable (จร)
    1: 1, 4: 1, 7: 1, 10: 1,   # fixed (สถิร)
    2: 2, 5: 2, 8: 2, 11: 2,   # dual (ทวิภาวะ)
}
UTTAMANAMSA_INDEX: Dict[int, int] = {0: 1, 1: 5, 2: 9}  # rasi_type → nav_index


# ============================================================
# การตีความรวม (rashi dignity + navamsa dignity)
# ============================================================
COMBINED_MEANING: Dict[Tuple[str, str], dict] = {
    # rashi_good × nav_good → ดีทั้งคู่ = แรงสุด
    ("strong", "strong"): {
        "label": "ยอดเยี่ยม",
        "icon": "⭐",
        "color_class": "nav-combined-excellent",
        "meaning": "ดาวแข็งแกร่งทั้งในราศีจักรและนวางค์จักร — ให้คุณเต็มที่ ไร้อุปสรรค",
        "tone": "good",
    },
    ("strong", "neutral"): {
        "label": "ดีมาก",
        "icon": "✨",
        "color_class": "nav-combined-good",
        "meaning": "ดาวแข็งในราศีจักร ปานกลางในนวางค์ — ให้คุณดี แต่ผลอาจไม่สมบูรณ์แบบ 100%",
        "tone": "good",
    },
    ("strong", "weak"): {
        "label": "ท่าดีทีเหลว",
        "icon": "⚠️",
        "color_class": "nav-combined-mixed-bad",
        "meaning": "ดาวได้ตำแหน่งดีในราศีจักร (ดูดีภายนอก) แต่นวางค์อ่อนกำลัง — "
                   "ผลดีที่คาดหวังจะไม่สมบูรณ์ อาจมีอุปสรรคเบื้องหลัง หรือให้ผลน้อยกว่าที่ควร",
        "tone": "warning",
    },
    ("neutral", "strong"): {
        "label": "ดีในนวางค์",
        "icon": "✦",
        "color_class": "nav-combined-nav-good",
        "meaning": "ดาวปานกลางในราศีจักร แต่แข็งในนวางค์ — จิตใจและโชคชะตาภายในดีกว่าที่ปรากฏ",
        "tone": "good",
    },
    ("neutral", "neutral"): {
        "label": "ปานกลาง",
        "icon": "○",
        "color_class": "nav-combined-neutral",
        "meaning": "ดาวปานกลางทั้งสองระบบ — ให้คุณโทษพอกัน ผลขึ้นอยู่กับบริบทภพ",
        "tone": "neutral",
    },
    ("neutral", "weak"): {
        "label": "ค่อนข้างอ่อน",
        "icon": "▾",
        "color_class": "nav-combined-weak",
        "meaning": "ดาวปานกลางในราศีจักร อ่อนในนวางค์ — ต้องใช้ความพยายามมากกว่าคนอื่น",
        "tone": "warning",
    },
    ("weak", "strong"): {
        "label": "ยิ่งตกยิ่งดี",
        "icon": "🔄",
        "color_class": "nav-combined-mixed-good",
        "meaning": "ดาวอ่อนในราศีจักร (ดูไม่ดีภายนอก) แต่แข็งในนวางค์ — "
                   "ผลร้ายจากดวงเดิมจะบรรเทาลง เจ้าชาตาสามารถฟื้นฟูและก้าวหน้าได้ในที่สุด",
        "tone": "good",
    },
    ("weak", "neutral"): {
        "label": "อ่อนแต่ทนได้",
        "icon": "▾",
        "color_class": "nav-combined-weak",
        "meaning": "ดาวอ่อนในราศีจักร นวางค์ปานกลาง — ผลร้ายเบาลงบ้าง ต้องพยายามมาก",
        "tone": "warning",
    },
    ("weak", "weak"): {
        "label": "อ่อนแรงมาก",
        "icon": "✖",
        "color_class": "nav-combined-very-weak",
        "meaning": "ดาวอ่อนกำลังทั้งราศีจักรและนวางค์จักร — เรื่องที่ดาวนี้ดูแลจะมีอุปสรรคหนัก "
                   "ต้องระวังเป็นพิเศษ ดาวนี้แทบไม่ให้คุณ",
        "tone": "heavy",
    },
}

# ประเกษตร — สถานะพิเศษ (override combined_meaning)
PRAKSHTRA_INFO = {
    "label": "ประเกษตร",
    "icon": "⚔️",
    "color_class": "nav-combined-prakshtra",
    "meaning": "ดาวอยู่ราศีเกษตรในราศีจักร แต่นวางค์ลงราศีศัตรู — "
               "มีความสามารถแต่ต้องฝ่าฟันอุปสรรคก่อนเสมอ ถูกขัดขวาง กลั่นแกล้ง "
               "แต่มีไหวพริบและเอาตัวรอดได้ดี (ท่าดีทีเหลวในระดับเกษตร)",
    "tone": "warning",
}

# Vargottama — สถานะพิเศษ (เพิ่มความแรง 3 เท่า)
VARGOTTAMA_INFO = {
    "label": "วรโคตรนวางค์",
    "icon": "⭐⭐",
    "color_class": "nav-combined-vargottama",
    "meaning": "ดาวอยู่ราศีเดียวกันทั้งราศีจักรและนวางค์จักร — กำลังแข็งกว่าปกติ 3 เท่า "
               "เป็นตำแหน่งมงคลที่สุด ส่งผลดีอย่างชัดเจนในเรื่องที่ดาวนี้ดูแล",
    "tone": "good",
}

# Uttamanamsa — สถานะพิเศษ (กำลังสูงสุด)
UTTAMANAMSA_INFO = {
    "label": "อุตตมางศ์",
    "icon": "👑",
    "color_class": "nav-combined-uttama",
    "meaning": "ดาวตกในนวางค์ลูกพิเศษ (จรราศีลูก 1, สถิรราศีลูก 5, ทวิภาวะราศีลูก 9) "
               "ซึ่งเจ้านวางค์เป็นดาวเดียวกับเกษตรราศีนั้น — กำลังพิเศษสูงสุด เสมือนได้อุจน์คู่",
    "tone": "good",
}


# ============================================================
# ไส้ชะตา (Deep interpretation) — navamsa × เจ้าเรือนภพ
# ============================================================
# หลักการ: ราศีจักร = เปลือกนอก/รูปลักษณ์/ช่วงต้นชีวิต
#          นวางค์จักร = ไส้ใน/แก่นแท้/ดอกผล/บั้นปลายชีวิต
# ดาวเป็น "เจ้าเรือน" ของภพใด = ดูแลเรื่องนั้นในชีวิต
# กำลังนวางค์ของดาว → บอก "ไส้ใน" ของเรื่องที่ดาวนั้นดูแล
#
# ตำราอ้างอิงหลักการ D9:
#   - Parashara Hora Shastra (นวางค์ = ผลของต้นไม้, ราศี = ต้นไม้)
#   - อ.สิงห์โต สุริยาอาลักษณ์ / อ.บุศรินทร์ ปัทมาคม

# เรื่องที่แต่ละภพดูแล (ฉบับสั้น สำหรับเล่าไส้ชะตา)
BHAVA_DOMAIN_SHORT: Dict[int, str] = {
    1:  "ตัวตน บุคลิก และสุขภาพภาพรวม",
    2:  "การเงิน ทรัพย์สิน และคำพูด",
    3:  "พี่น้อง การสื่อสาร และความกล้า",
    4:  "ครอบครัว บ้าน และความสุขทางใจ",
    5:  "บุตร ความรัก และสติปัญญา",
    6:  "สุขภาพ หนี้สิน ศัตรู และงานหนัก",
    7:  "คู่ครอง หุ้นส่วน และการร่วมมือ",
    8:  "การเปลี่ยนแปลงใหญ่ มรดก และเรื่องลับ",
    9:  "บุญวาสนา โชค การศึกษา และการเดินทางไกล",
    10: "การงาน อาชีพ และชื่อเสียง",
    11: "ลาภยศ มิตรสหาย และรายได้พิเศษ",
    12: "การปล่อยวาง ต่างแดน และสิ่งซ่อนเร้น",
}

# โดเมนตามธรรมชาติของดาว (ใช้กับดาวที่ไม่ครองภพ — เกตุ/มฤตยู)
PLANET_NATURAL_DOMAIN: Dict[str, str] = {
    "อาทิตย์":  "อำนาจ เกียรติยศ บิดา และตัวตน",
    "จันทร์":   "จิตใจ อารมณ์ มารดา และความนิยม",
    "อังคาร":   "พลังขับเคลื่อน ความกล้า และการต่อสู้",
    "พุธ":      "สติปัญญา การสื่อสาร และการค้า",
    "พฤหัสบดี": "ปัญญา คุณธรรม โชควาสนา และครูบาอาจารย์",
    "ศุกร์":    "ความรัก ความงาม ศิลปะ และความสุข",
    "เสาร์":    "ความอดทน วินัย งานหนัก และกรรมเก่า",
    "ราหู":     "ความทะเยอทะยาน สิ่งแปลกใหม่ และต่างแดน",
    "เกตุ":     "การปล่อยวาง จิตวิญญาณ และปัญญาหยั่งรู้",
    "มฤตยู":    "การเปลี่ยนแปลงฉับพลัน นวัตกรรม และอิสระ",
}

BHAVA_NAMES_TH = [
    "ตนุ", "กดุมภะ", "สหัชชะ", "พันธุ", "ปุตตะ", "อริ",
    "ปัตนิ", "มรณะ", "ศุภะ", "กัมมะ", "ลาภะ", "วินาส",
]

# คำเล่าไส้ชะตา ตาม (rashi_strength, nav_strength)
# {areas} = เรื่องที่ดาวดูแล
_DEEP_NARRATIVE: Dict[Tuple[str, str], str] = {
    ("weak", "strong"):
        "ภายนอก{areas}อาจดูสะดุด เริ่มต้นช้า หรือไม่โดดเด่นในช่วงต้น "
        "แต่ไส้ในแข็งแรงกว่าที่ตาเห็นมาก — บั้นปลายเรื่องเหล่านี้จะตั้งตัวได้มั่นคง "
        "และงอกงามเกินคาด ยิ่งผ่านเวลายิ่งดี",
    ("strong", "weak"):
        "ภายนอก{areas}ดูราบรื่นน่าพอใจ แต่ไส้ในยังกลวง — "
        "ระวังว่าผลที่ได้มาง่ายจะไม่ยั่งยืน ควรลงรากให้ลึกและไม่ประมาท "
        "อย่าวางใจกับความสำเร็จในช่วงต้น",
    ("strong", "strong"):
        "{areas}แข็งทั้งเปลือกนอกและไส้ใน — เป็นจุดแข็งแท้จริงที่ทั้งดูดีและให้ผลจริง "
        "พึ่งพาเรื่องเหล่านี้เป็นเสาหลักของชีวิตได้เต็มที่",
    ("weak", "weak"):
        "{areas}ยังอ่อนทั้งภายนอกและไส้ใน — เรื่องเหล่านี้ต้องใช้ความเพียรและเวลา "
        "มากเป็นพิเศษ อย่าเพิ่งคาดหวังผลเร็ว ค่อยๆ สะสมรากฐานทีละน้อย",
    ("neutral", "strong"):
        "ภายนอก{areas}ดูธรรมดา แต่ไส้ในดีกว่าที่ปรากฏ — "
        "มีโชคหนุนอยู่ลึกๆ จะค่อยๆ เผยผลดีเมื่อถึงเวลา",
    ("strong", "neutral"):
        "{areas}มีพื้นฐานภายนอกที่ดี ไส้ในระดับกลาง — ให้ผลดีพอควร "
        "แต่จะสมบูรณ์ยิ่งขึ้นถ้าหมั่นดูแลแก่นของเรื่องไม่ให้กลวง",
    ("neutral", "weak"):
        "ภายนอก{areas}พอไปได้ แต่ไส้ในค่อนข้างอ่อน — "
        "ต้องประคองและใส่ใจมากกว่าคนทั่วไป กันไม่ให้เรื่องเหล่านี้ทรุดในระยะยาว",
    ("weak", "neutral"):
        "ภายนอก{areas}อาจเริ่มต้นลำบาก แต่ไส้ในพอมีทุนเดิม — "
        "ถ้าอดทนผ่านช่วงต้นไปได้ เรื่องเหล่านี้จะค่อยๆ ทรงตัวดีขึ้น",
    ("neutral", "neutral"):
        "{areas}อยู่ในเกณฑ์กลางทั้งเปลือกและไส้ใน — "
        "ผลขึ้นอยู่กับความตั้งใจและจังหวะชีวิตเป็นหลัก ไม่มีพรหรือกรรมพิเศษกำกับ",
}


# ============================================================
# Dataclasses
# ============================================================

@dataclass(frozen=True)
class NavamsaPosition:
    """ตำแหน่งในนวางค์จักร"""
    nav_rashi: int          # 0-11 (ราศีในวงนวางค์)
    nav_index: int          # 1-9 (ลำดับนวางค์ในราศีเดิม)
    is_vargottama: bool     # True ถ้า nav_rashi == rashi เดิม
    is_uttamanamsa: bool = False  # True ถ้าเป็นวรโคตรนวางค์
    navamsa_type: str = "นะระ"   # เทวะ / นะระ / รากษส


@dataclass
class NavamsaAnalysis:
    """ผลการวิเคราะห์นวางค์รายดาว"""
    planet: str
    rashi: int
    rashi_name: str
    nav_rashi: int
    nav_rashi_name: str
    nav_index: int
    navamsa_type: str            # เทวะ / นะระ / รากษส
    navamsa_type_icon: str
    is_vargottama: bool
    is_uttamanamsa: bool
    is_prakshtra: bool
    rashi_dignity: str           # รหัส dignity (อุจน์/เกษตร/ประ/นิจ/...)
    rashi_dignity_label: str
    rashi_strength: str          # "strong" / "neutral" / "weak"
    nav_dignity: str
    nav_dignity_label: str
    nav_strength: str
    combined_label: str          # ป้ายสรุป (ยอดเยี่ยม/ท่าดีทีเหลว/...)
    combined_icon: str
    combined_color_class: str
    combined_meaning: str
    combined_tone: str           # good / warning / heavy / neutral
    special_note: str = ""       # หมายเหตุพิเศษ (วรโคตร/อุตตมางศ์/ประเกษตร)
    # ===== ไส้ชะตา (deep interpretation) =====
    ruled_bhavas: List[int] = field(default_factory=list)  # ภพที่ดาวเป็นเจ้าเรือน
    governs: str = ""            # "เจ้าเรือนภพ3 (สหัชชะ) — ดูแล..."
    deep_meaning: str = ""       # คำทำนายไส้ชะตาเชิงลึก


@dataclass
class NavamsaChartAnalysis:
    """ผลการวิเคราะห์ดวงนวางค์จักรทั้งดวง"""
    lagna_nav_rashi: int
    lagna_nav_rashi_name: str
    lagna_navamsa_type: str
    lagna_navamsa_type_icon: str
    lagna_navamsa_meaning: str
    lagna_is_vargottama: bool
    lagna_is_uttamanamsa: bool
    planets: List[NavamsaAnalysis] = field(default_factory=list)
    planets_by_nav_rashi: Dict[int, List[str]] = field(default_factory=dict)
    vargottama_planets: List[str] = field(default_factory=list)
    uttamanamsa_planets: List[str] = field(default_factory=list)
    prakshtra_planets: List[str] = field(default_factory=list)
    strong_in_nav: List[str] = field(default_factory=list)   # ดาวที่แข็งในนวางค์
    weak_in_nav: List[str] = field(default_factory=list)     # ดาวที่อ่อนในนวางค์
    reversal_good: List[str] = field(default_factory=list)   # อ่อนราศี+แข็งนวางค์ (ยิ่งตกยิ่งดี)
    reversal_bad: List[str] = field(default_factory=list)    # แข็งรา ศี+อ่อนนวางค์ (ท่าดีทีเหลว)


# ============================================================
# Core functions
# ============================================================

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
    nav_index = nav_index_0 + 1  # 1-9

    is_varg = (nav_rashi == rashi)

    rasi_type = RASI_TYPE_MAP[rashi]
    is_uttama = (nav_index == UTTAMANAMSA_INDEX[rasi_type])

    nav_type = NAVAMSA_TYPE_MAP.get(nav_index, "นะระ")

    return NavamsaPosition(
        nav_rashi=nav_rashi,
        nav_index=nav_index,
        is_vargottama=is_varg,
        is_uttamanamsa=is_uttama,
        navamsa_type=nav_type,
    )


def _dignity_to_strength(dignity: str) -> str:
    """แปลง dignity code → "strong" / "neutral" / "weak"

    หมายเหตุ: "อุจจาวิลาส" = ราศีนิจ (debilitation rashi) ของดาว 7 ดวงหลัก
    ในระบบไทย priority check ทำให้ดาวในราศีนิจได้ "อุจจาวิลาส" ก่อน "นิจ"
    → จึง map อุจจาวิลาส และ ศัตรู เป็น weak เพื่อให้สอดคล้องกับตำราครู
    """
    STRONG = {"อุจน์", "มหาจักร", "จุลจักร", "ราชาโชค", "เทวีโชค", "เกษตร"}
    WEAK = {"นิจ", "ประ", "ศัตรู", "อุจจาวิลาส"}
    if dignity in STRONG:
        return "strong"
    if dignity in WEAK:
        return "weak"
    return "neutral"


def is_prakshtra(planet: str, rashi: int, nav_rashi: int) -> bool:
    """ตรวจสอบว่าดาวอยู่ในสถานะ "ประเกษตร" หรือไม่

    ประเกษตร = ดาวอยู่ราศีเกษตร (swakshetra) ในราศีจักร
               แต่นวางค์ลงในราศีศัตรู/ประ (ไม่ใช่เกษตร/อุจน์)

    Args:
        planet: ชื่อดาว
        rashi: ราศีในราศีจักร (0-11)
        nav_rashi: ราศีในนวางค์จักร (0-11)
    """
    from .dignities import SWAKSHETRA, EXALTATION_RASI, PLANET_RELATIONS
    # ตรวจว่าอยู่เกษตรในราศีจักรก่อน
    sw = SWAKSHETRA.get(planet, set())
    if rashi not in sw:
        return False
    # ตรวจ nav_rashi — ถ้าเป็นเกษตร/อุจน์ ของดาว ก็ไม่ใช่ประเกษตร
    if nav_rashi in sw:
        return False
    if nav_rashi == EXALTATION_RASI.get(planet, -1):
        return False
    # ถ้า nav_rashi เป็นราศีศัตรู = ประเกษตร
    rels = PLANET_RELATIONS.get(planet, {})
    enemies = rels.get("enemies", set())
    # หาดาวเจ้านวางค์ราศีนั้น แล้วตรวจว่าเป็นศัตรูไหม
    from .planets import RASI_LORD
    nav_lord = RASI_LORD[nav_rashi]
    if nav_lord in enemies:
        return True
    # เพิ่มเติม: ถ้า nav_rashi ตรงกับ debilitation rashi ก็นับด้วย
    from .dignities import DEBILITATION_RASI
    if nav_rashi == DEBILITATION_RASI.get(planet, -1):
        return True
    return False


def analyze_planet_navamsa(
    planet: str,
    rashi: int,
    degree: int,
    arcmin: int,
    rashi_dignity: str,
    rashi_dignity_label: str,
) -> NavamsaAnalysis:
    """วิเคราะห์นวางค์ของดาว 1 ดวง

    Args:
        planet: ชื่อดาว
        rashi: ราศีจักร (0-11)
        degree, arcmin: ตำแหน่งในราศี
        rashi_dignity: dignity code ในราศีจักร
        rashi_dignity_label: ป้ายภาษาไทย

    Returns:
        NavamsaAnalysis
    """
    from .planets import RASI_NAMES_TH
    from .dignities import compute_dignity

    nv = compute_navamsa(rashi, degree, arcmin)
    nav_di = compute_dignity(planet, nv.nav_rashi)

    rashi_str = _dignity_to_strength(rashi_dignity)
    nav_str = _dignity_to_strength(nav_di.dignity)

    # ตรวจสถานะพิเศษ
    prakshtra = is_prakshtra(planet, rashi, nv.nav_rashi)
    vargottama = nv.is_vargottama
    uttama = nv.is_uttamanamsa

    # เลือก combined meaning
    if vargottama:
        cm = VARGOTTAMA_INFO.copy()
        special = "วรโคตรนวางค์ — ดาวอยู่ราศีเดียวกันทั้งสองวง"
    elif uttama:
        cm = UTTAMANAMSA_INFO.copy()
        special = "อุตตมางศ์ — นวางค์ลูกพิเศษที่เจ้านวางค์ตรงกับเกษตรราศีเดิม"
    elif prakshtra:
        cm = PRAKSHTRA_INFO.copy()
        special = "ประเกษตร — อยู่เกษตรราศีจักรแต่นวางค์ตกราศีศัตรู"
    else:
        key = (rashi_str, nav_str)
        cm = COMBINED_MEANING.get(key, COMBINED_MEANING[("neutral", "neutral")]).copy()
        special = ""

    nav_type_info = NAVAMSA_TYPE_INFO.get(nv.navamsa_type, NAVAMSA_TYPE_INFO["นะระ"])

    return NavamsaAnalysis(
        planet=planet,
        rashi=rashi,
        rashi_name=RASI_NAMES_TH[rashi],
        nav_rashi=nv.nav_rashi,
        nav_rashi_name=RASI_NAMES_TH[nv.nav_rashi],
        nav_index=nv.nav_index,
        navamsa_type=nv.navamsa_type,
        navamsa_type_icon=nav_type_info["icon"],
        is_vargottama=vargottama,
        is_uttamanamsa=uttama,
        is_prakshtra=prakshtra,
        rashi_dignity=rashi_dignity,
        rashi_dignity_label=rashi_dignity_label,
        rashi_strength=rashi_str,
        nav_dignity=nav_di.dignity,
        nav_dignity_label=nav_di.label,
        nav_strength=nav_str,
        combined_label=cm["label"],
        combined_icon=cm["icon"],
        combined_color_class=cm["color_class"],
        combined_meaning=cm["meaning"],
        combined_tone=cm["tone"],
        special_note=special,
    )


def build_deep_meaning(analysis: NavamsaAnalysis, ruled_bhavas: List[int]) -> Tuple[str, str]:
    """สร้างคำทำนาย "ไส้ชะตา" — navamsa dignity × เรื่องที่ดาวดูแล (เจ้าเรือนภพ)

    หลักการ: ดาวเป็นเจ้าเรือนภพใด = ดูแลเรื่องนั้น;
    กำลังนวางค์ = ไส้ใน/แก่นแท้ของเรื่องนั้น (ตรงข้าม/เสริมกับเปลือกนอก=ราศีจักร)

    Returns:
        (governs, deep_meaning)
    """
    # 1) สร้างข้อความ "ดาวนี้ดูแลเรื่องอะไร"
    if ruled_bhavas:
        bh_labels = [f"ภพ{b} ({BHAVA_NAMES_TH[b - 1]})" for b in ruled_bhavas]
        domains = [BHAVA_DOMAIN_SHORT[b] for b in ruled_bhavas]
        governs = (
            f"เจ้าเรือน{' และ '.join(bh_labels)} — ดูแลเรื่อง"
            f"{' กับ '.join(domains)}"
        )
        # areas ที่ใช้ในประโยคไส้ชะตา (รวมเรื่องที่ดูแล)
        areas = "เรื่อง" + " กับ ".join(domains)
    else:
        # ดาวลอย ไม่ครองภพ (เกตุ/มฤตยู) → ใช้โดเมนธรรมชาติ
        dom = PLANET_NATURAL_DOMAIN.get(analysis.planet, "")
        governs = f"ดาวลอย (ไม่ได้ครองภพ) — มีอิทธิพลด้าน{dom}"
        areas = f"ด้าน{dom}"

    # 2) เลือกบทไส้ชะตา: สถานะพิเศษ override ก่อน
    if analysis.is_vargottama:
        deep = (
            f"{areas}คือแกนชีวิตที่มั่นคงที่สุดของคุณ — เปลือกนอกและไส้ในไปทางเดียวกัน "
            f"(วรโคตม กำลังแรง 3 เท่า) เรื่องเหล่านี้เป็นจุดยืนที่พึ่งพาได้จริงตลอดชีวิต "
            f"ยิ่งนานยิ่งหนักแน่น"
        )
    elif analysis.is_uttamanamsa:
        deep = (
            f"ไส้ในของ{areas}แข็งแกร่งระดับสูงสุด (อุตตมางค์) — แม้ภายนอกจะเป็นอย่างไร "
            f"แก่นแท้ของเรื่องนี้จะค่อยๆ เปล่งคุณค่าและให้ผลงดงามในบั้นปลาย"
        )
    elif analysis.is_prakshtra:
        deep = (
            f"{areas}ดูมีพื้นฐานดี (เกษตรในราศีจักร) แต่ไส้ในกลับเจอแรงต้าน "
            f"(นวางค์ตกราศีศัตรู) — คุณมีของจริง แต่ต้องฝ่าด่านคนหรือสถานการณ์ที่คอยขัดก่อนเสมอ "
            f"ความสำเร็จมาช้าแต่พิสูจน์ฝีมือได้"
        )
    else:
        tmpl = _DEEP_NARRATIVE.get(
            (analysis.rashi_strength, analysis.nav_strength),
            _DEEP_NARRATIVE[("neutral", "neutral")],
        )
        deep = tmpl.format(areas=areas)

    # 3) ปิดท้ายด้วยตำแหน่งนวางค์จริง (ให้เห็นที่มา)
    deep += (
        f" (ในนวางค์ดาวตก{analysis.nav_rashi_name} ได้ตำแหน่ง{analysis.nav_dignity_label})"
    )
    return governs, deep


def analyze_chart_navamsa(chart) -> NavamsaChartAnalysis:
    """วิเคราะห์นวางค์จักรของดวงชาตาทั้งดวง

    Returns:
        NavamsaChartAnalysis ครบทุกดาว + สรุปลัคนา
    """
    from .planets import RASI_NAMES_TH, PLANET_ORDER
    from .dignities import compute_dignity

    asc_z = chart.ascendant.zodiac
    asc_nv = compute_navamsa(asc_z.rasi, asc_z.degree, asc_z.arcminute)
    asc_type_info = NAVAMSA_TYPE_INFO.get(asc_nv.navamsa_type, NAVAMSA_TYPE_INFO["นะระ"])

    result = NavamsaChartAnalysis(
        lagna_nav_rashi=asc_nv.nav_rashi,
        lagna_nav_rashi_name=RASI_NAMES_TH[asc_nv.nav_rashi],
        lagna_navamsa_type=asc_nv.navamsa_type,
        lagna_navamsa_type_icon=asc_type_info["icon"],
        lagna_navamsa_meaning=asc_type_info["lagna_meaning"],
        lagna_is_vargottama=asc_nv.is_vargottama,
        lagna_is_uttamanamsa=asc_nv.is_uttamanamsa,
    )

    planets_by_nav_rashi: Dict[int, List[str]] = {i: [] for i in range(12)}

    # ภพที่แต่ละดาวเป็นเจ้าเรือน (inverse ของ chart.house_lords)
    ruled_map: Dict[str, List[int]] = {}
    for bhava, lord in getattr(chart, "house_lords", {}).items():
        ruled_map.setdefault(lord, []).append(bhava)

    for pname in PLANET_ORDER:
        if pname not in chart.planets:
            continue
        p = chart.planets[pname]
        z = p.zodiac
        ndi = compute_dignity(pname, z.rasi)
        analysis = analyze_planet_navamsa(
            pname, z.rasi, z.degree, z.arcminute,
            ndi.dignity, ndi.label,
        )
        # ไส้ชะตา: navamsa × เจ้าเรือนภพ
        ruled = sorted(ruled_map.get(pname, []))
        analysis.ruled_bhavas = ruled
        analysis.governs, analysis.deep_meaning = build_deep_meaning(analysis, ruled)
        result.planets.append(analysis)
        planets_by_nav_rashi[analysis.nav_rashi].append(pname)

        if analysis.is_vargottama:
            result.vargottama_planets.append(pname)
        if analysis.is_uttamanamsa:
            result.uttamanamsa_planets.append(pname)
        if analysis.is_prakshtra:
            result.prakshtra_planets.append(pname)
        if analysis.nav_strength == "strong":
            result.strong_in_nav.append(pname)
        if analysis.nav_strength == "weak":
            result.weak_in_nav.append(pname)
        if analysis.combined_tone == "good" and analysis.rashi_strength == "weak":
            result.reversal_good.append(pname)
        if analysis.combined_tone == "warning" and analysis.rashi_strength == "strong":
            result.reversal_bad.append(pname)

    result.planets_by_nav_rashi = planets_by_nav_rashi
    return result


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
