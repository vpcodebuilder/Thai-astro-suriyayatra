"""รูปดวง / โยค / เกณฑ์ ตามตำราโหราศาสตร์ไทย + ภารตะ

อิงฐานข้อมูล `astropattern.md` v1.0 — 26 rule:
    หมวด 1 รูปดวงไทย          (TH-001..004)  มาลัย / คันศร / จตุสดัย / ลัคนานำพล
    หมวด 2 อุดมเกณฑ์            (TH-101..104) นรเกณฑ์ / อัมพุเกณฑ์ / กีฏะเกณฑ์ / สัตวเกณฑ์
    หมวด 3 ปัญจมหาบุรุษ        (VE-001..005) รูจกะ / ภัทร / หังสะ / มาลวยะ / ศศะ
    หมวด 4 โยคสำคัญ             (VE-101..106) คชเกสรี / ลักษมี / อธิ / อมล / ราชา / ธน
    หมวด 5 จันทรโยค             (VE-201..205) สุนภา / อนภา / ทุรธรา / วาสิ / อุภยจารี
    หมวด 6 โยคเสีย              (MA-001..002) พินทุบาทว์ / บาปเคราะห์รุมลัคนา

API หลัก:
    detect_astro_patterns(chart, dignities) -> AstroPatternReport
      - matched      : List[AstroPattern]   ที่ดวงได้
      - near_misses  : List[AstroPattern]   เกือบได้ + คำแนะนำว่าขาดอะไร
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .planets import RASI_NAMES_TH, RASI_LORD, PLANET_ORDER
from .dignities import (
    PlanetDignity, EXALTATION_RASI, SWAKSHETRA, KENDRA_HOUSES, TRIKONA_HOUSES,
)


# ============================================================
# ค่าคงที่
# ============================================================
MAIN_PLANETS_7 = ["อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"]
BENEFICS = {"พฤหัสบดี", "ศุกร์", "พุธ", "จันทร์"}     # ศุภเคราะห์
MALEFICS = {"อาทิตย์", "อังคาร", "เสาร์", "ราหู", "เกตุ"}  # บาปเคราะห์

# กลุ่มลัคนา 4 กลุ่ม (TH-101..104) — ตามตำราไทยที่ใช้กำหนดกฎ องค์เกณฑ์/อุดมเกณฑ์
LAGNA_GROUP = {
    "นระเกณฑ์":   {2, 5, 6, 8, 10},   # ราศีคน: เมถุน/กันย์/ตุลย์/ธนู/กุมภ์
    "อัมพุเกณฑ์": {3, 9, 11},          # ราศีสัตว์น้ำ: กรกฎ/มกร/มีน
    "กีฏะเกณฑ์":  {7},                # ราศีแมลง: พิจิก
    "ปัศวะเกณฑ์": {0, 1, 4},          # ราศีสัตว์ 4 เท้า: เมษ/พฤษภ/สิงห์
}
LAGNA_GROUP_MEANING = {
    "นระเกณฑ์":   "ดวงทางปัญญา-วิชาการ-การสื่อสาร เด่นด้านคิดวิเคราะห์",
    "อัมพุเกณฑ์": "ดวงสายเกื้อหนุน-โชคลาภ-เมตตา มีคนช่วยเหลือมาตลอด",
    "กีฏะเกณฑ์":  "ดวงนักสู้-อดทน-พลิกวิกฤต ลึกซึ้งและเอาตัวรอดเก่ง",
    "ปัศวะเกณฑ์": "ดวงผู้นำ-กล้าหาญ-ชอบแข่งขัน รักความท้าทาย",
}

# === องค์เกณฑ์ (เน้นยศศักดิ์/อำนาจ) ===
# กฎ: ตามลัคนา → ดาวที่กำหนดต้องอยู่ในภพที่ระบุ → เข้าเกณฑ์
ONG_KEN_RULES = {
    "ปัศวะเกณฑ์": {
        "house": 10,
        "house_name": "กัมมะ",
        "planets": {"อาทิตย์", "จันทร์", "อังคาร", "ศุกร์"},
        "result": "ได้ยศถึงพระยา — ตำแหน่งสูงในราชการ/องค์กรใหญ่",
    },
    "นระเกณฑ์": {
        "house": 1,
        "house_name": "ตนุ (กุมลัคนา)",
        "planets": {"พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"},
        "result": "เด่นตัวเองตลอดชีวิต — ผู้ใหญ่หนุน ภาพลักษณ์ดี",
    },
    "อัมพุเกณฑ์": {
        "house": 4,
        "house_name": "พันธุ",
        "planets": {"จันทร์", "พุธ", "ศุกร์", "พฤหัสบดี"},
        "result": "ได้ยศถึงพระยา — มีบ้าน/ทรัพย์มรดก/ฐานครอบครัวมั่นคง",
    },
    "กีฏะเกณฑ์": {
        "house": 7,
        "house_name": "ปัตนิ",
        "planets": {"อังคาร", "ราหู"},
        "result": "ฐานะมั่นคงจากคู่ครอง/หุ้นส่วน — เจรจาเก่ง พลิกได้",
    },
}

# === อุดมเกณฑ์ (เน้นทรัพย์สิน/บริวาร) ===
# กฎ: ลัคนา นระเกณฑ์ → ดาวที่กำหนดในภพ 1/3/4/7/11
#     ลัคนากลุ่มอื่น → ดาวใด ๆ ในภพ 1/3/4/7/11
UDOM_HOUSES = {1, 3, 4, 7, 11}
UDOM_HOUSE_NAMES = {1: "ตนุ", 3: "สหัชชะ", 4: "พันธุ", 7: "ปัตนิ", 11: "ลาภะ"}
UDOM_NRA_PLANETS = {"พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"}

# ปัญจมหาบุรุษ: ดาว → (รหัส, ชื่อ, ความหมาย)
PANCHA = {
    "อังคาร":   ("VE-001", "รูจกะโยค",   "ผู้นำ นักรบ นักบริหาร ใจถึง"),
    "พุธ":       ("VE-002", "ภัทรโยค",     "ปัญญาเลิศ พูดเก่ง การค้าได้กำไร"),
    "พฤหัสบดี":  ("VE-003", "หังสะโยค",    "ครู นักวิชาการ ศีลธรรมสูง คนเคารพ"),
    "ศุกร์":     ("VE-004", "มาลวยะโยค",   "มั่งคั่ง ศิลปะ ความนิยม รสนิยมดี"),
    "เสาร์":    ("VE-005", "ศศะโยค",      "อำนาจ การจัดการ ความอดทน ขึ้นสูงได้"),
}


# ============================================================
# Dataclass
# ============================================================
@dataclass
class AstroPattern:
    code: str               # "TH-001"
    name: str               # "มาลัยโยค"
    category: str           # "รูปดวงไทย" | "อุดมเกณฑ์" | "ปัญจมหาบุรุษ" | "โยคสำคัญ" | "จันทรโยค" | "โยคเสีย"
    level: str              # A/B/C
    matched: bool           # ได้เกณฑ์หรือไม่
    tone: str               # "good" | "warning" | "neutral"
    description: str        # อธิบายสั้นว่าเกิดจากอะไร
    meaning: str            # ความหมายของโยค
    advice: str = ""        # ถ้าไม่ match — คำแนะนำว่าขาดอะไร / หากเทียบฤกษ์/ลัคนา
    planets_involved: List[str] = field(default_factory=list)


@dataclass
class AstroPatternReport:
    matched: List[AstroPattern]
    near_misses: List[AstroPattern]


# ============================================================
# Helpers
# ============================================================
def _rasi_to_house(rasi: int, asc_rasi: int) -> int:
    return ((rasi - asc_rasi) % 12) + 1


def _house_from_planet(target_rasi: int, ref_rasi: int) -> int:
    """house distance นับจาก ref ไป target (1..12)"""
    return ((target_rasi - ref_rasi) % 12) + 1


def _consecutive_rasi_span(rasis: Set[int]) -> int:
    """หาช่วงราศีต่อเนื่องที่ยาวที่สุดใน 12 ราศี (cyclic)"""
    if not rasis:
        return 0
    if len(rasis) == 12:
        return 12
    best = 0
    for start in range(12):
        cur = 0
        for off in range(12):
            if (start + off) % 12 in rasis:
                cur += 1
                if cur > best:
                    best = cur
            else:
                cur = 0
    return best


def _arc_span_degrees(rasis: List[int]) -> int:
    """ช่วงห่างของกลุ่มราศี (อนุมาน 15° กลางราศี)
    คืนค่าน้อยสุดของส่วนโค้งที่ครอบทุกตำแหน่ง"""
    if not rasis:
        return 0
    pts = sorted({r * 30 + 15 for r in rasis})
    if len(pts) == 1:
        return 0
    # หาช่องว่างที่กว้างที่สุด — ส่วนที่เหลือคือ minimum arc
    gaps = []
    for i in range(len(pts)):
        nxt = pts[(i + 1) % len(pts)]
        gap = (nxt - pts[i]) % 360
        if gap == 0:
            gap = 360
        gaps.append(gap)
    return 360 - max(gaps)


# ============================================================
# Pattern detectors
# ============================================================
def _check_th_rupduang(planets, dignities, asc_rasi) -> List[AstroPattern]:
    """หมวด 1 รูปดวงไทย"""
    out: List[AstroPattern] = []
    main_rasis = [planets[p].zodiac.rasi for p in MAIN_PLANETS_7 if p in planets]
    rasi_set = set(main_rasis)

    # TH-001 มาลัยโยค: ดาวสำคัญ ≥ 5 ดวงในราศีต่อเนื่อง
    span = _consecutive_rasi_span(rasi_set)
    out.append(AstroPattern(
        code="TH-001", name="มาลัยโยค", category="รูปดวงไทย", level="A",
        matched=span >= 5,
        tone="good",
        description=f"ราศีต่อเนื่องที่มีดาวสำคัญ = {span} ราศี",
        meaning="ชีวิตมีทิศทางต่อเนื่อง สร้างฐานะด้วยตนเอง สำเร็จค่อยเป็นค่อยไป เหมาะสร้างกิจการ",
        advice=(
            "" if span >= 5 else
            f"ขาดอีก {5 - span} ราศีต่อเนื่อง — ถ้าดาวจรเสาร์/พฤหัสเข้าราศีติดกัน "
            "ระยะนั้นเรื่องราวจะลื่นไหลขึ้นชั่วคราว"
        ),
    ))

    # TH-002 คันศรโยค: ดาวทั้งหมดอยู่ในครึ่งวงจักร (≤ 180°)
    all_rasis = [planets[p].zodiac.rasi for p in planets if p in MAIN_PLANETS_7]
    arc = _arc_span_degrees(all_rasis)
    out.append(AstroPattern(
        code="TH-002", name="คันศรโยค", category="รูปดวงไทย", level="A",
        matched=arc <= 180,
        tone="good",
        description=f"ช่วงราศีของดาวสำคัญกินมุม ≈ {arc}°",
        meaning="มุ่งมั่น เป้าหมายชัด สำเร็จจากความเชี่ยวชาญเฉพาะด้าน",
        advice=(
            "" if arc <= 180 else
            f"ดาวกระจายกว้าง {arc}° (เกิน 180°) — ดวงนี้ถนัดหลายเรื่อง ต้องเลือกโฟกัสเอง"
        ),
    ))

    # TH-003 จตุสดัย: ดาวสำคัญในราศีจร (จัตุรัส) — เมษ(0), กรกฎ(3), ตุลย์(6), มกร(9)
    # ตามตำราไทย "ราศีทวารทั้งสี่" — รูปคล้ายจัตุรัสในจักรราศี
    CHARA_RASI = {0, 3, 6, 9}
    chara_planets = [
        p for p in MAIN_PLANETS_7
        if p in planets and planets[p].zodiac.rasi in CHARA_RASI
    ]
    out.append(AstroPattern(
        code="TH-003", name="จตุสดัย", category="รูปดวงไทย", level="A",
        matched=len(chara_planets) >= 3,
        tone="good",
        description=(
            f"ดาวสำคัญในราศีจร (เมษ/กรกฎ/ตุลย์/มกร): "
            f"{len(chara_planets)} ดวง ({', '.join(chara_planets) or '—'})"
        ),
        meaning="ดวงผู้นำ มีอำนาจการบริหาร ได้รับการยอมรับจากสังคม รักการริเริ่ม",
        planets_involved=chara_planets,
        advice=(
            "" if len(chara_planets) >= 3 else
            f"ขาดอีก {3 - len(chara_planets)} ดวงในราศีจร — "
            "ช่วงดาวจรเสาร์/พฤหัสเข้าราศีจร (เมษ/กรกฎ/ตุลย์/มกร) "
            "จะหนุนเรื่องการเริ่มต้นและบารมีให้ชั่วคราว"
        ),
    ))

    # TH-004 ลัคนานำพล: จำนวนดาวในเรือน 1-6 > 7-12
    upper = sum(
        1 for p in MAIN_PLANETS_7
        if p in planets and 1 <= _rasi_to_house(planets[p].zodiac.rasi, asc_rasi) <= 6
    )
    lower = sum(
        1 for p in MAIN_PLANETS_7
        if p in planets and 7 <= _rasi_to_house(planets[p].zodiac.rasi, asc_rasi) <= 12
    )
    out.append(AstroPattern(
        code="TH-004", name="ลัคนานำพล", category="รูปดวงไทย", level="A",
        matched=upper > lower,
        tone="good",
        description=f"ดาวเรือน 1-6 = {upper} ดวง / เรือน 7-12 = {lower} ดวง",
        meaning="ผู้นำ กล้าตัดสินใจ ชอบริเริ่ม — พึ่งตนเองได้สูง",
        advice=(
            "" if upper > lower else
            "ดวงเอนไปฝั่งคู่ครอง/หุ้นส่วน (ภพ 7-12 มากกว่า) — ความสำเร็จจะมาจากการร่วมมือมากกว่าทำคนเดียว"
        ),
    ))
    return out


def _lagna_group_of(asc_rasi: int) -> Optional[str]:
    """หาว่าลัคนาอยู่ในกลุ่มไหน (นระ/อัมพุ/กีฏะ/ปัศวะ)"""
    for name, rasi_set in LAGNA_GROUP.items():
        if asc_rasi in rasi_set:
            return name
    return None


def _check_th_lagna(asc_rasi: int) -> List[AstroPattern]:
    """หมวด 2 กลุ่มลัคนา (TH-101..104) — เลือก match กลุ่มเดียว"""
    out: List[AstroPattern] = []
    for name, rasi_set in LAGNA_GROUP.items():
        out.append(AstroPattern(
            code=f"TH-{101 + list(LAGNA_GROUP).index(name)}",
            name=name, category="กลุ่มลัคนา", level="A",
            matched=asc_rasi in rasi_set,
            tone="good",
            description=f"ลัคนา{RASI_NAMES_TH[asc_rasi]}อยู่ในกลุ่ม{name}",
            meaning=LAGNA_GROUP_MEANING[name],
            advice="",
        ))
    return [p for p in out if p.matched]


def _check_ong_udom(asc_rasi: int, planets) -> List[AstroPattern]:
    """องค์เกณฑ์ + อุดมเกณฑ์ ตามตำราไทย (TH-105, TH-106)

    องค์เกณฑ์ = ดาวที่กำหนด ลงในภพเฉพาะ ตามกลุ่มลัคนา → ยศศักดิ์/อำนาจ
    อุดมเกณฑ์ = ดาวลงในภพ 1/3/4/7/11 → ทรัพย์สิน/บริวาร
        - ลัคนานระเกณฑ์: เฉพาะดาวพุธ/พฤหัส/ศุกร์/เสาร์
        - ลัคนากลุ่มอื่น: ดาวใด ๆ
    """
    out: List[AstroPattern] = []
    group = _lagna_group_of(asc_rasi)
    if group is None:
        return out

    # ---- TH-105 องค์เกณฑ์ ----
    rule = ONG_KEN_RULES[group]
    target_house = rule["house"]
    target_planets = rule["planets"]
    qualifying = [
        p for p in target_planets
        if p in planets
        and _rasi_to_house(planets[p].zodiac.rasi, asc_rasi) == target_house
    ]
    ok = len(qualifying) >= 1
    planets_str = "/".join(sorted(target_planets))
    out.append(AstroPattern(
        code="TH-105", name="องค์เกณฑ์", category="เกณฑ์ลัคนา (ยศ-ทรัพย์)", level="A",
        matched=ok, tone="good",
        description=(
            f"ลัคนากลุ่ม{group} → ต้องมีดาว {planets_str} "
            f"ในภพ {target_house} ({rule['house_name']}) — "
            f"พบ {len(qualifying)} ดวง ({', '.join(qualifying) or '—'})"
        ),
        meaning=rule["result"],
        planets_involved=qualifying,
        advice=("" if ok else
                f"ขาด: ต้องมีดาว {planets_str} อย่างน้อย 1 ดวง ลงภพ {target_house} "
                f"({rule['house_name']}) — ดาวจรเสริมที่ภพนี้จะช่วยชั่วคราว"),
    ))

    # ---- TH-106 อุดมเกณฑ์ ----
    if group == "นระเกณฑ์":
        allowed = UDOM_NRA_PLANETS
        rule_text = f"ดาว {'/'.join(sorted(allowed))} ลงภพ 1/3/4/7/11"
    else:
        allowed = set(MAIN_PLANETS_7) | {"ราหู", "เกตุ", "มฤตยู"}
        rule_text = "ดาวใด ๆ ลงภพ 1/3/4/7/11 (โบราณจารย์อนุโลม)"

    udom_planets = []
    for p in allowed:
        if p in planets:
            h = _rasi_to_house(planets[p].zodiac.rasi, asc_rasi)
            if h in UDOM_HOUSES:
                udom_planets.append(f"{p}(ภพ{h})")

    ok2 = len(udom_planets) >= 1
    out.append(AstroPattern(
        code="TH-106", name="อุดมเกณฑ์", category="เกณฑ์ลัคนา (ยศ-ทรัพย์)", level="A",
        matched=ok2, tone="good",
        description=(
            f"ลัคนากลุ่ม{group} → {rule_text} — "
            f"พบ {len(udom_planets)} ดวง ({', '.join(udom_planets) or '—'})"
        ),
        meaning="ทรัพย์สิน เงินทอง บริวารพร้อม — ความมั่งคั่งและความสมบูรณ์พูนสุข",
        planets_involved=[s.split("(")[0] for s in udom_planets],
        advice=("" if ok2 else
                "ไม่มีดาวเข้าภพอุดม (1/3/4/7/11) — รายได้ต้องพึ่งความขยันมากกว่าโชค"),
    ))
    return out


def _check_pancha(planets, dignities, asc_rasi) -> List[AstroPattern]:
    """หมวด 3 ปัญจมหาบุรุษ (VE-001..005)"""
    out: List[AstroPattern] = []
    for planet, (code, name, meaning) in PANCHA.items():
        if planet not in planets or planet not in dignities:
            continue
        d = dignities[planet]
        house = _rasi_to_house(planets[planet].zodiac.rasi, asc_rasi)
        is_strong = d.is_exalted or d.dignity == "เกษตร" or d.dignity == "มูล"
        is_kendra = house in KENDRA_HOUSES
        matched = is_strong and is_kendra

        if matched:
            desc = (
                f"{planet}{d.label} ในราศี{d.rasi_name} (ภพ {house}) — เกณฑ์ครบ"
            )
            advice = ""
        else:
            missing = []
            if not is_strong:
                missing.append(f"ดาว{planet}ยังไม่ได้ตำแหน่งแกร่ง ({d.label})")
            if not is_kendra:
                missing.append(f"อยู่ภพ {house} ไม่ใช่ภพเกณฑ์ (1/4/7/10)")
            desc = f"{planet}อยู่ราศี{d.rasi_name} ({d.label}) ภพ {house}"
            advice = "ขาด: " + " และ ".join(missing)

        out.append(AstroPattern(
            code=code, name=name, category="ปัญจมหาบุรุษ", level="B",
            matched=matched,
            tone="good",
            description=desc,
            meaning=meaning,
            planets_involved=[planet],
            advice=advice,
        ))
    return out


def _check_yoga_major(planets, dignities, asc_rasi, house_lords) -> List[AstroPattern]:
    """หมวด 4 โยคสำคัญ (VE-101..106)"""
    out: List[AstroPattern] = []
    moon_rasi = planets["จันทร์"].zodiac.rasi if "จันทร์" in planets else None
    jup_rasi = planets["พฤหัสบดี"].zodiac.rasi if "พฤหัสบดี" in planets else None

    # VE-101 คชเกสรีโยค: พฤหัส อยู่ 1/4/7/10 จากจันทร์ + พฤหัสไม่นิจ/ประ
    # ตำราภารตะ (Phaladeepika): พฤหัสต้องไม่อยู่ในราศีศัตรู/นิจ
    if moon_rasi is not None and jup_rasi is not None and "พฤหัสบดี" in dignities:
        d_jup = _house_from_planet(jup_rasi, moon_rasi)
        in_kendra = d_jup in (1, 4, 7, 10)
        jup_dig = dignities["พฤหัสบดี"]
        jup_ok = not jup_dig.is_weak  # ไม่นิจ/ประ/ศัตรู
        ok = in_kendra and jup_ok
        missing = []
        if not in_kendra:
            missing.append(f"พฤหัสอยู่ห่างจันทร์ {d_jup} ราศี (ต้องเป็น 1/4/7/10)")
        if not jup_ok:
            missing.append(f"พฤหัสตก{jup_dig.label} (ต้องไม่นิจ/ประ)")
        out.append(AstroPattern(
            code="VE-101", name="คชเกสรีโยค", category="โยคสำคัญ", level="B",
            matched=ok, tone="good",
            description=(
                f"พฤหัสห่างจันทร์ {d_jup} ราศี + พฤหัส{jup_dig.label}"
            ),
            meaning="ชื่อเสียง บารมี สติปัญญา ได้รับการยอมรับ — โยคที่ตำราภารตะอ้างถึงมากที่สุด",
            planets_involved=["พฤหัสบดี", "จันทร์"],
            advice=("" if ok else
                    "ขาด: " + " และ ".join(missing) +
                    " — ช่วงดาวจรพฤหัสเข้ากุม/เกณฑ์จันทร์เดิม จะหนุนชั่วคราว"),
        ))

    # VE-102 ลักษมีโยค: เจ้าเรือน 9 แข็งแรง + อยู่ภพเกณฑ์/โกณ
    lord9 = house_lords.get(9)
    if lord9 and lord9 in planets and lord9 in dignities:
        d = dignities[lord9]
        house_of_lord = _rasi_to_house(planets[lord9].zodiac.rasi, asc_rasi)
        is_strong = d.is_strong
        in_kt = house_of_lord in (KENDRA_HOUSES | TRIKONA_HOUSES)
        ok = is_strong and in_kt
        out.append(AstroPattern(
            code="VE-102", name="ลักษมีโยค", category="โยคสำคัญ", level="B",
            matched=ok, tone="good",
            description=(
                f"เจ้าเรือนภพ 9 = {lord9} ({d.label}) อยู่ภพ {house_of_lord}"
            ),
            meaning="มั่งคั่ง วาสนา ความสำเร็จระยะยาว — บุญเก่าหนุนเรื่องการเงิน",
            planets_involved=[lord9],
            advice=("" if ok else
                    f"เจ้าเรือนภพ 9 ยังไม่เข้าเกณฑ์ — รักษาดาว{lord9}ไว้ดี ๆ "
                    "(หลีกเลี่ยงตัดสินใจใหญ่ตอนดาวจร{lord9}อ่อนกำลัง)"),
        ))

    # VE-103 อธิโยค: พุธ+พฤหัส+ศุกร์ ครบทั้ง 3 ดวง อยู่ในภพ 6/7/8 จากจันทร์
    # (ตำราภารตะ Brihat Parashara — ต้องครบ 3 ดวง ไม่ใช่แค่บางส่วน)
    if moon_rasi is not None:
        members = []
        for p in ("พุธ", "พฤหัสบดี", "ศุกร์"):
            if p in planets:
                d_h = _house_from_planet(planets[p].zodiac.rasi, moon_rasi)
                if d_h in (6, 7, 8):
                    members.append(p)
        ok = len(members) == 3
        out.append(AstroPattern(
            code="VE-103", name="อธิโยค", category="โยคสำคัญ", level="B",
            matched=ok, tone="good",
            description=(
                f"ศุภเคราะห์ในภพ 6/7/8 จากจันทร์: {len(members)}/3 ดวง "
                f"({', '.join(members) or '—'})"
            ),
            meaning="ตำแหน่งสูง ผู้บริหาร ขุนนาง — บารมีในที่ทำงาน",
            planets_involved=members,
            advice=("" if ok else
                    f"ขาดอีก {3 - len(members)} ดวง — ต้องอาศัยจังหวะดาวจรของศุภเคราะห์ "
                    "เข้าตำแหน่ง 6/7/8 จากจันทร์เดิมพร้อมกันถึงเกิดผล"),
        ))

    # VE-104 อมลโยค: ศุภเคราะห์อยู่ภพ 10
    in_h10 = []
    for p in BENEFICS:
        if p in planets and _rasi_to_house(planets[p].zodiac.rasi, asc_rasi) == 10:
            in_h10.append(p)
    out.append(AstroPattern(
        code="VE-104", name="อมลโยค", category="โยคสำคัญ", level="B",
        matched=len(in_h10) >= 1, tone="good",
        description=f"ศุภเคราะห์ในภพ 10 (กัมมะ): {', '.join(in_h10) or '—'}",
        meaning="ชื่อเสียงดี คุณธรรม เกียรติยศ — งานสะอาด คนชม",
        planets_involved=in_h10,
        advice=("" if in_h10 else
                "ไม่มีศุภเคราะห์ในภพการงาน — ระวังภาพลักษณ์อาชีพ ทำงานต้องโปร่งใส"),
    ))

    # VE-105 ราชาโยค: เจ้าเรือนเกณฑ์ (1/4/7/10) สัมพันธ์ (กุมหรือเล็ง) เจ้าเรือนโกณ (1/5/9)
    kendra_lords = {house_lords[h] for h in (1, 4, 7, 10) if h in house_lords}
    trikona_lords = {house_lords[h] for h in (1, 5, 9) if h in house_lords}
    pairs = []
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl == tl:
                continue
            if kl in planets and tl in planets:
                r1 = planets[kl].zodiac.rasi
                r2 = planets[tl].zodiac.rasi
                if r1 == r2 or (r1 - r2) % 12 == 6:
                    pairs.append((kl, tl))
    out.append(AstroPattern(
        code="VE-105", name="ราชาโยค", category="โยคสำคัญ", level="B",
        matched=bool(pairs), tone="good",
        description=(
            "เจ้าเรือนเกณฑ์-โกณสัมพันธ์: "
            + (", ".join(f"{a}↔{b}" for a, b in pairs[:3]) or "ไม่พบคู่")
        ),
        meaning="อำนาจ วาสนา ความสำเร็จทางสังคม — ดวง 'เกิดเป็นเจ้าคน'",
        planets_involved=list({p for pair in pairs for p in pair}),
        advice=("" if pairs else
                "เจ้าเรือนเกณฑ์/โกณยังไม่พบกัน — ต้องสร้างเครือข่ายเอง อย่ารอโอกาสมาเอง"),
    ))

    # VE-106 ธนโยค: เจ้าเรือน 2/5/9/11 สัมพันธ์ (กุม/เล็ง) ตั้งแต่ 2 คู่ขึ้นไป
    wealth_houses = (2, 5, 9, 11)
    wealth_lords = [(h, house_lords.get(h)) for h in wealth_houses if h in house_lords]
    connections = []
    for i, (h1, l1) in enumerate(wealth_lords):
        for h2, l2 in wealth_lords[i + 1:]:
            if not l1 or not l2 or l1 == l2:
                continue
            if l1 in planets and l2 in planets:
                r1 = planets[l1].zodiac.rasi
                r2 = planets[l2].zodiac.rasi
                if r1 == r2 or (r1 - r2) % 12 == 6:
                    connections.append((h1, h2, l1, l2))
    out.append(AstroPattern(
        code="VE-106", name="ธนโยค", category="โยคสำคัญ", level="B",
        matched=len(connections) >= 1, tone="good",
        description=f"คู่เจ้าเรือนทรัพย์ (2/5/9/11) ที่สัมพันธ์กัน: {len(connections)} คู่",
        meaning="ทรัพย์สิน สะสมความมั่งคั่ง — เก็บเงินอยู่",
        planets_involved=list({l for *_, l1, l2 in connections for l in (l1, l2)}),
        advice=("" if connections else
                "เจ้าเรือนทรัพย์ทั้ง 4 ยังไม่เชื่อมโยงกัน — รายได้แต่ละช่องไม่หนุนกัน ต้องบริหารแยก"),
    ))
    return out


def _check_chandra_yoga(planets, asc_rasi) -> List[AstroPattern]:
    """หมวด 5 จันทรโยค (VE-201..205)"""
    out: List[AstroPattern] = []
    if "จันทร์" not in planets or "อาทิตย์" not in planets:
        return out
    moon_rasi = planets["จันทร์"].zodiac.rasi
    sun_rasi = planets["อาทิตย์"].zodiac.rasi
    others = [p for p in MAIN_PLANETS_7 if p not in ("จันทร์", "อาทิตย์") and p in planets]

    in2_moon = [p for p in others if _house_from_planet(planets[p].zodiac.rasi, moon_rasi) == 2]
    in12_moon = [p for p in others if _house_from_planet(planets[p].zodiac.rasi, moon_rasi) == 12]
    in12_sun = [p for p in others if _house_from_planet(planets[p].zodiac.rasi, sun_rasi) == 12]
    in2_sun = [p for p in others if _house_from_planet(planets[p].zodiac.rasi, sun_rasi) == 2]

    out.append(AstroPattern(
        code="VE-201", name="สุนภาโยค", category="จันทรโยค", level="B",
        matched=bool(in2_moon), tone="good",
        description=f"ดาวอยู่ราศีที่ 2 จากจันทร์: {', '.join(in2_moon) or '—'}",
        meaning="พูดดี หาเงินเก่ง — รายได้จากคำพูด/การเจรจา",
        planets_involved=in2_moon,
        advice="" if in2_moon else "ราศีที่ 2 จากจันทร์ว่าง — ต้องเรียนรู้พัฒนาทักษะสื่อสารเอง",
    ))
    out.append(AstroPattern(
        code="VE-202", name="อนภาโยค", category="จันทรโยค", level="B",
        matched=bool(in12_moon), tone="good",
        description=f"ดาวอยู่ราศีที่ 12 จากจันทร์: {', '.join(in12_moon) or '—'}",
        meaning="พึ่งตนเอง สุขุม รอบคอบ — รู้จักออม",
        planets_involved=in12_moon,
        advice="" if in12_moon else "ราศี 12 จากจันทร์ว่าง — ใจไม่มั่นคงเอง ต้องฝึกสมาธิ",
    ))
    out.append(AstroPattern(
        code="VE-203", name="ทุรธราโยค", category="จันทรโยค", level="B",
        matched=bool(in2_moon) and bool(in12_moon), tone="good",
        description=f"มีดาวทั้งราศี 2 และ 12 จากจันทร์",
        meaning="ฐานะมั่นคง ชีวิตสมดุล — ดวงดี 2 ทาง รับ+ออม",
        planets_involved=in2_moon + in12_moon,
        advice=("" if in2_moon and in12_moon else
                "ต้องได้ทั้ง 2 ฝั่ง (สุนภา+อนภา) — ตอนนี้ขาดอย่างน้อย 1 ฝั่ง"),
    ))
    out.append(AstroPattern(
        code="VE-204", name="วาสิโยค", category="จันทรโยค", level="B",
        matched=bool(in12_sun), tone="good",
        description=f"ดาวอยู่ราศีที่ 12 จากอาทิตย์: {', '.join(in12_sun) or '—'}",
        meaning="นักวางแผน นักคิดเงียบ ๆ — งานเบื้องหลัง",
        planets_involved=in12_sun,
        advice="" if in12_sun else "ราศี 12 จากอาทิตย์ว่าง — ตัดสินใจเร็วเกินไป ต้องฝึกใจเย็น",
    ))
    out.append(AstroPattern(
        code="VE-205", name="อุภยจารีโยค", category="จันทรโยค", level="B",
        matched=bool(in2_sun) and bool(in12_sun), tone="good",
        description=f"มีดาวทั้งราศี 2 และ 12 จากอาทิตย์",
        meaning="ความสามารถรอบด้าน ได้รับการยอมรับ",
        planets_involved=in2_sun + in12_sun,
        advice=("" if in2_sun and in12_sun else
                "ขาดดาวฝั่งใดฝั่งหนึ่งของอาทิตย์ — ทำได้ดีบางด้านแต่ไม่ครบ"),
    ))
    return out


def _check_evil_yoga(planets, asc_rasi) -> List[AstroPattern]:
    """หมวด 6 โยคเสีย (MA-001..002)"""
    out: List[AstroPattern] = []
    # บาปเคราะห์ที่กระทบลัคนา: กุม (ภพ 1) หรือ เล็ง (ภพ 7)
    afflict = []
    for p in ("อังคาร", "เสาร์", "ราหู"):
        if p not in planets:
            continue
        h = _rasi_to_house(planets[p].zodiac.rasi, asc_rasi)
        if h in (1, 7):
            afflict.append((p, h))

    # MA-001 พินทุบาทว์: บาปเคราะห์กระทบลัคนาอย่างรุนแรง (อย่างน้อย 1 ดวงกุมลัคนาโดยตรง)
    direct = [(p, h) for p, h in afflict if h == 1]
    out.append(AstroPattern(
        code="MA-001", name="พินทุบาทว์", category="โยคเสีย", level="A",
        matched=bool(direct), tone="warning",
        description=(
            "บาปเคราะห์กุมลัคนาโดยตรง: "
            + (", ".join(p for p, _ in direct) or "ไม่มี")
        ),
        meaning="อุปสรรค ความขัดแย้ง เหตุไม่คาดคิด — ต้องระวังตัวเอง",
        planets_involved=[p for p, _ in direct],
        advice=(
            "" if not direct else
            "ป้องกัน: ทำบุญดาวที่ตก, ระวังหุนหันพลันแล่น, หลีกเลี่ยงการตัดสินใจช่วงดาวจรซ้ำ"
        ),
    ))

    # MA-002 บาปเคราะห์รุมลัคนา: ≥ 2 ดวงกระทบ (กุม+เล็ง รวมกัน)
    out.append(AstroPattern(
        code="MA-002", name="บาปเคราะห์รุมลัคนา", category="โยคเสีย", level="A",
        matched=len(afflict) >= 2, tone="warning",
        description=f"บาปเคราะห์กระทบลัคนา {len(afflict)} ดวง: {', '.join(f'{p}(ภพ{h})' for p,h in afflict) or '—'}",
        meaning="ชีวิตต้องต่อสู้ มีแรงกดดันสูง — แต่คนผ่านได้จะแข็งแกร่งกว่าใคร",
        planets_involved=[p for p, _ in afflict],
        advice=(
            "" if len(afflict) >= 2 else
            "ลัคนาไม่ถูกบาปเคราะห์รุม — ใช้ช่วงนี้สะสมทุน/บุญไว้รับมือดาวจรหนัก ๆ ในอนาคต"
        ),
    ))
    return out


# ============================================================
# Public API
# ============================================================
def detect_astro_patterns(
    chart, dignities: Dict[str, PlanetDignity]
) -> AstroPatternReport:
    """ตรวจหารูปดวง/โยค/เกณฑ์ตาม astropattern.md

    Args:
        chart: thai_astro.chart.Chart
        dignities: ผลลัพธ์ของ compute_all_dignities()
    Returns:
        AstroPatternReport(matched, near_misses)
    """
    asc_rasi = chart.ascendant.zodiac.rasi
    planets = chart.planets
    house_lords = chart.house_lords

    all_patterns: List[AstroPattern] = []
    all_patterns += _check_th_rupduang(planets, dignities, asc_rasi)

    # หมวด 2+3: กลุ่มลัคนา + องค์เกณฑ์ + อุดมเกณฑ์
    # กฎใหม่: แสดง "กลุ่มลัคนา" (TH-101..104) เฉพาะเมื่อเข้าทั้ง TH-105 + TH-106
    lagna_patterns = _check_th_lagna(asc_rasi)
    ong_udom_patterns = _check_ong_udom(asc_rasi, planets)
    ong_ok = any(p.matched and p.code == "TH-105" for p in ong_udom_patterns)
    udom_ok = any(p.matched and p.code == "TH-106" for p in ong_udom_patterns)
    if ong_ok and udom_ok:
        all_patterns += lagna_patterns
    all_patterns += ong_udom_patterns

    all_patterns += _check_pancha(planets, dignities, asc_rasi)
    all_patterns += _check_yoga_major(planets, dignities, asc_rasi, house_lords)
    all_patterns += _check_chandra_yoga(planets, asc_rasi)
    all_patterns += _check_evil_yoga(planets, asc_rasi)

    matched = [p for p in all_patterns if p.matched]
    # near-misses: เฉพาะโยคดีที่พอจะได้ (มี advice) + โยคเสียที่ "เกือบเข้า"
    near_misses = [
        p for p in all_patterns
        if not p.matched and p.advice and p.tone == "good"
    ]
    return AstroPatternReport(matched=matched, near_misses=near_misses)
