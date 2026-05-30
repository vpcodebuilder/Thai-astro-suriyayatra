"""พยากรณ์โหรทายหนู — แบบโหราศาสตร์ไทย (significator + bhava interpretation)

หลักการ:
1. ตีคำถาม → ดาว significator (ดาวที่เกี่ยวข้องกับเรื่องนั้น)
2. ดูดาว significator ในผัง: อยู่ราศีอะไร, ภพอะไร, มีดาวอะไรครองร่วม
3. ดูเจ้าเรือน (ดาวเกษตรของราศีที่ดาวอยู่)
4. สร้างคำทำนายตามตำแหน่ง + ความสัมพันธ์

ตัวอย่าง: "ของรักหาย"
   - significator = ศุกร์ (ดาว 6 = ของรัก/ของมีค่า)
   - ถ้าศุกร์อยู่พันธุ (ภพ 4) → ของอยู่ในบ้าน
   - ถ้าศุกร์อยู่เกษตร (พฤษภ/ตุล) → ของยังอยู่กับเจ้าของ ไม่หาย
"""

from __future__ import annotations

from dataclasses import dataclass

from thai_astro.horathaynu.core.bhava import BHAVA_NAMES_TH
from thai_astro.horathaynu.core.caster import Chart
from thai_astro.horathaynu.data.lordship import lord_of
from thai_astro.horathaynu.data.planet_meanings import PLANET_NAME_TH


# ===== ความหมายเชิงพยากรณ์ของดาว (สำหรับเป็น significator) =====
PLANET_SIGNIFICATIONS = {
    "sun":     ["ผู้ใหญ่", "บิดา", "อำนาจ", "ราชการ", "สามี (ของผู้หญิง)", "ผู้นำ"],
    "moon":    ["มารดา", "ผู้หญิง", "เด็ก", "น้ำ", "อารมณ์", "ของเหลว"],
    "mars":    ["พี่น้องชาย", "นักรบ", "อาวุธ", "การต่อสู้", "ไฟ", "เหล็ก", "เลือด"],
    "mercury": ["การพูด", "การค้า", "นักเรียน", "เด็ก", "หนังสือ", "ของสะสม", "สมุด"],
    "jupiter": ["ครู", "ที่ปรึกษา", "พระ", "ลูก", "บุญ", "ความรู้", "ทอง"],
    "venus":   ["คู่รัก", "ของรัก", "หญิงสาว", "ภรรยา", "ของมีค่า", "ดอกไม้", "เครื่องประดับ", "สิ่งสวยงาม"],
    "saturn":  ["คนแก่", "ผู้สูงวัย", "งานหนัก", "ของเก่า", "อุปสรรค", "ที่ดิน", "บ้าน (โครงสร้าง)"],
    "rahu":    ["ของลึกลับ", "ของแปลก", "ของหาย", "ลาภลอย", "เรื่องคาดไม่ถึง"],
    "ketu":    ["การพลัดพราก", "เรื่องเก่า", "ของเก่า", "ความหลุดพ้น"],
    "uranus":  ["เทคโนโลยี", "เรื่องใหม่", "ความรวดเร็ว", "พลังงาน"],
}

# ===== ภพ → สถานที่/บุคคล (สำหรับ "ของหายอยู่ไหน") =====
BHAVA_LOCATIONS = {
    1:  "ที่ตัวเจ้าชะตา (อยู่กับคุณ/ในร่างกาย/ติดกายอยู่)",
    2:  "ในที่เก็บทรัพย์/กระเป๋า/ตู้เก็บของ/ใกล้ที่กินที่ใช้",
    3:  "ที่พี่น้อง เพื่อน หรือทางที่ใกล้บ้าน (เพื่อนบ้าน)",
    4:  "ในบ้าน ที่อยู่อาศัย ใกล้บิดามารดา หรือใต้ของ",
    5:  "ที่ลูก คนรัก หรือที่นั่งเล่น/เรียนหนังสือ",
    6:  "ที่ลูกน้อง บริวาร ศัตรู หรือถูกขโมย/ของอยู่กับผู้ที่ไม่เป็นมิตร",
    7:  "ที่คู่ครอง คู่หุ้นส่วน หรือคนที่ทำธุรกิจด้วย",
    8:  "ที่ลับ ของอาจสูญหายโดยไม่กลับมา หรือถูกเก็บซ่อนไว้",
    9:  "ที่ผู้ใหญ่ ครู หรือไกลบ้าน (เดินทางพาไป)",
    10: "ในที่ทำงาน หรือกับเจ้านาย",
    11: "ที่มิตรสหาย ของจะกลับมาในรูปลาภ",
    12: "ที่ลับ ในที่มืด ใต้ของ หรือนอกบ้าน — มีโอกาสสูญหายถาวร",
}

# ===== โทนของภพ — สำหรับสรุปดี/ร้าย =====
BHAVA_TONE = {
    1: "good", 2: "good", 3: "neutral", 4: "good",
    5: "good", 6: "warning", 7: "neutral", 8: "warning",
    9: "good", 10: "good", 11: "good", 12: "warning",
}

# ===== Keyword → significator planet + question category =====
# category ใช้เลือกรูปแบบคำทำนาย
QUESTION_KEYWORDS = [
    # (keywords list, significator_planet, category)
    (["ของรัก", "ของหาย", "ของรักหาย", "เครื่องประดับ", "ของมีค่า", "ทอง"],
        "venus", "lost_item"),
    (["รัก", "ความรัก", "แฟน", "คนรัก", "คู่รัก", "ผู้หญิง", "ภรรยา"],
        "venus", "love"),
    (["สามี", "ผู้ชาย", "ผู้ใหญ่", "บิดา", "เจ้านาย", "ราชการ"],
        "sun", "person"),
    (["มารดา", "แม่"],
        "moon", "person"),
    (["บุตร", "ลูก", "ทายาท"],
        "jupiter", "person"),
    (["พี่น้อง", "น้องชาย", "พี่ชาย"],
        "mars", "person"),
    (["เพื่อน", "มิตร"],
        "mercury", "person"),
    (["ครู", "อาจารย์", "ที่ปรึกษา", "พระ"],
        "jupiter", "person"),
    (["เงิน", "ทรัพย์", "การเงิน", "ลาภ", "รายได้"],
        "jupiter", "wealth"),  # พฤหัสเป็น indicator ของลาภ
    (["งาน", "การงาน", "อาชีพ", "ตำแหน่ง", "เลื่อนขั้น"],
        "sun", "career"),
    (["สุขภาพ", "ป่วย", "หาย", "หมอ", "โรค"],
        "sun", "health"),  # อาทิตย์ = ชีวิต/พลัง
    (["บ้าน", "ที่อยู่", "ที่ดิน", "อสังหา"],
        "saturn", "property"),
    (["เดินทาง", "ไปไหน", "ออกจากบ้าน"],
        "mercury", "travel"),
    (["ศึกษา", "เรียน", "สอบ", "หนังสือ"],
        "mercury", "study"),
    (["ศัตรู", "คดี", "ความ", "ฟ้องร้อง", "ทะเลาะ", "เบาะแว้ง", "พิพาท"],
        "mars", "enemy"),
    (["โชค", "โชคลาภ", "ลาภลอย", "ดวง"],
        "jupiter", "wealth"),
    (["เหตุการณ์", "จะเกิด", "อนาคต", "ระยะสั้น", "สงสัย"],
        "lagna", "current_event"),
]


@dataclass
class ProphecyResult:
    significator: str
    significator_th: str
    category: str
    sig_rashi_index: int
    sig_rashi_name: str
    sig_house: int
    sig_bhava: str
    co_planets: list[str]    # ดาวอื่นที่อยู่ราศีเดียวกัน
    sign_lord_key: str       # ดาวเกษตรของราศีที่ดาวสำคัญอยู่
    sign_lord_th: str
    is_own_sign: bool        # ดาวสำคัญอยู่เกษตรของตน
    tone: str                # "good" / "warning" / "neutral"
    text: str                # คำทำนายเต็ม


RASHI_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุล", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]


def _classify_question(question: str) -> tuple[str, str, list[str]]:
    """รับคำถาม → (significator_planet, category, matched_keywords)

    ถ้าไม่ match → fallback ใช้ลัคนา + category 'general'
    """
    q = question.strip().lower()
    matched_keywords = []
    for keywords, planet, category in QUESTION_KEYWORDS:
        for kw in keywords:
            if kw in q:
                matched_keywords.append(kw)
                return planet, category, matched_keywords
    # fallback
    return "lagna", "general", []


def _make_text_lost_item(r: ProphecyResult) -> str:
    """คำทำนายแบบ 'ของหาย/ของอยู่ที่ไหน'"""
    loc = BHAVA_LOCATIONS.get(r.sig_house, "")
    parts = [
        f"📍 {r.significator_th}เป็นตัวแทนของรัก/ของมีค่า อยู่ราศี{r.sig_rashi_name} "
        f"ในภพ{r.sig_house} ({r.sig_bhava})",
    ]
    if r.is_own_sign:
        parts.append(
            f"✨ {r.significator_th}อยู่เกษตรของตน — ของยังคงอยู่กับเจ้าของ "
            f"ไม่ได้สูญหายไปไหน อาจจะหลงลืมในที่ใกล้ตัว"
        )
    else:
        parts.append(f"🔍 ที่ตั้งโดยประมาณ: {loc}")
        parts.append(
            f"👁 เจ้าเรือนของราศี{r.sig_rashi_name} คือ{r.sign_lord_th} "
            f"— อาจอยู่กับ/ในบริเวณของ{r.sign_lord_th}"
        )
    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 ดาวครองร่วม: {co_names}")
    return "\n".join(parts)


def _make_text_person(r: ProphecyResult) -> str:
    """คำทำนายเกี่ยวกับบุคคล"""
    sigs = "/".join(PLANET_SIGNIFICATIONS.get(r.significator, [r.significator_th])[:2])
    parts = [
        f"👤 {r.significator_th} ({sigs}) อยู่ราศี{r.sig_rashi_name} "
        f"ภพ{r.sig_house} ({r.sig_bhava})",
    ]
    bhava_msg = {
        1: "บุคคลนั้นอยู่ใกล้ตัวคุณมาก หรือกำลังคิดถึงคุณอยู่",
        4: "บุคคลนั้นอยู่ที่บ้าน หรือใกล้ที่อยู่อาศัย",
        7: "บุคคลนั้นมีความสัมพันธ์ฉันท์คู่ครอง หรือพันธมิตร",
        10: "บุคคลนั้นอยู่ที่ทำงาน หรือเกี่ยวข้องกับการงาน",
        11: "บุคคลนั้นจะนำลาภและความสำเร็จมาให้",
        6: "บุคคลนั้นอาจมีปัญหา/อุปสรรค หรือไม่ค่อยเป็นมิตร",
        12: "บุคคลนั้นอยู่ไกลตัว หรืออาจมีการพลัดพราก",
    }.get(r.sig_house, f"ความสัมพันธ์เกี่ยวกับ{r.sig_bhava}")
    parts.append(f"💬 {bhava_msg}")
    if r.is_own_sign:
        parts.append(f"✨ {r.significator_th}อยู่เกษตร — บุคคลนั้นยังมีอิทธิพล/มั่นคง")
    return "\n".join(parts)


def _make_text_love(r: ProphecyResult) -> str:
    parts = [
        f"💕 ความรัก ({r.significator_th}) อยู่ราศี{r.sig_rashi_name} "
        f"ภพ{r.sig_house} ({r.sig_bhava})",
    ]
    msg = {
        1: "ความรักเริ่มจากตัวคุณก่อน คุณจะเป็นฝ่ายเริ่ม",
        2: "ความรักนำมาซึ่งทรัพย์สิน หรือคนรักช่วยเรื่องการเงิน",
        4: "ความรักมั่นคง อยู่ในครอบครัว เริ่มต้นที่บ้าน",
        5: "ความรักหวานชื่น มีความสุข อาจเกิดจากเสน่ห์",
        7: "ความรักเข้าสู่การเป็นคู่ครอง มีโอกาสแต่งงาน",
        11: "ความรักจะให้ลาภและความสำเร็จ",
        12: "ความรักเป็นเรื่องลับ หรืออาจไม่สมหวัง",
        6: "ความรักมีอุปสรรค ต้องระวังคนแทรก",
        8: "ความรักมีการเปลี่ยนแปลงใหญ่ อาจสิ้นสุดหรือเริ่มใหม่",
    }.get(r.sig_house, "ตีความเรื่องรักตามธรรมชาติของ" + r.sig_bhava)
    parts.append(f"💬 {msg}")
    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 มีดาวประกอบ: {co_names}")
    return "\n".join(parts)


def _make_text_wealth(r: ProphecyResult) -> str:
    parts = [
        f"💰 ทรัพย์สิน/การเงิน ({r.significator_th}) อยู่ราศี{r.sig_rashi_name} "
        f"ภพ{r.sig_house} ({r.sig_bhava})",
    ]
    msg = {
        2: "ทรัพย์อยู่ที่ตน เก็บออมได้ดี",
        11: "ลาภมาจากมิตรและความปรารถนาที่หวัง",
        5: "ทรัพย์มาจากการสร้างสรรค์ ลูก หรือการลงทุน",
        4: "ทรัพย์เป็นอสังหา/ที่ดิน/บ้าน",
        9: "ลาภมาจากผู้ใหญ่ บุญเก่า หรือต่างถิ่น",
        10: "ทรัพย์มาจากการงาน ตำแหน่ง",
        6: "ระวังการสูญเสีย หนี้สิน หรือคู่แข่ง",
        8: "ทรัพย์อาจมาทางมรดก แต่ต้องระวังการเปลี่ยนแปลงใหญ่",
        12: "ระวังการใช้จ่ายมาก หรือทรัพย์รั่วไหล",
    }.get(r.sig_house, "ตีความทรัพย์ตามธรรมชาติของ" + r.sig_bhava)
    parts.append(f"💬 {msg}")
    return "\n".join(parts)


def _make_text_general(r: ProphecyResult, question: str) -> str:
    """คำทำนายทั่วไป (ไม่ match keyword) — อ่านจากลัคนา"""
    parts = [
        f"📜 เกี่ยวกับ \"{question}\" — อ่านจากลัคนา {r.sig_rashi_name} "
        f"(ดาวเกษตร: {r.sign_lord_th})",
        f"🎯 ลัคนาตั้งที่ราศี{r.sig_rashi_name} ภพตนุ — เรื่องนี้เริ่มจากตัวเจ้าชะตา",
    ]
    if r.is_own_sign:
        parts.append("✨ ลัคนาอยู่เกษตรของตน — เรื่องนี้เจ้าชะตามีอำนาจตัดสินใจเอง")
    parts.append(
        f"💡 (สำหรับคำถามเฉพาะ — ใช้คำว่า 'ของรัก', 'การงาน', 'การเงิน', "
        f"'บุตร', 'รัก', 'สุขภาพ', 'บ้าน', ฯลฯ เพื่อให้ตีความเฉพาะเจาะจง)"
    )
    return "\n".join(parts)


def _make_text_generic_category(r: ProphecyResult, category: str) -> str:
    """fallback สำหรับ category ที่ยังไม่มี renderer เฉพาะ"""
    cat_label = {
        "career": "การงาน/อาชีพ",
        "health": "สุขภาพ",
        "property": "บ้าน/ที่ดิน",
        "travel": "การเดินทาง",
        "study": "การศึกษา",
        "enemy": "ศัตรู/คดีความ",
    }.get(category, category)
    parts = [
        f"📌 เรื่อง{cat_label} — ตัวแทนคือ{r.significator_th} "
        f"อยู่ราศี{r.sig_rashi_name} ภพ{r.sig_house} ({r.sig_bhava})",
    ]
    if r.is_own_sign:
        parts.append(f"✨ {r.significator_th}อยู่เกษตรของตน — มีพลังในเรื่องนี้")
    tone_msg = {
        "good": "👍 ภพนี้เป็นภพดี — แนวโน้มเป็นบวก",
        "warning": "⚠️ ภพนี้เป็นภพหนัก — ต้องระวังอุปสรรค",
        "neutral": "🟡 ภพนี้เป็นกลาง — ขึ้นกับการปฏิบัติ",
    }.get(r.tone, "")
    if tone_msg:
        parts.append(tone_msg)
    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 ดาวครองร่วม: {co_names}")
    return "\n".join(parts)


def predict(chart: Chart, question: str) -> ProphecyResult:
    """พยากรณ์โหรทายหนูจากคำถาม

    Returns ProphecyResult ที่มี .text เป็นคำทำนายพร้อมใช้
    """
    significator, category, _kws = _classify_question(question)

    if significator not in chart.placements:
        # ดาว significator ไม่มีในผัง (เช่น ลัคนาก็ใช้ key 'lagna' ที่มีอยู่)
        significator = "lagna"
        category = "general"

    p = chart.placements[significator]
    sig_rashi_index = p.sign
    sig_house = p.house
    sig_rashi_name = RASHI_TH[sig_rashi_index]
    sig_bhava = BHAVA_NAMES_TH[sig_house - 1]

    # ดาวครองร่วม (ดาวอื่นที่อยู่ราศีเดียวกัน, ไม่นับตัวเอง, ไม่นับลัคนา)
    co_planets = [
        k for k, pp in chart.placements.items()
        if pp.sign == sig_rashi_index and k != significator and k != "lagna"
    ]

    # ดาวเกษตรของราศีนั้น
    sign_lord_key = lord_of(sig_rashi_index)
    sign_lord_th = PLANET_NAME_TH.get(sign_lord_key, sign_lord_key)

    is_own_sign = (sign_lord_key == significator)

    result = ProphecyResult(
        significator=significator,
        significator_th=PLANET_NAME_TH.get(significator, significator),
        category=category,
        sig_rashi_index=sig_rashi_index,
        sig_rashi_name=sig_rashi_name,
        sig_house=sig_house,
        sig_bhava=sig_bhava,
        co_planets=co_planets,
        sign_lord_key=sign_lord_key,
        sign_lord_th=sign_lord_th,
        is_own_sign=is_own_sign,
        tone=BHAVA_TONE.get(sig_house, "neutral"),
        text="",  # populate below
    )

    # เลือก renderer ตาม category
    if category == "lost_item":
        text = _make_text_lost_item(result)
    elif category == "person":
        text = _make_text_person(result)
    elif category == "love":
        text = _make_text_love(result)
    elif category == "wealth":
        text = _make_text_wealth(result)
    elif category == "general" or category == "current_event":
        text = _make_text_general(result, question)
    else:
        text = _make_text_generic_category(result, category)

    result.text = text
    return result
