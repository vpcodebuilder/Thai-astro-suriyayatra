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
from thai_astro.horathaynu.data.question_mapping import (
    QuestionMapping,
    classify_question as _classify_v2,
)
from thai_astro.horathaynu.data.planet_in_bhava import get_planet_in_bhava
from thai_astro.horathaynu.data.bhava_meanings_prashna import get_bhava as _get_bhava_meaning
from thai_astro.horathaynu.data.lord_in_bhava import predict_for_primary_bhava
from thai_astro.horathaynu.data.planet_combo import find_combos


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
    # ----- ของเดิม (คงไว้เพื่อ backward compat กับ webapp) -----
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

    # ----- Phase 1: เพิ่ม fields สำหรับชั้น 1+2 (ใช้ใน Phase 6) -----
    primary_bhava: int = 0                           # ภพหลักของ "คำถาม"
    primary_bhava_name: str = ""                     # ชื่อไทย
    secondary_bhavas: tuple[int, ...] = ()           # ภพรอง (1-3 ตัว)
    co_significators: tuple[str, ...] = ()           # ดาวรอง
    matched_keywords: tuple[str, ...] = ()           # debug
    category_label: str = ""                         # ป้ายแสดงผล เช่น "การงาน"
    tone_hint: str = "neutral"                       # จาก QuestionMapping


RASHI_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุล", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]


def _classify_question(question: str) -> tuple[str, str, list[str]]:
    """[Legacy] รับคำถาม → (significator_planet, category, matched_keywords)

    Phase 1: delegate ไป classify_question() ใหม่ที่ใช้ score-based matching.
    เก็บ signature เดิมไว้กันโค้ดอื่นที่อาจ import (ไม่มีในตอนนี้แต่กันไว้).
    """
    mapping, matched = _classify_v2(question)
    return mapping.significator, mapping.category, matched


# ===========================================================================
# Phase A+C: Category Lens + Verdict
# ===========================================================================
# บทบาทของดาวใน prashna (ใช้สรุปสั้นเวลา reframe)
PLANET_ROLES_TH: dict[str, str] = {
    "sun":     "อำนาจ/ผู้ใหญ่",
    "moon":    "อารมณ์/มารดา",
    "mars":    "พลังต่อสู้",
    "mercury": "การสื่อสาร",
    "jupiter": "บุญ/ที่ปรึกษา",
    "venus":   "ความรัก/ความงาม",
    "saturn":  "ความช้า/อุปสรรค",
    "rahu":    "ของลึก/ลาภลอย",
    "ketu":    "การปล่อยวาง/ของเก่า",
    "uranus":  "การเปลี่ยนแปลงฉับพลัน",
    "lagna":   "ตัวเจ้าชะตา",
}

# ภพที่ "ทับ" กับ category — ถ้าดาว significator อยู่ในภพ set นี้
# = on-topic, แสดง planet×bhava text เต็ม; ไม่อยู่ = off-topic, ใช้แค่ lens
CATEGORY_RELEVANT_BHAVAS: dict[str, set[int]] = {
    "love":           {5, 7, 11},
    "marriage":       {5, 7, 11, 2},
    "breakup":        {7, 8, 12},
    "career":         {6, 10, 11, 1},
    "job_search":     {7, 10, 11},
    "resign":         {3, 10, 12, 6},
    "wealth":         {2, 5, 8, 9, 11},
    "luck_windfall":  {5, 9, 11},
    "debt":           {6, 8, 12},
    "health":         {1, 6, 8},
    "study":          {3, 4, 5, 9},
    "child":          {5, 11},
    "parent":         {1, 4, 9},
    "sibling_friend": {3, 11, 7},
    "travel_near":    {3, 9, 12},
    "travel_far":     {3, 9, 12},
    "lawsuit":        {6, 7, 12},
    "enemy":          {6, 7, 12},
    "property_home":  {2, 4, 11},
    "business":       {2, 7, 10, 11},
    "lost_item":      {2, 4, 12, 5, 8},
    "lost_animal":    {2, 6, 12},
    "lost_person":    {1, 7, 8, 12},
    "current_event":  set(range(1, 13)),
    "general":        set(range(1, 13)),
}


def _is_on_topic(category: str, sig_house: int) -> bool:
    """ตรวจว่าตำแหน่งดาว significator อยู่ในภพที่เกี่ยวข้องกับเรื่องที่ถามไหม.

    ถ้าใช่ → planet × bhava text มี relevance สูง แสดงเต็ม
    ถ้าไม่ใช่ → text อาจ off-topic ใช้แค่ category lens
    """
    relevant = CATEGORY_RELEVANT_BHAVAS.get(category, set(range(1, 13)))
    return sig_house in relevant


# ธีมสั้นของภพ (ใช้ใน category lens)
BHAVA_SHORT_THEME_TH: dict[int, str] = {
    1:  "ตัวเจ้าชะตาเอง",
    2:  "ทรัพย์และของกินของใช้",
    3:  "พี่น้อง เพื่อน การติดต่อ",
    4:  "ครอบครัวและที่อยู่อาศัย",
    5:  "ลูก คนรัก และความสนุก",
    6:  "ศัตรู คู่แข่ง อุปสรรค",
    7:  "คู่ครอง คู่ค้า หุ้นส่วน",
    8:  "เรื่องลึก การเปลี่ยนแปลงใหญ่",
    9:  "ผู้ใหญ่ ครู ต่างแดน บุญ",
    10: "การงาน ตำแหน่ง ชื่อเสียง",
    11: "มิตร ลาภ ความสมหวัง",
    12: "การสูญเสีย ที่ลับ ต่างถิ่น",
}


def _format_category_lens(
    category_label: str,
    significator_key: str,
    significator_th: str,
    sig_house: int,
    sig_bhava_name: str,
) -> str:
    """Phase A — เขียนประโยค frame ดาว×ภพ ในบริบทของคำถาม

    แทนที่จะอ่าน 'ดาวอยู่ภพไหน' โดดๆ — บอกว่าเรื่องที่ถามจะ
    เกี่ยวพันกับ theme ของภพที่ดาวสำคัญลงตรงไหน
    """
    role = PLANET_ROLES_TH.get(significator_key, significator_th)
    theme = BHAVA_SHORT_THEME_TH.get(sig_house, sig_bhava_name)
    return (
        f"🌌 {significator_th} ({role}) อยู่ที่ภพ{sig_house} ({sig_bhava_name}) "
        f"— เรื่อง{category_label}จะเกี่ยวพันกับ{theme}"
    )


def _compute_verdict(
    sig_planet: str, sig_house: int, layer2_tone: str | None, combo_tones: list[str]
) -> tuple[str, str]:
    """Phase C — สังเคราะห์ verdict สั้นจาก tone หลายชั้น

    คืน (tone, headline_text)
    """
    votes = {"good": 0.0, "warning": 0.0, "neutral": 0.0}

    # Layer 3: planet × bhava
    pib = get_planet_in_bhava(sig_planet, sig_house)
    if pib is not None:
        votes[pib.tone] += 1.0

    # Layer 2: lord × bhava
    if layer2_tone in votes:
        votes[layer2_tone] += 1.0

    # Layer 3.5: combos (น้ำหนักน้อยกว่า)
    for t in combo_tones:
        if t in votes:
            votes[t] += 0.5

    if votes["good"] > votes["warning"] + 0.3:
        return ("good",
                "🎯 คำตอบ: แนวโน้มดี — มีโอกาสและบุญหนุน เดินหน้าได้")
    if votes["warning"] > votes["good"] + 0.3:
        return ("warning",
                "🎯 คำตอบ: ต้องระวัง — มีอุปสรรคหรือเงื่อนไขที่ต้องคิดให้รอบคอบ")
    return ("neutral",
            "🎯 คำตอบ: ก้ำกึ่ง — ขึ้นกับการตัดสินใจและการเตรียมตัวของคุณ")


def _format_planet_in_bhava_line(planet: str, house: int) -> tuple[str, str] | None:
    """ดึง entry จากตาราง 84 entries แล้ว format เป็น (text_line, advice_line).

    คืน None ถ้าไม่มี entry (เช่น ราหู/เกตุ/มฤตยู ยังไม่ทำ Phase 3 รอบนี้).
    """
    entry = get_planet_in_bhava(planet, house)
    if entry is None:
        return None
    tone_emoji = {"good": "✨", "warning": "⚠️", "neutral": "🟡"}.get(entry.tone, "📍")
    return (
        f"{tone_emoji} {entry.text}",
        f"💡 {entry.advice}",
    )


def _emoji_for_tone(tone: str) -> str:
    return {"good": "✨", "warning": "⚠️", "neutral": "🟡"}.get(tone, "📍")


def _bhava_theme_line(house: int) -> str | None:
    """ดึง theme ของภพจาก bhava_meanings_prashna — สำหรับบรรทัดบริบท."""
    try:
        b = _get_bhava_meaning(house)
    except ValueError:
        return None
    return f"📍 {b.theme}"


def _format_combo_lines(
    significator: str,
    co_planets: list[str],
    category: str,
) -> list[str]:
    """Phase 5 — สร้างบรรทัด planet combo (ดาวครองร่วมที่มีนัยพิเศษ).

    significator + ทุก co_planet → หาคู่ที่ตำราเรียกว่า "พิเศษ"
    คืนเฉพาะ combo ที่ category ตรงกับเรื่องที่ถาม
    """
    if not co_planets:
        return []
    # รวม significator เข้าไปด้วยเพื่อหา combo ที่เกี่ยวกับ sig
    all_planets = [significator] + list(co_planets)
    combos = find_combos(all_planets, category=category)
    if not combos:
        return []

    lines: list[str] = []
    tone_emoji = {"good": "🤝", "warning": "⚠️", "neutral": "🤝"}
    # แสดงสูงสุด 2 combos กันยาวเกิน
    for c in combos[:2]:
        emoji = tone_emoji.get(c.tone, "🤝")
        lines.append(f"{emoji} {c.label}")
        lines.append(f"   ↳ {c.text}")
    return lines


def _format_lord_in_bhava_lines(chart: Chart, primary_bhava: int) -> list[str]:
    """Phase 4 — สร้างบรรทัดชั้นที่ 2 (ภพผสมภพ).

    คืน list ของ 2 บรรทัด: header + คำทำนาย
    คืน [] ถ้าไม่มีข้อมูล (primary_bhava=0 หรือคำนวณไม่ได้)
    """
    if primary_bhava < 1 or primary_bhava > 12:
        return []
    r = predict_for_primary_bhava(chart, primary_bhava)
    if r is None:
        return []
    tone_emoji = {"good": "🌟", "warning": "⚠️", "neutral": "🌀"}.get(r.tone, "🌀")
    if r.is_same_bhava:
        # เจ้าเรือนภพ X อยู่ภพ X เอง — เป็นรูปแบบมั่นคง
        header = (
            f"{tone_emoji} ชั้นที่ 2 (ภพผสมภพ): เจ้าเรือนภพ{r.primary_bhava} "
            f"({r.primary_bhava_name}) คือ{r.lord_planet_th} "
            f"อยู่เกษตรของตน → เรื่องนี้มั่นคงในตัวเอง"
        )
    else:
        header = (
            f"{tone_emoji} ชั้นที่ 2 (ภพผสมภพ): เจ้าเรือนภพ{r.primary_bhava} "
            f"({r.primary_bhava_name}) คือ{r.lord_planet_th} "
            f"ไปอยู่ภพ{r.located_bhava} ({r.located_bhava_name})"
        )
    return [header, f"   ↳ {r.text}"]


def _make_text_lost_item(r: ProphecyResult) -> str:
    """คำทำนายแบบ 'ของหาย/ของอยู่ที่ไหน' — Phase 3: ใช้ bhava_meanings_prashna + planet_in_bhava."""
    parts = [
        f"🔮 {r.significator_th}เป็นตัวแทนของรัก/ของมีค่า อยู่ราศี{r.sig_rashi_name} "
        f"ในภพ{r.sig_house} ({r.sig_bhava})",
    ]

    # ที่ตั้งโดยประมาณ จาก bhava_meanings_prashna (ละเอียดขึ้น)
    try:
        bm = _get_bhava_meaning(r.sig_house)
        parts.append(f"📍 ที่ตั้งโดยประมาณ: {bm.objects_places}")
    except ValueError:
        # fallback ถ้าหลุดช่วง
        loc = BHAVA_LOCATIONS.get(r.sig_house, "")
        if loc:
            parts.append(f"📍 ที่ตั้งโดยประมาณ: {loc}")

    if r.is_own_sign:
        parts.append(
            f"🏠 {r.significator_th}อยู่เกษตรของตน — ของยังคงอยู่กับเจ้าของ "
            f"ไม่ได้สูญหายไปไหน อาจจะหลงลืมในที่ใกล้ตัว"
        )
    else:
        parts.append(
            f"👁 เจ้าเรือนของราศี{r.sig_rashi_name} คือ{r.sign_lord_th} "
            f"— อาจอยู่กับ/ในบริเวณของ{r.sign_lord_th}"
        )

    # Phase 3: เพิ่ม insight จาก planet × bhava table
    pib = _format_planet_in_bhava_line(r.significator, r.sig_house)
    if pib is not None:
        parts.append(pib[0])
        parts.append(pib[1])

    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 ดาวครองร่วม: {co_names}")
    return "\n".join(parts)


def _make_text_person(r: ProphecyResult) -> str:
    """คำทำนายเกี่ยวกับบุคคล — Phase 3: ใช้ bhava_meanings_prashna + planet_in_bhava."""
    sigs = "/".join(PLANET_SIGNIFICATIONS.get(r.significator, [r.significator_th])[:2])
    parts = [
        f"👤 {r.significator_th} ({sigs}) อยู่ราศี{r.sig_rashi_name} "
        f"ภพ{r.sig_house} ({r.sig_bhava})",
    ]

    # บุคคลในภพนี้ จาก bhava_meanings_prashna
    try:
        bm = _get_bhava_meaning(r.sig_house)
        parts.append(f"💬 {bm.people}")
    except ValueError:
        pass

    # Phase 3: insight ลึกจาก planet × bhava
    pib = _format_planet_in_bhava_line(r.significator, r.sig_house)
    if pib is not None:
        parts.append(pib[0])
        parts.append(pib[1])

    if r.is_own_sign:
        parts.append(f"🏠 {r.significator_th}อยู่เกษตร — บุคคลนั้นยังมีอิทธิพล/มั่นคง")
    return "\n".join(parts)


def _make_text_love(r: ProphecyResult) -> str:
    """ความรัก — Phase 3: ใช้ planet × bhava table."""
    parts = [
        f"💕 ความรัก ({r.significator_th}) อยู่ราศี{r.sig_rashi_name} "
        f"ภพ{r.sig_house} ({r.sig_bhava})",
    ]

    # ใช้ planet_in_bhava ก่อน — ลึกที่สุด
    pib = _format_planet_in_bhava_line(r.significator, r.sig_house)
    if pib is not None:
        parts.append(pib[0])
        parts.append(pib[1])
    else:
        # fallback ไป bhava theme ถ้าไม่มี entry
        try:
            bm = _get_bhava_meaning(r.sig_house)
            parts.append(f"💬 {bm.theme}")
        except ValueError:
            pass

    if r.is_own_sign:
        parts.append(f"🏠 {r.significator_th}อยู่เกษตรของตน — รักนี้ตัวคุณกุมสมดุล")

    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 มีดาวประกอบ: {co_names}")
    return "\n".join(parts)


def _make_text_wealth(r: ProphecyResult) -> str:
    """ทรัพย์ — Phase 3: ใช้ planet × bhava table."""
    parts = [
        f"💰 ทรัพย์สิน/การเงิน ({r.significator_th}) อยู่ราศี{r.sig_rashi_name} "
        f"ภพ{r.sig_house} ({r.sig_bhava})",
    ]

    pib = _format_planet_in_bhava_line(r.significator, r.sig_house)
    if pib is not None:
        parts.append(pib[0])
        parts.append(pib[1])
    else:
        try:
            bm = _get_bhava_meaning(r.sig_house)
            parts.append(f"💬 {bm.theme}")
        except ValueError:
            pass

    if r.is_own_sign:
        parts.append(f"🏠 {r.significator_th}อยู่เกษตร — ทรัพย์มาเองโดยไม่ต้องไขว่คว้า")

    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 ดาวครองร่วม: {co_names}")
    return "\n".join(parts)


def _make_text_general(r: ProphecyResult, question: str) -> str:
    """คำทำนายทั่วไป — อ่านจากลัคนา + bhava theme.

    Note: Banner "ไม่พบคำสำคัญ" ย้ายไปแสดงเป็นกล่องเตือนใน UI แล้ว
    (server.py ส่ง warning field ใน JSON response)
    """
    parts: list[str] = [
        f"📜 เกี่ยวกับ \"{question}\" — อ่านจากลัคนา {r.sig_rashi_name} "
        f"(ดาวเกษตร: {r.sign_lord_th})"
    ]
    try:
        bm = _get_bhava_meaning(r.sig_house)
        parts.append(f"🎯 {bm.theme}")
    except ValueError:
        parts.append(
            f"🎯 ลัคนาตั้งที่ราศี{r.sig_rashi_name} ภพ{r.sig_bhava} "
            f"— เรื่องนี้เริ่มจากตัวเจ้าชะตา"
        )

    if r.is_own_sign:
        parts.append("🏠 ลัคนาอยู่เกษตรของตน — เรื่องนี้เจ้าชะตามีอำนาจตัดสินใจเอง")

    parts.append(
        "💡 ใช้คำเฉพาะ เช่น 'การงาน' 'ความรัก' 'หวย' 'ของหาย' 'คดี' "
        "จะได้คำทำนายลึกขึ้น"
    )
    return "\n".join(parts)


def _make_text_generic_category(r: ProphecyResult, category: str) -> str:
    """Render คำทำนายแบบ generic — ใช้กับ category ที่ไม่มี renderer เฉพาะ.

    Phase 3: ดึงจากตาราง 84 entries (planet × bhava) เพื่อให้คำทำนายลึกขึ้น
    """
    cat_label = r.category_label or {
        "career": "การงาน/อาชีพ",
        "health": "สุขภาพ",
        "property": "บ้าน/ที่ดิน",
        "travel": "การเดินทาง",
        "study": "การศึกษา",
        "enemy": "ศัตรู/คดีความ",
    }.get(category, category)

    parts: list[str] = [
        f"📌 เรื่อง{cat_label} — ตัวแทนคือ{r.significator_th} "
        f"อยู่ราศี{r.sig_rashi_name} ภพ{r.sig_house} ({r.sig_bhava})",
    ]

    # ===== Phase A: Category lens — frame ดาว×ภพ ในบริบทคำถาม (เสมอ) =====
    parts.append(_format_category_lens(
        cat_label, r.significator, r.significator_th, r.sig_house, r.sig_bhava
    ))

    # ===== Phase 3: ดาว × ภพ — แสดงเฉพาะเมื่อ on-topic เท่านั้น =====
    # ถ้าไม่ on-topic, generic text อาจหลุดบริบท (เช่น Saturn×7 พูดเรื่องคู่
    # ทั้งที่คำถามเป็นเรื่องลาออก) — เลี่ยงเพื่อให้คำตอบไม่สับสน
    if _is_on_topic(r.category, r.sig_house):
        pib = _format_planet_in_bhava_line(r.significator, r.sig_house)
        if pib is not None:
            parts.append(pib[0])     # text
            parts.append(pib[1])     # advice

    if r.is_own_sign:
        parts.append(
            f"🏠 {r.significator_th}อยู่เกษตรของตน "
            f"— มีพลังเต็มในเรื่องนี้ ดาวอยู่ในบ้านของตัวเอง"
        )

    if r.co_planets:
        co_names = ", ".join(PLANET_NAME_TH[k] for k in r.co_planets)
        parts.append(f"🤝 ดาวครองร่วม: {co_names}")

    return "\n".join(parts)


def predict(chart: Chart, question: str) -> ProphecyResult:
    """พยากรณ์โหรทายหนูจากคำถาม

    Returns ProphecyResult ที่มี .text เป็นคำทำนายพร้อมใช้
    """
    mapping, matched_keywords = _classify_v2(question)
    significator = mapping.significator
    category = mapping.category

    if significator not in chart.placements:
        # ดาว significator ไม่มีในผัง (เช่น ลัคนาก็ใช้ key 'lagna' ที่มีอยู่)
        significator = "lagna"
        category = "general"
        mapping = _classify_v2("")[0]  # fallback general mapping

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

    # Phase 1: ภพหลักของคำถาม (ต่างจาก sig_house = ที่ดาว sig อยู่จริง)
    primary_bhava = mapping.primary_bhava
    primary_bhava_name = (
        BHAVA_NAMES_TH[primary_bhava - 1]
        if 1 <= primary_bhava <= 12
        else ""
    )

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
        # ----- Phase 1 fields -----
        primary_bhava=primary_bhava,
        primary_bhava_name=primary_bhava_name,
        secondary_bhavas=mapping.secondary_bhavas,
        co_significators=mapping.co_significators,
        matched_keywords=tuple(matched_keywords),
        category_label=mapping.label_th,
        tone_hint=mapping.tone_hint,
    )

    # เลือก renderer ตาม category — render ชั้นที่ 3 (ดาว × ภพ) + Layer 1 บริบท
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

    # ===== Phase 5: ดาวครองร่วม (planet combo) ที่มีนัยพิเศษ =====
    same_house_planets = [
        k for k, pp in chart.placements.items()
        if pp.house == sig_house and k != significator and k != "lagna"
    ]
    combo_candidates = list({*result.co_planets, *same_house_planets})
    combo_lines = _format_combo_lines(
        result.significator, combo_candidates, result.category
    )

    # คำนวณ tones ของ combos สำหรับ verdict
    combo_tones: list[str] = []
    for c in find_combos(
        [result.significator] + combo_candidates, category=result.category
    )[:2]:
        combo_tones.append(c.tone)

    if combo_lines:
        text = text + "\n" + "\n".join(combo_lines)

    # ===== Phase 4: เพิ่มชั้นที่ 2 (ภพผสมภพ) ต่อท้าย =====
    layer2_tone: str | None = None
    if result.primary_bhava >= 1:
        layer2_result = predict_for_primary_bhava(chart, result.primary_bhava)
        if layer2_result is not None:
            layer2_tone = layer2_result.tone
        layer2_lines = _format_lord_in_bhava_lines(chart, result.primary_bhava)
        if layer2_lines:
            text = text + "\n" + "\n".join(layer2_lines)

    # ===== Phase C: Verdict — สังเคราะห์ tone ทุกชั้น แล้วใส่ด้านบนสุด =====
    verdict_tone, verdict_line = _compute_verdict(
        result.significator, result.sig_house, layer2_tone, combo_tones
    )
    text = verdict_line + "\n" + text

    result.text = text
    return result
