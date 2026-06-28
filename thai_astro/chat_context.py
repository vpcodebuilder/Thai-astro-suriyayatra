"""สร้าง context สำหรับ chat AI โหร — เลือก facts จากดวงตามคำถาม

หลักการ:
1. classify_intent(question)  → 1-2 หมวดจาก 5 หมวด
2. build_context(chart, intents, today, transit_chart)  → dict ของ facts
3. format_for_prompt(context)  → ข้อความสั้นภาษาไทย ส่งเข้า Claude prompt

5 หมวด:
  money    = การเงิน (ภพ 2, 11)
  career   = การงาน/อาชีพ (ภพ 6, 10)
  love     = ความรัก/คู่ครอง (ภพ 5, 7)
  health   = สุขภาพ (ภพ 1, 6, 8)
  warning  = เกณฑ์ต้องระวัง (ภพ 8, 12 + กาลกิณี + ดาวจรหนัก)

`warning` จะถูก auto-trigger เพิ่ม ถ้าตรวจพบ severity สูงหรือกาลกิณี
แม้คำถามจะไม่ได้พูดถึงตรง ๆ
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

from .chart import Chart
from .taksa import compute_taksa, Taksa
from .dignities import compute_all_dignities, PlanetDignity
from .transit_prophecy import find_transit_aspects, generate_summary
from .bhava_lord_prophecy import (
    predict_natal_lords,
    predict_transit_lords,
    BhavaLordPrediction,
)

# ============================================================
# 1. Intent classification
# ============================================================

INTENT_KEYWORDS: Dict[str, List[str]] = {
    "money": [
        "เงิน", "ทรัพย์", "หนี้", "ลงทุน", "รวย", "จน", "การเงิน",
        "โชค", "ลาภ", "รายได้", "ทุน", "ขาดทุน", "กำไร", "ค้าขาย",
        "หุ้น", "ออม", "ฝัน",
    ],
    "career": [
        "งาน", "อาชีพ", "เปลี่ยนงาน", "ลาออก", "ตำแหน่ง", "ลูกค้า",
        "ธุรกิจ", "สมัครงาน", "ย้ายงาน", "เลื่อนตำแหน่ง", "เจ้านาย",
        "บริษัท", "ทำงาน", "หางาน", "เริ่มงาน", "เปิดร้าน", "เคลื่อนย้าย",
    ],
    "love": [
        "รัก", "คู่", "แต่งงาน", "แฟน", "คนรัก", "สามี", "ภรรยา",
        "ความรัก", "มีคู่", "เลิก", "หย่า", "นอกใจ", "ครอบครัว",
    ],
    "health": [
        "สุขภาพ", "ป่วย", "โรค", "หมอ", "ผ่าตัด", "แข็งแรง",
        "เจ็บ", "ปวด", "นอน", "เครียด", "ฟื้น", "รักษา",
    ],
    "warning": [
        "ระวัง", "อันตราย", "เคราะห์", "ปลอดภัย", "อุบัติเหตุ",
        "ภัย", "ทำลาย", "เสีย", "ร้าย", "แย่", "ผิดพลาด", "ล้มเหลว",
    ],
}

# ภพหลักของแต่ละ intent (1-12)
INTENT_BHAVAS: Dict[str, List[int]] = {
    "money":   [2, 11],
    "career":  [6, 10],
    "love":    [5, 7],
    "health":  [1, 6, 8],
    "warning": [8, 12],
}


def classify_intent(question: str) -> List[str]:
    """จับคำถาม → list ของ intent (1-2 หมวด)

    ถ้าจับไม่ได้เลย → คืน ["career"] เป็น default (เพราะคำถามทั่วไปมักเป็นเรื่องชีวิต/อาชีพ)
    """
    q = question.strip()
    hits: Dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in q)
        if count > 0:
            hits[intent] = count

    if not hits:
        return ["career"]

    # เรียงตามจำนวน hit (มาก→น้อย) เลือก 1-2 หมวด
    sorted_intents = sorted(hits.items(), key=lambda x: -x[1])
    primary = sorted_intents[0][0]
    out = [primary]
    if len(sorted_intents) >= 2 and sorted_intents[1][1] >= sorted_intents[0][1] / 2:
        out.append(sorted_intents[1][0])
    return out


# ============================================================
# 2. Build context
# ============================================================

@dataclass
class ChatContext:
    """facts ที่ดึงมาจากดวงเฉพาะ intent ที่เกี่ยวกับคำถาม"""
    question: str
    intents: List[str]
    auto_warning_triggered: bool

    # ข้อมูลพื้นฐาน
    age: int
    ascendant_rasi: str
    chart_lord: str
    chart_lord_dignity: str

    # ทักษา (timing)
    current_dasa_planet: str
    current_dasa_bhava: str         # ชื่อบริวาร เช่น "ศรี"
    current_dasa_tone: str          # good/bad
    age_in_current_dasa: int
    next_dasa_planet: str
    years_until_next_dasa: int
    taksa_summary: str

    # ดาวจร (top 3 + warnings)
    transit_headline: str
    transit_top: List[dict]         # top 3 aspect ที่ severity สูง
    transit_warnings: List[dict]    # aspect tone=heavy/warning
    transit_severity_total: int     # ตัวเลขรวม สำหรับ auto-trigger warning

    # เจ้าเรือนภพที่เกี่ยวกับคำถาม
    relevant_natal_lords: List[dict]    # เจ้าเรือน X ไปอยู่ภพ Y
    relevant_transit_lords: List[dict]  # เจ้าเรือนเดิม ขณะนี้ดาวจรอยู่ภพไหน

    # ดาวเด่นในดวง (top 3 ตามกำลัง)
    top_dignities: List[dict]


def build_context(
    chart: Chart,
    question: str,
    today: Optional[date] = None,
    transit_chart: Optional[Chart] = None,
) -> ChatContext:
    """รวบรวม facts จากดวงเฉพาะที่เกี่ยวกับคำถาม

    chart           = ดวงกำเนิด
    question        = คำถามของผู้ใช้
    today           = วันที่อ้างอิง (ถ้า None ใช้วันนี้ ตามเวลาไทย)
    transit_chart   = ดวงจร (ถ้า None ใช้ "ตอนนี้" ที่กรุงเทพฯ)
    """
    if today is None:
        thai_tz = timezone(timedelta(hours=7))
        today = datetime.now(thai_tz).date()

    if transit_chart is None:
        now = datetime.now(timezone(timedelta(hours=7)))
        transit_chart = Chart.calculate(
            year=now.year, month=now.month, day=now.day,
            hour=now.hour, minute=now.minute,
            province="กรุงเทพมหานคร",
        )

    intents = classify_intent(question)

    # ---- ข้อมูลพื้นฐาน ----
    asc_rasi = chart.ascendant.zodiac.rasi
    asc_rasi_name = chart.ascendant.zodiac.rasi_name
    dignities = compute_all_dignities(chart.planets)
    chart_lord = chart.chart_lord
    chart_lord_dig = dignities.get(chart_lord)

    # ---- ทักษา ----
    taksa = compute_taksa(
        chart.ce_year, chart.month, chart.day,
        chart.hour, chart.minute,
        today=today,
    )
    years_to_next = taksa.next_dasa_age - taksa.year_of_life

    # ---- ดาวจร ----
    aspects = find_transit_aspects(
        natal_planets=chart.planets,
        transit_planets=transit_chart.planets,
        include_minor=False,
    )
    transit_summary = generate_summary(aspects)
    severity_total = sum(a.severity for a in aspects if a.severity >= 2)

    # ---- Auto-trigger warning ----
    auto_warn = False
    explicit_warning = "warning" in intents
    n_warn = transit_summary["tones"]["heavy"] + transit_summary["tones"]["warning"]
    if (
        n_warn >= 3
        or severity_total >= 8
        or taksa.current_dasa_bhava.name == "กาลกิณี"
    ):
        if not explicit_warning:
            intents = intents + ["warning"]
            auto_warn = True

    # ---- เจ้าเรือนภพที่เกี่ยวกับคำถาม ----
    bhavas_of_interest: Set[int] = set()
    for it in intents:
        bhavas_of_interest.update(INTENT_BHAVAS.get(it, []))

    natal_lords = predict_natal_lords(asc_rasi, chart.planets, dignities=dignities)
    transit_dignities = compute_all_dignities(transit_chart.planets)
    transit_lords = predict_transit_lords(
        asc_rasi, transit_chart.planets, dignities=transit_dignities,
    )

    relevant_natal = [
        _pred_to_dict(p) for p in natal_lords if p.lord_bhava in bhavas_of_interest
    ]
    relevant_transit = [
        _pred_to_dict(p) for p in transit_lords if p.lord_bhava in bhavas_of_interest
    ]

    # ---- ดาวเด่นในดวง ----
    sorted_dig = sorted(
        dignities.items(), key=lambda kv: -kv[1].strength
    )
    top_dig = [
        {
            "planet": name, "rasi": d.rasi_name,
            "dignity": d.dignity, "label": d.label, "strength": d.strength,
        }
        for name, d in sorted_dig[:3]
    ]

    # ---- compact top transit + warnings ----
    top_transit = [
        {
            "transit_planet": t["transit_planet"],
            "natal_planet":   t["natal_planet"],
            "aspect_type":    t["aspect_type"],
            "tone":           t["tone_label"],
            "theme":          t["theme"],
            "duration":       t["duration"],
        }
        for t in transit_summary["top_items"][:3]
    ]
    warnings_list = [
        {
            "transit_planet": w["transit_planet"],
            "natal_planet":   w["natal_planet"],
            "aspect_type":    w["aspect_type"],
            "theme":          w.get("theme", ""),
        }
        for w in transit_summary["warn_items"][:3]
    ]

    return ChatContext(
        question=question,
        intents=intents,
        auto_warning_triggered=auto_warn,
        age=taksa.age_completed_years,
        ascendant_rasi=asc_rasi_name,
        chart_lord=chart_lord,
        chart_lord_dignity=chart_lord_dig.label if chart_lord_dig else "",
        current_dasa_planet=taksa.current_dasa_planet,
        current_dasa_bhava=taksa.current_dasa_bhava.name,
        current_dasa_tone=taksa.current_dasa_bhava.tone,
        age_in_current_dasa=taksa.age_in_current_dasa,
        next_dasa_planet=taksa.next_dasa_planet,
        years_until_next_dasa=years_to_next,
        taksa_summary=taksa.overall_summary,
        transit_headline=transit_summary["headline"],
        transit_top=top_transit,
        transit_warnings=warnings_list,
        transit_severity_total=severity_total,
        relevant_natal_lords=relevant_natal,
        relevant_transit_lords=relevant_transit,
        top_dignities=top_dig,
    )


def _pred_to_dict(p: BhavaLordPrediction) -> dict:
    return {
        "lord_bhava": p.lord_bhava,
        "lord_bhava_name": p.lord_bhava_name,
        "lord_planet": p.lord_planet,
        "located_bhava": p.located_bhava,
        "located_bhava_name": p.located_bhava_name,
        "tone": p.tone_label,
        "dignity": p.dignity_label,
        "text": p.prediction,
    }


# ============================================================
# 3. Format for prompt
# ============================================================

INTENT_LABEL_TH = {
    "money":   "การเงิน",
    "career":  "การงาน/อาชีพ",
    "love":    "ความรัก/คู่ครอง",
    "health":  "สุขภาพ",
    "warning": "เกณฑ์ต้องระวัง",
}


def format_for_prompt(ctx: ChatContext) -> str:
    """render context → ข้อความสั้นภาษาไทย ใส่ใน prompt ของ Claude

    เป้าหมาย: ประหยัด token แต่ครบ facts ที่ต้องใช้ตอบ
    """
    lines: List[str] = []
    intent_str = " + ".join(INTENT_LABEL_TH.get(i, i) for i in ctx.intents)
    lines.append(f"[คำถามผู้ใช้] {ctx.question}")
    lines.append(f"[หมวด] {intent_str}"
                 + ("  (ระบบตรวจพบเกณฑ์ระวัง จึงเสริมหมวดนี้)" if ctx.auto_warning_triggered else ""))
    lines.append("")
    lines.append(f"[ดวงพื้นฐาน] ลัคนา{ctx.ascendant_rasi}  เจ้าชะตา={ctx.chart_lord} ({ctx.chart_lord_dignity})  อายุ {ctx.age} ปี")

    # ดาวเด่น 3 ดวง
    dig_str = ", ".join(
        f"{d['planet']}({d['dignity']})" for d in ctx.top_dignities
    )
    lines.append(f"[ดาวเด่น] {dig_str}")

    # ทักษา (timing)
    lines.append(
        f"[ทักษาเสวยอายุ] {ctx.current_dasa_planet} ตำแหน่ง{ctx.current_dasa_bhava}"
        f" (โทน {ctx.current_dasa_tone}) ปีที่ {ctx.age_in_current_dasa} ในช่วงนี้"
        f" — อีก {ctx.years_until_next_dasa} ปีจะเปลี่ยนเป็น {ctx.next_dasa_planet}"
    )
    lines.append(f"  สรุปทักษา: {ctx.taksa_summary}")
    lines.append("")

    # เจ้าเรือนภพที่เกี่ยวกับคำถาม
    if ctx.relevant_natal_lords:
        lines.append("[เจ้าเรือนพื้นฐาน — เฉพาะภพที่เกี่ยวคำถาม]")
        for p in ctx.relevant_natal_lords:
            lines.append(
                f"  ภพ{p['lord_bhava']} {p['lord_bhava_name']} (เจ้าเรือน={p['lord_planet']})"
                f" → สถิตภพ{p['located_bhava']} {p['located_bhava_name']}"
                f"  โทน:{p['tone']}  {('('+p['dignity']+')') if p['dignity'] else ''}"
            )

    if ctx.relevant_transit_lords:
        lines.append("[เจ้าเรือนเดิม ขณะดาวจร]")
        for p in ctx.relevant_transit_lords:
            lines.append(
                f"  ภพ{p['lord_bhava']} {p['lord_bhava_name']} (เจ้าเรือน={p['lord_planet']})"
                f" → ขณะนี้อยู่ภพ{p['located_bhava']} {p['located_bhava_name']}"
                f"  โทน:{p['tone']}"
            )
    lines.append("")

    # ดาวจรเด่น
    lines.append(f"[ดาวจรขณะนี้] {ctx.transit_headline}")
    for t in ctx.transit_top:
        lines.append(
            f"  • {t['transit_planet']}จร {t['aspect_type']} {t['natal_planet']}เดิม"
            f"  เรื่อง:{t['theme']}  โทน:{t['tone']}  ({t['duration']})"
        )

    # warnings
    if ctx.transit_warnings and "warning" in ctx.intents:
        lines.append("[เกณฑ์ระวัง — ดาวจรหนัก]")
        for w in ctx.transit_warnings:
            lines.append(
                f"  • {w['transit_planet']}จร {w['aspect_type']} {w['natal_planet']}เดิม"
                f"  ({w['theme']})"
            )

    lines.append("")
    lines.append("[กติกาตอบ] ใช้ facts ข้างต้นเท่านั้น ตอบเข้าประเด็นคำถาม อย่าแต่งดาวเพิ่ม"
                 " อย่าตอบเรื่องที่ไม่เกี่ยวกับหมวดที่ระบุ"
                 " ถ้ามีเกณฑ์ระวัง ให้เตือนตรง ๆ แบบเห็นใจ ไม่ใช่ขู่")
    return "\n".join(lines)
