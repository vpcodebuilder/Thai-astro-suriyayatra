"""ฤกษ์เฉพาะบุคคล — ประเมินฤกษ์จากมุมมองของเจ้าชะตา

7 เกณฑ์หักคะแนน (total range: -12 ถึง 0; is_suitable = total >= 0):
    A. ลัคนาฤกษ์ตกภพของเจ้าชะตา = อริ/มรณะ/วินาส     → −2/−3/−2
    B. ฤกษ์ตรง "วันกาลีจร" ของช่วงทักษาจร              → −2
    C1. ดาวสำคัญของกิจกรรม ตกภพเสีย (6/8/12) ของฤกษ์   → −2
    C2. ราศีของดาวสำคัญ ตกภพเสียของเจ้าชะตา            → −2
    C3. ดาวสำคัญได้ตำแหน่งนิจ/ประ                       → −1
    D. ดาวเจ้าเรือนตนุของฤกษ์ (chart lord) ตกภพเสีย    → −1
    E. ดาวจันทร์ของฤกษ์ ตกภพเสียของฤกษ์                  → −1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

from .chart import Chart
from .taksa import (
    compute_taksa, compute_transit_taksa, Taksa,
    WEEKDAY_PLANET, WEEKDAY_NAME_TH, TAKSA_CYCLE, DASA_YEARS_PER_PLANET,
)
from .dignities import compute_dignity, DIGNITY_STRENGTH
from .planets import RASI_LORD


PLANET_TO_WEEKDAY: Dict[str, int] = {p: w for w, p in WEEKDAY_PLANET.items()}

_BHAVA_NAME_12 = [
    "ตนุ", "กดุมภะ", "สหัชชะ", "พันธุ", "ปุตตะ", "อริ",
    "ปัตนิ", "มรณะ", "ศุภะ", "กัมมะ", "ลาภะ", "วินาส",
]
GOOD_BHAVAS = {1, 4, 5, 7, 9, 10, 11}     # kendra + trikona + ลาภะ
DUSTHANA_BHAVAS = {6, 8, 12}              # อริ / มรณะ / วินาส
NEUTRAL_BHAVAS = {2, 3}

# ความหมายดาว (สำหรับ chip "ดาวสำคัญของกิจกรรม")
PLANET_MEANINGS_SHORT = {
    "อาทิตย์":   "ตำแหน่ง-อำนาจ",
    "จันทร์":    "อารมณ์-มารดา",
    "อังคาร":    "พลังกาย-ความกล้า",
    "พุธ":       "ปัญญา-การสื่อสาร",
    "พฤหัสบดี":  "ความเจริญ-ครู",
    "ศุกร์":     "ความรัก-ความงาม",
    "เสาร์":     "อดทน-วินัย",
    "ราหู":      "เปลี่ยนแปลง-ลึกลับ",
    "เกตุ":      "ปล่อยวาง-จิตวิญญาณ",
    "มฤตยู":     "นวัตกรรม-ปฏิวัติ",
}

# ความหมายภพ (สำหรับ chip "ภพสำคัญของกิจกรรม")
BHAVA_MEANINGS_SHORT = {
    1: "ตัวคุณ",
    2: "ทรัพย์",
    3: "พี่น้อง",
    4: "บ้าน-ครอบครัว",
    5: "บุญ-บุตร",
    6: "ศัตรู-สุขภาพ",
    7: "คู่ครอง",
    8: "อันตราย",
    9: "บุญใหญ่",
    10: "การงาน-องค์กร",
    11: "โชค-สมหวัง",
    12: "เสียหาย",
}

# Personal score range (sum ของ A..E)
PERSONAL_SCORE_MIN = -12   # ทุกเกณฑ์ลบเต็มที่
PERSONAL_SCORE_MAX = 7     # ทุกเกณฑ์บวกเต็มที่


def _bhava_full(n: int) -> str:
    """'ภพ 1 ตนุ' format"""
    return f"ภพ {n} {_BHAVA_NAME_12[n - 1]}"


def _rotated_kalee_planet(birth_planet: str, year_of_life: int) -> Tuple[str, int]:
    """ดาวกาลีจร — กาลกิณีของช่วงทักษาจรปัจจุบัน (12-year dasa)"""
    birth_idx = TAKSA_CYCLE.index(birth_planet)
    dasa_idx = ((max(year_of_life, 1) - 1) // DASA_YEARS_PER_PLANET) % len(TAKSA_CYCLE)
    new_kalee_idx = (birth_idx + dasa_idx + 7) % len(TAKSA_CYCLE)
    return TAKSA_CYCLE[new_kalee_idx], dasa_idx


def _bhava_of(rasi: int, lakkana_rasi: int) -> int:
    """คืนภพ 1-12 ของราศีที่อยู่ เทียบกับลัคนา"""
    return ((rasi - lakkana_rasi) % 12) + 1


# ============================================================
# Dataclasses
# ============================================================
@dataclass
class PlanetCheck:
    """1 ดาวสำคัญ ตรวจ 3 มิติ"""
    planet: str
    meaning: str                # "ตำแหน่ง-อำนาจ"
    rasi_name: str
    dignity: str
    moment_bhava: int           # ในดวงฤกษ์
    moment_bhava_label: str
    natal_bhava: int            # ในดวงเจ้าชะตา
    natal_bhava_label: str
    c1: int                     # ภพในฤกษ์
    c2: int                     # ภพในเจ้าชะตา
    c3: int                     # dignity
    sum: int                    # c1+c2+c3


@dataclass
class EventKeyAnalysis:
    """วิเคราะห์ดาวสำคัญของกิจกรรม (รองรับหลายดาว — average)"""
    event_key: str
    event_label: str
    # multi-planet
    planet_checks: List[PlanetCheck] = field(default_factory=list)
    favored_planets: List[str] = field(default_factory=list)        # ทุกดาวที่ event ใช้
    favored_bhavas: List[int] = field(default_factory=list)         # ทุกภพที่ event เน้น
    planet_chips: List[dict] = field(default_factory=list)          # for UI panel header
    bhava_chips: List[dict] = field(default_factory=list)
    # คะแนน averaged
    c1_score: int = 0
    c2_score: int = 0
    c3_score: int = 0
    score: int = 0                                                  # = c1+c2+c3 averaged
    tone: str = "neutral"
    narrative_lines: List[str] = field(default_factory=list)
    # backward-compat fields (จุดแรกของ favored_planets)
    key_planet: str = ""
    moment_rasi: int = 0
    moment_rasi_name: str = ""
    moment_dignity: str = ""
    moment_dignity_strength: int = 0
    moment_bhava: int = 1
    moment_bhava_label: str = ""
    natal_bhava: int = 1
    natal_bhava_label: str = ""


@dataclass
class ChartHealth:
    """D + E — สุขภาพดวงฤกษ์ (chart_lord + moon ต้องไม่ตกภพเสีย)"""
    chart_lord_planet: str                 # ดาวเจ้าเรือนตนุของฤกษ์
    chart_lord_rasi_name: str
    chart_lord_bhava: int                  # ในดวงฤกษ์
    chart_lord_bhava_label: str
    d_score: int                           # 0 หรือ −1
    moon_rasi_name: str
    moon_bhava: int                        # ในดวงฤกษ์
    moon_bhava_label: str
    e_score: int                           # 0 หรือ −1
    score: int                             # d + e


@dataclass
class PersonalEval:
    """ผลประเมินฤกษ์ต่อเจ้าชะตา"""
    # --- A: ลัคนาฤกษ์ → ภพของเจ้าชะตา ---
    bhava: int
    bhava_label: str
    bhava_quality: str
    bhava_tone: str
    bhava_score: int                       # 0 / −2 / −3

    # --- B: ทักษาจร (ดาวกาลีจร) ---
    year_of_life: int
    dasa_planet: str                       # info
    dasa_position: str                     # info
    dasa_kalee_planet: str
    dasa_kalee_weekday_name: Optional[str]
    is_dasa_kalee: bool
    dasa_kalee_score: int                  # 0 / −2

    # --- C: event key planet ---
    event_analysis: Optional[EventKeyAnalysis] = None

    # --- D + E: chart health ---
    chart_health: Optional[ChartHealth] = None

    # --- Vargottama (chip only) ---
    vargottama_planets: List[str] = field(default_factory=list)

    # --- รวม ---
    total_score: int = 0
    is_suitable: bool = True
    has_warning: bool = False
    warning_lines: List[str] = field(default_factory=list)

    # Backward-compat
    kalee_planet: str = ""
    kalee_weekday_name: Optional[str] = None
    is_weekday_kalee: bool = False
    weekday_kalee_score: int = 0


# ============================================================
# A: ลัคนาฤกษ์ตกภพของเจ้าชะตา — บวก/ลบ ทั้ง 2 ฝั่ง
# ============================================================
_BHAVA_SCORE_A = {
    1:  (+2, "ตนุ — ภพหลัก (ตัวคุณเอง)",   "good"),
    2:  ( 0, "กดุมภะ — ทรัพย์",             "neutral"),
    3:  ( 0, "สหัชชะ — พี่น้อง การเดินทาง",  "neutral"),
    4:  (+1, "พันธุ — ครอบครัว บ้าน",       "good"),
    5:  (+1, "ปุตตะ — บุญ บุตร",            "good"),
    6:  (-2, "อริ — ศัตรู โรคภัย",          "warning"),
    7:  (+1, "ปัตนิ — คู่ครอง",             "good"),
    8:  (-3, "มรณะ — เลี่ยง",               "warning"),
    9:  (+1, "ศุภะ — บุญใหญ่",              "good"),
    10: (+1, "กัมมะ — การงาน เกียรติ",      "good"),
    11: (+1, "ลาภะ — สมหวัง",               "good"),
    12: (-2, "วินาส — เสียหาย",             "warning"),
}


def _score_c1_c2(bhava: int) -> int:
    """ดาวสำคัญตกภพไหน (C1, C2): good +1 / neutral 0 / bad −2"""
    if bhava in DUSTHANA_BHAVAS:
        return -2
    if bhava in GOOD_BHAVAS:
        return +1
    return 0


def _score_d_e(bhava: int) -> int:
    """chart_lord (D) + จันทร์ (E): good +1 / neutral 0 / bad −1"""
    if bhava in DUSTHANA_BHAVAS:
        return -1
    if bhava in GOOD_BHAVAS:
        return +1
    return 0


def _bhava_info(bhava: int) -> Tuple[int, str, str, str]:
    sc, label, tone = _BHAVA_SCORE_A[bhava]
    return sc, label, tone, _BHAVA_NAME_12[bhava - 1]


# ============================================================
# NatalContext
# ============================================================
@dataclass
class NatalContext:
    chart: Chart
    asc_rasi: int
    taksa: Taksa
    kalee_planet: str
    kalee_weekday: Optional[int]
    kalee_weekday_name: Optional[str]
    birth_date: date


def build_natal_context(birth_dt: datetime, province: str) -> NatalContext:
    chart = Chart.calculate(
        birth_dt.year, birth_dt.month, birth_dt.day,
        birth_dt.hour, birth_dt.minute, province=province,
    )
    taksa = compute_taksa(
        birth_dt.year, birth_dt.month, birth_dt.day,
        birth_dt.hour, birth_dt.minute,
    )
    kalee_planet = taksa.bhavas[7].planet
    kalee_weekday = PLANET_TO_WEEKDAY.get(kalee_planet)
    kalee_weekday_name = WEEKDAY_NAME_TH.get(kalee_weekday) if kalee_weekday is not None else None
    return NatalContext(
        chart=chart, asc_rasi=chart.ascendant.zodiac.rasi,
        taksa=taksa,
        kalee_planet=kalee_planet,
        kalee_weekday=kalee_weekday,
        kalee_weekday_name=kalee_weekday_name,
        birth_date=date(birth_dt.year, birth_dt.month, birth_dt.day),
    )


# ============================================================
# C: Event key planet analysis
# ============================================================
def _round_avg(values: List[int]) -> int:
    """round average ปัดแบบ banker's (เหมาะกับ int ที่อยู่ในช่วง [-2..+1])"""
    if not values:
        return 0
    return round(sum(values) / len(values))


def analyze_event_key_planet(
    event_key: str,
    moment_chart: Chart,
    natal: NatalContext,
) -> Optional[EventKeyAnalysis]:
    """วิเคราะห์ดาวสำคัญทุกดวงของกิจกรรม + ภพสำคัญ — average score per planet"""
    from .muhurta_criteria import EVENTS
    ev = EVENTS.get(event_key)
    if not ev or not ev.favored_planets:
        return None

    moment_asc = moment_chart.ascendant.zodiac.rasi

    # --- planet chips (info สำหรับ panel header) ---
    planet_chips = [
        {"planet": p, "meaning": PLANET_MEANINGS_SHORT.get(p, "")}
        for p in ev.favored_planets
    ]
    bhava_chips = [
        {"bhava": b, "name": _BHAVA_NAME_12[b - 1], "meaning": BHAVA_MEANINGS_SHORT.get(b, "")}
        for b in ev.favored_bhavas
    ]

    # --- ตรวจทุกดาวสำคัญ ---
    checks: List[PlanetCheck] = []
    for planet in ev.favored_planets:
        if planet not in moment_chart.planets:
            continue
        po = moment_chart.planets[planet]
        rasi = po.zodiac.rasi
        rasi_name = po.zodiac.rasi_name
        dig = compute_dignity(planet, rasi)
        moment_bhava = _bhava_of(rasi, moment_asc)
        natal_bhava = _bhava_of(rasi, natal.asc_rasi)
        c1 = _score_c1_c2(moment_bhava)
        c2 = _score_c1_c2(natal_bhava)
        if dig.is_strong:
            c3 = +1
        elif dig.is_weak:
            c3 = -1
        else:
            c3 = 0
        checks.append(PlanetCheck(
            planet=planet,
            meaning=PLANET_MEANINGS_SHORT.get(planet, ""),
            rasi_name=rasi_name,
            dignity=dig.dignity,
            moment_bhava=moment_bhava,
            moment_bhava_label=_BHAVA_NAME_12[moment_bhava - 1],
            natal_bhava=natal_bhava,
            natal_bhava_label=_BHAVA_NAME_12[natal_bhava - 1],
            c1=c1, c2=c2, c3=c3,
            sum=c1 + c2 + c3,
        ))

    if not checks:
        return None

    # คะแนน — average across planets, round → range เท่าเดิม
    c1_avg = _round_avg([c.c1 for c in checks])
    c2_avg = _round_avg([c.c2 for c in checks])
    c3_avg = _round_avg([c.c3 for c in checks])
    total = c1_avg + c2_avg + c3_avg
    tone = "warning" if total < 0 else ("good" if total > 0 else "neutral")

    # narrative — ภาษาธรรมดา ไม่มี c1/c2/c3
    def _bhava_descr(b: int) -> str:
        """คืน 'ภพดี' / 'ภพปกติ' / 'ภพเสีย'"""
        if b in DUSTHANA_BHAVAS:
            return "ภพเสีย"
        if b in GOOD_BHAVAS:
            return "ภพดี"
        return "ภพปกติ"

    def _dignity_descr(d: str, c3: int) -> str:
        if c3 > 0:
            return "แข็งแรง"
        if c3 < 0:
            return "อ่อนกำลัง"
        return "ปกติ"

    lines: List[str] = []
    for pc in checks:
        head = f"<strong>{pc.planet}</strong> ({pc.meaning}) — อยู่ราศี{pc.rasi_name} ตำแหน่ง<strong>{pc.dignity}</strong>"
        lines.append(head)
        # ในดวงฤกษ์
        m_descr = _bhava_descr(pc.moment_bhava)
        m_icon = "✓" if pc.c1 > 0 else ("⚠️" if pc.c1 < 0 else "·")
        lines.append(f"  {m_icon} ในดวงฤกษ์: ตกภพ{pc.moment_bhava} {pc.moment_bhava_label} ({m_descr})")
        # ในดวงเจ้าชะตา
        n_descr = _bhava_descr(pc.natal_bhava)
        n_icon = "✓" if pc.c2 > 0 else ("⚠️" if pc.c2 < 0 else "·")
        lines.append(f"  {n_icon} ในดวงเจ้าชะตา: ราศี{pc.rasi_name}ตกภพ{pc.natal_bhava} {pc.natal_bhava_label} ({n_descr})")
        # dignity
        d_icon = "✓" if pc.c3 > 0 else ("⚠️" if pc.c3 < 0 else "·")
        d_descr = _dignity_descr(pc.dignity, pc.c3)
        lines.append(f"  {d_icon} ตำแหน่ง {pc.dignity} ({d_descr})")

    first = checks[0]
    return EventKeyAnalysis(
        event_key=event_key, event_label=ev.label,
        planet_checks=checks,
        favored_planets=list(ev.favored_planets),
        favored_bhavas=list(ev.favored_bhavas),
        planet_chips=planet_chips,
        bhava_chips=bhava_chips,
        c1_score=c1_avg, c2_score=c2_avg, c3_score=c3_avg,
        score=total, tone=tone, narrative_lines=lines,
        # backward-compat
        key_planet=first.planet,
        moment_rasi=0,
        moment_rasi_name=first.rasi_name,
        moment_dignity=first.dignity,
        moment_dignity_strength=DIGNITY_STRENGTH.get(first.dignity, 0),
        moment_bhava=first.moment_bhava,
        moment_bhava_label=first.moment_bhava_label,
        natal_bhava=first.natal_bhava,
        natal_bhava_label=first.natal_bhava_label,
    )


# ============================================================
# D + E: Chart health (chart lord + moon in moment chart)
# ============================================================
def analyze_chart_health(moment_chart: Chart) -> ChartHealth:
    asc_rasi = moment_chart.ascendant.zodiac.rasi
    chart_lord = RASI_LORD[asc_rasi]

    # D: chart_lord ตกภพไหนในดวงฤกษ์
    if chart_lord in moment_chart.planets:
        lord_planet_obj = moment_chart.planets[chart_lord]
        lord_rasi = lord_planet_obj.zodiac.rasi
        lord_rasi_name = lord_planet_obj.zodiac.rasi_name
        lord_bhava = _bhava_of(lord_rasi, asc_rasi)
    else:
        lord_rasi_name = "—"
        lord_bhava = 1
    lord_label = _BHAVA_NAME_12[lord_bhava - 1]
    d_score = _score_d_e(lord_bhava)

    # E: จันทร์ ตกภพไหนในดวงฤกษ์
    if "จันทร์" in moment_chart.planets:
        moon = moment_chart.planets["จันทร์"]
        moon_rasi_name = moon.zodiac.rasi_name
        moon_bhava = _bhava_of(moon.zodiac.rasi, asc_rasi)
    else:
        moon_rasi_name = "—"
        moon_bhava = 1
    moon_label = _BHAVA_NAME_12[moon_bhava - 1]
    e_score = _score_d_e(moon_bhava)

    return ChartHealth(
        chart_lord_planet=chart_lord,
        chart_lord_rasi_name=lord_rasi_name,
        chart_lord_bhava=lord_bhava,
        chart_lord_bhava_label=lord_label,
        d_score=d_score,
        moon_rasi_name=moon_rasi_name,
        moon_bhava=moon_bhava,
        moon_bhava_label=moon_label,
        e_score=e_score,
        score=d_score + e_score,
    )


# ============================================================
# Main evaluator
# ============================================================
def evaluate_personal(
    moment: datetime,
    moment_chart: Chart,
    natal: NatalContext,
    vargottama_planets: Optional[List[str]] = None,
    event_key: Optional[str] = None,
) -> PersonalEval:
    # A: ลัคนาฤกษ์ตกภพของเจ้าชะตา
    asc_now = moment_chart.ascendant.zodiac.rasi
    bhava_num = _bhava_of(asc_now, natal.asc_rasi)
    bhava_sc, bhava_label, bhava_tone, _ = _bhava_info(bhava_num)

    # B: ทักษาจร (ดาวกาลีจร)
    completed_y = moment.year - natal.birth_date.year
    if (moment.month, moment.day) < (natal.birth_date.month, natal.birth_date.day):
        completed_y -= 1
    if completed_y < 0:
        completed_y = 0
    year_of_life = completed_y + 1

    try:
        tt = compute_transit_taksa(natal.taksa, year_of_life)
        dasa_planet_info = tt.current_planet
        dasa_position_info = "ตากลาง" if tt.is_on_center else f"ตา {tt.current_cycle_position}"
    except Exception:
        dasa_planet_info = "—"
        dasa_position_info = "—"

    dasa_kalee_planet, _dasa_idx = _rotated_kalee_planet(natal.taksa.birth_planet, year_of_life)
    dasa_kalee_weekday = PLANET_TO_WEEKDAY.get(dasa_kalee_planet)
    dasa_kalee_weekday_name = (
        WEEKDAY_NAME_TH.get(dasa_kalee_weekday) if dasa_kalee_weekday is not None else None
    )
    is_dasa_kalee = (
        dasa_kalee_weekday is not None and moment.weekday() == dasa_kalee_weekday
    )
    dasa_kalee_score = -2 if is_dasa_kalee else 0

    # C: event key analysis
    event_an = None
    c_score = 0
    if event_key:
        try:
            event_an = analyze_event_key_planet(event_key, moment_chart, natal)
            if event_an:
                c_score = event_an.score
        except Exception:
            pass

    # D + E: chart health (always compute)
    try:
        ch = analyze_chart_health(moment_chart)
        de_score = ch.score
    except Exception:
        ch = None
        de_score = 0

    # รวม (range: PERSONAL_SCORE_MIN..MAX)
    total = bhava_sc + dasa_kalee_score + c_score + de_score
    # เหมาะ = ผลรวม ≥ 0 (ไม่ติดเกณฑ์เสียมาก / มีบวกชดเชยพอ)
    is_suitable = total >= 0

    # warnings สำหรับ banner (เฉพาะ A + B + critical C)
    warnings = []
    if bhava_tone == "warning":
        warnings.append(f"ลัคนาฤกษ์ตก {bhava_label}")
    if is_dasa_kalee:
        warnings.append(f"ตรงวันกาลีจร ({dasa_kalee_weekday_name} — ดาว{dasa_kalee_planet})")
    if event_an and (event_an.c1_score < 0 or event_an.c2_score < 0):
        warnings.append(f"ดาวสำคัญ ({event_an.key_planet}) ตกภพเสีย")
    if ch and (ch.d_score < 0 or ch.e_score < 0):
        bits = []
        if ch.d_score < 0:
            bits.append(f"เจ้าเรือน ({ch.chart_lord_planet})")
        if ch.e_score < 0:
            bits.append("จันทร์")
        warnings.append(f"ดวงฤกษ์เสีย: {', '.join(bits)} ตกภพเสีย")

    varg_list = list(vargottama_planets) if vargottama_planets else []

    return PersonalEval(
        bhava=bhava_num,
        bhava_label=bhava_label,
        bhava_quality=bhava_label,
        bhava_tone=bhava_tone,
        bhava_score=bhava_sc,
        year_of_life=year_of_life,
        dasa_planet=dasa_planet_info,
        dasa_position=dasa_position_info,
        dasa_kalee_planet=dasa_kalee_planet,
        dasa_kalee_weekday_name=dasa_kalee_weekday_name,
        is_dasa_kalee=is_dasa_kalee,
        dasa_kalee_score=dasa_kalee_score,
        event_analysis=event_an,
        chart_health=ch,
        vargottama_planets=varg_list,
        total_score=total,
        is_suitable=is_suitable,
        has_warning=bool(warnings),
        warning_lines=warnings,
        # backward compat
        kalee_planet=dasa_kalee_planet,
        kalee_weekday_name=dasa_kalee_weekday_name,
        is_weekday_kalee=is_dasa_kalee,
        weekday_kalee_score=0,
    )
