"""Web app สำหรับผูกดวงโหราศาสตร์ไทย (FastAPI + Jinja2)

เริ่มต้น:
    uvicorn webapp.server:app --reload
    หรือ
    python -m webapp.server
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
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
from thai_astro.taksa import (
    compute_taksa, compute_transit_taksa, transit_aspects_on_taksa,
)
from thai_astro.lunar import compute_lunar_date
from thai_astro.triyangka import (
    get_triyangka_info,
    all_decanate_lords,
    ELEMENT_INFO,
    POISON_INFO,
    RASHI_ELEMENT,
)
from thai_astro.horathaynu.api import predict as horathaynu_predict, predict_from_datetime as horathaynu_predict_dt
from thai_astro.horathaynu.core.caster import cast_chain as horathaynu_cast
from thai_astro.horathaynu.core.bhava import BHAVA_NAMES_TH as HORATHAYNU_BHAVA_NAMES
from thai_astro.horathaynu.core.caster import PLACEMENT_ORDER as HORATHAYNU_PLACEMENT_ORDER
from thai_astro.horathaynu.core.time_to_yam import yam_range as horathaynu_yam_range
from thai_astro.horathaynu.core.time_precision import time_to_bhava_cell as horathaynu_time_cell
from thai_astro.horathaynu.data.lordship import lord_of as horathaynu_lord_of
from thai_astro.horathaynu.data.planet_meanings import PLANET_NAME_TH as HORATHAYNU_PLANET_NAME_TH
from thai_astro.horathaynu.core.prophecy import predict as horathaynu_prophecy


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
    {"name": "มฤตยู",    "abbr": "๐", "abbr_arabic": "0", "color_class": "planet-uranus"},
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
R_LABEL = 222                     # ชื่อราศี (ขยับเข้าใน — กันบังตรียางค์ ที่อยู่ R=248)
R_BHAVA = 110                     # ชื่อภพ (เข้าใกล้ขอบใน)
R_PLANET = 175                    # natal planet chips
R_PLANET_OUTER = 200              # แถวนอกเมื่อมีดาวเยอะ
R_PLANET_INNER = 150              # แถวในเมื่อมีดาวเยอะ
R_TRANSIT = 286                   # transit planet chips (ระหว่างขอบนอกของวงราศี กับขอบสุด)
R_LAGNA_MARKER = 200              # ตำแหน่ง "ลั" - ระหว่าง planet chips กับ rasi label
R_TRIYANGKA_LORD = 248            # ดาวตรียางค์ — ระหว่างชื่อราศี กับขอบนอกของวงราศี
R_TRIYANGKA_RING_INNER = 240      # ขอบในของวงตรียางค์ (rim line)
R_TRIYANGKA_RING_OUTER = 258      # ขอบนอกของวงตรียางค์ (rim line)
R_ELEMENT_MARKER = 130            # ไอคอนธาตุ — ออกข้างนอกขึ้น (กันบังภพที่ R=110)
R_TRIYANGKA_LABEL_INNER = R_TRIYANGKA_RING_INNER


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
    """กระจาย planet chip ในเซกเตอร์หนึ่งราศี (legacy — ใช้กับ rashi center)

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


def _chip_layout_by_decanate(
    planets: list[dict],
    rashi_start_angle: float,
    base_radius: float = R_PLANET,
) -> list[tuple[float, float]]:
    """วาง chip ตามตรียางค์ที่ดาวกำเนิดตก

    เกณฑ์:
        - decanate 0 (degree 0-10): center_angle = rashi_start + 5
        - decanate 1 (degree 10-20): center_angle = rashi_start + 15
        - decanate 2 (degree 20-30): center_angle = rashi_start + 25
        - ดาวหลายดวงในช่องเดียวกัน: spread แนวรัศมี (in/out)
    """
    n = len(planets)
    if n == 0:
        return []

    # จัดกลุ่มตาม decanate
    groups: dict[int, list[int]] = {0: [], 1: [], 2: []}
    for i, p in enumerate(planets):
        deg = p.get("degree", 0) + p.get("arcminute", 0) / 60.0
        dec = 0 if deg < 10 else (1 if deg < 20 else 2)
        groups[dec].append(i)

    out: list[tuple[float, float] | None] = [None] * n
    for dec, idxs in groups.items():
        sub_center = rashi_start_angle + 5 + dec * 10
        m = len(idxs)
        if m == 1:
            out[idxs[0]] = _polar_to_xy(sub_center, base_radius)
        elif m == 2:
            # 2 chip — ในกับนอก
            out[idxs[0]] = _polar_to_xy(sub_center, base_radius - 14)
            out[idxs[1]] = _polar_to_xy(sub_center, base_radius + 14)
        else:
            # 3+ chip — แบ่ง in/out แล้วกระจายตามมุม
            half = (m + 1) // 2
            for j, idx in enumerate(idxs[:half]):
                spread = min(7 * (half - 1), 12)
                step = spread / (half - 1) if half > 1 else 0
                ang = sub_center - spread / 2 + j * step
                out[idx] = _polar_to_xy(ang, base_radius + 14)
            for j, idx in enumerate(idxs[half:]):
                rest = m - half
                spread = min(7 * (rest - 1), 12)
                step = spread / (rest - 1) if rest > 1 else 0
                ang = sub_center - spread / 2 + j * step if rest > 1 else sub_center
                out[idx] = _polar_to_xy(ang, base_radius - 14)
    return [pt for pt in out if pt is not None]  # type: ignore


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


# ===== Orbit view (geocentric solar-system style) =====
# rx/ry/rot ของวงรีแต่ละดวง (เรียงจากใน → นอกตามความเร็วโคจร)
# Earth/ลัคนา อยู่ center; ทุก orbit รอบ center
ORBIT_PARAMS = {
    # rotation values: เอียงเด่นขึ้น + กระจายต่าง ๆ กัน เลียนรูปอ้างอิง solar system
    "จันทร์":    {"rx":  45, "ry":  36, "rot":   8, "level": 0},
    "อาทิตย์":   {"rx":  72, "ry":  56, "rot":  22, "level": 1},
    "พุธ":       {"rx":  95, "ry":  74, "rot":  -5, "level": 2},
    "ศุกร์":     {"rx": 118, "ry":  92, "rot":  14, "level": 3},
    "อังคาร":    {"rx": 142, "ry": 110, "rot": -18, "level": 4},
    "พฤหัสบดี":  {"rx": 168, "ry": 132, "rot":  18, "level": 5},
    "เสาร์":     {"rx": 195, "ry": 152, "rot":  -8, "level": 6},
    "มฤตยู":     {"rx": 222, "ry": 175, "rot":  28, "level": 7},
    "ราหู":      {"rx": 250, "ry": 195, "rot": -32, "level": 8},
    "เกตุ":      {"rx": 250, "ry": 195, "rot": -32, "level": 8},
}
ORBIT_RASI_RING = 295  # รัศมีของป้ายราศี 12 ทิศรอบนอกสุด (พอดี SVG 660/2 = 330)
ORBIT_DIVIDER_INNER = 28   # เส้นแบ่งราศีเริ่มที่รัศมีนี้ (จาก center)
ORBIT_DIVIDER_OUTER = 278  # เส้นแบ่งราศีจบที่รัศมีนี้


def _orbit_point(rx: float, ry: float, rot_deg: float, angle_deg: float) -> tuple[float, float]:
    """คำนวณตำแหน่ง (x, y) ของจุดบนวงรีที่หมุน rot_deg — parametric angle

    angle_deg: parametric t (ไม่ตรงกับ geometric angle ของ ray จาก center ถ้า ellipse rotated)
    """
    rot = math.radians(rot_deg)
    ang = math.radians(angle_deg)
    x_local = rx * math.cos(ang)
    y_local = ry * math.sin(ang)
    x = x_local * math.cos(rot) - y_local * math.sin(rot)
    y = x_local * math.sin(rot) + y_local * math.cos(rot)
    return (SVG_CENTER + x, SVG_CENTER - y)


def _orbit_point_at_ray_angle(
    rx: float, ry: float, rot_deg: float, angle_deg: float
) -> tuple[float, float]:
    """หาจุด (x, y) บน ellipse ที่ ray จาก center ออกไปที่มุม angle_deg (geometric)

    ใช้สำหรับวาง chip ดาวบน orbit ring โดยให้ตำแหน่ง angular **ตรงกับ longitude
    ของดาวในจักรราศี** (ไม่หมุนตาม ring rotation) — ทำให้ราศีบนผังตรงกับราศีจริง

    Solve ray ∩ rotated_ellipse:
        t² · (cos²(θ−rot)/rx² + sin²(θ−rot)/ry²) = 1
    """
    th = math.radians(angle_deg)
    rot = math.radians(rot_deg)
    diff = th - rot
    denom_sq = (math.cos(diff) / rx) ** 2 + (math.sin(diff) / ry) ** 2
    t = 1.0 / math.sqrt(denom_sq)
    x = t * math.cos(th)
    y = t * math.sin(th)
    return (SVG_CENTER + x, SVG_CENTER - y)


def _build_ellipse_path(cx: float, cy: float, rx: float, ry: float, rot_deg: float) -> str:
    """สร้าง SVG path สำหรับวงรีที่หมุนรอบ center"""
    # ใช้ <ellipse> + transform แทน — ง่ายกว่า return path
    return f"M {cx - rx} {cy} a {rx} {ry} 0 1 0 {2*rx} 0 a {rx} {ry} 0 1 0 {-2*rx} 0"


def build_orbit_layout(
    natal_planets: list[dict],
    transit_planets: Optional[list[dict]] = None,
    ascendant: Optional[dict] = None,
) -> dict:
    """สร้าง orbit-style layout: รอบ center มีวงรี 8-9 วง ดาวอยู่บน ring ของมัน

    natal_planets, transit_planets: list ของ dict ที่มี name, rasi (0-11), degree, arcminute
                                     และ chip metadata (abbr, color_class, etc.)
    """
    rings = []
    chips = []
    transit_chips = []

    def _angle_from_zodiac(rasi_idx: int, deg_in_rasi: float) -> float:
        """zodiac longitude → SVG polar angle

        degree 0° ของราศี = ขอบเริ่ม (ใกล้ราศีก่อนหน้า)
        degree 30° = ขอบจบ (ใกล้ราศีถัดไป)
        Sector ของราศี i บน screen = [75 + 30i, 105 + 30i]
        เมษ 0° = ขอบ มีน/เมษ = angle 75°, เมษ 15° = กลาง = 90° (บน), เมษ 30° = ขอบ เมษ/พฤษภ = 105°
        """
        return 75 + 30 * rasi_idx + deg_in_rasi

    # rings
    for planet_name, params in ORBIT_PARAMS.items():
        # ราหู/เกตุ ใช้ ring เดียวกัน → render ครั้งเดียว (ใช้ planet = "ราหู")
        if planet_name == "เกตุ":
            continue
        rings.append({
            "name": planet_name,
            "rx": params["rx"],
            "ry": params["ry"],
            "rot": params["rot"],
            "level": params["level"],
        })

    # natal chips — ใช้ ray-intersection เพื่อให้ตำแหน่งบนผังตรงกับราศีจริง
    for p in natal_planets:
        params = ORBIT_PARAMS.get(p["name"])
        if not params:
            continue
        deg = p.get("degree", 0) + p.get("arcminute", 0) / 60.0
        ang = _angle_from_zodiac(p.get("rasi", 0), deg)
        x, y = _orbit_point_at_ray_angle(
            params["rx"], params["ry"], params["rot"], ang
        )
        chips.append({**p, "x": x, "y": y, "level": params["level"]})

    # transit chips (วาง offset เล็กน้อยจาก natal — ring ใหญ่ขึ้น 8 หน่วย)
    if transit_planets:
        for p in transit_planets:
            params = ORBIT_PARAMS.get(p["name"])
            if not params:
                continue
            deg = p.get("degree", 0) + p.get("arcminute", 0) / 60.0
            ang = _angle_from_zodiac(p.get("rasi", 0), deg)
            x, y = _orbit_point_at_ray_angle(
                params["rx"] + 8, params["ry"] + 8, params["rot"], ang
            )
            transit_chips.append({**p, "x": x, "y": y, "level": params["level"]})

    # เส้นแบ่งราศี 12 เส้น (radial) — ลากจาก inner ไป outer ที่มุมแบ่ง 75°, 105°, ...
    rasi_dividers = []
    for i in range(12):
        ang = 75 + 30 * i        # เส้นแบ่ง (= ขอบของแต่ละราศี)
        rad = math.radians(ang)
        x1 = SVG_CENTER + ORBIT_DIVIDER_INNER * math.cos(rad)
        y1 = SVG_CENTER - ORBIT_DIVIDER_INNER * math.sin(rad)
        x2 = SVG_CENTER + ORBIT_DIVIDER_OUTER * math.cos(rad)
        y2 = SVG_CENTER - ORBIT_DIVIDER_OUTER * math.sin(rad)
        rasi_dividers.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})

    # ป้าย 12 ราศี รอบนอกสุด (เมษอยู่บนสุด, ทวนเข็มไปเรื่อยๆ — เหมือนผังเดิม)
    rasi_labels = []
    for i in range(12):
        ang = 90 + 30 * i        # center ของราศี
        x = SVG_CENTER + ORBIT_RASI_RING * math.cos(math.radians(ang))
        y = SVG_CENTER - ORBIT_RASI_RING * math.sin(math.radians(ang))
        rasi_labels.append({
            "name": RASI_NAMES_TH[i],
            "x": x, "y": y,
            "is_ascendant": (ascendant is not None and ascendant.get("rasi") == i),
        })

    # marker ลัคนา ที่ center
    asc_marker = None
    if ascendant is not None:
        asc_marker = {
            "rasi_name": RASI_NAMES_TH[ascendant["rasi"]],
            "degree": ascendant["degree"],
            "arcminute": ascendant.get("arcminute", 0),
        }

    return {
        "rings": rings,
        "chips": chips,
        "transit_chips": transit_chips,
        "rasi_labels": rasi_labels,
        "rasi_dividers": rasi_dividers,
        "asc_marker": asc_marker,
        "rasi_ring_radius": ORBIT_RASI_RING,
    }


def build_circular_layout(
    rasis: list[dict],
    transits_by_rasi: Optional[dict[int, list[dict]]] = None,
    ascendant: Optional[dict] = None,
    position_by_degree: bool = True,
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

    # ----- เส้นแบ่งตรียางค์ (2 เส้น/ราศี = 24 เส้น) ที่ 10° และ 20° ในแต่ละราศี -----
    # ใช้ class แยกเพื่อให้ toggle ซ่อน/แสดงได้
    triyangka_dividers = []
    for i in range(12):
        for sub in (1, 2):       # 1/3 และ 2/3 ของราศี
            angle = 75 + 30 * i + 10 * sub
            tx1, ty1 = _polar_to_xy(angle, R_INNER)
            tx2, ty2 = _polar_to_xy(angle, R_TRIYANGKA_LABEL_INNER)
            triyangka_dividers.append(
                {"x1": tx1, "y1": ty1, "x2": tx2, "y2": ty2}
            )

    rasi_out = []
    # planet name → เลขอารบิก 1-7 (ตามตำราโหรไทย):
    # 1=อาทิตย์ 2=จันทร์ 3=อังคาร 4=พุธ 5=พฤหัสบดี 6=ศุกร์ 7=เสาร์
    _planet_short = {
        "อาทิตย์":  "1",
        "จันทร์":   "2",
        "อังคาร":   "3",
        "พุธ":      "4",
        "พฤหัสบดี": "5",
        "ศุกร์":    "6",
        "เสาร์":    "7",
    }
    for r in rasis:
        center_angle = 90 + 30 * r["index"]
        label_x, label_y = _polar_to_xy(center_angle, R_LABEL)
        bhava_x, bhava_y = _polar_to_xy(center_angle, R_BHAVA)

        # ----- ตรียางค์: 3 ดาวครองในแต่ละราศี -----
        # center angle ของแต่ละช่อง 10°:
        #   ปฐม (deg 0-10) → SVG center = 75+30i + 5 = center_angle - 10
        #   ทุติย (deg 10-20) → center_angle
        #   ตติย (deg 20-30) → center_angle + 10
        # หมายเหตุ: ในระบบเราเมษอยู่บน → angle ราศี = 90+30i, sub-sector ตามนี้
        from thai_astro.triyangka import all_decanate_lords as _all_lords
        # อ่าน lord ของราศีนี้ ทั้ง 3 ตรียางค์ (decanate 0, 1, 2)
        rashi_idx = r["index"]
        # คำนวณตำแหน่งของแต่ละ decanate ในมุม SVG
        # decanate 0 (degree 0-10) อยู่ที่ "ขอบล่าง" ของราศีบน SVG (มุมน้อยกว่า center)
        # decanate 2 (degree 20-30) อยู่ที่ "ขอบบน" (มุมมากกว่า center)
        triyangka_markers = []
        for dec in range(3):
            from thai_astro.triyangka import (
                triyangka_lord as _tlord,
                POISON_MAP as _PMAP, POISON_INFO as _PINFO,
            )
            sub_center = (75 + 30 * rashi_idx) + 10 * dec + 5
            tx, ty = _polar_to_xy(sub_center, R_TRIYANGKA_LORD)
            lord_th = _tlord(rashi_idx, dec)
            short = _planet_short.get(lord_th, lord_th[:1])
            # ตรวจพิษของช่องนี้
            poison_type = None
            poison_icon = None
            if rashi_idx in _PMAP and _PMAP[rashi_idx][1] == dec:
                poison_type = _PMAP[rashi_idx][0]
                poison_icon = _PINFO[poison_type]["icon"]
            triyangka_markers.append({
                "decanate": dec,
                "x": tx, "y": ty,
                "lord": lord_th,
                "short": short,
                "is_poison": poison_type is not None,
                "poison_type": poison_type,
                "poison_icon": poison_icon,
            })

        # ----- Element marker ของราศี -----
        elem_key = RASHI_ELEMENT[rashi_idx]
        elem_info = ELEMENT_INFO[elem_key]
        ex, ey = _polar_to_xy(center_angle, R_ELEMENT_MARKER)
        element_marker = {
            "key": elem_key,
            "name_th": elem_info["name_th"],
            "icon": elem_info["icon"],
            "symbol": elem_info["symbol"],
            "color": elem_info["color"],
            "x": ex, "y": ey,
        }

        # natal chips
        if position_by_degree:
            # วางตามตรียางค์ที่ดาวกำเนิดตก (สุริยยาตร์ — ดาวมีองศา)
            rashi_start_angle = 75 + 30 * r["index"]
            chip_xy = _chip_layout_by_decanate(r["planets"], rashi_start_angle)
        else:
            # วางกระจายในเซกเตอร์ราศี (โหรทายหนู — ดาวไม่มีองศา)
            chip_xy = _chip_layout(len(r["planets"]), center_angle)
        chip_data = []
        for (x, y), planet in zip(chip_xy, r["planets"]):
            chip_data.append({**planet, "x": x, "y": y})

        # transit chips (วงนอก) — วางตามองศา/ตรียางค์ของดาวจรในราศีนั้น
        transit_chips = []
        if has_transit:
            tlist = transits_by_rasi.get(r["index"], [])
            rashi_start_angle = 75 + 30 * r["index"]
            txys = _chip_layout_by_decanate(
                tlist, rashi_start_angle, base_radius=R_TRANSIT
            )
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
            "triyangka_markers": triyangka_markers,
            "element_marker": element_marker,
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
        "r_triyangka_inner": R_TRIYANGKA_RING_INNER,
        "r_triyangka_outer": R_TRIYANGKA_RING_OUTER,
        "has_transit": has_transit,
        "dividers": dividers,
        "triyangka_dividers": triyangka_dividers,
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
            _ti = get_triyangka_info(p.zodiac.rasi, p.zodiac.degree, p.zodiac.arcminute)
            planets_here.append({
                **info,
                "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
                "degree": p.zodiac.degree,
                "arcminute": p.zodiac.arcminute,
                "arcsecond": p.zodiac.arcsecond,
                "retrograde": p.retrograde,
                "source": "กำเนิด",
                "is_poison": _ti.is_poison,
                "poison_type": _ti.poison_type,
                "poison_icon": _ti.poison_icon,
                "poison_severity": _ti.poison_severity,
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
            _tti = get_triyangka_info(p.zodiac.rasi, p.zodiac.degree, p.zodiac.arcminute)
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
                "is_poison": _tti.is_poison,
                "poison_type": _tti.poison_type,
                "poison_icon": _tti.poison_icon,
                "poison_severity": _tti.poison_severity,
            }
            transits_by_rasi[p.zodiac.rasi].append(transit_planet)
            transit_positions.append({
                "name": name,
                "abbr": info["abbr_arabic"],
                "color_class": info["color_class"],
                "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
                "degree": p.zodiac.degree,
                "arcminute": p.zodiac.arcminute,
                "arcsecond": p.zodiac.arcsecond,
                "retrograde": p.retrograde,
                # triyangka data (สำหรับตาราง)
                "triyangka_decanate": _tti.decanate + 1,
                "triyangka_name": _tti.decanate_name_th,
                "triyangka_lord": _tti.lord_planet,
                "is_poison": _tti.is_poison,
                "poison_type": _tti.poison_type,
                "poison_name_th": _tti.poison_name_th,
                "poison_icon": _tti.poison_icon,
                "poison_severity": _tti.poison_severity,
                "element": _tti.element,
                "element_name_th": _tti.element_name_th,
                "element_icon": _tti.element_icon,
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
        # ---- triyangka ของดาวกำเนิด ----
        tinfo = get_triyangka_info(p.zodiac.rasi, p.zodiac.degree, p.zodiac.arcminute)
        planet_positions.append({
            "name": name,
            "abbr": info["abbr"],
            "color_class": info["color_class"],
            "rasi_name": RASI_NAMES_TH[p.zodiac.rasi],
            "degree": p.zodiac.degree,
            "arcminute": p.zodiac.arcminute,
            "arcsecond": p.zodiac.arcsecond,
            "house": house,
            "bhava": BHAVA_NAMES[house - 1],
            "retrograde": p.retrograde,
            # triyangka data
            "triyangka_decanate": tinfo.decanate + 1,        # 1/2/3 สำหรับแสดง
            "triyangka_name": tinfo.decanate_name_th,
            "triyangka_lord": tinfo.lord_planet,
            "is_poison": tinfo.is_poison,
            "poison_type": tinfo.poison_type,
            "poison_name_th": tinfo.poison_name_th,
            "poison_icon": tinfo.poison_icon,
            "poison_severity": tinfo.poison_severity,
            "element": tinfo.element,
            "element_name_th": tinfo.element_name_th,
            "element_icon": tinfo.element_icon,
        })

    # คำทำนายเจ้าเรือนครองภพ (Bhava Lord)
    natal_lord_preds = predict_natal_lords(chart.ascendant.zodiac.rasi, chart.planets)
    natal_lord_summary = generate_bhava_lord_summary(natal_lord_preds)
    # ไฮไลต์ 5 ภพสำคัญสำหรับโหมดดูดวง
    natal_lord_summary["highlights_top5"] = _pick_lord_highlights(natal_lord_preds)
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

    # ทักษา (Taksa) — ดาวประจำวันเกิด + 8 บริวาร + ดาวเสวยอายุ
    taksa = compute_taksa(
        chart.ce_year, chart.month, chart.day, chart.hour, chart.minute,
    )
    taksa_transit_aspects = transit_aspects_on_taksa(
        taksa,
        chart.planets,
        transit_chart.planets if transit_chart is not None else None,
    )
    # ทักษาจร (Transit Taksa) — เดิน 9 ช่องปีละ 1 ตา
    transit_taksa = compute_transit_taksa(taksa, taksa.year_of_life)

    # ปฏิทินจันทรคติ (Thai Lunar Calendar)
    lunar = compute_lunar_date(chart.desire, chart.planets["อาทิตย์"].zodiac.rasi)

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
        "birth_month_num": chart.month,
        "birth_day_num": chart.day,
        "birth_hour": chart.hour,
        "birth_minute": chart.minute,
        "ascendant": ((lambda _asc: {
            "rasi_name": _asc.zodiac.rasi_name,
            "degree": _asc.zodiac.degree,
            "arcminute": _asc.zodiac.arcminute,
            "arcsecond": _asc.zodiac.arcsecond,
            # ตรียางค์ของลัคนา
            **((lambda _ti: {
                "triyangka_decanate": _ti.decanate + 1,
                "triyangka_name": _ti.decanate_name_th,
                "triyangka_lord": _ti.lord_planet,
                "is_poison": _ti.is_poison,
                "poison_type": _ti.poison_type,
                "poison_name_th": _ti.poison_name_th,
                "poison_icon": _ti.poison_icon,
                "poison_severity": _ti.poison_severity,
                "element": _ti.element,
                "element_name_th": _ti.element_name_th,
                "element_icon": _ti.element_icon,
            })(get_triyangka_info(_asc.zodiac.rasi, _asc.zodiac.degree, _asc.zodiac.arcminute))),
        })(chart.ascendant)),
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
        "orbit": build_orbit_layout(
            natal_planets=[
                {
                    "name": name,
                    "abbr": PLANET_INFO_MAP[name]["abbr"],
                    "color_class": PLANET_INFO_MAP[name]["color_class"],
                    "rasi": chart.planets[name].zodiac.rasi,
                    "rasi_name": RASI_NAMES_TH[chart.planets[name].zodiac.rasi],
                    "degree": chart.planets[name].zodiac.degree,
                    "arcminute": chart.planets[name].zodiac.arcminute,
                    "arcsecond": chart.planets[name].zodiac.arcsecond,
                    "retrograde": chart.planets[name].retrograde,
                }
                for name in PLANET_ORDER if name in chart.planets
            ],
            transit_planets=(
                [
                    {
                        "name": name,
                        "abbr": PLANET_INFO_MAP[name]["abbr_arabic"],
                        "color_class": PLANET_INFO_MAP[name]["color_class"],
                        "rasi": transit_chart.planets[name].zodiac.rasi,
                        "rasi_name": RASI_NAMES_TH[transit_chart.planets[name].zodiac.rasi],
                        "degree": transit_chart.planets[name].zodiac.degree,
                        "arcminute": transit_chart.planets[name].zodiac.arcminute,
                        "arcsecond": transit_chart.planets[name].zodiac.arcsecond,
                        "retrograde": transit_chart.planets[name].retrograde,
                    }
                    for name in PLANET_ORDER if name in transit_chart.planets
                ] if transit_chart is not None else None
            ),
            ascendant={
                "rasi": chart.ascendant.zodiac.rasi,
                "degree": chart.ascendant.zodiac.degree,
                "arcminute": chart.ascendant.zodiac.arcminute,
            },
        ),
        "planets": planet_positions,
        # planets grouped by bhava (house 1-12) สำหรับแสดงในตารางความหมายภพ
        "planets_by_bhava": {
            h: [
                {"name": p["name"], "abbr": p["abbr"], "color_class": p["color_class"]}
                for p in planet_positions if p["house"] == h
            ]
            for h in range(1, 13)
        },
        "transit": ({
            "date_th": transit_meta.get("date_th") if transit_meta else None,
            "time": transit_meta.get("time") if transit_meta else None,
            "time_24": transit_meta.get("time_24") if transit_meta else None,
            "date_iso": transit_meta.get("date_iso") if transit_meta else None,
            "province": transit_meta.get("province") if transit_meta else None,
            "planets": transit_positions,
            "aspects": transit_aspects,
            "summary": transit_summary,
            "bhava_lords": transit_lord_data["summary"] if transit_lord_data else None,
        } if transit_chart is not None else None),
        "natal_bhava_lords": natal_lord_summary,
        "oracle": oracle_reading,
        "taksa": _taksa_to_view(taksa, taksa_transit_aspects, transit_taksa),
        "birth_weekday_name": taksa.birth_weekday_name,
        "lunar": {
            "phase_name": lunar.phase_name,
            "day_in_phase": lunar.day_in_phase,
            "lunar_month": lunar.lunar_month,
            "lunar_month_name": lunar.lunar_month_name,
            "zodiac_year_name": lunar.zodiac_year_name,
            "zodiac_animal_en": lunar.zodiac_animal_en,
            "is_leap_month_year": lunar.is_leap_month_year,
            "cs_year": lunar.cs_year,
            "pretty": lunar.pretty,
            "pretty_short": lunar.pretty_short,
        },
        "info": {
            "cs_year": sr.thaloengsok_cs_year,
            "thaloengsok": f"{sr.thaloengsok.day} {THAI_MONTHS[sr.thaloengsok.month]} {sr.thaloengsok.be_year}",
            "surathin": sr.total_days,
            "horakhun": d.horakhun,
            "horakhun_at_midnight": d.horakhun_at_midnight,
            "julian": d.julian_date,
            "thai_minor_era": d.thai_minor_era,
            "kammatchaphon": d.kammatchaphon,
            "ujapon": d.ujapon,
            "mas": d.mas,
            "awaman": d.awaman,
            "dithi": d.dithi,
            "ujapon_remainder": d.ujapon_remainder,
        },
    }


THAI_TZ = timezone(timedelta(hours=7))


# ============================================================
# Taksa 3x3 grid layout (ทิศ → ตำแหน่งใน grid)
# Layout:
#   พายัพ(NW) | อุดร(N)   | อีสาน(NE)
#   ประจิม(W) | [center]  | บูรพา(E)
#   หรดี(SW)  | ทักษิณ(S) | อาคเนย์(SE)
# ============================================================
TAKSA_GRID_POSITIONS = {
    "พายัพ":  (0, 0),
    "อุดร":   (0, 1),
    "อีสาน":  (0, 2),
    "ประจิม": (1, 0),
    "บูรพา":  (1, 2),
    "หรดี":   (2, 0),
    "ทักษิณ": (2, 1),
    "อาคเนย์": (2, 2),
}


def _taksa_to_view(taksa, transit_aspects, transit_taksa=None):
    """แปลง Taksa เป็น dict สำหรับ template (มี 3x3 grid + ทักษาจร)"""
    # Build map: direction → transit cell info
    transit_by_direction = {}
    if transit_taksa is not None:
        for c in transit_taksa.cells:
            key = "กลาง" if c.is_center else c.direction
            transit_by_direction[key] = {
                "years_visited": c.years_visited,
                "cycle_position": c.cycle_first_position,
                "is_current": c.is_current,
            }

    grid = [[None for _ in range(3)] for _ in range(3)]
    for b in taksa.bhavas:
        r, c = TAKSA_GRID_POSITIONS[b.direction]
        info = PLANET_INFO_MAP.get(b.planet, {})
        t_info = transit_by_direction.get(b.direction, {})
        grid[r][c] = {
            "position": b.position, "name": b.name, "theme": b.theme,
            "tone": b.tone, "planet": b.planet,
            "direction": b.direction, "direction_en": b.direction_en,
            "age_range": f"{b.age_range[0]}-{b.age_range[1]}",
            "prediction": b.prediction,
            "is_current_dasa": b.is_current_dasa,
            "abbr": info.get("abbr", ""),
            "color_class": info.get("color_class", ""),
            "transit_years": t_info.get("years_visited", []),
            "transit_cycle_pos": t_info.get("cycle_position", 0),
            "transit_is_current": t_info.get("is_current", False),
        }

    return {
        "birth_weekday_name": taksa.birth_weekday_name,
        "birth_planet": taksa.birth_planet,
        "birth_planet_note": taksa.birth_planet_note,
        "age_completed_years": taksa.age_completed_years,
        "year_of_life": taksa.year_of_life,
        "current_dasa_planet": taksa.current_dasa_planet,
        "current_dasa_bhava_name": taksa.current_dasa_bhava.name,
        "current_dasa_prediction": taksa.current_dasa_bhava.prediction,
        "age_in_current_dasa": taksa.age_in_current_dasa,
        "next_dasa_age": taksa.next_dasa_age,
        "next_dasa_planet": taksa.next_dasa_planet,
        "summary": taksa.overall_summary,
        "grid": grid,
        "center_transit": transit_by_direction.get("กลาง", {}),
        "bhavas": [
            {
                "position": b.position, "name": b.name, "theme": b.theme,
                "tone": b.tone, "planet": b.planet,
                "direction": b.direction, "direction_en": b.direction_en,
                "age_range": f"{b.age_range[0]}-{b.age_range[1]}",
                "prediction": b.prediction,
                "is_current_dasa": b.is_current_dasa,
                "abbr": PLANET_INFO_MAP.get(b.planet, {}).get("abbr", ""),
                "color_class": PLANET_INFO_MAP.get(b.planet, {}).get("color_class", ""),
            }
            for b in taksa.bhavas
        ],
        "transit_aspects": [
            {
                **a,
                "transit_abbr": PLANET_INFO_MAP.get(a["transit_planet"], {}).get("abbr_arabic", ""),
                "transit_color": PLANET_INFO_MAP.get(a["transit_planet"], {}).get("color_class", ""),
                "natal_abbr": PLANET_INFO_MAP.get(a["natal_planet"], {}).get("abbr", ""),
                "natal_color": PLANET_INFO_MAP.get(a["natal_planet"], {}).get("color_class", ""),
            }
            for a in (transit_aspects or [])
        ],
        "transit_taksa": (
            {
                "current_planet": transit_taksa.current_planet,
                "current_cycle_position": transit_taksa.current_cycle_position,
                "is_on_center": transit_taksa.is_on_center,
                "natal_bhava_at_current": transit_taksa.natal_bhava_at_current,
                "natal_bhava_tone": transit_taksa.natal_bhava_tone,
                "summary": transit_taksa.summary,
                "overlay_note": transit_taksa.overlay_note,
                "overlay_chart": [
                    {
                        "position": b.position, "name": b.name, "theme": b.theme,
                        "tone": b.tone, "planet": b.planet,
                        "direction": b.direction, "direction_en": b.direction_en,
                        "prediction": b.prediction,
                        "abbr": PLANET_INFO_MAP.get(b.planet, {}).get("abbr", ""),
                        "color_class": PLANET_INFO_MAP.get(b.planet, {}).get("color_class", ""),
                    }
                    for b in (transit_taksa.overlay_chart or [])
                ] if transit_taksa.overlay_chart else None,
                "overlay_combos": [
                    {
                        **c,
                        "abbr": PLANET_INFO_MAP.get(c["planet"], {}).get("abbr", ""),
                        "color_class": PLANET_INFO_MAP.get(c["planet"], {}).get("color_class", ""),
                    }
                    for c in (transit_taksa.overlay_combos or [])
                ] if transit_taksa.overlay_combos else None,
            }
            if transit_taksa is not None else None
        ),
    }


def _pick_lord_highlights(predictions) -> list:
    """เลือก 5 ภพสำคัญสำหรับโหมดดูดวง:
       ภพ 2 (การเงิน), 7 (คู่ครอง), 10 (การงาน), 11 (ลาภ) + 1 warn
       ถ้าไม่มี warn → เลือกภพ 4 (ครอบครัว) แทน
    """
    by_bhava = {p.lord_bhava: p for p in predictions}
    important = [2, 7, 10, 11]
    out = []
    for b in important:
        if b in by_bhava:
            p = by_bhava[b]
            out.append({
                "lord_bhava": p.lord_bhava,
                "lord_bhava_name": p.lord_bhava_name,
                "lord_planet": p.lord_planet,
                "lord_rasi": p.lord_rasi,
                "located_bhava": p.located_bhava,
                "located_bhava_name": p.located_bhava_name,
                "prediction": p.prediction,
                "tone": p.tone,
                "tone_label": p.tone_label,
            })
    # หา 1 warn ที่ไม่ซ้ำ
    warn = next(
        (p for p in predictions
         if p.tone == "warning" and p.lord_bhava not in important),
        None,
    )
    if warn:
        out.append({
            "lord_bhava": warn.lord_bhava,
            "lord_bhava_name": warn.lord_bhava_name,
            "lord_planet": warn.lord_planet,
            "lord_rasi": warn.lord_rasi,
            "located_bhava": warn.located_bhava,
            "located_bhava_name": warn.located_bhava_name,
            "prediction": warn.prediction,
            "tone": warn.tone,
            "tone_label": warn.tone_label,
        })
    elif 4 in by_bhava and not any(o["lord_bhava"] == 4 for o in out):
        p = by_bhava[4]
        out.append({
            "lord_bhava": p.lord_bhava,
            "lord_bhava_name": p.lord_bhava_name,
            "lord_planet": p.lord_planet,
            "lord_rasi": p.lord_rasi,
            "located_bhava": p.located_bhava,
            "located_bhava_name": p.located_bhava_name,
            "prediction": p.prediction,
            "tone": p.tone,
            "tone_label": p.tone_label,
        })
    return out


def _default_form() -> dict:
    """ค่าเริ่มต้นของฟอร์ม"""
    return {
        "name": "",
        "birth_date_th": "",
        "birth_time": "",
        "province": "กรุงเทพมหานคร",
    }


def _latest_version() -> str:
    """อ่าน version ล่าสุดจาก changelog (สำหรับ badge ใน nav)"""
    try:
        from webapp.changelog import CHANGELOG
        return CHANGELOG[0]["version"] if CHANGELOG else ""
    except Exception:
        return ""


def _common_context(request: Request, **extra) -> dict:
    base = {
        "request": request,
        "provinces": PROVINCES,
        "bhava_meanings": BHAVA_MEANINGS,
        "latest_version": _latest_version(),
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
            form=_default_form(),
            error=None,
            scroll_target="",
        ),
    )


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request) -> HTMLResponse:
    """หน้าเกี่ยวกับ + version history"""
    from webapp.changelog import CHANGELOG
    return templates.TemplateResponse(
        request,
        "about.html",
        {"request": request, "changelog": CHANGELOG, "latest_version": _latest_version()},
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
    transit_date_iso: str = Form(""),   # YYYY-MM-DD; ว่าง = ใช้ now
    transit_time_24: str = Form(""),    # HH:MM;       ว่าง = ใช้ now
    scroll_to_transit: str = Form(""),  # "1" → scroll ไปที่ scrubber หลัง load
) -> HTMLResponse:
    form = {
        "name": name,
        "birth_date_th": birth_date_th,
        "birth_time": birth_time,
        "province": province,
    }
    error: Optional[str] = None
    result = None
    scroll_target = scroll_to_transit.strip()

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

        # ดาวจร — ใช้ override ถ้ามี ไม่งั้นเป็น now()
        if transit_date_iso.strip() and transit_time_24.strip():
            try:
                ty, tm_t, tday = [int(x) for x in transit_date_iso.split("-")]
                th_h, tmin = [int(x) for x in transit_time_24.split(":")]
            except (ValueError, IndexError):
                raise ValueError("รูปแบบวันที่/เวลาดาวจรไม่ถูกต้อง")
        else:
            now = datetime.now(THAI_TZ)
            ty, tm_t, tday = now.year, now.month, now.day
            th_h, tmin = now.hour, now.minute

        transit_chart = Chart.calculate(
            ty, tm_t, tday, th_h, tmin,
            province="กรุงเทพมหานคร",
        )
        transit_meta = {
            "date_th": _format_thai_date_ce(ty, tm_t, tday),
            "time": f"{th_h:02d}:{tmin:02d}",
            "time_24": f"{th_h:02d}:{tmin:02d}",
            "date_iso": f"{ty:04d}-{tm_t:02d}-{tday:02d}",
            "province": "กรุงเทพมหานคร",
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
            scroll_target=scroll_target,
        ),
    )


# ============================================================
# โหรทายหนู (ดวงยามอัฐุกาล — ฉบับ อ.กานดา)
# ============================================================

HORATHAYNU_WEEKDAYS = ["อาทิตย์", "จันทร์", "อังคาร", "พุธ",
                      "พฤหัสบดี", "ศุกร์", "เสาร์"]

HORATHAYNU_RASHI_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
                       "ตุล", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]

HORATHAYNU_ORDER_LABEL = [
    "ดาว ๑", "ดาว ๒", "ดาว ๓", "ดาว ๔", "ดาว ๕",
    "ดาว ๖", "ดาว ๗", "ดาว ๘", "ลัคนา", "ดาว ๙", "ดาว ๐",
]

# เลขดาวเกษตรประจำราศี (เมษ → มีน, เวียนซ้าย)
# 1=อาทิตย์ 2=จันทร์ 3=อังคาร 4=พุธ 5=พฤหัส 6=ศุกร์ 7=เสาร์ 8=ราหู
# หมายเหตุ: กุมภ์ใช้ราหู (=8) ไม่ใช่เสาร์ ตามตำราโหรทายหนู
HORATHAYNU_LORD_NUMBERS = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 8, 5]

# รัศมีของเลขเกษตรในผัง — อยู่ระหว่างวงในกับ chip ดาว
R_HORATHAYNU_LORD = 138

# วงนอกเวลายาม — แสดง 12 cell ละ 7.5 นาที (เริ่มที่ภพของเจ้าเรือนลัคนา)
R_HORATHAYNU_TIME_INNER = 268   # ขอบในของวงเวลา
R_HORATHAYNU_TIME_OUTER = 308   # ขอบนอก
R_HORATHAYNU_TIME_LABEL = 288   # รัศมีของ text เวลา


def _horathaynu_default_form() -> dict:
    """ค่าเริ่มต้น — วันนี้/เวลานี้"""
    now = datetime.now(THAI_TZ)
    return {
        "date_th": f"{now.day:02d}/{now.month:02d}/{now.year + 543}",
        "time": f"{now.hour:02d}:{now.minute:02d}",
    }


def _horathaynu_prophesy(question: str, chart) -> dict:
    """พยากรณ์ผ่าน prophecy module → คืน dict สำหรับ JSON response"""
    r = horathaynu_prophecy(chart, question)
    return {
        "significator": r.significator_th,
        "category": r.category,
        "rashi": r.sig_rashi_name,
        "bhava": r.sig_bhava,
        "house": r.sig_house,
        "tone": r.tone,
        "is_own_sign": r.is_own_sign,
        "co_planets": [HORATHAYNU_PLANET_NAME_TH[k] for k in r.co_planets],
        "sign_lord": r.sign_lord_th,
        "text": r.text,
    }


def _horathaynu_chart_view(chart, asked_time: Optional[str] = None,
                           date_th: str = "", question: str = "") -> dict:
    """แปลง horathaynu Chart → dict สำหรับ template"""
    placements = []
    for i, key in enumerate(HORATHAYNU_PLACEMENT_ORDER):
        p = chart.placements[key]
        info = PLANET_INFO_MAP.get(HORATHAYNU_PLANET_NAME_TH.get(key, ""))
        placements.append({
            "order": HORATHAYNU_ORDER_LABEL[i],
            "key": key,
            "name_th": HORATHAYNU_PLANET_NAME_TH.get(key, key),
            "count": chart.counts[i],
            "rashi": HORATHAYNU_RASHI_TH[p.sign],
            "rashi_index": p.sign,
            "house": p.house,
            "bhava": HORATHAYNU_BHAVA_NAMES[p.house - 1],
            "abbr": info["abbr"] if info else "?",
            "color_class": info["color_class"] if info else "",
        })

    # group ดาวตามราศี (สำหรับวงกลม)
    by_sign: dict[int, list[dict]] = {i: [] for i in range(12)}
    for pl in placements:
        if pl["key"] == "lagna":
            continue  # ลัคนาแสดงเป็น marker แยก
        by_sign[pl["rashi_index"]].append(pl)

    # สร้าง rasis layout
    asc = chart.ascendant_sign
    rasis = []
    for rasi_idx in range(12):
        house_num = ((rasi_idx - asc) % 12) + 1
        rasis.append({
            "index": rasi_idx,
            "name": HORATHAYNU_RASHI_TH[rasi_idx],
            "house": house_num,
            "bhava": HORATHAYNU_BHAVA_NAMES[house_num - 1],
            "planets": by_sign[rasi_idx],
            "is_ascendant": rasi_idx == asc,
        })

    circle = build_circular_layout(
        rasis,
        transits_by_rasi=None,
        ascendant={"rasi": asc, "degree": 15, "arcminute": 0},
        position_by_degree=False,   # โหรทายหนูไม่ track องศา → กระจายในเซกเตอร์
    )

    # เพิ่มเลขดาวเกษตรในแต่ละช่องราศี (เฉพาะ horathaynu)
    for r in circle["rasis"]:
        lord_num = HORATHAYNU_LORD_NUMBERS[r["index"]]
        lord_x, lord_y = _polar_to_xy(r["center_angle"], R_HORATHAYNU_LORD)
        r["lord_number"] = lord_num
        r["lord_x"] = lord_x
        r["lord_y"] = lord_y

    # เจ้าเรือนลัคนา + จุดลงเวลา
    lagna_lord_key = horathaynu_lord_of(asc)
    lagna_lord_th = HORATHAYNU_PLANET_NAME_TH.get(lagna_lord_key, lagna_lord_key)
    lord_house = chart.placements[lagna_lord_key].house
    lord_bhava = HORATHAYNU_BHAVA_NAMES[lord_house - 1]

    # วงนอกเวลายาม — 12 cell ตามภพ เริ่มที่ภพของเจ้าเรือนลัคนา
    # ตัวอย่างหน้า 8: ลัคนาพฤษภ → เจ้าเรือน=ศุกร์ → ศุกร์อยู่ภพ 6 (อริ=ตุล)
    #                ยาม 4 (10:30-12:00) → cell แรก 10:30-10:37.30 ที่ตุล
    yam_start_t, _yam_end_t = horathaynu_yam_range(chart.yam_index)
    start_minutes = yam_start_t.hour * 60 + yam_start_t.minute
    # ราศีของ start_bhava (เจ้าเรือนลัคนาอยู่ที่ภพ lord_house)
    start_sign = (asc + lord_house - 1) % 12

    def _fmt_time(total_min: float) -> str:
        h = int(total_min // 60) % 24
        m_float = total_min % 60
        m_int = int(m_float)
        sec = int(round((m_float - m_int) * 60))
        if sec == 0:
            return f"{h:02d}:{m_int:02d}"
        return f"{h:02d}:{m_int:02d}:{sec:02d}"

    time_by_sign = {}
    for cell_idx in range(12):
        cell_sign = (start_sign + cell_idx) % 12
        cell_start_min = start_minutes + cell_idx * 7.5
        time_by_sign[cell_sign] = {
            "start": _fmt_time(cell_start_min),
            "end": _fmt_time(cell_start_min + 7.5),
            "cell_idx": cell_idx,
        }

    for r in circle["rasis"]:
        t = time_by_sign.get(r["index"])
        if t:
            tx, ty = _polar_to_xy(r["center_angle"], R_HORATHAYNU_TIME_LABEL)
            r["time_label"] = t["start"]
            r["time_end"] = t["end"]
            r["time_cell_idx"] = t["cell_idx"]
            r["time_x"] = tx
            r["time_y"] = ty

    # ขยายเส้นแบ่ง 12 เส้นออกถึงวงเวลา + เพิ่มข้อมูลวงนอก
    new_dividers = []
    for i in range(12):
        angle = 75 + 30 * i
        x1, y1 = _polar_to_xy(angle, R_INNER)
        x2, y2 = _polar_to_xy(angle, R_HORATHAYNU_TIME_OUTER)
        new_dividers.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
    circle["dividers"] = new_dividers
    circle["r_time_inner"] = R_HORATHAYNU_TIME_INNER
    circle["r_time_outer"] = R_HORATHAYNU_TIME_OUTER
    # เพิ่ม size ของ SVG ให้พอกับวงเวลา
    circle["size"] = 660  # SVG_SIZE
    circle["pad"] = 25     # ระยะขอบในวง

    time_precision = None
    if asked_time:
        from datetime import time as time_cls
        h, m = [int(x) for x in asked_time.split(":")]
        bhava_at_time, cell_offset = horathaynu_time_cell(
            time_cls(h, m), chart.yam_index, lord_house
        )
        time_precision = {
            "asked_time": asked_time,
            "bhava_at_time": bhava_at_time,
            "bhava_at_time_name": HORATHAYNU_BHAVA_NAMES[bhava_at_time - 1],
            "cell_offset": cell_offset,
        }

    yam_start, yam_end = horathaynu_yam_range(chart.yam_index)
    yam_local = chart.yam_index if chart.yam_index <= 8 else chart.yam_index - 8
    yam_half = "กลางวัน" if chart.yam_index <= 8 else "กลางคืน"

    return {
        "date_th": date_th,
        "time": asked_time,
        "question": question,
        "day_name": HORATHAYNU_WEEKDAYS[chart.day],
        "yam_index_global": chart.yam_index,
        "yam_index_local": yam_local,
        "yam_half": yam_half,
        "yam_range": f"{yam_start.strftime('%H:%M')}-{yam_end.strftime('%H:%M')}",
        "counts": list(chart.counts),
        "ascendant_rashi": HORATHAYNU_RASHI_TH[asc],
        "lagna_lord_name": lagna_lord_th,
        "lord_house": lord_house,
        "lord_bhava": lord_bhava,
        "placements": placements,
        "rasis": rasis,
        "circle": circle,
        "time_precision": time_precision,
    }


@app.get("/horathaynu", response_class=HTMLResponse)
async def horathaynu_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "horathaynu.html",
        {
            "request": request,
            "form": _horathaynu_default_form(),
            "result": None,
            "error": None,
            "latest_version": _latest_version(),
        },
    )


def _compute_horathaynu_chart(date_th: str, time_str: str) -> dict:
    """รับ date_th + time_str → คำนวณ chart_view"""
    if not date_th.strip():
        raise ValueError("กรุณากรอกวันที่ (พ.ศ.)")
    if not time_str.strip():
        raise ValueError("กรุณากรอกเวลา")
    y, m, d = parse_thai_date(date_th)
    h, mi = [int(x) for x in time_str.split(":")]
    dt = datetime(y, m, d, h, mi)
    from thai_astro.horathaynu.core.time_to_yam import datetime_to_day_yam
    day, yam_index = datetime_to_day_yam(dt)
    chart = horathaynu_cast(day, yam_index)
    return _horathaynu_chart_view(chart, asked_time=time_str, date_th=date_th)


@app.post("/horathaynu", response_class=HTMLResponse)
async def horathaynu_calculate(
    request: Request,
    date_th: str = Form(""),
    time: str = Form(""),
) -> HTMLResponse:
    """ตั้งดวงยาม (ใหม่ — รีเซ็ต history)"""
    form = {"date_th": date_th, "time": time}
    error: Optional[str] = None
    result = None
    try:
        result = _compute_horathaynu_chart(date_th, time)
    except (ValueError, IndexError) as e:
        error = f"กรอกข้อมูลไม่ถูกต้อง: {e}"

    return templates.TemplateResponse(
        request,
        "horathaynu.html",
        {"request": request, "form": form, "result": result, "error": error,
         "latest_version": _latest_version()},
    )


def _count_thai_chars(s: str) -> int:
    """นับเฉพาะตัวอักษรไทย (consonant + vowel) — ตัด space/punct/ASCII/digits"""
    return sum(
        1 for c in s
        if ("ก" <= c <= "ฮ")    # consonant ก-ฮ
        or ("ะ" <= c <= "ฺ")    # vowel ะ-ฺ
        or ("เ" <= c <= "๎")    # vowel เ-๎
    )


# Thai vowel/tone characters (ไม่ใช่พยัญชนะ)
_THAI_VOWELS_TONES = set("ะาำิีึืุูเแโใไๅัๆ์ฺ่้๊๋๎")


def _looks_like_gibberish(s: str) -> bool:
    """Heuristic ตรวจ "ฟ้อนคีย์มั่ว" (พิมพ์ตัวอักษรซ้ำหรือไม่เป็นคำ)

    เกณฑ์:
    1. มีอักษรซ้ำติดกัน ≥ 4 ตัว (เช่น "าาาาา") → gibberish
    2. สัดส่วนสระ/วรรณยุกต์ > พยัญชนะ + 2 → gibberish (ภาษาไทยจริงพยัญชนะมากกว่า)
    3. ใช้พยัญชนะไม่ซ้ำกัน ≤ 2 ตัวในข้อความยาว ≥ 8 → gibberish
    """
    if len(s) < 4:
        return False

    # (1) อักษรซ้ำติดกัน 4+
    for i in range(len(s) - 3):
        if s[i] == s[i + 1] == s[i + 2] == s[i + 3]:
            return True

    # (2) สระเยอะกว่าพยัญชนะ + 2
    consonants = sum(1 for c in s if "ก" <= c <= "ฮ")
    vowels_tones = sum(1 for c in s if c in _THAI_VOWELS_TONES)
    if vowels_tones > consonants + 2:
        return True

    # (3) พยัญชนะที่ใช้มีน้อยกว่า 3 ชนิด ในข้อความยาว ≥ 8 อักษรไทย
    thai_total = consonants + vowels_tones
    if thai_total >= 8:
        unique_consonants = len(
            {c for c in s if "ก" <= c <= "ฮ"}
        )
        if unique_consonants <= 2:
            return True

    # (4) ข้อความยาว ≥ 8 อักษรไทย แต่ไม่มีสระเลย → พิมพ์มั่ว
    if thai_total >= 8 and vowels_tones == 0:
        return True

    # (5) Pattern ซ้ำ — เช่น "ทดสอบทดสอบทดสอบ" หรือ "กขกขกข"
    # หา pattern ความยาว 2-8 ที่ซ้ำต่อกัน ≥ 3 ครั้งและกินพื้นที่ ≥ 60% ของข้อความ
    n = len(s)
    if n >= 9:
        for plen in range(2, 9):
            if plen * 3 > n:
                break
            pattern = s[:plen]
            repeat_count = 1
            for i in range(plen, n - plen + 1, plen):
                if s[i:i + plen] == pattern:
                    repeat_count += 1
                else:
                    break
            if repeat_count >= 3 and repeat_count * plen >= n * 0.6:
                return True

    return False


# จำกัดความยาวคำถาม — ป้องกันการพิมพ์ยาวเกินจำเป็น
MAX_QUESTION_LENGTH = 200


def _validate_horathaynu_question(q: str, matched_count: int) -> str | None:
    """ตรวจคำถาม gibberish หรือเปล่า.

    คืน None ถ้าผ่าน, คืน error message ถ้าไม่ผ่าน
    """
    # ตรวจ gibberish ก่อน — ต่อให้ Thai >= 5 ถ้ารูปแบบมั่ว ก็ปฏิเสธ
    if _looks_like_gibberish(q):
        return (
            "🤔 ดูเหมือนคำถามจะพิมพ์มั่วไปนิด ลองพิมพ์เป็นประโยคจริง "
            "หรือเลือกหัวข้อจากแนวคำถามข้างบนครับ"
        )

    # ถ้า match keyword อย่างน้อย 1 → ผ่านเสมอ (กัน reject คำสั้นๆ ที่ valid เช่น "งาน")
    if matched_count > 0:
        return None
    # ไม่ match แต่ภาษาไทย ≥ 5 ตัว → ผ่าน (general + banner)
    if _count_thai_chars(q) >= 5:
        return None
    return (
        "🤔 ไม่เข้าใจคำถามครับ ลองพิมพ์เป็นภาษาไทยให้ครบความ "
        "หรือเลือกหัวข้อจากแนวคำถามข้างบน"
    )


@app.post("/horathaynu/ask")
async def horathaynu_ask(
    date_th: str = Form(""),
    time: str = Form(""),
    question: str = Form(""),
) -> JSONResponse:
    """ถาม-ทำนาย → JSON (สำหรับ AJAX, ไม่ refresh หน้า)"""
    q = question.strip()
    if not q:
        return JSONResponse({"error": "กรุณาพิมพ์คำถาม"}, status_code=400)

    # length guard
    if len(q) > MAX_QUESTION_LENGTH:
        return JSONResponse(
            {"error": f"คำถามยาวเกินไป (สูงสุด {MAX_QUESTION_LENGTH} ตัวอักษร) "
                      f"— ลองพิมพ์ใหม่ให้สั้นและตรงประเด็น"},
            status_code=400,
        )

    # gibberish guard — ตรวจก่อนเข้าระบบทำนาย
    from thai_astro.horathaynu.data.question_mapping import classify_question as _cq
    _mapping, _matched = _cq(q)
    err = _validate_horathaynu_question(q, len(_matched))
    if err is not None:
        return JSONResponse({"error": err}, status_code=400)
    try:
        if not date_th.strip() or not time.strip():
            return JSONResponse(
                {"error": "กรุณาตั้งดวงก่อน (กรอกวันที่และเวลา)"},
                status_code=400,
            )
        y, m, d = parse_thai_date(date_th)
        h, mi = [int(x) for x in time.split(":")]
        dt = datetime(y, m, d, h, mi)
        from thai_astro.horathaynu.core.time_to_yam import datetime_to_day_yam
        day, yam_index = datetime_to_day_yam(dt)
        chart = horathaynu_cast(day, yam_index)
        prophecy = _horathaynu_prophesy(q, chart)
    except (ValueError, IndexError) as e:
        return JSONResponse({"error": f"กรอกข้อมูลไม่ถูกต้อง: {e}"}, status_code=400)

    now = datetime.now(THAI_TZ)
    # warning เมื่อคำถามตกใน general fallback (ไม่ match keyword)
    warning = None
    if prophecy.get("category") == "general":
        warning = (
            "ระบบไม่พบคำสำคัญในคำถาม จึงตีความเป็นภาพรวมจากลัคนา "
            "— เพื่อความแม่นยำ ลองเลือกหัวข้อด้านบน หรือใช้คำเฉพาะ "
            "เช่น \"การงาน\" \"ความรัก\" \"หวย\" \"ของหาย\" \"คดี\""
        )
    return JSONResponse({
        "question": q,
        "answer": prophecy["text"],
        "significator": prophecy["significator"],
        "category": prophecy.get("category"),
        "warning": warning,
        "rashi": prophecy["rashi"],
        "bhava": prophecy["bhava"],
        "house": prophecy["house"],
        "tone": prophecy["tone"],
        "co_planets": prophecy["co_planets"],
        "sign_lord": prophecy["sign_lord"],
        "is_own_sign": prophecy["is_own_sign"],
        "timestamp": now.strftime("%H:%M:%S"),
    })


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
