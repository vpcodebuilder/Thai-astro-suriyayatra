"""หาฤกษ์ (Muhurta) — Orchestrator

รวบรวมข้อมูล:
    - วาร (Wan) จากวัน — ดาวประจำวัน + คุณภาพ
    - ดิถี (Tithi) — ขึ้น/แรม + คุณภาพ
    - นักษัตร (Nakshatra) — 27 ฤกษ์จากตำแหน่งจันทร์
    - กาลโยค (Kalayok) — ธงชัย/อธิบดี/อุบาทว์/โลกาวินาศ
    - เกณฑ์พิเศษ (Special) — กนกนารี/กนกกุญชร/จักขุมายา
    - คะแนนกิจกรรม (optional)
แล้วสรุปเป็น **verdict** + activity suggestions

ตำราอ้างอิง:
    - mahamongkol.com/m/content.php?id=491
    - horapayakorn.com (id=539993303)
    - อ.เทพย์ สาริกบุตร — หลักเกณฑ์ฤกษ์
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .chart import Chart
from .nakshatra import compute_from_moon_position, NakshatraPosition
from .navamsa import chart_to_navamsa_view
from .kalayok import compute_kalayok, KalayokYear, match_wan, match_dithi, match_roek
from .muhurta_criteria import (
    evaluate_special_criteria, CriterionMatch, event_score, EVENTS,
    planet_house_from_lakkana,
)
from .lunar import compute_lunar_date, LunarDate


# ============================================================
# วาร (Wan) — ดาวประจำวัน + คุณภาพ
# ============================================================
# Python weekday: Mon=0..Sun=6 → Wan number (1=อา..7=ส)
WEEKDAY_TO_WAN = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
WAN_PLANET = {
    1: "อาทิตย์", 2: "จันทร์", 3: "อังคาร", 4: "พุธ",
    5: "พฤหัสบดี", 6: "ศุกร์", 7: "เสาร์",
}
# คุณภาพวาร (ทั่วไป — ตำราหลายเล่มไม่ตรงกัน ใช้ค่ามาตรฐาน)
WAN_QUALITY = {
    1: ("กลาง",   "วันอาทิตย์ ดีสำหรับงานราชการ ตำแหน่ง"),
    2: ("ดี",     "วันจันทร์ ดีสำหรับงานละมุน แต่งงาน เปิดร้าน"),
    3: ("ระวัง",  "วันอังคาร ดุ เหมาะกิจกล้าหาญ ไม่ควรแต่งงาน"),
    4: ("ดี",     "วันพุธ ดีสำหรับการค้า สัญญา เจรจา"),
    5: ("ดีมาก",  "วันพฤหัสฯ ดีที่สุด เหมาะการมงคลทุกประเภท"),
    6: ("ดี",     "วันศุกร์ ดีสำหรับศิลปะ แต่งงาน หาคู่"),
    7: ("ระวัง",  "วันเสาร์ หนัก เหมาะงานหนัก ไม่เหมาะมงคล"),
}


# ============================================================
# ดิถี — คุณภาพ
# ============================================================
# ขึ้น 1-15 ค่ำ = tithi 0-14, แรม 1-15 ค่ำ = tithi 15-29
# Auspicious tithis (general): 2, 3, 5, 7, 10, 11, 13
# Inauspicious: 4, 9, 14 (พิเศษ tithi 9 = "นวมี" หนัก)
TITHI_QUALITY_WAXING = {
    1: "กลาง", 2: "ดี", 3: "ดี", 4: "ระวัง", 5: "ดี",
    6: "ดี", 7: "ดี", 8: "กลาง", 9: "ระวัง", 10: "ดี",
    11: "ดี", 12: "ดี", 13: "ดี", 14: "ระวัง", 15: "ดีมาก",  # เพ็ญ
}
TITHI_QUALITY_WANING = {
    1: "กลาง", 2: "ดี", 3: "ดี", 4: "ระวัง", 5: "กลาง",
    6: "กลาง", 7: "ระวัง", 8: "กลาง", 9: "ระวัง", 10: "กลาง",
    11: "กลาง", 12: "ระวัง", 13: "ระวัง", 14: "ระวัง", 15: "ระวัง",  # ดับ
}


def tithi_quality(lunar: LunarDate) -> str:
    table = TITHI_QUALITY_WAXING if lunar.waxing else TITHI_QUALITY_WANING
    return table.get(lunar.day_in_phase, "กลาง")


# ============================================================
# Result dataclasses
# ============================================================
@dataclass
class MuhurtaResult:
    """ผลลัพธ์การหาฤกษ์ ณ ขณะหนึ่ง"""
    when: datetime
    province: str
    chart: Chart

    # วาร
    wan: int
    wan_planet: str
    wan_quality: str
    wan_remark: str

    # ดิถี
    lunar: LunarDate
    tithi_quality: str

    # นักษัตร
    nakshatra: NakshatraPosition

    # กาลโยค
    kalayok: KalayokYear
    kalayok_matches: Dict[str, Dict[str, bool]]  # {component: {entry: hit}}

    # เกณฑ์พิเศษ
    special_criteria: List[CriterionMatch]

    # นวางค์
    navamsa: Dict                                # {planet: NavamsaPosition}
    vargottama_planets: List[str]                # ดาวที่เป็น Vargottama

    # Verdict
    score: int
    verdict: str                                 # "ดีเยี่ยม"/"ดี"/"กลาง"/"ระวัง"
    activity_suggestions: List[str]
    cautions: List[str]

    # Event-specific (optional)
    event_key: Optional[str] = None
    event_score: Dict = field(default_factory=dict)


# ============================================================
# Score → Verdict mapping
# ============================================================
def _to_verdict(score: int) -> str:
    if score >= 8:
        return "ดีเยี่ยม"
    if score >= 4:
        return "ดี"
    if score >= 0:
        return "กลาง"
    if score >= -3:
        return "ระวัง"
    return "ไม่เหมาะ"


# ============================================================
# Main computation
# ============================================================
def compute_muhurta(
    when: datetime,
    province: str = "กรุงเทพมหานคร",
    event_key: Optional[str] = None,
) -> MuhurtaResult:
    """คำนวณฤกษ์ ณ datetime ที่ระบุ"""
    chart = Chart.calculate(
        when.year, when.month, when.day,
        when.hour, when.minute,
        province=province,
    )

    # วาร
    py_wd = when.weekday()
    wan = WEEKDAY_TO_WAN[py_wd]
    wan_planet = WAN_PLANET[wan]
    wan_q, wan_remark = WAN_QUALITY[wan]

    # ดิถี + ปฏิทินจันทรคติ
    sun_rasi = chart.planets["อาทิตย์"].zodiac.rasi
    lunar = compute_lunar_date(chart.desire, sun_rasi)
    t_q = tithi_quality(lunar)

    # นักษัตร (จากตำแหน่งจันทร์)
    moon_arcmin = chart.planets["จันทร์"].somput
    nak = compute_from_moon_position(moon_arcmin)

    # กาลโยค
    cs_year = chart.desire.surathin.thaloengsok_cs_year
    kalayok = compute_kalayok(cs_year)
    kalayok_matches = {
        "wan": match_wan(kalayok, wan),
        "dithi": match_dithi(kalayok, lunar.tithi),
        "roek": match_roek(kalayok, nak.number),
    }

    # เกณฑ์พิเศษ
    specials = evaluate_special_criteria(chart)

    # นวางค์
    nav_view = chart_to_navamsa_view(chart)
    vargottama = [name for name, pos in nav_view.items() if pos.is_vargottama]

    # ============================================================
    # Score & verdict
    # ============================================================
    score = 0
    suggestions: List[str] = []
    cautions: List[str] = []

    # วาร
    if wan_q == "ดีมาก":
        score += 3
    elif wan_q == "ดี":
        score += 2
    elif wan_q == "ระวัง":
        score -= 2
    suggestions.append(f"วาร: {wan_remark}")

    # ดิถี
    if t_q == "ดีมาก":
        score += 3
    elif t_q == "ดี":
        score += 2
    elif t_q == "ระวัง":
        score -= 2

    # นักษัตร
    if nak.is_auspicious:
        score += 2
        suggestions.append(f"{nak.roek_name} ({nak.name}): {nak.meaning}")
    else:
        score -= 2
        cautions.append(f"{nak.roek_name} ({nak.name}): {nak.meaning}")

    # กาลโยค: ถ้าตก ธงชัย/อธิบดี = ดี; อุบาทว์/โลกาวินาศ = ระวัง
    for comp, hits in kalayok_matches.items():
        if hits["thongchai"]:
            score += 2
            suggestions.append(f"ตรงกาลโยค ธงชัย ({comp}) — มงคล")
        if hits["athibodi"]:
            score += 1
            suggestions.append(f"ตรงกาลโยค อธิบดี ({comp}) — มงคล")
        if hits["ubat"]:
            score -= 2
            cautions.append(f"ตรงกาลโยค อุบาทว์ ({comp}) — เลี่ยง")
        if hits["lokawinat"]:
            score -= 3
            cautions.append(f"ตรงกาลโยค โลกาวินาศ ({comp}) — อันตราย")

    # เกณฑ์พิเศษ
    for sc in specials:
        if sc.matched and sc.tone == "good":
            score += 2
            suggestions.append(f"{sc.name}: {sc.detail}")
        elif sc.matched and sc.tone == "warning":
            score -= 3
            cautions.append(f"{sc.name}: {sc.detail}")

    # Vargottama: ถ้ามีดาวมงคลเป็น Vargottama → ดี
    for p in vargottama:
        if p in ("พฤหัสบดี", "ศุกร์", "พุธ", "จันทร์"):
            score += 1
            suggestions.append(f"{p} เป็น Vargottama — กำลังแข็ง")

    # Event-specific
    ev_result = {}
    if event_key:
        ev_result = event_score(chart, event_key)
        score += ev_result["score"]
        for note in ev_result["notes"]:
            if note.startswith("✓"):
                suggestions.append(note)
            else:
                cautions.append(note)

    verdict = _to_verdict(score)

    return MuhurtaResult(
        when=when, province=province, chart=chart,
        wan=wan, wan_planet=wan_planet,
        wan_quality=wan_q, wan_remark=wan_remark,
        lunar=lunar, tithi_quality=t_q,
        nakshatra=nak,
        kalayok=kalayok, kalayok_matches=kalayok_matches,
        special_criteria=specials,
        navamsa=nav_view, vargottama_planets=vargottama,
        score=score, verdict=verdict,
        activity_suggestions=suggestions, cautions=cautions,
        event_key=event_key, event_score=ev_result,
    )


# ============================================================
# Date range scanner
# ============================================================
@dataclass
class ScanHit:
    """1 hit ในการ scan ช่วงวัน"""
    when: datetime
    score: int
    verdict: str
    summary: str  # one-liner
    period: Optional[str] = None    # morning/late_morning/noon/evening/dusk/night
    # personal mode (optional)
    personal_bhava: Optional[int] = None        # ภพที่ลัคนาฤกษ์ตกของเจ้าชะตา (1-12)
    personal_bhava_quality: Optional[str] = None  # คำอธิบาย
    personal_bhava_tone: Optional[str] = None     # good/warning/neutral
    matched_criteria: Optional[List[str]] = None  # ชื่อเกณฑ์พิเศษที่ตก


def _period_of_hour(hour: int) -> str:
    """แปลง hour 0-23 → period key"""
    for k, (lo, hi) in TIME_OF_DAY_RANGES.items():
        if hi > 24:  # night wrap
            if hour >= lo or hour < (hi - 24):
                return k
        else:
            if lo <= hour < hi:
                return k
    return "night"


def _bhava_quality_label(bhava: int) -> tuple[str, str]:
    """คืน (label, tone)"""
    KENDRA = {1, 4, 7, 10}
    TRIKONA = {1, 5, 9}
    DUSTHANA = {6, 8, 12}
    if bhava in KENDRA and bhava in TRIKONA:
        return "ภพหลัก+บุญ (ดีเยี่ยม)", "good"
    if bhava in KENDRA:
        return "ภพหลัก (มั่นคง)", "good"
    if bhava in TRIKONA:
        return "ภพบุญ (โชคลาภ)", "good"
    if bhava in DUSTHANA:
        return "ภพทุกข์ (เลี่ยง)", "warning"
    return "กลาง", "neutral"


def scan_range(
    start: datetime,
    end: datetime,
    province: str = "กรุงเทพมหานคร",
    event_key: Optional[str] = None,
    step_minutes: int = 60,
    top_n: int = 10,
    min_score: int = 0,
    birth_datetime: Optional[datetime] = None,
    birth_province: Optional[str] = None,
    max_days: int = 90,
) -> List[ScanHit]:
    """Scan range — เลือกฤกษ์ดีที่สุดในช่วง

    Args:
        start, end: datetime range (max max_days)
        step_minutes: ความถี่การ scan (default 60 = ทุกชั่วโมง)
        top_n: คืนกี่อันดับ
        min_score: filter score ขั้นต่ำ
        birth_datetime/province: ถ้ามี → ใส่ข้อมูล personal_bhava ลงใน ScanHit

    Returns:
        list ของ ScanHit เรียงตาม score desc
    """
    if (end - start).days > max_days:
        raise ValueError(f"ช่วงเวลาเกิน {max_days} วัน — แบ่งเป็นช่วงสั้นกว่า")

    # คำนวณดวงเจ้าชะตา 1 ครั้ง (cache)
    natal_chart = None
    natal_asc_rasi = None
    if birth_datetime is not None:
        from .chart import Chart
        natal_chart = Chart.calculate(
            birth_datetime.year, birth_datetime.month, birth_datetime.day,
            birth_datetime.hour, birth_datetime.minute,
            province=birth_province or "กรุงเทพมหานคร",
        )
        natal_asc_rasi = natal_chart.ascendant.zodiac.rasi

    hits: List[ScanHit] = []
    cursor = start
    step = timedelta(minutes=step_minutes)

    while cursor <= end:
        try:
            mr = compute_muhurta(cursor, province, event_key)
            score_eff = mr.score
            personal_bhava = None
            bhava_q = None
            bhava_tone = None
            if natal_asc_rasi is not None:
                # ลัคนาฤกษ์ตกภพไหนของเจ้าชะตา
                asc_now = mr.chart.ascendant.zodiac.rasi
                personal_bhava = ((asc_now - natal_asc_rasi) % 12) + 1
                bhava_q, bhava_tone = _bhava_quality_label(personal_bhava)
                if bhava_tone == "good":
                    score_eff += 2
                elif bhava_tone == "warning":
                    score_eff -= 2

            if score_eff >= min_score:
                summary_parts = [
                    f"วัน{mr.wan_planet}",
                    mr.lunar.pretty_short,
                    mr.nakshatra.roek_name,
                ]
                if mr.vargottama_planets:
                    summary_parts.append(
                        f"วรโคตม: {', '.join(mr.vargottama_planets[:2])}"
                    )
                matched_specials = [s.name for s in mr.special_criteria if s.matched]
                hits.append(ScanHit(
                    when=cursor, score=score_eff, verdict=_to_verdict(score_eff),
                    summary=" • ".join(summary_parts),
                    personal_bhava=personal_bhava,
                    personal_bhava_quality=bhava_q,
                    personal_bhava_tone=bhava_tone,
                    matched_criteria=matched_specials or None,
                ))
        except Exception:
            pass
        cursor += step

    hits.sort(key=lambda h: (-h.score, h.when))
    return hits[:top_n]


# ช่วงเวลาในวัน (Thai standard)
TIME_OF_DAY_RANGES = {
    "morning":      (6, 9),
    "late_morning": (9, 12),
    "noon":         (12, 15),
    "evening":      (15, 18),
    "dusk":         (18, 21),
    "night":        (21, 30),  # 21:00-05:59 (wrap)
}


def _hour_in_periods(hour: int, periods: List[str]) -> bool:
    """True ถ้าชั่วโมงอยู่ในช่วงที่เลือก (หรือไม่ได้เลือกช่วงไหน = ทั้งหมด)"""
    if not periods:
        return True
    for p in periods:
        if p not in TIME_OF_DAY_RANGES:
            continue
        lo, hi = TIME_OF_DAY_RANGES[p]
        if hi > 24:
            if hour >= lo or hour < (hi - 24):
                return True
        else:
            if lo <= hour < hi:
                return True
    return False


def scan_range_multi_events(
    start: datetime,
    end: datetime,
    event_keys: List[str],
    province: str = "กรุงเทพมหานคร",
    step_minutes: int = 60,
    top_n_per_event: int = 8,
    min_score: int = -99,
    birth_datetime: Optional[datetime] = None,
    birth_province: Optional[str] = None,
    max_days: int = 90,
    time_periods: Optional[List[str]] = None,
    max_per_day: int = 2,
) -> Dict[str, List[ScanHit]]:
    """Scan ครั้งเดียว — คำนวณ chart ของแต่ละ moment 1 ครั้ง แล้ว
    ให้คะแนนทุก event ที่ moment นั้น (เร็วกว่า scan_range ต่อ event)

    คืน {event_key: [ScanHit]}
    """
    from .chart import Chart
    from .muhurta_criteria import EVENTS, event_score as _event_score

    if (end - start).days > max_days:
        raise ValueError(f"ช่วงเวลาเกิน {max_days} วัน — แบ่งเป็นช่วงสั้นกว่า")

    # natal cache
    natal_asc_rasi = None
    if birth_datetime is not None:
        nc = Chart.calculate(
            birth_datetime.year, birth_datetime.month, birth_datetime.day,
            birth_datetime.hour, birth_datetime.minute,
            province=birth_province or "กรุงเทพมหานคร",
        )
        natal_asc_rasi = nc.ascendant.zodiac.rasi

    # ลำดับ event ที่จะตรวจ — กรองที่อยู่ใน EVENTS
    keys = [k for k in event_keys if k in EVENTS]
    if not keys:
        return {}

    out: Dict[str, List[ScanHit]] = {k: [] for k in keys}
    cursor = start
    step = timedelta(minutes=step_minutes)

    while cursor <= end:
        # filter ตามช่วงเวลา (server-side)
        if time_periods and not _hour_in_periods(cursor.hour, time_periods):
            cursor += step
            continue
        try:
            # compute base muhurta แค่ครั้งเดียว (ไม่มี event_key เพราะจะคำนวณ event_score ต่างหาก)
            base = compute_muhurta(cursor, province, event_key=None)

            # personal bhava (ครั้งเดียวต่อ moment)
            personal_bhava = None
            bhava_q = None
            bhava_tone = None
            if natal_asc_rasi is not None:
                asc_now = base.chart.ascendant.zodiac.rasi
                personal_bhava = ((asc_now - natal_asc_rasi) % 12) + 1
                bhava_q, bhava_tone = _bhava_quality_label(personal_bhava)

            base_score = base.score
            if bhava_tone == "good":
                base_score += 2
            elif bhava_tone == "warning":
                base_score -= 2

            matched_specials = [s.name for s in base.special_criteria if s.matched]

            # summary 1 ครั้ง (ใช้ร่วมทุก event)
            summary_parts = [
                f"วัน{base.wan_planet}",
                base.lunar.pretty_short,
                base.nakshatra.roek_name,
            ]
            if base.vargottama_planets:
                summary_parts.append(
                    f"วรโคตม: {', '.join(base.vargottama_planets[:2])}"
                )
            summary = " • ".join(summary_parts)

            # ให้คะแนนแต่ละ event ที่ moment นี้
            for ek in keys:
                ev_extra = _event_score(base.chart, ek)
                final_score = base_score + ev_extra["score"]
                if final_score < min_score:
                    continue
                out[ek].append(ScanHit(
                    when=cursor, score=final_score, verdict=_to_verdict(final_score),
                    summary=summary,
                    period=_period_of_hour(cursor.hour),
                    personal_bhava=personal_bhava,
                    personal_bhava_quality=bhava_q,
                    personal_bhava_tone=bhava_tone,
                    matched_criteria=matched_specials or None,
                ))
        except Exception:
            pass
        cursor += step

    # sort + กระจายวัน (max_per_day) + trim
    for ek in out:
        out[ek].sort(key=lambda h: (-h.score, h.when))
        if max_per_day > 0:
            by_day: Dict = {}
            spread: List[ScanHit] = []
            for h in out[ek]:
                k = h.when.date()
                if by_day.get(k, 0) >= max_per_day:
                    continue
                by_day[k] = by_day.get(k, 0) + 1
                spread.append(h)
                if len(spread) >= top_n_per_event:
                    break
            out[ek] = spread
        else:
            out[ek] = out[ek][:top_n_per_event]
    return out


def scan_range_grouped(
    start: datetime,
    end: datetime,
    province: str = "กรุงเทพมหานคร",
    step_minutes: int = 60,
    top_n_per_event: int = 3,
    min_score: int = 2,
    birth_datetime: Optional[datetime] = None,
    birth_province: Optional[str] = None,
    max_days: int = 90,
) -> Dict[str, List[ScanHit]]:
    """Scan ทุกกิจกรรม + จัดกลุ่มผลลัพธ์ตาม event_key

    คืน {event_key: [ScanHit ...]} เรียง top_n_per_event ต่อกิจกรรม
    """
    from .muhurta_criteria import EVENTS as _EVENTS
    out: Dict[str, List[ScanHit]] = {}
    for ek in _EVENTS:
        try:
            hits = scan_range(
                start, end, province=province, event_key=ek,
                step_minutes=step_minutes, top_n=top_n_per_event,
                min_score=min_score,
                birth_datetime=birth_datetime,
                birth_province=birth_province,
                max_days=max_days,
            )
            if hits:
                out[ek] = hits
        except Exception:
            continue
    return out
