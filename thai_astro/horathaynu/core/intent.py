"""Phase 1 — Intent detection สำหรับโหรทายหนู

แตกคำถามเป็น 3 มิติ:
    1. intent_type — ผู้ถามต้องการอะไร?
        yes_no   = "จะ...ไหม / ได้ไหม / หรือเปล่า"
        when     = "เมื่อไหร่ / กี่วัน / กี่เดือน"
        where    = "ที่ไหน / อยู่ไหน"
        who      = "ใคร / คนไหน"
        why      = "ทำไม / สาเหตุ"
        how      = "อย่างไร / ทำยังไง"
        outcome  = "ผลจะเป็นยังไง" (default)

    2. polarity — ผู้ถามใจเอนไปทางไหน?
        hope     = อยาก / หวัง / ต้องการ
        worry    = กลัว / ห่วง / กังวล
        neutral  = (ไม่ระบุ)

    3. topic — noun ที่ถาม (สำหรับ contextualize)

ตัวอย่าง:
    "จะได้งานไหม"                → (yes_no, hope, "งาน")
    "เมื่อไหร่จะได้งาน"             → (when, hope, "งาน")
    "ลูกอยู่ที่ไหน"                  → (where, worry, "ลูก")
    "ทำไมเขาไม่ตอบ"                → (why, worry, "การติดต่อ")
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionIntent:
    intent_type: str    # yes_no / when / where / who / why / how / outcome
    polarity: str       # hope / worry / neutral
    topic: str          # คำนามหลัก (เช่น "งาน", "ความรัก")


# ===========================================================================
# Patterns เรียงตามความเฉพาะเจาะจง — เช็คอันแรก ๆ มี priority สูงกว่า
# ===========================================================================

# yes_no patterns
YES_NO_PATTERNS = [
    "ไหม", "มั้ย", "หรือเปล่า", "รึเปล่า", "หรือไม่",
    "ได้ไหม", "ได้มั้ย", "จะได้", "จะ", "จะมี", "จะเกิด",
]

# when patterns
WHEN_PATTERNS = [
    "เมื่อไหร่", "เมื่อใด", "ตอนไหน", "กี่วัน", "กี่เดือน", "กี่ปี",
    "วันไหน", "เดือนไหน", "ปีไหน", "ช่วงไหน", "เร็วๆนี้", "นานแค่ไหน",
    "ภายในเมื่อไหร่", "ต้องรออีกนาน",
]

# where patterns
WHERE_PATTERNS = [
    "ที่ไหน", "อยู่ไหน", "อยู่ที่ไหน", "ทำที่ไหน", "ในนี้ไหม",
    "นอกบ้านไหม", "ที่บ้านไหม",
]

# who patterns
WHO_PATTERNS = [
    "ใคร", "คนไหน", "คนนี้", "ใครเป็น", "ผู้ใด",
]

# why patterns
WHY_PATTERNS = [
    "ทำไม", "เพราะอะไร", "เพราะเหตุใด", "สาเหตุ", "เหตุใด",
]

# how patterns
HOW_PATTERNS = [
    "อย่างไร", "ยังไง", "ทำยังไง", "ทำอย่างไร", "วิธี",
    "แก้ยังไง", "เริ่มยังไง",
]

# polarity — hope
HOPE_PATTERNS = [
    "อยาก", "หวัง", "ต้องการ", "ปรารถนา", "อยากให้",
    "ขอให้", "หวังว่า",
]

# polarity — worry
WORRY_PATTERNS = [
    "กลัว", "ห่วง", "กังวล", "วิตก", "หวั่น", "เป็นห่วง",
    "เครียด", "ทุกข์", "เสีย", "พลาด", "พัง", "เลิก",
]


def detect_intent_type(q: str) -> str:
    """ตรวจ intent_type จากคำถาม.

    ลำดับเช็ค: when > where > who > why > how > yes_no > outcome (default)
    เหตุผล: คำถามอาจมีหลาย marker — when แม่นกว่า yes_no
    """
    for kw in WHEN_PATTERNS:
        if kw in q:
            return "when"
    for kw in WHERE_PATTERNS:
        if kw in q:
            return "where"
    for kw in WHO_PATTERNS:
        if kw in q:
            return "who"
    for kw in WHY_PATTERNS:
        if kw in q:
            return "why"
    for kw in HOW_PATTERNS:
        if kw in q:
            return "how"
    for kw in YES_NO_PATTERNS:
        if kw in q:
            return "yes_no"
    return "outcome"


def detect_polarity(q: str) -> str:
    """ตรวจ polarity (hope/worry/neutral)."""
    has_hope = any(kw in q for kw in HOPE_PATTERNS)
    has_worry = any(kw in q for kw in WORRY_PATTERNS)
    if has_worry and not has_hope:
        return "worry"
    if has_hope and not has_worry:
        return "hope"
    if has_hope and has_worry:
        return "worry"   # worry มี weight สูงกว่า (โดน push)
    return "neutral"


def parse_intent(question: str, topic: str = "") -> QuestionIntent:
    """แปลงคำถามเป็น QuestionIntent.

    topic ถูก derive จากภายนอก (จาก category mapping) — ส่งเข้ามา
    """
    q = question.strip().lower()
    return QuestionIntent(
        intent_type=detect_intent_type(q),
        polarity=detect_polarity(q),
        topic=topic or "เรื่องนี้",
    )


# ===========================================================================
# Render helper — ใช้สำหรับสร้าง headline ตาม intent
# ===========================================================================
INTENT_HEADLINE_TEMPLATES: dict[str, dict[str, str]] = {
    "yes_no": {
        "hope":    "🤔 คุณอยากรู้ว่าจะได้{topic}ไหม...",
        "worry":   "😟 คุณกังวลว่า{topic}จะเป็นยังไง...",
        "neutral": "🔮 คำถามแบบ yes/no — มาดูคำตอบกัน",
    },
    "when": {
        "hope":    "⏳ คุณอยากรู้ว่าเมื่อไหร่จะได้{topic}...",
        "worry":   "⏰ คุณห่วงว่าจะรอ{topic}อีกนานแค่ไหน...",
        "neutral": "⏳ มาดูช่วงเวลาที่{topic}จะเข้ามา",
    },
    "where": {
        "hope":    "📍 คุณกำลังหา{topic}อยู่...",
        "worry":   "📍 คุณห่วงว่า{topic}อยู่ที่ไหน...",
        "neutral": "📍 มาดูตำแหน่งของ{topic}",
    },
    "who": {
        "hope":    "👤 คุณอยากรู้ว่า{topic}คือใคร...",
        "worry":   "👤 คุณสงสัยว่า{topic}เป็นใคร...",
        "neutral": "👤 มาดูว่า{topic}เกี่ยวข้องกับใคร",
    },
    "why": {
        "hope":    "❓ คุณอยากเข้าใจว่าทำไม{topic}...",
        "worry":   "❓ คุณกังวลกับสาเหตุของ{topic}...",
        "neutral": "❓ มาดูเหตุของ{topic}",
    },
    "how": {
        "hope":    "🛠 คุณอยากรู้วิธีทำให้{topic}สำเร็จ...",
        "worry":   "🛠 คุณกังวลว่าจะแก้{topic}ยังไง...",
        "neutral": "🛠 มาดูวิธีดำเนินกับ{topic}",
    },
    "outcome": {
        "hope":    "🌟 คุณอยากรู้ผลของ{topic}...",
        "worry":   "🌫 คุณกังวลกับผลของ{topic}...",
        "neutral": "🌟 มาดูผลของ{topic}",
    },
}


def make_intent_headline(intent: QuestionIntent) -> str:
    """สร้างประโยคหัวข้อตาม intent."""
    tmpl_set = INTENT_HEADLINE_TEMPLATES.get(intent.intent_type, INTENT_HEADLINE_TEMPLATES["outcome"])
    tmpl = tmpl_set.get(intent.polarity, tmpl_set.get("neutral", "🔮 คำถามของคุณ"))
    return tmpl.format(topic=intent.topic)


__all__ = ["QuestionIntent", "parse_intent", "make_intent_headline"]
