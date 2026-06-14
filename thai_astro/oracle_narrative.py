"""บทพูดโหร (Oracle Narrative) — เวอร์ชัน 2

สังเคราะห์จาก:
    - transit_prophecy (ดาวจรกระทบดาวเดิม)
    - bhava_lord_prophecy (เจ้าเรือนครองภพ - natal + transit)
    - dignities (อุจน์/เกษตร/นิจ + เกณฑ์โยค)

ใช้ภาษาคนคุยกัน — มีจังหวะหยุด, มีคำเชื่อม, มีคำแนะนำเฉพาะเรื่อง
ผสมหลักการ "เกณฑ์/โยค" เพื่อพลิกร้ายเป็นดี (ปทุมเกณฑ์, อุดมเกณฑ์, นิจภังคราชโยค ฯลฯ)
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from .dignities import PlanetDignity, Yoga


# ============================================================
# Modern vocabulary
# ============================================================
MODERN_NATAL_THEME = {
    "อาทิตย์":   "การงาน ตำแหน่ง ภาพลักษณ์ของคุณ และคุณพ่อหรือผู้บังคับบัญชา",
    "จันทร์":    "อารมณ์ สภาพจิตใจ ครอบครัว และคุณแม่",
    "อังคาร":    "พลังกาย ความมุ่งมั่น การแข่งขัน และเรื่องที่ต้องตัดสินใจเร็ว",
    "พุธ":       "การสื่อสาร การเจรจา โซเชียล สัญญา และการเรียน",
    "พฤหัสบดี":  "โชค การเงิน บุญเก่า ผู้ใหญ่อุปถัมภ์ และการลงทุน",
    "ศุกร์":     "ความรัก ความสุข ของสวยงาม การเข้าสังคม",
    "เสาร์":     "ภาระ ความรับผิดชอบ งานที่ต้องอดทน และสุขภาพระยะยาว",
    "ราหู":      "การเปลี่ยนแปลง สิ่งใหม่ที่ไม่คุ้น เทคโนโลยี และเรื่องลึกลับ",
    "เกตุ":      "การปล่อยวาง จิตใจ ความสงบ และเรื่องที่จบลง",
}

LIFE_AREAS = {
    "money":   {"bhavas": [2, 11], "title": "💰 การเงินและรายได้"},
    "career":  {"bhavas": [10, 6], "title": "💼 การงานและอาชีพ"},
    "love":    {"bhavas": [5, 7],  "title": "❤️ ความรักและความสัมพันธ์"},
    "family":  {"bhavas": [4],     "title": "🏠 ครอบครัวและบ้าน"},
    "health":  {"bhavas": [1, 6, 8], "title": "🌿 สุขภาพและจิตใจ"},
    "growth":  {"bhavas": [9, 3],  "title": "✨ โอกาส การเรียนรู้ และการเดินทาง"},
    "change":  {"bhavas": [8, 12], "title": "🔄 การเปลี่ยนแปลงและเรื่องซ่อนเร้น"},
}

# ทำให้ฟังเป็นมนุษย์: คำเชื่อม / interjections
HUMAN_CONNECTORS_GOOD = [
    "ที่ดีนะ คือ", "อันนี้น่ายินดี —", "ฟังให้ดีนะ", "ขอชมก่อนเลย",
    "อันนี้ต้องบอกว่าโชคดีมาก —",
]
HUMAN_CONNECTORS_WARN = [
    "ส่วนเรื่องที่ห่วงคือ", "อันนี้อยากเตือนแบบจริงจัง —", "เรื่องที่ต้องจับตา",
    "เปิดใจฟังนะ", "พูดตรง ๆ ว่า",
]


# ============================================================
# Greetings & Closings (ภาษาคน หลายเฉด)
# ============================================================
GREETINGS_GOOD = [
    "นั่งให้สบายก่อนนะ เปิดดวงให้แล้ว — บอกตามตรงเลยว่าช่วงนี้ของคุณ "
    "ลมพัดเข้าทางพอดี ดาวที่ควรเด่นก็เด่น ดาวที่เคยขัดก็เริ่มลื่นไหล",

    "เปิดดวงดูแล้ว ขอบอกแบบไม่อ้อมเลย — ช่วงนี้คุณกำลังอยู่ในจังหวะที่หลายอย่างเข้าทาง "
    "อย่ารอ \"พร้อม\" เพราะถ้าดูจากดาว นี่คือพร้อมที่สุดแล้ว",

    "ฟังก่อนนะ — ดวงคุณช่วงนี้เปิดอยู่จริง ๆ ใครที่อยากเริ่มอะไรใหม่ ๆ ต้องเริ่มตอนนี้ "
    "เพราะอีกไม่นานดาวจะหมุนไป จังหวะอย่างนี้ไม่ได้มาบ่อย",
]
GREETINGS_HEAVY = [
    "ตั้งสติฟังก่อนนะ — บอกแบบนี้ไม่ได้ให้กลัว แต่ให้รู้ตัว "
    "ดวงช่วงนี้ของคุณค่อนข้างหนัก มีเรื่องต้องระวังหลายเรื่อง แต่ทุกอย่างมีทางออก",

    "เปิดดวงให้แล้ว — ขอพูดตรง ช่วงนี้ไม่ใช่ช่วงสบาย "
    "แต่อย่าเพิ่งท้อ เพราะดาวที่กดอยู่จะเดินผ่านไป สิ่งที่ทำตอนนี้คือเตรียมตัวรับมือ ไม่ใช่หนี",

    "นั่งก่อน — เปิดดวงให้คุณแล้ว ช่วงเวลานี้ใครก็ตามที่ได้ดวงแบบนี้ จะรู้สึกหนัก "
    "แต่จำไว้ ดวงนี้กำลังคัดกรองคนที่จะเดินต่อไปได้แข็งแรงกว่าเดิม",
]
GREETINGS_MIXED = [
    "เปิดดวงให้แล้ว ไม่ใช่ขาวไม่ใช่ดำเลยนะ — ช่วงนี้มีหลายเรื่องเกิดพร้อมกัน "
    "บางอย่างเข้าทาง บางอย่างต้องเสียสละ ฟังแล้วเก็บไปคิดดู ๆ",

    "ดูตามดาวแล้ว ช่วงนี้คือช่วง 'เรียนรู้' — ไม่ใช่ช่วงเฉลิมฉลอง ไม่ใช่ช่วงตกต่ำ "
    "แต่เป็นช่วงที่ชีวิตจะคัดสิ่งที่ใช่ออกจากสิ่งที่ไม่ใช่ให้คุณ",

    "เปิดดวงให้ดูแล้ว — น่าสนใจมาก เพราะมีโอกาสและบทเรียนมาเป็นคู่ "
    "ขอเล่าทีละเรื่องนะ คุณจะเลือกฟังเรื่องไหนก่อนก็ได้",
]
GREETINGS_NEUTRAL = [
    "เปิดดวงให้ดูแล้ว — ช่วงนี้ค่อนข้างสงบ ไม่มีคลื่นใหญ่ "
    "เหมาะกับการตั้งหลัก วางแผน และทำสิ่งเล็ก ๆ ให้ดีขึ้นทีละเรื่อง",

    "ช่วงนี้ของคุณเดินไปตามครรลอง ไม่มีอะไรหวือหวา "
    "แต่ก็มีรายละเอียดน่าสนใจที่อยากเล่าให้ฟัง",
]

CLOSINGS_GOOD = [
    "สุดท้ายก่อนแยกย้าย — ฝากไว้ว่าโอกาสแบบนี้ไม่ได้มาบ่อย "
    "อย่ามัวลังเลกับเรื่องเล็ก ๆ ที่เคยติดอยู่ ลงมือทำเลย "
    "ดวงดีไม่ได้แปลว่าได้ฟรี แต่หมายความว่าทำแล้วผลจะกลับมาเร็ว",

    "ปิดท้ายด้วยคำเตือนเล็ก ๆ — ช่วงดีแบบนี้คนมักประมาท "
    "ขอให้อยู่กับฐานเดิม อย่าเปลี่ยนตัวเองตามความสำเร็จเร็วเกินไป "
    "แล้วผลดีจะยั่งยืน",
]
CLOSINGS_HEAVY = [
    "ก่อนแยกย้าย ฝากไว้ว่า — ช่วงแบบนี้ขอให้ดูแลตัวเอง 3 เรื่อง "
    "ร่างกาย เงิน และคนใกล้ตัว ส่วนเรื่องตัดสินใจใหญ่ ๆ — รอก่อน อย่ารีบ "
    "ดวงจะเปลี่ยน และเมื่อเปลี่ยน คุณจะมีพลังกลับมา",

    "ปิดท้ายแบบนี้นะ — คนที่ผ่านช่วงแบบนี้มาได้ จะเข้มแข็งกว่าเดิมเสมอ "
    "อย่าเอาตัวเองไปเทียบใครในช่วงนี้ เก็บพลังไว้สู้ในเรื่องที่สำคัญจริง ๆ "
    "ส่วนเรื่องเล็กที่ทำให้คุณเหนื่อย ปล่อยมันไป",
]
CLOSINGS_MIXED = [
    "สรุปท้ายว่า — ช่วงนี้คือช่วง 'คัดกรอง' อะไรที่ดีจริงจะอยู่ อะไรที่ไม่ใช่จะหลุดออก "
    "อย่าฝืน อย่าเสียดาย ปล่อยให้ทุกอย่างเดินตามจังหวะของมัน "
    "ในอีกไม่กี่เดือนคุณจะเห็นภาพชัดขึ้นมาก",

    "ปิดท้ายว่า — โอกาสกับบทเรียนมาคู่กันเสมอ จับโอกาสที่เห็น ยอมรับบทเรียนที่มา "
    "อย่าเอาดวงตัวเองไปเทียบคนอื่น เพราะแต่ละคนเดินคนละเส้น",
]
CLOSINGS_NEUTRAL = [
    "ฝากไว้ว่า — ช่วงเงียบ ๆ แบบนี้คือช่วงที่ดีที่สุดในการลงทุนกับตัวเอง "
    "อ่านหนังสือ เรียนทักษะใหม่ ออกกำลังกาย พอดวงเปลี่ยนรอบหน้า คุณจะพร้อมกว่าใคร",
]


# ============================================================
# Yoga callouts — ประโยคชม / พลิกร้ายเป็นดี
# ============================================================
YOGA_HEADLINE = {
    "ปทุมเกณฑ์": (
        "เรื่องแรกที่อยากบอกก่อน — ดวงคุณมี §§ปทุมเกณฑ์§§ "
        "ดาวสำคัญหลายดวงเข้าเกณฑ์พอดี เป็นดวงของคนที่มีอำนาจวาสนา "
        "ฐานะมั่นคง และเป็นที่นับหน้าถือตา — อันนี้คือต้นทุนชีวิตที่ดีมาก"
    ),
    "อุดมเกณฑ์": (
        "อีกเรื่องที่อยากให้รู้ — ดวงคุณมี §§อุดมเกณฑ์§§ "
        "ดาวสำคัญได้ตำแหน่งอุจน์หลายดวง แปลว่า ความสามารถของคุณเหนือคนทั่วไป "
        "และดวงนี้ \"พลิกร้ายให้กลายเป็นดี\" ได้บ่อยครั้ง"
    ),
    "องค์เกณฑ์": (
        "ดวงคุณมี §§องค์เกณฑ์§§ — ดาวสำคัญหลายดวงอยู่ในตำแหน่งกำลังของตัวเอง "
        "แปลว่าคุณพึ่งตัวเองได้ดี โอกาสมักมาเองโดยไม่ต้องเหนื่อยมาก"
    ),
    "มหาภูตเกณฑ์": (
        "ดวงคุณมี §§มหาภูตเกณฑ์§§ — ดาวอยู่ในตรีโกณหลายดวง บุญเก่าหนุนชีวิตเรื่อย ๆ "
        "เรื่องสำคัญในชีวิตมักสมหวัง และคนรอบตัวมักจะอยากช่วย"
    ),
    "นิจภังคราชโยค": (
        "ที่น่าสนใจมากคือ — ดวงคุณมี §§นิจภังคราชโยค§§ "
        "ถึงจะมีดาวที่อ่อนกำลัง แต่ดาวเจ้าราศีที่รับไว้กลับแข็งแกร่ง "
        "หมายความว่า เรื่องที่ \"ควรร้าย\" ในชีวิตคุณ จะพลิกกลายเป็น \"ดีกว่าเดิม\" "
        "เริ่มจากจุดต่ำแล้วลุกขึ้นได้สูงกว่าคนที่เริ่มจากจุดสูงเสียอีก"
    ),
}


# ============================================================
# Helpers
# ============================================================
def _pick(seq, seed_key: str) -> str:
    if not seq:
        return ""
    rng = random.Random(hash(seed_key) & 0xFFFFFFFF)
    return rng.choice(seq)


def _strip_modifier(text: str) -> str:
    if not text:
        return ""
    for sep in ("  (แบบ ", " (แบบ "):
        if sep in text:
            text = text.split(sep)[0]
    return text.strip()


def _person_address(person_name: str) -> str:
    name = (person_name or "").strip()
    return f"คุณ{name}" if name else "คุณ"


# ============================================================
# Yoga interaction with predictions
# ============================================================
def _compute_overall_strength(yogas: List[Yoga]) -> int:
    """ระดับ \"ดวงดีพื้นฐาน\" จากโยค: ใช้ tilt ผลคำทำนาย"""
    score = 0
    for y in yogas:
        score += y.severity  # 1-3 ต่อโยค
    return score


def _flip_warning_with_yoga(text: str, has_flip_yoga: bool) -> Tuple[str, bool]:
    """ถ้ามีโยคพลิกดวง (นิจภังค/อุดม) ให้เติมข้อความปลอบใจท้าย"""
    if not has_flip_yoga:
        return text, False
    extra = " — แต่ด้วยเกณฑ์ดวงพื้นฐานของคุณ เรื่องนี้จะไม่หนักเท่าที่ควรเป็น"
    return text + extra, True


# ============================================================
# Build sections
# ============================================================
def _build_overall(
    transit_summary: Optional[dict],
    natal_lord_summary: Optional[dict],
    transit_lord_summary: Optional[dict],
    yogas: List[Yoga],
    address: str,
    seed: str,
) -> Tuple[str, str]:
    n_good = 0
    n_warn = 0
    if transit_summary:
        n_good += transit_summary["tones"].get("good", 0)
        n_warn += transit_summary["tones"].get("heavy", 0) + transit_summary["tones"].get("warning", 0)
    if transit_lord_summary:
        n_good += transit_lord_summary["counts"].get("good", 0)
        n_warn += transit_lord_summary["counts"].get("warning", 0)

    yoga_boost = _compute_overall_strength(yogas)
    # โยคหนัก ๆ ทำให้โทนเอนไปดี
    n_good += yoga_boost // 2

    if n_good >= 3 and n_warn <= 1:
        greeting = _pick(GREETINGS_GOOD, seed + "g")
        tone_class = "good"
    elif n_warn >= 3 and n_good <= 1 and yoga_boost < 4:
        greeting = _pick(GREETINGS_HEAVY, seed + "h")
        tone_class = "heavy"
    elif n_warn >= 3 and yoga_boost >= 4:
        # โยคดีมากพอจะพลิก — ใช้ greeting แบบ mixed
        greeting = _pick(GREETINGS_MIXED, seed + "m")
        tone_class = "mixed"
    elif n_good > 0 and n_warn > 0:
        greeting = _pick(GREETINGS_MIXED, seed + "m")
        tone_class = "mixed"
    else:
        greeting = _pick(GREETINGS_NEUTRAL, seed + "n")
        tone_class = "neutral"

    if address != "คุณ":
        greeting = greeting.replace("ของคุณ", f"ของ{address}", 1)
        greeting = greeting.replace("คุณช่วงนี้", f"{address}ช่วงนี้", 1)

    return greeting, tone_class


def _emphasize(text: str) -> str:
    """แปลง §§...§§ เป็น <strong>...</strong> สำหรับ render เป็น HTML"""
    import re
    return re.sub(r"§§([^§]+)§§", r"<strong>\1</strong>", text)


def _build_yoga_messages(yogas: List[Yoga]) -> List[dict]:
    """สร้างประโยคชม/พลิกดวงจากโยคที่มี (deprecated — เก็บไว้ใช้กับ astro_patterns)"""
    msgs = []
    seen_names = set()
    for y in sorted(yogas, key=lambda y: -y.severity):
        if y.name in seen_names:
            continue
        seen_names.add(y.name)
        text = YOGA_HEADLINE.get(y.name)
        if text is None:
            text = (
                f"ดวงคุณมีเรื่องดี — §§{y.name}§§ "
                f"({y.description}). {y.effect}"
            )
        msgs.append({
            "name": y.name, "text": _emphasize(text),
            "effect": y.effect, "planets": y.planets_involved,
            "severity": y.severity,
        })
    return msgs[:4]


def _build_yoga_messages_from_patterns(matched_patterns: List) -> List[dict]:
    """สรุป 'เกณฑ์ดวงพื้นฐาน' จาก astro_patterns ที่ match จริง
    (เลือกเฉพาะ tone=good — โยคเสียจัดแยกในคำเตือน)"""
    if not matched_patterns:
        return []
    # ลำดับความสำคัญ — โยคใหญ่ขึ้นก่อน
    priority_order = {
        "ปัญจมหาบุรุษ": 10,
        "โยคสำคัญ": 9,
        "เกณฑ์ลัคนา (ยศ-ทรัพย์)": 8,
        "รูปดวงไทย": 7,
        "จันทรโยค": 5,
        "กลุ่มลัคนา": 4,
        "โยคเสีย": 0,
    }
    goods = [p for p in matched_patterns if p.tone == "good"]
    goods.sort(key=lambda p: -priority_order.get(p.category, 0))

    msgs = []
    intro_phrases = [
        "เรื่องแรกที่อยากบอกก่อน",
        "อีกเรื่องที่อยากให้รู้",
        "ที่น่าสนใจมากคือ",
        "ขอชมก่อนเลย",
    ]
    for i, p in enumerate(goods[:4]):
        intro = intro_phrases[i] if i < len(intro_phrases) else "และอีกเรื่อง"
        text = (
            f"{intro} — ดวงคุณมี §§{p.name}§§ "
            f"({p.category}) {p.meaning}"
        )
        msgs.append({
            "name": p.name,
            "text": _emphasize(text),
            "effect": p.meaning,
            "planets": p.planets_involved,
            "severity": 3 if p.category in ("ปัญจมหาบุรุษ", "โยคสำคัญ") else 2,
        })
    return msgs


def _build_headline(
    transit_summary: Optional[dict],
    has_flip_yoga: bool,
    seed: str,
) -> str:
    if not transit_summary or not transit_summary.get("top_items"):
        return ""
    top = transit_summary["top_items"][0]
    aspect = top["aspect_type"]
    theme = MODERN_NATAL_THEME.get(top["natal_planet"], top.get("theme", ""))
    tp = top["transit_planet"]
    np_ = top["natal_planet"]

    if top["tone"] == "good":
        return (
            f"เรื่องเด่นที่สุดในช่วงนี้คือ — ดาว{tp}กำลังจร{aspect}กับ{np_}เดิม "
            f"เรื่อง{theme} จะมีจังหวะดี ๆ เข้ามาแน่นอน อย่าพลาดที่จะรับ"
        )
    elif top["tone"] in ("heavy", "warning"):
        base = (
            f"สิ่งแรกที่อยากเตือน — ดาว{tp}จร{aspect}{np_}เดิม "
            f"จะกระทบเรื่อง{theme} ช่วงนี้ต้องเดินด้วยสติเป็นพิเศษ"
        )
        text, _ = _flip_warning_with_yoga(base, has_flip_yoga)
        return text
    return (
        f"จุดเด่นในช่วงนี้คือดาว{tp}จร{aspect}{np_}เดิม "
        f"เกี่ยวข้องกับ{theme}โดยตรง"
    )


def _build_life_area_section(
    area_key: str,
    natal_lord_summary: Optional[dict],
    transit_lord_summary: Optional[dict],
    has_flip_yoga: bool,
) -> Optional[dict]:
    """รวมคำทำนาย "ดวงเดิม" + "ดาวจร" สำหรับ section นี้

    หลักการ:
        - แสดงดวงเดิมก่อน (รวม good/warn เท่าที่มี) → แยกเส้นคั่น → ตามด้วยดาวจร
        - ดาวจร: รับประกันมีอย่างน้อย 1 line ถ้ามีข้อมูล (ใช้ neutral fallback)
    """
    info = LIFE_AREAS[area_key]
    target = set(info["bhavas"])

    def _bucket(summary: Optional[dict]) -> Tuple[List[str], List[str], List[str]]:
        g, w, n = [], [], []
        if not summary:
            return g, w, n
        for p in summary.get("all_items", []):
            if p["lord_bhava"] not in target and p["located_bhava"] not in target:
                continue
            line = _strip_modifier(p["prediction"])
            tone = p["tone"]
            if tone == "good":
                g.append(line)
            elif tone == "warning":
                if has_flip_yoga:
                    line, _ = _flip_warning_with_yoga(line, True)
                w.append(line)
            else:
                n.append(line)
        return g, w, n

    n_good, n_warn, n_neutral = _bucket(natal_lord_summary)
    t_good, t_warn, t_neutral = _bucket(transit_lord_summary)

    # ====== ดวงเดิม (natal) ======
    natal_good: List[str] = []
    natal_warn: List[str] = []
    for line in n_good[:2]:
        natal_good.append(line)
    for line in n_warn[:2]:
        natal_warn.append(line)
    # ถ้าไม่มี good/warn ลงตัว ใช้ neutral 1 line
    if not natal_good and not natal_warn and n_neutral:
        natal_good.append(n_neutral[0])

    # ====== ดาวจร (transit) ======
    transit_good: List[str] = []
    transit_warn: List[str] = []
    for line in t_good[:2]:
        transit_good.append(line)
    for line in t_warn[:2]:
        transit_warn.append(line)
    if not transit_good and not transit_warn and t_neutral:
        transit_good.append(t_neutral[0])

    has_natal = bool(natal_good or natal_warn)
    has_transit = bool(transit_good or transit_warn)
    if not has_natal and not has_transit:
        return None

    # backward-compat: รวมเป็น good/warn flat (เผื่อ template เก่า)
    flat_good = [f"ดวงเดิม: {x}" for x in natal_good] + [f"ดาวจร: {x}" for x in transit_good]
    flat_warn = [f"ดวงเดิม: {x}" for x in natal_warn] + [f"ดาวจร: {x}" for x in transit_warn]

    return {
        "key": area_key,
        "title": info["title"],
        "natal": {"good": natal_good, "warn": natal_warn},
        "transit": {"good": transit_good, "warn": transit_warn},
        "has_natal": has_natal,
        "has_transit": has_transit,
        # backward-compat
        "good": flat_good,
        "warn": flat_warn,
    }


def _build_warnings(
    transit_summary: Optional[dict],
    transit_lord_summary: Optional[dict],
    has_flip_yoga: bool,
) -> List[str]:
    warnings: List[str] = []
    if transit_summary:
        for w in transit_summary.get("warn_items", [])[:3]:
            theme = MODERN_NATAL_THEME.get(w["natal_planet"], "")
            short = _strip_modifier(w["short"])
            line = f"{short} — เกี่ยวกับ{theme}" if theme else short
            if has_flip_yoga:
                line, _ = _flip_warning_with_yoga(line, True)
            warnings.append(line)

    if transit_lord_summary:
        for w in transit_lord_summary.get("warn_items", [])[:2]:
            line = _strip_modifier(w["prediction"])
            if has_flip_yoga:
                line, _ = _flip_warning_with_yoga(line, True)
            warnings.append(line)

    seen = set()
    unique = []
    for w in warnings:
        key = w[:30]
        if key not in seen:
            seen.add(key)
            unique.append(w)
    return unique[:5]


def _build_opportunities(
    transit_summary: Optional[dict],
    transit_lord_summary: Optional[dict],
) -> List[str]:
    opps: List[str] = []
    if transit_summary:
        for g in transit_summary.get("good_items", [])[:3]:
            theme = MODERN_NATAL_THEME.get(g["natal_planet"], "")
            short = _strip_modifier(g["short"])
            opps.append(f"{short} — ในด้าน{theme}" if theme else short)
    if transit_lord_summary:
        for g in transit_lord_summary.get("good_items", [])[:2]:
            opps.append(_strip_modifier(g["prediction"]))
    seen = set()
    unique = []
    for o in opps:
        key = o[:30]
        if key not in seen:
            seen.add(key)
            unique.append(o)
    return unique[:5]


def _build_closing(tone_class: str, has_flip_yoga: bool, seed: str) -> str:
    if has_flip_yoga and tone_class == "heavy":
        # โยคพลิก + โทนหนัก → ใช้ closing แบบให้กำลังใจเป็นพิเศษ
        base = _pick(CLOSINGS_HEAVY, seed + "ch")
        return base + (
            " และอย่าลืม — ดวงพื้นฐานของคุณมีเกณฑ์พลิกร้ายเป็นดีอยู่ "
            "เรื่องหนัก ๆ ที่มา จะออกผลดีในอีกไม่นาน"
        )
    if tone_class == "good":
        return _pick(CLOSINGS_GOOD, seed + "cg")
    if tone_class == "heavy":
        return _pick(CLOSINGS_HEAVY, seed + "ch")
    if tone_class == "mixed":
        return _pick(CLOSINGS_MIXED, seed + "cm")
    return _pick(CLOSINGS_NEUTRAL, seed + "cn")


# ============================================================
# Public API
# ============================================================
def compose_oracle_reading(
    person_name: str,
    transit_summary: Optional[dict] = None,
    natal_lord_summary: Optional[dict] = None,
    transit_lord_summary: Optional[dict] = None,
    yogas: Optional[List[Yoga]] = None,
    dignities: Optional[Dict[str, PlanetDignity]] = None,
    astro_patterns_matched: Optional[List] = None,
    seed: str = "default",
    transit_date_label: Optional[str] = None,
) -> dict:
    yogas = yogas or []
    dignities = dignities or {}
    astro_patterns_matched = astro_patterns_matched or []

    # โยคที่มีคุณสมบัติ "พลิกดวง" — ใช้ปรับคำเตือน
    flip_yoga_names = {"นิจภังคราชโยค", "อุดมเกณฑ์", "ปทุมเกณฑ์", "นิจภังค"}
    has_flip_yoga = (
        any(y.name in flip_yoga_names for y in yogas)
        or any(p.name in flip_yoga_names or "นิจภังค" in p.name
               for p in astro_patterns_matched)
    )

    address = _person_address(person_name)
    greeting, tone_class = _build_overall(
        transit_summary, natal_lord_summary, transit_lord_summary,
        yogas, address, seed,
    )

    # ใช้ astro_patterns เป็นแหล่งหลัก ถ้ามี — ไม่งั้น fallback dignities yogas
    if astro_patterns_matched:
        yoga_messages = _build_yoga_messages_from_patterns(astro_patterns_matched)
    else:
        yoga_messages = _build_yoga_messages(yogas)
    headline = _build_headline(transit_summary, has_flip_yoga, seed)

    life_areas = []
    for key in ["money", "career", "love", "family", "health", "growth", "change"]:
        sec = _build_life_area_section(
            key, natal_lord_summary, transit_lord_summary, has_flip_yoga
        )
        if sec:
            life_areas.append(sec)

    opportunities = _build_opportunities(transit_summary, transit_lord_summary)
    warnings = _build_warnings(transit_summary, transit_lord_summary, has_flip_yoga)
    closing = _build_closing(tone_class, has_flip_yoga, seed)

    # สรุปกำลังดาวรายดวง — แสดงครบทุกดวง (เด่น/อ่อน/กลาง)
    # เรียงตามกำลัง: อุจน์ > เกษตร > มูล > มิตร > สมพล > ประ/ศัตรู > นิจ
    dignity_highlights = []
    for name, d in dignities.items():
        dignity_highlights.append({
            "planet": name,
            "rasi": d.rasi_name,
            "label": d.label,
            "dignity": d.dignity,
            "strength": d.strength,
            "is_strong": d.is_strong,
            "is_weak": d.is_weak,
            "is_exalted": d.is_exalted,
            "is_debilitated": d.is_debilitated,
        })
    dignity_highlights.sort(key=lambda x: -x["strength"])

    return {
        "address": address,
        "tone_class": tone_class,
        "greeting": greeting,
        "yoga_messages": yoga_messages,
        "headline": headline,
        "life_areas": life_areas,
        "opportunities": opportunities,
        "warnings": warnings,
        "dignity_highlights": dignity_highlights,
        "has_flip_yoga": has_flip_yoga,
        "closing": closing,
        "transit_date_label": transit_date_label,
    }
