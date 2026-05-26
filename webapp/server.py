"""Web app สำหรับผูกดวงโหราศาสตร์ไทย (FastAPI + Jinja2)

เริ่มต้น:
    uvicorn webapp.server:app --reload
    หรือ
    python -m webapp.server
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# เพิ่ม path เพื่อ import thai_astro package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thai_astro.chart import Chart
from thai_astro.lakkana import LOCALITY_ADJUST_SECONDS
from thai_astro.planets import RASI_NAMES_TH, PLANET_ORDER, RASI_LORD
from thai_astro.transit_prophecy import find_transit_aspects, generate_summary
from thai_astro.bhava_lord_prophecy import (
    predict_natal_lords,
    predict_transit_lords,
    generate_bhava_lord_summary,
)
from thai_astro.oracle_narrative import compose_oracle_reading
from thai_astro.dignities import compute_all_dignities, detect_yogas


BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="ผูกดวงโหราศาสตร์ไทย")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# เรียงจังหวัด: กรุงเทพฯ ก่อน แล้วเรียงตามตัวอักษร
PROVINCES = ["กรุงเทพมหานคร"] + sorted(
    [p for p in LOCALITY_ADJUST_SECONDS if p != "กรุงเทพมหานคร"]
)

# ลำดับแสดงดาวพร้อมตัวย่อและสีในธีมไทย
# abbr = เลขไทย (กำเนิด), abbr_arabic = เลขอารบิก (ดาวจร)
PLANET_INFO = [
    {"name": "อาทิตย์",   "abbr": "๑", "abbr_arabic": "1", "color_class": "planet-sun"},
    {"name": "จันทร์",    "abbr": "๒", "abbr_arabic": "2", "color_class": "planet-moon"},
    {"name": "อังคาร",   "abbr": "๓", "abbr_arabic": "3", "color_class": "planet-mars"},
    {"name": "พุธ",       "abbr": "๔", "abbr_arabic": "4", "color_class": "planet-mercury"},
    {"name": "พฤหัสบดี", "abbr": "๕", "abbr_arabic": "5", "color_class": "planet-jupiter"},
    {"name": "ศุกร์",     "abbr": "๖", "abbr_arabic": "6", "color_class": "planet-venus"},
    {"name": "เสาร์",    "abbr": "๗", "abbr_arabic": "7", "color_class": "planet-saturn"},
    {"name": "ราหู",      "abbr": "๘", "abbr_arabic": "8", "color_class": "planet-rahu"},
    {"name": "เกตุ",      "abbr": "๙", "abbr_arabic": "9", "color_class": "planet-ketu"},
]
PLANET_INFO_MAP = {p["name"]: p for p in PLANET_INFO}


THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]

# ชื่อภพไทยดั้งเดิม 12 ภพ (index 0 = ภพ 1 = ตนุ)
BHAVA_NAMES = [
    "ตนุ",       # 1
    "กดุมภะ",   # 2
    "สหัชชะ",   # 3
    "พันธุ",     # 4
    "ปุตตะ",     # 5
    "อริ",       # 6
    "ปัตนิ",     # 7
    "มรณะ",      # 8
    "ศุภะ",      # 9
    "กัมมะ",     # 10
    "ลาภะ",      # 11
    "วินาส",     # 12
]

# ความหมายของภพแต่ละหลัก (สำหรับคนทั่วไป)
BHAVA_MEANINGS = [
    {"name": "ตนุ",     "short": "ตัวตน",          "full": "ตัวเอง บุคลิกภาพ รูปร่างหน้าตา สุขภาพพื้นฐาน"},
    {"name": "กดุมภะ", "short": "ทรัพย์สิน",      "full": "เงินทอง ทรัพย์สมบัติ รายได้ คำพูด"},
    {"name": "สหัชชะ", "short": "พี่น้อง",          "full": "พี่น้อง เพื่อน การเดินทางใกล้ การสื่อสาร"},
    {"name": "พันธุ",   "short": "ครอบครัว",      "full": "บิดามารดา ครอบครัว ที่อยู่อาศัย จิตใจ"},
    {"name": "ปุตตะ",   "short": "บุตร/ความรัก", "full": "บุตร ความรัก ความสุข สติปัญญา ความคิดสร้างสรรค์"},
    {"name": "อริ",     "short": "ศัตรู/โรค",      "full": "ศัตรู โรคภัยไข้เจ็บ ลูกน้อง อุปสรรค หนี้สิน"},
    {"name": "ปัตนิ",   "short": "คู่ครอง",         "full": "คู่ครอง คู่สัญญา หุ้นส่วน ความสัมพันธ์"},
    {"name": "มรณะ",    "short": "อายุ/อันตราย",  "full": "อายุขัย อันตราย มรดก ความลับ การเปลี่ยนแปลงใหญ่"},
    {"name": "ศุภะ",    "short": "บุญ/โชค",        "full": "บุญกุศล โชคลาภ การศึกษา ความเชื่อ การเดินทางไกล"},
    {"name": "กัมมะ",   "short": "การงาน",         "full": "การงาน อาชีพ เกียรติยศ ตำแหน่ง ชื่อเสียง"},
    {"name": "ลาภะ",    "short": "ลาภยศ",          "full": "ลาภยศ มิตรสหาย ความสำเร็จตามที่หวัง รายได้พิเศษ"},
    {"name": "วินาส",   "short": "สูญเสีย",         "full": "การสูญเสีย ศัตรูลับ ความทุกข์ คุก โรงพยาบาล ต่างแดน"},
]


# ===== ค่าคงที่สำหรับวงกลมจักรราศี (SVG) =====
SVG_SIZE = 660                    # ขยายเพื่อเผื่อพื้นที่วงดาวจร
SVG_CENTER = SVG_SIZE / 2
R_OUTER = 260                     # ขอบนอกของวงราศี
R_OUTER_TRANSIT = 312             # ขอบนอกสุด (รวมวงดาวจร)
R_INNER = 100                     # ขอบในของวงราศี
R_LABEL = 232                     # ชื่อราศี
R_BHAVA = 118                     # ชื่อภพ (ติดวงใน)
R_PLANET = 175                    # natal planet chips
R_PLANET_OUTER = 200              # แถวนอกเมื่อมีดาวเยอะ
R_PLANET_INNER = 150              # แถวในเมื่อมีดาวเยอะ
R_TRANSIT = 286                   # transit planet chips (ระหว่างขอบนอกของวงราศี กับขอบสุด)
R_LAGNA_MARKER = 215              # ตำแหน่ง "ลั" - ระหว่าง planet chips กับ rasi label


def parse_thai_date(s: str) -> tuple[int, int, int]:
    """แปลงสตริงรูปแบบ dd/mm/yyyy (พ.ศ.) เป็น (ค.ศ. year, month, day)

    ตัวอย่าง: '15/05/2533' -> (1990, 5, 15)
    """
    s = s.strip()
    parts = s.split("/")
    if len(parts) != 3:
        raise ValueError(f"รูปแบบต้องเป็น DD/MM/YYYY ({s})")
    day = int(parts[0])
    month = int(parts[1])
    be_year = int(parts[2])
    if be_year < 1000:
        # เผื่อเผลอกรอกปี ค.ศ. โดยไม่ตั้งใจ
        raise ValueError(f"ปีต้องเป็น พ.ศ. (4 หลัก) — ได้รับ {be_year}")
    ce_year = be_year - 543
    if not (1 <= month <= 12 and 1 <= day <= 31):
        raise ValueError(f"วันหรือเดือนไม่ถูกต้อง ({s})")
    return ce_year, month, day


def _polar_to_xy(angle_deg: float, radius: float) -> tuple[float, float]:
    """แปลงมุม (องศา) + รัศมี เป็นพิกัด SVG (มี y กลับด้าน)
    องศาแบบคณิตศาสตร์: 0° = ทิศตะวันออก (ขวา), 90° = ทิศเหนือ (บน)
    """
    rad = math.radians(angle_deg)
    return (
        SVG_CENTER + radius * math.cos(rad),
        SVG_CENTER - radius * math.sin(rad),
    )


def _chip_layout(
    n: int,
    center_angle: float,
    base_radius: float = R_PLANET,
    spread_inner: float = 22,
    spread_outer: float = 22,
) -> list[tuple[float, float]]:
    """กระจาย planet chip ในเซกเตอร์หนึ่งราศี

    1 ดวง: ตรงกลาง
    2-3 ดวง: เรียงในแนวอาร์คเดียว
    4+ ดวง: แบ่ง 2 แถว (นอก-ใน)
    """
    if n == 0:
        return []
    if n == 1:
        return [_polar_to_xy(center_angle, base_radius)]
    if n <= 3:
        spread = 10
        step = spread / (n - 1)
        return [
            _polar_to_xy(center_angle - spread / 2 + i * step, base_radius)
            for i in range(n)
        ]
    half = (n + 1) // 2
    rows: list[list[tuple[float, float]]] = []
    for count, radius in [
        (half, base_radius + spread_outer),
        (n - half, base_radius - spread_inner),
    ]:
        if count == 0:
            continue
        if count == 1:
            rows.append([_polar_to_xy(center_angle, radius)])
        else:
            spread = 14
            step = spread / (count - 1)
            rows.append([
                _polar_to_xy(center_angle - spread / 2 + i * step, radius)
                for i in range(count)
            ])
    out: list[tuple[float, float]] = []
    for row in rows:
        out.extend(row)
    return out


def _transit_chip_layout(n: int, center_angle: float) -> list[tuple[float, float]]:
    """กระจาย transit chip ในวงนอก (radius เล็กกว่า แถวเดียวเป็นหลัก)"""
    if n == 0:
        return []
    if n == 1:
        return [_polar_to_xy(center_angle, R_TRANSIT)]
    spread = min(18, 7 * (n - 1))
    step = spread / (n - 1) if n > 1 else 0
    return [
        _polar_to_xy(center_angle - spread / 2 + i * step, R_TRANSIT)
        for i in range(n)
    ]


def build_circular_layout(
    rasis: list[dict],
    transits_by_rasi: Optional[dict[int, list[dict]]] = None,
    ascendant: Optional[dict] = None,
) -> dict:
    """สร้างข้อมูลพิกัด SVG สำหรับวงกลมจักรราศี

    เมษ (index 0) อยู่ด้านบน (มุม 90°) ทวนเข็มนาฬิกาไปจนถึงมีน (index 11)
    แต่ละราศีกว้าง 30° เซกเตอร์ของราศี i อยู่ระหว่างมุม [75 + 30i, 105 + 30i]

    transits_by_rasi: mapping จาก rasi_index -> list ของ transit planet dict
                      (มี name/abbr_arabic/color_class) — ถ้ามี จะวาดวงดาวจรนอก
    """
    has_transit = bool(transits_by_rasi)
    r_outer_max = R_OUTER_TRANSIT if has_transit else R_OUTER

    dividers = []
    # 12 เส้นแบ่ง ที่มุม 75°, 105°, 135°, ..., 45°
    # ขยายถึง R_OUTER_TRANSIT ถ้ามีวงดาวจร
    for i in range(12):
        angle = 75 + 30 * i
        x1, y1 = _polar_to_xy(angle, R_INNER)
        x2, y2 = _polar_to_xy(angle, r_outer_max)
        dividers.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})

    rasi_out = []
    for r in rasis:
        center_angle = 90 + 30 * r["index"]
        label_x, label_y = _polar_to_xy(center_angle, R_LABEL)
        bhava_x, bhava_y = _polar_to_xy(center_angle, R_BHAVA)

        # natal chips
        chip_xy = _chip_layout(len(r["planets"]), center_angle)
        chip_data = []
        for (x, y), planet in zip(chip_xy, r["planets"]):
            chip_data.append({**planet, "x": x, "y": y})

        # transit chips (วงนอก)
        transit_chips = []
        if has_transit:
            tlist = transits_by_rasi.get(r["index"], [])
            txys = _transit_chip_layout(len(tlist), center_angle)
            for (x, y), tp in zip(txys, tlist):
                transit_chips.append({**tp, "x": x, "y": y})

        # arc path สำหรับ highlight ราศีลัคนา (จาก R_INNER ถึง r_outer_max)
        start_angle = center_angle - 15
        end_angle = center_angle + 15
        sx1, sy1 = _polar_to_xy(start_angle, R_INNER)
        sx2, sy2 = _polar_to_xy(start_angle, r_outer_max)
        ex1, ey1 = _polar_to_xy(end_angle, r_outer_max)
        ex2, ey2 = _polar_to_xy(end_angle, R_INNER)
        sector_path = (
            f"M {sx1:.2f} {sy1:.2f} "
            f"L {sx2:.2f} {sy2:.2f} "
            f"A {r_outer_max} {r_outer_max} 0 0 0 {ex1:.2f} {ey1:.2f} "
            f"L {ex2:.2f} {ey2:.2f} "
            f"A {R_INNER} {R_INNER} 0 0 1 {sx1:.2f} {sy1:.2f} Z"
        )

        rasi_out.append({
            **r,
            "center_angle": center_angle,
            "label_x": label_x,
            "label_y": label_y,
            "bhava_x": bhava_x,
            "bhava_y": bhava_y,
            "chips": chip_data,
            "transit_chips": transit_chips,
            "sector_path": sector_path,
        })

    # ตำแหน่งลัคนา (เป๊ะตามองศาในราศี)
    # ในระบบของเรา เซกเตอร์ราศี i อยู่ระหว่างมุม SVG [75+30i, 105+30i]
    # ที่ degree 0° ในราศี = ขอบล่าง (SVG angle = 75+30i)
    # ที่ degree 30° ในราศี = ขอบบน (SVG angle = 105+30i)
    lagna_marker = None
    if ascendant is not None:
        asc_rasi = ascendant["rasi"]
        asc_deg = ascendant["degree"] + ascendant.get("arcminute", 0) / 60.0
        asc_angle = 75 + 30 * asc_rasi + asc_deg
        lx, ly = _polar_to_xy(asc_angle, R_LAGNA_MARKER)
        # เส้นชี้ลัคนา จากขอบในมาขอบของ chip
        line_x1, line_y1 = _polar_to_xy(asc_angle, R_INNER)
        line_x2, line_y2 = _polar_to_xy(asc_angle, R_LAGNA_MARKER - 18)
        lagna_marker = {
            "x": lx,
            "y": ly,
            "angle": asc_angle,
            "line_x1": line_x1,
            "line_y1": line_y1,
            "line_x2": line_x2,
            "line_y2": line_y2,
        }

    return {
        "size": SVG_SIZE,
        "center": SVG_CENTER,
        "r_outer": R_OUTER,
        "r_outer_transit": R_OUTER_TRANSIT,
        "r_inner": R_INNER,
        "has_transit": has_transit,
        "dividers": dividers,
        "rasis": rasi_out,
        "lagna_marker": lagna_marker,
    }


def chart_to_view(
    chart: Chart,
    person_name: str,
    transit_chart: Optional[Chart] = None,
    transit_meta: Optional[dict] = None,
) -> dict:
    """แปลง Chart เป็น dict สำหรับ template

    หมายเหตุ: ผังดวงใช้ตำแหน่งราศี fix (เมษอยู่บนช่องที่ 2, ไล่ทวนเข็มจนถึงมีน)
    แต่ละช่องราศีจะคำนวณว่าเป็นภพอะไรตามลัคนา
    transit_chart: ถ้ามี จะแสดงดาวจรในวงนอก
    """
    asc_rasi = chart.ascendant.zodiac.rasi

    # สร้างข้อมูลทีละราศี (0..11)
    rasis = []
    for rasi_idx in range(12):
        house_num = ((rasi_idx - asc_rasi) % 12) + 1
        planets_here = []
        for name in PLANET_ORDER:
            p = chart.planets[name]
            if p.zodiac.rasi != rasi_idx:
                continue
            info = PLANET_INFO_MAP[name]
            planets_here.append({
                **info,
                "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
                "degree": p.zodiac.degree,
                "arcminute": p.zodiac.arcminute,
                "arcsecond": p.zodiac.arcsecond,
                "retrograde": p.retrograde,
                "source": "กำเนิด",
            })
        rasis.append({
            "index": rasi_idx,
            "name": RASI_NAMES_TH[rasi_idx],
            "house": house_num,
            "bhava": BHAVA_NAMES[house_num - 1],
            "lord": RASI_LORD[rasi_idx],
            "planets": planets_here,
            "is_ascendant": rasi_idx == asc_rasi,
        })

    # ดาวจร (transit) — จัดกลุ่มตามราศี + คำทำนาย
    transits_by_rasi: Optional[dict[int, list[dict]]] = None
    transit_positions = None
    transit_aspects = None
    transit_summary = None
    if transit_chart is not None:
        transits_by_rasi = {i: [] for i in range(12)}
        transit_positions = []
        for name in PLANET_ORDER:
            if name not in transit_chart.planets:
                continue
            p = transit_chart.planets[name]
            info = PLANET_INFO_MAP[name]
            transit_planet = {
                "name": name,
                "abbr": info["abbr_arabic"],     # ใช้เลขอารบิก
                "color_class": info["color_class"],
                "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
                "degree": p.zodiac.degree,
                "arcminute": p.zodiac.arcminute,
                "arcsecond": p.zodiac.arcsecond,
                "retrograde": p.retrograde,
                "source": "จร",
            }
            transits_by_rasi[p.zodiac.rasi].append(transit_planet)
            transit_positions.append({
                "name": name,
                "abbr": info["abbr_arabic"],
                "color_class": info["color_class"],
                "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
                "degree": p.zodiac.degree,
                "arcminute": p.zodiac.arcminute,
                "retrograde": p.retrograde,
            })

        # คำทำนายดาวจรกระทบดาวเดิม
        aspects = find_transit_aspects(chart.planets, transit_chart.planets)
        transit_summary = generate_summary(aspects)
        transit_aspects = []
        for a in aspects:
            transit_aspects.append({
                "transit_planet": a.transit_planet,
                "transit_abbr": PLANET_INFO_MAP[a.transit_planet]["abbr_arabic"],
                "transit_color": PLANET_INFO_MAP[a.transit_planet]["color_class"],
                "transit_rasi": a.transit_rasi,
                "natal_planet": a.natal_planet,
                "natal_abbr": PLANET_INFO_MAP[a.natal_planet]["abbr"],
                "natal_color": PLANET_INFO_MAP[a.natal_planet]["color_class"],
                "natal_rasi": a.natal_rasi,
                "aspect_type": a.aspect_type,
                "prediction": a.prediction,
                "severity": a.severity,
                "duration": a.duration_note,
            })

    planet_positions = []
    for name in PLANET_ORDER:
        if name not in chart.planets:
            continue
        p = chart.planets[name]
        house = chart._rasi_to_house(p.zodiac.rasi)
        info = PLANET_INFO_MAP[name]
        planet_positions.append({
            "name": name,
            "abbr": info["abbr"],
            "color_class": info["color_class"],
            "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
            "degree": p.zodiac.degree,
            "arcminute": p.zodiac.arcminute,
            "house": house,
            "bhava": BHAVA_NAMES[house - 1],
            "retrograde": p.retrograde,
        })

    # คำทำนายเจ้าเรือนครองภพ (Bhava Lord)
    natal_lord_preds = predict_natal_lords(chart.ascendant.zodiac.rasi, chart.planets)
    natal_lord_summary = generate_bhava_lord_summary(natal_lord_preds)
    transit_lord_data = None
    if transit_chart is not None:
        transit_lord_preds = predict_transit_lords(
            chart.ascendant.zodiac.rasi, transit_chart.planets
        )
        transit_lord_data = {
            "summary": generate_bhava_lord_summary(transit_lord_preds),
        }

    # ตำแหน่งกำลังดาว + เกณฑ์โยค
    dignities = compute_all_dignities(chart.planets)
    yogas = detect_yogas(chart.ascendant.zodiac.rasi, chart.planets, dignities)

    # บทพูดโหร (oracle narrative) — สังเคราะห์ทุก source
    oracle_seed = f"{chart.ce_year}-{chart.month}-{chart.day}-{chart.hour}-{chart.minute}"
    oracle_reading = compose_oracle_reading(
        person_name=person_name,
        transit_summary=transit_summary,
        natal_lord_summary=natal_lord_summary,
        transit_lord_summary=transit_lord_data["summary"] if transit_lord_data else None,
        yogas=yogas,
        dignities=dignities,
        seed=oracle_seed,
    )

    d = chart.desire
    sr = d.surathin

    return {
        "person_name": person_name,
        "birth_date_th": f"{chart.day} {THAI_MONTHS[chart.month]} พ.ศ. {chart.be_year}",
        "birth_date_iso": f"{chart.ce_year:04d}-{chart.month:02d}-{chart.day:02d}",
        "birth_time": f"{chart.hour:02d}:{chart.minute:02d}",
        "province": chart.province,
        "ce_year": chart.ce_year,
        "be_year": chart.be_year,
        "ascendant": {
            "rasi_name": chart.ascendant.zodiac.rasi_name,
            "degree": chart.ascendant.zodiac.degree,
            "arcminute": chart.ascendant.zodiac.arcminute,
        },
        "chart_lord": chart.chart_lord,
        "rasis": rasis,
        "circle": build_circular_layout(
            rasis,
            transits_by_rasi,
            ascendant={
                "rasi": chart.ascendant.zodiac.rasi,
                "degree": chart.ascendant.zodiac.degree,
                "arcminute": chart.ascendant.zodiac.arcminute,
            },
        ),
        "planets": planet_positions,
        "transit": ({
            "date_th": transit_meta.get("date_th") if transit_meta else None,
            "time": transit_meta.get("time") if transit_meta else None,
            "province": transit_meta.get("province") if transit_meta else None,
            "planets": transit_positions,
            "aspects": transit_aspects,
            "summary": transit_summary,
            "bhava_lords": transit_lord_data["summary"] if transit_lord_data else None,
        } if transit_chart is not None else None),
        "natal_bhava_lords": natal_lord_summary,
        "oracle": oracle_reading,
        "info": {
            "cs_year": sr.thaloengsok_cs_year,
            "thaloengsok": f"{sr.thaloengsok.day} {THAI_MONTHS[sr.thaloengsok.month]} {sr.thaloengsok.be_year}",
            "surathin": sr.total_days,
            "horakhun": d.horakhun,
            "julian": d.julian_date,
            "kammatchaphon": d.kammatchaphon,
            "ujapon": d.ujapon,
            "dithi": d.dithi,
        },
    }


_DEFAULT_FORM = {
    "name": "",
    "birth_date_th": "",
    "birth_time": "",
    "province": "กรุงเทพมหานคร",
    "transit_date_th": "",
    "transit_time": "",
    "transit_province": "กรุงเทพมหานคร",
}


def _common_context(request: Request, **extra) -> dict:
    base = {
        "request": request,
        "provinces": PROVINCES,
        "bhava_meanings": BHAVA_MEANINGS,
    }
    base.update(extra)
    return base


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        _common_context(
            request,
            result=None,
            form=_DEFAULT_FORM.copy(),
            error=None,
        ),
    )


def _format_thai_date_ce(year: int, month: int, day: int) -> str:
    return f"{day} {THAI_MONTHS[month]} พ.ศ. {year + 543}"


@app.post("/", response_class=HTMLResponse)
async def calculate(
    request: Request,
    name: str = Form(""),
    birth_date_th: str = Form(""),
    birth_time: str = Form(""),
    province: str = Form("กรุงเทพมหานคร"),
    transit_date_th: str = Form(""),
    transit_time: str = Form(""),
    transit_province: str = Form("กรุงเทพมหานคร"),
) -> HTMLResponse:
    form = {
        "name": name,
        "birth_date_th": birth_date_th,
        "birth_time": birth_time,
        "province": province,
        "transit_date_th": transit_date_th,
        "transit_time": transit_time,
        "transit_province": transit_province,
    }
    error: Optional[str] = None
    result = None

    try:
        if not birth_date_th.strip():
            raise ValueError("กรุณากรอกวันเดือนปีเกิด (พ.ศ.)")
        if not birth_time.strip():
            raise ValueError("กรุณากรอกเวลาเกิด")
        y, m, d = parse_thai_date(birth_date_th)
        h, mi = [int(x) for x in birth_time.split(":")]
        if province not in LOCALITY_ADJUST_SECONDS:
            province = "กรุงเทพมหานคร"
        chart = Chart.calculate(y, m, d, h, mi, province=province)

        # ดาวจร — กรอกหรือไม่ก็ได้
        transit_chart = None
        transit_meta = None
        if transit_date_th and transit_time:
            ty, tm, td = parse_thai_date(transit_date_th)
            th, tmin = [int(x) for x in transit_time.split(":")]
            tprov = (
                transit_province
                if transit_province in LOCALITY_ADJUST_SECONDS
                else "กรุงเทพมหานคร"
            )
            transit_chart = Chart.calculate(ty, tm, td, th, tmin, province=tprov)
            transit_meta = {
                "date_th": _format_thai_date_ce(ty, tm, td),
                "time": transit_time,
                "province": tprov,
            }

        result = chart_to_view(
            chart,
            person_name=name,
            transit_chart=transit_chart,
            transit_meta=transit_meta,
        )
    except (ValueError, IndexError) as e:
        error = f"กรอกข้อมูลไม่ถูกต้อง: {e}"

    return templates.TemplateResponse(
        request,
        "index.html",
        _common_context(
            request,
            result=result,
            form=form,
            error=error,
        ),
    )


def main() -> None:
    import uvicorn
    uvicorn.run(
        "webapp.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
