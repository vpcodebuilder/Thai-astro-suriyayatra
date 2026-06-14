"""Web app สำหรับผูกดวงโหราศาสตร์ไทย (FastAPI + Jinja2)

เริ่มต้น:
    uvicorn webapp.server:app --reload
    หรือ
    python -m webapp.server
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timedelta, timezone, date as _date
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
from thai_astro.astro_patterns import detect_astro_patterns
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


# ============================================================
# Startup: auto-migrate + seed (resilient — เผื่อ Procfile release ไม่ run)
# ============================================================
@app.on_event("startup")
async def _init_db_safely() -> None:
    """รัน alembic migration + seed ตอน startup แบบ best-effort
    ใช้กรณี Railway/Heroku ไม่ honor Procfile release หรือ SQLite ephemeral
    """
    try:
        from alembic.config import Config
        from alembic import command
        cfg = Config(str(BASE_DIR.parent / "alembic.ini"))
        command.upgrade(cfg, "head")
        print("[startup] alembic upgrade head: ok", flush=True)
    except Exception as e:
        print(f"[startup] alembic upgrade failed: {e}", flush=True)

    try:
        from webapp.seed import main as seed_main
        seed_main()
    except SystemExit:
        pass  # seed_main calls sys.exit on missing file path; safe to ignore
    except Exception as e:
        print(f"[startup] seed failed: {e}", flush=True)

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
    original_birth_intl: Optional[tuple] = None,  # (ce_y, m, d, h, mi) วันเกิดสากลจริง (ก่อน sunrise shift)
) -> dict:
    """แปลง Chart เป็น dict สำหรับ template

    หมายเหตุ: ผังดวงใช้ตำแหน่งราศี fix (เมษอยู่บนช่องที่ 2, ไล่ทวนเข็มจนถึงมีน)
    แต่ละช่องราศีจะคำนวณว่าเป็นภพอะไรตามลัคนา
    transit_chart: ถ้ามี จะแสดงดาวจรในวงนอก
    original_birth_intl: ถ้ามี = วันเกิดสากล (ก่อน sunrise shift) — ใช้แสดง 2 บรรทัด
        (สูติกาลตำราไทย: chart.day/month — vs สากล: original)
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

    # ตำแหน่งกำลังดาว + เกณฑ์โยค (คำนวณก่อนเพื่อส่งเข้า bhava lord predictor)
    dignities = compute_all_dignities(chart.planets)
    yogas = detect_yogas(chart.ascendant.zodiac.rasi, chart.planets, dignities)
    astro_report = detect_astro_patterns(chart, dignities)
    transit_dignities = (
        compute_all_dignities(transit_chart.planets) if transit_chart is not None else None
    )

    # คำทำนายเจ้าเรือนครองภพ (Bhava Lord) — ใส่ dignity context เข้าไปด้วย
    natal_lord_preds = predict_natal_lords(
        chart.ascendant.zodiac.rasi, chart.planets, dignities=dignities,
    )
    natal_lord_summary = generate_bhava_lord_summary(natal_lord_preds)
    # ไฮไลต์ 5 ภพสำคัญสำหรับโหมดดูดวง
    natal_lord_summary["highlights_top5"] = _pick_lord_highlights(natal_lord_preds)
    transit_lord_data = None
    if transit_chart is not None:
        transit_lord_preds = predict_transit_lords(
            chart.ascendant.zodiac.rasi, transit_chart.planets,
            dignities=transit_dignities,
        )
        transit_lord_data = {
            "summary": generate_bhava_lord_summary(transit_lord_preds),
        }

    # ทักษา (Taksa) — sync ตามวัน transit ถ้ามี (ไม่งั้นใช้ default = now)
    taksa_reference_date = None
    taksa_disabled = False
    taksa_disabled_reason = None
    if transit_chart is not None:
        taksa_reference_date = _date(
            transit_chart.ce_year, transit_chart.month, transit_chart.day,
        )
        birth_d = _date(chart.ce_year, chart.month, chart.day)
        if taksa_reference_date < birth_d:
            taksa_disabled = True
            taksa_disabled_reason = "วันที่ดาวจรอยู่ก่อนวันเกิด — ยังไม่เกิดในเวลานี้"

    taksa = compute_taksa(
        chart.ce_year, chart.month, chart.day, chart.hour, chart.minute,
        today=taksa_reference_date,
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
    transit_date_label = None
    if transit_meta:
        _dt = transit_meta.get("date_th") or ""
        _tt = transit_meta.get("time") or ""
        transit_date_label = (f"{_dt} เวลา {_tt} น." if _dt and _tt else (_dt or _tt or None))
    oracle_reading = compose_oracle_reading(
        person_name=person_name,
        transit_summary=transit_summary,
        natal_lord_summary=natal_lord_summary,
        transit_lord_summary=transit_lord_data["summary"] if transit_lord_data else None,
        yogas=yogas,
        dignities=dignities,
        astro_patterns_matched=astro_report.matched,
        seed=oracle_seed,
        transit_date_label=transit_date_label,
    )

    d = chart.desire
    sr = d.surathin

    # ===== วันเกิดสากล (ก่อน Thai sunrise shift) — แสดงเป็นบรรทัด "ตรงกับสากล" =====
    intl_view = None
    if original_birth_intl is not None:
        o_y, o_m, o_d, o_h, o_mi = original_birth_intl
        intl_be = o_y + 543
        intl_weekday_idx = _date(o_y, o_m, o_d).weekday()  # 0=Mon, 6=Sun
        intl_weekday_names_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
        intl_view = {
            "weekday_name": "วัน" + intl_weekday_names_th[intl_weekday_idx],
            "date_th": f"{o_d} {THAI_MONTHS[o_m]} พ.ศ. {intl_be}",
            "time": f"{o_h:02d}:{o_mi:02d}",
            "shifted": (o_y, o_m, o_d) != (chart.ce_year, chart.month, chart.day),
        }

    # ===== Taksa reference label (ทำนายตามวันที่ดาวจร / ตามปัจจุบัน) =====
    taksa_ref_label = None
    taksa_age_label = None
    if taksa_reference_date is not None:
        # มี transit chart
        # อายุ ณ วันนั้น
        birth_d2 = _date(chart.ce_year, chart.month, chart.day)
        delta_days = (taksa_reference_date - birth_d2).days
        if delta_days < 0:
            taksa_age_label = "ก่อนเกิด"
        else:
            years = taksa_reference_date.year - birth_d2.year
            months_diff = taksa_reference_date.month - birth_d2.month
            days_diff = taksa_reference_date.day - birth_d2.day
            if days_diff < 0:
                months_diff -= 1
            if months_diff < 0:
                years -= 1
                months_diff += 12
            taksa_age_label = f"อายุ {years} ปี {months_diff} เดือน"
        taksa_ref_label = (
            f"{taksa_reference_date.day} {THAI_MONTHS[taksa_reference_date.month]} "
            f"พ.ศ. {taksa_reference_date.year + 543}"
        )

    return {
        "person_name": person_name,
        "birth_date_th": f"{chart.day} {THAI_MONTHS[chart.month]} พ.ศ. {chart.be_year}",
        "birth_date_iso": f"{chart.ce_year:04d}-{chart.month:02d}-{chart.day:02d}",
        "birth_time": f"{chart.hour:02d}:{chart.minute:02d}",
        "birth_intl": intl_view,        # อาจเป็น None ถ้าไม่ส่ง original_birth_intl
        "taksa_ref_label": taksa_ref_label,    # "DD MMM พ.ศ. YYYY" หรือ None
        "taksa_age_label": taksa_age_label,    # "อายุ X ปี Y เดือน" หรือ "ก่อนเกิด"
        "taksa_disabled": taksa_disabled,
        "taksa_disabled_reason": taksa_disabled_reason,
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
            "day": transit_meta.get("day") if transit_meta else None,
            "month": transit_meta.get("month") if transit_meta else None,
            "be_year": transit_meta.get("be_year") if transit_meta else None,
            "province": transit_meta.get("province") if transit_meta else None,
            "planets": transit_positions,
            "aspects": transit_aspects,
            "summary": transit_summary,
            "bhava_lords": transit_lord_data["summary"] if transit_lord_data else None,
        } if transit_chart is not None else None),
        "natal_bhava_lords": natal_lord_summary,
        "oracle": oracle_reading,
        "astro_patterns": _astro_patterns_to_view(astro_report),
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


def _astro_patterns_to_view(report):
    """แปลง AstroPatternReport เป็น dict สำหรับ Jinja2 template"""
    def _pat(p):
        return {
            "code": p.code, "name": p.name, "category": p.category,
            "level": p.level, "matched": p.matched, "tone": p.tone,
            "description": p.description, "meaning": p.meaning,
            "advice": p.advice, "planets_involved": p.planets_involved,
        }
    # group matched ตาม category สำหรับ render
    matched = [_pat(p) for p in report.matched]
    near = [_pat(p) for p in report.near_misses]
    categories_order = [
        "รูปดวงไทย", "กลุ่มลัคนา", "เกณฑ์ลัคนา (ยศ-ทรัพย์)",
        "ปัญจมหาบุรุษ", "โยคสำคัญ", "จันทรโยค", "โยคเสีย",
    ]
    matched_by_cat = []
    for cat in categories_order:
        items = [p for p in matched if p["category"] == cat]
        if items:
            matched_by_cat.append({"category": cat, "patterns": items})
    return {
        "matched": matched,
        "matched_by_category": matched_by_cat,
        "near_misses": near,
        "matched_count": len(matched),
        "near_miss_count": len(near),
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
        "usage_counts": _stat_get_counts(),
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
            today_widget=_today_widget(),
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


# ============================================================
# เทียบปฏิทิน — จันทรคติ ⇄ สุริยคติ (Phase 1)
# ============================================================
from thai_astro.calendar_convert import (
    solar_to_lunar as _solar_to_lunar,
    lunar_to_solar as _lunar_to_solar,
)
from thai_astro.calendar import (
    ce_to_mahasakarat as _ce_to_ms,
    ce_to_ratanakosin as _ce_to_rs,
    convert_year_to_ce as _year_to_ce,
)
from webapp.calendar_data import (
    CALENDAR_EPOCHS, HOLY_DAYS, NATIONAL_HOLIDAYS,
    find_holy_day, find_national_holiday,
)
from webapp.usage import (
    increment as _stat_increment,
    get_counts as _stat_get_counts,
    FEATURE_SURIYAYATRA, FEATURE_HORATHAYNU_SET, FEATURE_HORATHAYNU_ASK,
    FEATURE_MUHURTA, FEATURE_MUHURTA_CHECK,
)


def _pair_to_dict(pair) -> dict:
    """แปลง SolarLunarPair → dict สำหรับ JSON response"""
    lun = pair.lunar
    holy = find_holy_day(
        lun.lunar_month, lun.waxing, lun.day_in_phase,
        is_leap_month_year=lun.is_leap_month_year,
        is_intercalary_month=lun.is_intercalary_month,
    )
    national = find_national_holiday(pair.month, pair.day)
    is_uposatha = lun.day_in_phase in (8, 15)
    return {
        "ce_year": pair.ce_year,
        "be_year": pair.be_year,
        "month": pair.month,
        "day": pair.day,
        "weekday_th": pair.weekday_th,
        "weekday_idx": pair.weekday_idx,
        "julian_day": pair.julian_day,
        "solar_pretty": pair.solar_pretty,
        "solar_iso": pair.solar_iso,
        "lunar": {
            "phase_name": lun.phase_name,
            "waxing": lun.waxing,
            "day_in_phase": lun.day_in_phase,
            "lunar_month": lun.lunar_month,
            "lunar_month_name": lun.lunar_month_name,
            "zodiac_year_name": lun.zodiac_year_name,
            "is_leap_month_year": lun.is_leap_month_year,
            "is_intercalary_month": lun.is_intercalary_month,
            "cs_year": lun.cs_year,
            "be_year_lunar": lun.be_year_lunar,
            "pretty": lun.pretty,
            "pretty_short": lun.pretty_short,
        },
        "holy_day": holy,            # None ถ้าไม่ใช่วันสำคัญ
        "is_uposatha": is_uposatha,  # วันพระ
        "national_holiday": national,  # วันสำคัญทางราชการ (None ถ้าไม่ใช่)
        "ms_year": _ce_to_ms(pair.ce_year),   # ม.ศ.
        "rs_year": _ce_to_rs(pair.ce_year),   # ร.ศ. (อาจติดลบสำหรับปีก่อน 1782)
        "is_ancient": pair.be_year < 1181,    # ยุคพุทธกาล (ใช้ Meeus ประมาณ)
        # warning ว่าผลลัพธ์อาจคลาดเคลื่อน ±1 วันจากปฏิทินทางการ
        # (สูตร approximation อวมาน/ดิถี — ดู Known Limitations Phase 1)
        "official_calendar_warning": holy is not None,
    }


def _today_widget() -> dict:
    """วันนี้ — สุริยคติ + จันทรคติ + วันสำคัญ (สำหรับ widget บนหน้าต่างๆ)

    ใช้ Thai sunrise convention: ถ้าก่อนพระอาทิตย์ขึ้น (~06:00) ถือเป็นวันก่อนหน้า
    """
    now = datetime.now(THAI_TZ)
    try:
        # Adjust ตามนิยมไทย (พระอาทิตย์ขึ้นจริงของกรุงเทพ)
        from thai_astro.sunrise import thai_birth_day_adjust
        adj_date, _, _ = thai_birth_day_adjust(
            now.replace(tzinfo=None), "กรุงเทพมหานคร", "real_sunrise",
        )
        # ใช้วันที่ปรับแล้ว
        now_adj = now.replace(year=adj_date.year, month=adj_date.month, day=adj_date.day)
        pair = _solar_to_lunar(now_adj.year + 543, now_adj.month, now_adj.day)
        lun = pair.lunar
        holy = find_holy_day(
            lun.lunar_month, lun.waxing, lun.day_in_phase,
            is_leap_month_year=lun.is_leap_month_year,
            is_intercalary_month=lun.is_intercalary_month,
        )
        national = find_national_holiday(now_adj.month, now_adj.day)
        is_uposatha = lun.day_in_phase in (8, 15)
        return {
            "solar_pretty": pair.solar_pretty,
            "solar_iso": pair.solar_iso,
            "lunar_pretty_short": lun.pretty_short,
            "zodiac_year_name": lun.zodiac_year_name,
            "holy_day": holy,
            "national_holiday": national,
            "is_uposatha": is_uposatha and holy is None,
        }
    except Exception:
        return None


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request) -> HTMLResponse:
    """หน้าเทียบปฏิทิน"""
    now = datetime.now(THAI_TZ)
    default_form = {
        "direction": "solar_to_lunar",
        "be_year": now.year + 543,
        "month": now.month,
        "day": now.day,
        "lunar_month": 6,
        "lunar_phase": "waxing",
        "lunar_day": 15,
    }
    return templates.TemplateResponse(
        request,
        "calendar.html",
        _common_context(
            request,
            form=default_form,
            result=None,
            error=None,
            epochs=CALENDAR_EPOCHS,
            holy_days=HOLY_DAYS,
        ),
    )


@app.post("/calendar/convert")
async def calendar_convert(
    request: Request,
    direction: str = Form("solar_to_lunar"),
    be_year: int = Form(2567),
    era: str = Form("be"),  # be/ce/ms/cs/rs — ศักราชของ input year
    month: int = Form(1),
    day: int = Form(1),
    lunar_month: int = Form(6),
    lunar_phase: str = Form("waxing"),
    lunar_day: int = Form(15),
    lunar_intercalary: str = Form(""),  # "1" = เดือน 8 หลัง (intercalary)
) -> JSONResponse:
    """API: แปลงปฏิทิน (JSON response) — รองรับ พ.ศ./ค.ศ./ม.ศ./จ.ศ./ร.ศ."""
    try:
        # แปลง input year → พ.ศ. (ที่ underlying function ใช้)
        try:
            ce_year = _year_to_ce(be_year, era)
            be_year_normalized = ce_year + 543
        except ValueError as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

        if direction == "solar_to_lunar":
            pair = _solar_to_lunar(be_year_normalized, month, day)
            return JSONResponse({
                "ok": True,
                "direction": direction,
                "matches": [_pair_to_dict(pair)],
            })
        elif direction == "lunar_to_solar":
            waxing = (lunar_phase == "waxing")
            intercalary = (lunar_intercalary == "1")
            matches = _lunar_to_solar(
                be_year_normalized, lunar_month, waxing, lunar_day,
                is_intercalary_month=intercalary,
            )
            return JSONResponse({
                "ok": True,
                "direction": direction,
                "matches": [_pair_to_dict(m) for m in matches],
            })
        else:
            return JSONResponse(
                {"ok": False, "error": f"ทิศทาง '{direction}' ไม่ถูกต้อง"},
                status_code=400,
            )
    except ValueError as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": f"เกิดข้อผิดพลาด: {e}"}, status_code=500
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
    sunrise_mode: str = Form("real_sunrise"),  # 'real_sunrise' (default) | 'six_am'
    transit_date_iso: str = Form(""),   # YYYY-MM-DD; ว่าง = ใช้ now
    transit_time_24: str = Form(""),    # HH:MM;       ว่าง = ใช้ now
    scroll_to_transit: str = Form(""),  # "1" → scroll ไปที่ scrubber หลัง load
) -> HTMLResponse:
    form = {
        "name": name,
        "birth_date_th": birth_date_th,
        "birth_time": birth_time,
        "province": province,
        "sunrise_mode": sunrise_mode,
    }
    error: Optional[str] = None
    result = None
    scroll_target = scroll_to_transit.strip()
    sunrise_info = None  # ส่งให้ template แสดง info banner

    try:
        if not birth_date_th.strip():
            raise ValueError("กรุณากรอกวันเดือนปีเกิด (พ.ศ.)")
        if not birth_time.strip():
            raise ValueError("กรุณากรอกเวลาเกิด")
        y, m, d = parse_thai_date(birth_date_th)
        h, mi = [int(x) for x in birth_time.split(":")]
        if province not in LOCALITY_ADJUST_SECONDS:
            province = "กรุงเทพมหานคร"

        # ============================================================
        # Thai sunrise convention — ปรับวันเกิดตามนิยมไทย
        # (วันใหม่เริ่มที่พระอาทิตย์ขึ้น ไม่ใช่เที่ยงคืน)
        # ============================================================
        from thai_astro.sunrise import thai_birth_day_adjust, format_sunrise
        from datetime import datetime as _dt
        mode = "six_am" if sunrise_mode == "six_am" else "real_sunrise"
        # y, m, d เป็น CE year/month/day จาก parse_thai_date()
        adj_date, sunrise_h, _ = thai_birth_day_adjust(
            _dt(y, m, d, h, mi), province, mode,
        )
        was_shifted = (adj_date.day, adj_date.month, adj_date.year) != (d, m, y)
        sunrise_info = {
            "mode": mode,
            "sunrise": format_sunrise(sunrise_h),
            "shifted": was_shifted,
            "input_date": _format_thai_date_ce(y, m, d),
            "input_time": f"{h:02d}:{mi:02d}",
            "thai_date": _format_thai_date_ce(adj_date.year, adj_date.month, adj_date.day),
            "province": province,
        }
        # ใช้วันที่ปรับแล้วในการ build chart (Chart.calculate ใช้ CE year ตาม y จาก parse_thai_date)
        chart = Chart.calculate(adj_date.year, adj_date.month, adj_date.day, h, mi, province=province)

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
            "day": tday,
            "month": tm_t,
            "be_year": ty + 543,
            "province": "กรุงเทพมหานคร",
        }

        result = chart_to_view(
            chart,
            person_name=name,
            transit_chart=transit_chart,
            transit_meta=transit_meta,
            original_birth_intl=(y, m, d, h, mi),  # วันเกิดสากลก่อน sunrise shift
        )
        # ✓ chart computed successfully → bump usage stat (ไม่เก็บข้อมูลดวง)
        _stat_increment(FEATURE_SURIYAYATRA)
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
            sunrise_info=sunrise_info,
            today_widget=_today_widget(),
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
        "category_label": r.category_label,
        "rashi": r.sig_rashi_name,
        "bhava": r.sig_bhava,
        "house": r.sig_house,
        "tone": r.tone,
        "is_own_sign": r.is_own_sign,
        "co_planets": [HORATHAYNU_PLANET_NAME_TH[k] for k in r.co_planets],
        "sign_lord": r.sign_lord_th,
        "text": r.text,
        # ----- Session 14 fields -----
        "intent_type": r.intent_type,
        "polarity": r.polarity,
        "intent_headline": r.intent_headline,
        "dignity_kind": r.dignity_kind,
        "dignity_label": r.dignity_label,
        "dignity_strength": r.dignity_strength,
        "house_relation_distance": r.house_relation_distance,
        "house_relation_name": r.house_relation_name,
        "house_relation_text": r.house_relation_text,
        "verdict_tier": r.verdict_tier,
        "verdict_percentage": r.verdict_percentage,
        "verdict_label": r.verdict_label,
        "verdict_factors": list(r.verdict_factors),
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
            "usage_counts": _stat_get_counts(),
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
        _stat_increment(FEATURE_HORATHAYNU_SET)
    except (ValueError, IndexError) as e:
        error = f"กรอกข้อมูลไม่ถูกต้อง: {e}"

    return templates.TemplateResponse(
        request,
        "horathaynu.html",
        {"request": request, "form": form, "result": result, "error": error,
         "latest_version": _latest_version(),
         "usage_counts": _stat_get_counts()},
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
        _stat_increment(FEATURE_HORATHAYNU_ASK)
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
        "category_label": prophecy.get("category_label"),
        "warning": warning,
        "rashi": prophecy["rashi"],
        "bhava": prophecy["bhava"],
        "house": prophecy["house"],
        "tone": prophecy["tone"],
        "co_planets": prophecy["co_planets"],
        "sign_lord": prophecy["sign_lord"],
        "is_own_sign": prophecy["is_own_sign"],
        # ----- Session 14 5-phase output -----
        "intent_type": prophecy.get("intent_type"),
        "polarity": prophecy.get("polarity"),
        "intent_headline": prophecy.get("intent_headline"),
        "dignity_kind": prophecy.get("dignity_kind"),
        "dignity_label": prophecy.get("dignity_label"),
        "dignity_strength": prophecy.get("dignity_strength"),
        "house_relation_distance": prophecy.get("house_relation_distance"),
        "house_relation_name": prophecy.get("house_relation_name"),
        "house_relation_text": prophecy.get("house_relation_text"),
        "verdict_tier": prophecy.get("verdict_tier"),
        "verdict_percentage": prophecy.get("verdict_percentage"),
        "verdict_label": prophecy.get("verdict_label"),
        "verdict_factors": prophecy.get("verdict_factors"),
        "timestamp": now.strftime("%H:%M:%S"),
    })


# ============================================================
# /muhurta — หาฤกษ์ (Muhurta)
# ============================================================
from thai_astro.muhurta import (
    compute_muhurta as _compute_muhurta,
    scan_range as _scan_range,
    scan_range_grouped as _scan_range_grouped,
    scan_range_multi_events as _scan_multi,
)
from thai_astro.muhurta_criteria import (
    list_events as _list_events,
    EVENTS as _MUHURTA_EVENTS,
    EVENT_CATEGORIES as _MUHURTA_CATEGORIES,
)
from thai_astro.navamsa import compute_navamsa as _compute_navamsa


# ----- Muhurta SVG dimensions (smaller — 2 charts side-by-side) -----
M_SVG_SIZE = 440
M_CENTER = M_SVG_SIZE / 2
M_R_INNER = 60
M_R_OUTER = 170                # ขอบนอกของวงราศี
M_R_LABEL = 145                # ชื่อราศี
M_R_CHIP = 110                 # planet chips
M_R_LAGNA = 130                # lagna marker
# Triyangka (decanate) dividers — เส้นแบ่ง 10°/20° ในแต่ละราศี
M_R_TRI_INNER = M_R_INNER
M_R_TRI_OUTER = M_R_OUTER - 6  # สั้นกว่าเส้นราศี (กันสับสน)
# Nakshatra ring (วงนอก) — 27 ฤกษ์
M_R_NAK_RING_IN = 175
M_R_NAK_RING_OUT = 218
M_R_NAK_LABEL_NAME = 184    # ชื่อนักษัตร (ใกล้ขอบใน)
M_R_NAK_LABEL_NUM = 205     # เลข (ใกล้ขอบนอก)

# planet abbreviation (เลขอารบิก) สำหรับ chip ฤกษ์
_MUHURTA_PLANET_ABBR = {
    "อาทิตย์": "1", "จันทร์": "2", "อังคาร": "3", "พุธ": "4",
    "พฤหัสบดี": "5", "ศุกร์": "6", "เสาร์": "7",
    "ราหู": "8", "เกตุ": "9", "มฤตยู": "0",
}
# planet color class (ตรงกับหน้าผูกดวงสุริยยาตร์)
_MUHURTA_PLANET_CLASS = {
    "อาทิตย์": "planet-sun", "จันทร์": "planet-moon", "อังคาร": "planet-mars",
    "พุธ": "planet-mercury", "พฤหัสบดี": "planet-jupiter", "ศุกร์": "planet-venus",
    "เสาร์": "planet-saturn", "ราหู": "planet-rahu", "เกตุ": "planet-ketu",
    "มฤตยู": "planet-uranus",
}


def _muhurta_polar(angle_deg: float, radius: float) -> tuple[float, float]:
    """เหมือน _polar_to_xy แต่คืนค่าเป็น offset จาก center (ไม่บวก SVG_CENTER)
    เพื่อใช้กับ canvas ขนาดอื่น (เช่น ผังหาฤกษ์ 380px)
    template ต้องบวก view.center เอง
    """
    rad = math.radians(angle_deg)
    return (radius * math.cos(rad), radius * math.sin(rad))


def _muhurta_svg_view(planets_by_rashi: dict, ascendant: Optional[dict] = None,
                      vargottama: Optional[set] = None,
                      show_triyangka: bool = False,
                      show_nakshatra: bool = False,
                      highlight_nakshatra_index: Optional[int] = None) -> dict:
    """SVG view สำหรับวงจักรราศีฤกษ์
    show_triyangka: วาดเส้นตรียางค์ 24 เส้น (10°/20° ในแต่ละราศี)
    show_nakshatra: วาดวงนอก + 27 ฤกษ์
    highlight_nakshatra_index: index 0-26 ของฤกษ์ที่จันทร์ตก
    ใช้พิกัด offset-from-center; template + view.center / - view.y
    """
    from thai_astro.nakshatra import NAKSHATRA_NAMES
    vargottama = vargottama or set()
    dividers = []
    r_outer_max = M_R_NAK_RING_OUT if show_nakshatra else M_R_OUTER
    for i in range(12):
        angle = 75 + 30 * i
        x1, y1 = _muhurta_polar(angle, M_R_INNER)
        x2, y2 = _muhurta_polar(angle, r_outer_max)
        dividers.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})

    # ตรียางค์ — 24 เส้น (10° และ 20° ในแต่ละราศี)
    triyangka_dividers = []
    if show_triyangka:
        for i in range(12):
            for sub in (1, 2):
                angle = 75 + 30 * i + 10 * sub
                tx1, ty1 = _muhurta_polar(angle, M_R_TRI_INNER)
                tx2, ty2 = _muhurta_polar(angle, M_R_TRI_OUTER)
                triyangka_dividers.append({"x1": tx1, "y1": ty1, "x2": tx2, "y2": ty2})

    # นักษัตร — 27 cell
    nakshatra_cells = []
    if show_nakshatra:
        STEP = 360.0 / 27
        # เลขไทย ๑-๒๗
        THAI_DIGITS = ["๐", "๑", "๒", "๓", "๔", "๕", "๖", "๗", "๘", "๙"]
        def _to_thai(n: int) -> str:
            return "".join(THAI_DIGITS[int(d)] for d in str(n))
        for j in range(27):
            cell_start = 75 + j * STEP
            cell_center = (cell_start + STEP / 2) % 360
            # divider ระหว่าง cell
            div_x1, div_y1 = _muhurta_polar(cell_start, M_R_NAK_RING_IN)
            div_x2, div_y2 = _muhurta_polar(cell_start, M_R_NAK_RING_OUT)
            # 2 ตำแหน่ง: เลข (วงนอก) + ชื่อ (วงใน)
            num_x, num_y = _muhurta_polar(cell_center, M_R_NAK_LABEL_NUM)
            name_x, name_y = _muhurta_polar(cell_center, M_R_NAK_LABEL_NAME)
            # ถ้า flip → ต้องสลับตำแหน่งเลขและชื่อให้ "เลขอยู่บน-ชื่ออยู่ล่าง" จากมุมมองคนอ่าน
            if 180 < cell_center < 360:
                num_x, name_x = name_x, num_x
                num_y, name_y = name_y, num_y
            # rotation: text ปกติเรียงในทิศพุ่งออกจากศูนย์กลาง (radial, อ่านจากในออกนอก)
            # rotation = 90 - cell_center
            # แต่ถ้า cell อยู่ครึ่งล่าง (SVG 180-360) text จะหัวลง — flip 180° เพื่ออ่านได้
            base_rot = 90 - cell_center
            need_flip = 180 < cell_center < 360
            label_rot = base_rot + 180 if need_flip else base_rot
            nakshatra_cells.append({
                "index": j,
                "number": j + 1,
                "number_th": _to_thai(j + 1),
                "name": NAKSHATRA_NAMES[j],
                "div_x1": div_x1, "div_y1": div_y1,
                "div_x2": div_x2, "div_y2": div_y2,
                "num_x": num_x, "num_y": num_y,
                "name_x": name_x, "name_y": name_y,
                "angle": cell_center,
                "label_rotation": label_rot,
                "highlight": (j == highlight_nakshatra_index),
            })

    rasis = []
    for ri in range(12):
        center_angle = 90 + 30 * ri
        label_x, label_y = _muhurta_polar(center_angle, M_R_LABEL)

        planet_names = planets_by_rashi.get(ri, [])
        chips = []
        n = len(planet_names)
        if n == 0:
            pass
        elif n == 1:
            cx, cy = _muhurta_polar(center_angle, M_R_CHIP)
            chips.append({"name": planet_names[0],
                          "abbr": _MUHURTA_PLANET_ABBR.get(planet_names[0], "?"),
                          "color_class": _MUHURTA_PLANET_CLASS.get(planet_names[0], ""),
                          "x": cx, "y": cy,
                          "varg": planet_names[0] in vargottama})
        else:
            # spread around center_angle
            spread = min(20, 5 * n)
            for i, pname in enumerate(planet_names):
                t = i / max(1, n - 1)
                ang = center_angle - spread / 2 + spread * t
                cx, cy = _muhurta_polar(ang, M_R_CHIP)
                chips.append({"name": pname,
                              "abbr": _MUHURTA_PLANET_ABBR.get(pname, "?"),
                              "color_class": _MUHURTA_PLANET_CLASS.get(pname, ""),
                              "x": cx, "y": cy,
                              "varg": pname in vargottama})

        rasis.append({
            "index": ri,
            "name": RASI_NAMES_TH[ri],
            "label_x": label_x, "label_y": label_y,
            "center_angle": center_angle,
            "chips": chips,
        })

    lagna = None
    if ascendant:
        asc_rasi = ascendant["rasi"]
        asc_deg = ascendant["degree"] + ascendant.get("arcminute", 0) / 60.0
        asc_angle = 75 + 30 * asc_rasi + asc_deg
        lx, ly = _muhurta_polar(asc_angle, M_R_LAGNA)
        lagna = {"x": lx, "y": ly, "angle": asc_angle}

    return {
        "size": M_SVG_SIZE, "center": M_CENTER,
        "r_inner": M_R_INNER, "r_outer": M_R_OUTER,
        "r_nak_in": M_R_NAK_RING_IN, "r_nak_out": M_R_NAK_RING_OUT,
        "dividers": dividers,
        "triyangka_dividers": triyangka_dividers,
        "nakshatra_cells": nakshatra_cells,
        "show_nakshatra": show_nakshatra,
        "rasis": rasis, "lagna": lagna,
    }


def _planets_by_rashi_from_chart(chart) -> dict:
    out: dict = {i: [] for i in range(12)}
    for name, p in chart.planets.items():
        out[p.zodiac.rasi].append(name)
    return out


def _planets_by_navamsa_rashi(chart) -> dict:
    """แต่ละดาวลงในวงนวางค์ตามตำแหน่ง nav_rashi"""
    out: dict = {i: [] for i in range(12)}
    for name, p in chart.planets.items():
        z = p.zodiac
        nv = _compute_navamsa(z.rasi, z.degree, z.arcminute)
        out[nv.nav_rashi].append(name)
    return out


def _muhurta_default_form() -> dict:
    """default = วันนี้ – +30 วัน, กรุงเทพฯ"""
    now = datetime.now(THAI_TZ).replace(tzinfo=None)
    end = now + timedelta(days=30)
    be1 = now.year + 543
    be2 = end.year + 543
    return {
        "mode": "general",
        "event_key": "",
        "start_date": f"{now.day:02d}/{now.month:02d}/{be1}",
        "end_date": f"{end.day:02d}/{end.month:02d}/{be2}",
        "range_days": "30",
        "province": "กรุงเทพมหานคร",
        "birth_date_th": "",
        "birth_time": "",
        "birth_province": "กรุงเทพมหานคร",
        "time_periods": [],
    }


def _muhurta_events_by_category() -> list:
    """list ของ {key, label, events: [EventCriteria]} ตามลำดับ EVENT_CATEGORIES"""
    grouped = {cat_key: [] for cat_key, _ in _MUHURTA_CATEGORIES}
    for ev in _MUHURTA_EVENTS.values():
        if ev.category in grouped:
            grouped[ev.category].append(ev)
    out = []
    for cat_key, cat_label in _MUHURTA_CATEGORIES:
        evs = grouped.get(cat_key, [])
        if evs:
            out.append({"key": cat_key, "label": cat_label, "events": evs})
    return out


MUHURTA_SCORE_MAX = 17    # ใช้เป็นเกณฑ์ 100% (จากการสำรวจ top hits จริง = 17)


def _score_to_percent(score: int) -> float:
    """แปลงคะแนนดิบเป็น % (0.00-100.00, 2 ทศนิยม).
    score >= MAX → 100.00, score <= 0 → 0.00
    """
    if score <= 0:
        return 0.0
    pct = score / MUHURTA_SCORE_MAX * 100
    pct = min(100.0, max(0.0, pct))
    return round(pct, 2)


def _percent_to_stars(pct: float) -> float:
    """แปลง % เป็นจำนวนดาว 0-5 (รองรับครึ่งดวง)
    100% → 5 ดวง, 90% → 4.5, 80% → 4, ..., 10% → 0.5, 0% → 0
    """
    stars = round(pct / 10) / 2     # ปัดทุก 10% เป็น half-star
    return max(0.0, min(5.0, stars))


def _score_to_grade(score: int) -> dict:
    """แปลงคะแนนเป็น grade + tier (สำหรับสี/ระดับ)
    หมายเหตุ: ดาวคิดจาก % แล้วแยก function (_percent_to_stars)
    """
    if score >= 12:
        return {"grade": "ดีเยี่ยม", "tier": "best",
                "summary": "ฤกษ์ดีเยี่ยม เหมาะที่สุดสำหรับงานสำคัญ"}
    if score >= 8:
        return {"grade": "ดีมาก", "tier": "great",
                "summary": "ฤกษ์ดีมาก องค์ประกอบเอื้ออำนวยส่วนใหญ่"}
    if score >= 5:
        return {"grade": "ดี", "tier": "good",
                "summary": "ฤกษ์ดี เหมาะการเริ่มกิจมงคล"}
    if score >= 2:
        return {"grade": "พอใช้", "tier": "fair",
                "summary": "ฤกษ์พอใช้ ดีกว่าวันธรรมดา"}
    if score >= 0:
        return {"grade": "กลาง", "tier": "neutral",
                "summary": "ฤกษ์กลาง ไม่ดีไม่ร้าย"}
    if score >= -3:
        return {"grade": "ระวัง", "tier": "warning",
                "summary": "ระวัง องค์ประกอบบางอย่างไม่เอื้อ"}
    return {"grade": "ไม่เหมาะ", "tier": "bad",
            "summary": "ไม่เหมาะ มีปัจจัยขัดข้องหลายอย่าง"}


_PERIOD_INFO = {
    "morning":      ("🌅", "เช้า"),
    "late_morning": ("☀️", "สาย"),
    "noon":         ("🌞", "บ่าย"),
    "evening":      ("🌇", "เย็น"),
    "dusk":         ("🌆", "ค่ำ"),
    "night":        ("🌙", "กลางคืน"),
}


def _serialize_dithi(h, event_label: Optional[str] = None) -> list:
    """Serialize dithi list with relevance tag for current event"""
    from thai_astro.dithi_classifier import DITHI_INFO, is_relevant_for, should_show_for_event
    # ดึง event category + key จาก event_label (look up จาก EVENTS)
    event_category = None
    event_key = None
    if event_label:
        for ev in _MUHURTA_EVENTS.values():
            if ev.label == event_label:
                event_category = ev.category
                event_key = ev.key
                break
    raw = list(h.dithi_classifications or [])
    # ถ้า raw มีแต่ entries ที่เป็น strict_event_only แล้วถูก filter ออกหมด
    # (เกิดกับวาร 3/4/7 — อ/พุธ/ส — ที่ classifier auto-เพิ่ม wan-taboo)
    # → ใส่ "ดิถีปกติ" เป็น fallback เพื่อไม่ให้แถวดิถีหายไปทั้งแถว
    filtered = [dc for dc in raw if should_show_for_event(dc, event_category, event_key)]
    if raw and not filtered:
        filtered = [DITHI_INFO["ปกติ"]]
    out = []
    for dc in filtered:
        cats = list(dc.relevant_categories)
        is_universal = "universal" in cats
        is_universal_bad = "universal_bad" in cats
        is_neutral = dc.severity == 0
        # คิดความเหมาะสมกับ event ที่เลือก
        if is_neutral:
            relevance = "neutral"
        elif is_universal:
            relevance = "universal_good"
        elif is_universal_bad:
            relevance = "universal_bad"
        elif event_category and is_relevant_for(dc, event_category, event_key=event_key):
            # ตรงกิจกรรม — แต่ต้องดูว่าเป็นดี/ร้าย
            relevance = "specific_match" if dc.is_auspicious else "specific_bad_match"
        else:
            relevance = "specific_other"   # ดี/ร้าย แต่เหมาะกับงานอื่น
        out.append({
            "name": dc.name,
            "is_auspicious": dc.is_auspicious,
            "short_desc": dc.short_desc,
            "long_desc": dc.long_desc,
            "severity": dc.severity,
            "suitable_for": dc.suitable_for,
            "relevance": relevance,
        })
    return out


def _serialize_roek(h, event_key: Optional[str]) -> Optional[dict]:
    """Serialize roek (ฤกษ์ใหญ่) for tag with relevance"""
    if not h.roek_name:
        return None
    from thai_astro.nakshatra import ROEK_INFO
    info = ROEK_INFO.get(h.roek_name, {})
    long_desc = info.get("long_desc", "")
    relevant_events = info.get("relevant_events", ())
    is_match = bool(event_key and event_key in relevant_events)
    return {
        "name": h.roek_name,
        "is_auspicious": h.roek_auspicious,
        "nakshatra_name": h.nakshatra_name,
        "nakshatra_number": h.nakshatra_number,
        "short_desc": h.roek_name,
        "long_desc": long_desc,
        "is_match": is_match,
        "suitable_for": "เหมาะกับ " + ", ".join(
            (_MUHURTA_EVENTS[k].label for k in relevant_events if k in _MUHURTA_EVENTS)
        ) if relevant_events else "ไม่เฉพาะกิจกรรมใด",
    }


def _serialize_criteria(h, event_key: Optional[str]) -> list:
    """Serialize matched special criteria with details"""
    from thai_astro.muhurta_criteria import CRITERION_INFO
    out = []
    for name in (h.matched_criteria or []):
        info = CRITERION_INFO.get(name, {})
        relevant_events = info.get("relevant_events", ())
        is_match = bool(event_key and event_key in relevant_events)
        out.append({
            "name": name,
            "long_desc": info.get("long_desc", ""),
            "tone": info.get("tone", "good"),
            "is_match": is_match,
            "suitable_for": "เหมาะกับ " + ", ".join(
                (_MUHURTA_EVENTS[k].label for k in relevant_events if k in _MUHURTA_EVENTS)
            ) if relevant_events else "",
        })
    return out


def _serialize_hit(h, event_label: Optional[str] = None) -> dict:
    grade = _score_to_grade(h.score)
    pct = _score_to_percent(h.score)
    stars = _percent_to_stars(pct)
    period_icon, period_label = _PERIOD_INFO.get(h.period or "", ("", ""))
    # ฤกษ์ใช้ได้ในช่วง 1 ชั่วโมง (เพราะ scan ทุก 60 นาที — ลัคนาเดียวกัน)
    end_time = (h.when + timedelta(hours=1)).strftime("%H:%M")
    # หา event_key สำหรับ filter relevance
    event_key = None
    for ev in _MUHURTA_EVENTS.values():
        if ev.label == event_label:
            event_key = ev.key
            break
    return {
        "when": h.when.strftime("%d/%m/%Y %H:%M"),
        "be_date": f"{h.when.day:02d}/{h.when.month:02d}/{h.when.year + 543}",
        "iso": h.when.strftime("%Y-%m-%dT%H:%M"),
        "time": h.when.strftime("%H:%M"),
        "time_end": end_time,
        "score": h.score,
        "score_max": MUHURTA_SCORE_MAX,
        "score_percent": pct,
        "verdict": h.verdict,
        "grade": grade["grade"],
        "stars": stars,
        "tier": grade["tier"],
        "grade_summary": grade["summary"],
        "summary": h.summary,
        "event_label": event_label,
        "period": h.period,
        "period_icon": period_icon,
        "period_label": period_label,
        "lunar_pretty": h.lunar_pretty,
        "dithi_classifications": _serialize_dithi(h, event_label),
        "roek": _serialize_roek(h, event_key),
        "matched_criteria_details": _serialize_criteria(h, event_key),
        "personal_bhava": h.personal_bhava,
        "personal_bhava_quality": h.personal_bhava_quality,
        "personal_bhava_tone": h.personal_bhava_tone,
        "matched_criteria": h.matched_criteria or [],
    }


def _serialize_muhurta(mr, natal_extra: Optional[dict] = None) -> dict:
    """Convert MuhurtaResult → dict for template

    natal_extra: optional dict from _compute_personal_extras()
    """
    varg_set = set(mr.vargottama_planets)
    rashi_view = _muhurta_svg_view(
        _planets_by_rashi_from_chart(mr.chart),
        ascendant={
            "rasi": mr.chart.ascendant.zodiac.rasi,
            "degree": mr.chart.ascendant.zodiac.degree,
            "arcminute": mr.chart.ascendant.zodiac.arcminute,
        },
        vargottama=varg_set,
        show_triyangka=True,
        show_nakshatra=True,
        highlight_nakshatra_index=mr.nakshatra.index,
    )
    navamsa_view = _muhurta_svg_view(
        _planets_by_navamsa_rashi(mr.chart),
        vargottama=varg_set,
    )
    base = {
        "when_str": mr.when.strftime("%d/%m/%Y %H:%M"),
        "province": mr.province,
        "verdict": mr.verdict,
        "score": mr.score,
        "wan": mr.wan,
        "wan_planet": mr.wan_planet,
        "wan_quality": mr.wan_quality,
        "wan_remark": mr.wan_remark,
        "lunar_pretty": mr.lunar.pretty,
        "lunar_short": mr.lunar.pretty_short,
        "tithi_quality": mr.tithi_quality,
        "nakshatra": {
            "number": mr.nakshatra.number,
            "name": mr.nakshatra.name,
            "pada": mr.nakshatra.pada,
            "lord": mr.nakshatra.lord,
            "roek_name": mr.nakshatra.roek_name,
            "is_auspicious": mr.nakshatra.is_auspicious,
            "meaning": mr.nakshatra.meaning,
        },
        "kalayok": {
            "cs_year": mr.kalayok.cs_year,
            "thongchai": {
                "wan_name": mr.kalayok.thongchai.wan_name,
                "yarm": mr.kalayok.thongchai.yarm,
                "rasi": mr.kalayok.thongchai.rasi,
                "dithi": mr.kalayok.thongchai.dithi,
                "roek": mr.kalayok.thongchai.roek,
            },
            "athibodi": {
                "wan_name": mr.kalayok.athibodi.wan_name,
                "yarm": mr.kalayok.athibodi.yarm,
                "rasi": mr.kalayok.athibodi.rasi,
                "dithi": mr.kalayok.athibodi.dithi,
                "roek": mr.kalayok.athibodi.roek,
            },
            "ubat": {
                "wan_name": mr.kalayok.ubat.wan_name,
                "yarm": mr.kalayok.ubat.yarm,
                "rasi": mr.kalayok.ubat.rasi,
                "dithi": mr.kalayok.ubat.dithi,
                "roek": mr.kalayok.ubat.roek,
            },
            "lokawinat": {
                "wan_name": mr.kalayok.lokawinat.wan_name,
                "yarm": mr.kalayok.lokawinat.yarm,
                "rasi": mr.kalayok.lokawinat.rasi,
                "dithi": mr.kalayok.lokawinat.dithi,
                "roek": mr.kalayok.lokawinat.roek,
            },
        },
        "kalayok_matches": mr.kalayok_matches,
        "specials": [
            {"name": s.name, "matched": s.matched, "tone": s.tone, "detail": s.detail}
            for s in mr.special_criteria
        ],
        "vargottama": mr.vargottama_planets,
        "suggestions": mr.activity_suggestions,
        "cautions": mr.cautions,
        "event_key": mr.event_key,
        "event_score": mr.event_score,
        "planets": [
            {
                "name": name,
                "rasi_name": p.zodiac.rasi_name,
                "degree": p.zodiac.degree,
                "arcminute": p.zodiac.arcminute,
            }
            for name, p in mr.chart.planets.items()
        ],
        "ascendant": {
            "rasi_name": mr.chart.ascendant.zodiac.rasi_name,
            "degree": mr.chart.ascendant.zodiac.degree,
            "arcminute": mr.chart.ascendant.zodiac.arcminute,
        },
        "svg_rashi": rashi_view,
        "svg_navamsa": navamsa_view,
    }
    if natal_extra:
        base["natal"] = natal_extra
    return base


def _compute_personal_extras(birth_date_th: str, birth_time: str, birth_province: str,
                              muhurta_chart) -> dict:
    """ผูกดวงเจ้าชะตา + เทียบฤกษ์กับลัคนาเดิม + transit_prophecy"""
    y, m, d = parse_thai_date(birth_date_th)
    hh, mm = (birth_time.strip().split(":") + ["0"])[:2]
    natal_chart = Chart.calculate(y, m, d, int(hh), int(mm), province=birth_province)

    # ลัคนาเดิม
    natal_asc_rasi = natal_chart.ascendant.zodiac.rasi

    # ฤกษ์ตกภพไหนของลัคนาเดิม
    # ลัคนา ณ ขณะหาฤกษ์ → ภพ (1-12) นับจากลัคนาเดิม
    asc_now_rasi = muhurta_chart.ascendant.zodiac.rasi
    target_bhava = ((asc_now_rasi - natal_asc_rasi) % 12) + 1

    KENDRA = {1, 4, 7, 10}
    TRIKONA = {1, 5, 9}
    DUSTHANA = {6, 8, 12}
    if target_bhava in KENDRA and target_bhava in TRIKONA:
        bhava_quality = "ดีเยี่ยม (เป็นทั้งภพหลักและภพแห่งบุญ)"
        bhava_tone = "good"
    elif target_bhava in KENDRA:
        bhava_quality = "ดี (ภพหลัก — มั่นคง)"
        bhava_tone = "good"
    elif target_bhava in TRIKONA:
        bhava_quality = "ดี (ภพแห่งบุญ — โชคลาภ)"
        bhava_tone = "good"
    elif target_bhava in DUSTHANA:
        bhava_quality = "ระวัง (ภพแห่งทุกข์ — เลี่ยงงานสำคัญ)"
        bhava_tone = "warning"
    else:
        bhava_quality = "กลาง"
        bhava_tone = "neutral"

    # transit aspects (ดาวจร = ดาว ณ ขณะหาฤกษ์)
    aspects = find_transit_aspects(natal_chart.planets, muhurta_chart.planets)
    summary = generate_summary(aspects)

    # serialize aspects (top 5)
    asp_out = []
    for a in aspects[:5]:
        asp_out.append({
            "transit": a.transit_planet,
            "natal": a.natal_planet,
            "kind": a.aspect_type,
            "rasi": a.transit_rasi,
            "text": a.prediction,
            "severity": a.severity,
        })

    return {
        "birth_date": birth_date_th,
        "birth_time": birth_time,
        "birth_province": birth_province,
        "natal_asc_rasi_name": natal_chart.ascendant.zodiac.rasi_name,
        "natal_asc_degree": natal_chart.ascendant.zodiac.degree,
        "natal_asc_arcminute": natal_chart.ascendant.zodiac.arcminute,
        "target_bhava": target_bhava,
        "bhava_quality": bhava_quality,
        "bhava_tone": bhava_tone,
        "aspects": asp_out,
        "summary_headline": summary.get("headline", ""),
        "summary_conclusion": summary.get("conclusion", ""),
    }


@app.get("/muhurta", response_class=HTMLResponse)
async def muhurta_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "muhurta.html",
        {
            "request": request,
            "provinces": PROVINCES,
            "events_by_cat": _muhurta_events_by_category(),
            "events_flat": _list_events(),
            "form": _muhurta_default_form(),
            "result": None,
            "error": None,
            "latest_version": _latest_version(),
            "usage_counts": _stat_get_counts(),
        },
    )


@app.post("/muhurta", response_class=HTMLResponse)
async def muhurta_calculate(
    request: Request,
    mode: str = Form(default="general"),
    event_keys: list[str] = Form(default=[]),
    time_periods: list[str] = Form(default=[]),
    start_date: str = Form(default=""),
    end_date: str = Form(default=""),
    range_days: str = Form(default="30"),
    province: str = Form(default="กรุงเทพมหานคร"),
    birth_date_th: str = Form(default=""),
    birth_time: str = Form(default=""),
    birth_province: str = Form(default=""),
) -> HTMLResponse:
    # filter เฉพาะ key ที่มีจริง
    selected_keys = [k for k in event_keys if k in _MUHURTA_EVENTS]
    valid_periods = {"morning", "late_morning", "noon", "evening", "dusk", "night"}
    selected_periods = [p for p in time_periods if p in valid_periods]
    form = {
        "mode": mode, "event_keys": selected_keys,
        "time_periods": selected_periods,
        "start_date": start_date, "end_date": end_date,
        "range_days": range_days, "province": province,
        "birth_date_th": birth_date_th, "birth_time": birth_time,
        "birth_province": birth_province or "กรุงเทพมหานคร",
    }
    error = None
    result = None
    try:
        if not selected_keys:
            raise ValueError("กรุณาเลือกกิจกรรมอย่างน้อย 1 อย่าง")

        y1, m1, d1 = parse_thai_date(start_date)
        y2, m2, d2 = parse_thai_date(end_date)
        start = datetime(y1, m1, d1, 6, 0)
        end = datetime(y2, m2, d2, 22, 0)
        if end < start:
            raise ValueError("วันสิ้นสุดต้องหลังวันเริ่ม")
        max_days = int(range_days) if range_days in ("15", "30", "45", "60", "90") else 30
        if (end - start).days > max_days:
            raise ValueError(f"ช่วงเกิน {max_days} วัน")

        # ใช้ step 60 นาทีคงที่ — ทำให้ผลลัพธ์ระหว่าง range เป็น subset
        # (15 วัน ⊆ 30 วัน ⊆ 45 วัน ⊆ ...)
        step_min = 60

        birth_dt = None
        bprov = None
        if mode in ("personal", "oracle"):
            if not (birth_date_th.strip() and birth_time.strip()):
                raise ValueError("โหมดเฉพาะบุคคล/โหร ต้องกรอกวันเวลาเกิด")
            by, bm, bd = parse_thai_date(birth_date_th)
            bhh, bmm = (birth_time.strip().split(":") + ["0"])[:2]
            birth_dt = datetime(by, bm, bd, int(bhh), int(bmm))
            bprov = birth_province or "กรุงเทพมหานคร"

        # FAST scan — กรอง threshold คุณภาพ ไม่ cap ด้วยจำนวน:
        #   - คะแนน >= 5 (เกรด "ดี" ขึ้นไป)
        #   - max 2 ฤกษ์/วัน (กระจายวัน)
        # ปลายทาง: 30 วัน ~25, 60 วัน ~50, 90 วัน ~75
        per_event_hits = _scan_multi(
            start, end,
            event_keys=selected_keys,
            province=province,
            step_minutes=step_min,
            top_n_per_event=999,         # ไม่ cap ด้วยจำนวน
            min_score=11,                 # >= 60% ของคะแนนเต็ม 17 (เกรด "ดีเยี่ยม cutoff")
            birth_datetime=birth_dt, birth_province=bprov,
            max_days=max_days,
            time_periods=None,
            max_per_day=2,
        )

        groups = []
        for ek in selected_keys:
            ev = _MUHURTA_EVENTS[ek]
            hits = per_event_hits.get(ek, [])
            shown = hits  # filter ทำใน scan แล้ว
            if not shown:
                continue
            groups.append({
                "event_key": ek,
                "event_label": ev.label,
                "event_icon": ev.icon,
                "event_category": ev.category,
                "event_description": ev.description,
                "hits": [_serialize_hit(h, ev.label) for h in shown],
                "total_found": len(shown),
            })

        result = {
            "mode": mode,
            "event_keys": selected_keys,
            "groups": groups,
            "total_events": len(groups),
            "total_requested": len(selected_keys),
        }

        if birth_dt:
            from thai_astro.chart import Chart as _Chart
            nc = _Chart.calculate(birth_dt.year, birth_dt.month, birth_dt.day,
                                   birth_dt.hour, birth_dt.minute, province=bprov)
            result["natal_info"] = {
                "date": birth_date_th,
                "time": birth_time,
                "province": bprov,
                "asc_rasi": nc.ascendant.zodiac.rasi_name,
                "asc_deg": nc.ascendant.zodiac.degree,
                "asc_min": nc.ascendant.zodiac.arcminute,
            }

    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"คำนวณไม่ได้: {e}"

    # นับการใช้งาน (ถ้าคำนวณสำเร็จ)
    if result is not None:
        try:
            _stat_increment(FEATURE_MUHURTA)
        except Exception:
            pass

    return templates.TemplateResponse(
        request,
        "muhurta.html",
        {
            "request": request,
            "provinces": PROVINCES,
            "events_by_cat": _muhurta_events_by_category(),
            "events_flat": _list_events(),
            "form": form,
            "result": result,
            "error": error,
            "latest_version": _latest_version(),
            "usage_counts": _stat_get_counts(),
        },
    )


@app.post("/muhurta/check")
async def muhurta_check(
    check_date: str = Form(default=""),
    check_time: str = Form(default=""),
    check_province: str = Form(default="กรุงเทพมหานคร"),
    check_event_key: str = Form(default=""),
    birth_date_th: str = Form(default=""),
    birth_time: str = Form(default=""),
    birth_province: str = Form(default=""),
) -> JSONResponse:
    """ตรวจสอบฤกษ์ของจุดเวลาเดียว (สำหรับฟอร์ม 'ตรวจสอบฤกษ์ของฉัน')"""
    try:
        y, m, d = parse_thai_date(check_date)
        hh, mm = (check_time.strip().split(":") + ["0"])[:2]
        when = datetime(y, m, d, int(hh), int(mm))
        ek = check_event_key if check_event_key in _MUHURTA_EVENTS else None
        mr = _compute_muhurta(when, check_province, ek)

        natal_extra = None
        if birth_date_th.strip() and birth_time.strip():
            try:
                natal_extra = _compute_personal_extras(
                    birth_date_th, birth_time,
                    birth_province or "กรุงเทพมหานคร",
                    mr.chart,
                )
            except Exception:
                pass

        # ใช้ score เดียวกับ scan: ถ้ามี natal → +bhava modifier; ถ้ามี event → +event_score
        final_score = mr.score
        bhava_info = None
        if natal_extra:
            bt = natal_extra["bhava_tone"]
            if bt == "good": final_score += 2
            elif bt == "warning": final_score -= 2
            bhava_info = {
                "bhava": natal_extra["target_bhava"],
                "quality": natal_extra["bhava_quality"],
                "tone": bt,
            }
        event_extra_score = 0
        if ek:
            from thai_astro.muhurta_criteria import event_score as _es
            ee = _es(mr.chart, ek)
            event_extra_score = ee["score"]
            final_score += event_extra_score

        grade = _score_to_grade(final_score)
        pct = _score_to_percent(final_score)
        stars = _percent_to_stars(pct)
        try:
            _stat_increment(FEATURE_MUHURTA_CHECK)
        except Exception:
            pass
        return JSONResponse({
            "when": when.strftime("%d/%m/%Y %H:%M"),
            "score_max": MUHURTA_SCORE_MAX,
            "score_percent": pct,
            "be_date": f"{when.day:02d}/{when.month:02d}/{when.year + 543}",
            "time": when.strftime("%H:%M"),
            "wan_planet": mr.wan_planet,
            "wan_quality": mr.wan_quality,
            "lunar": mr.lunar.pretty,
            "tithi_quality": mr.tithi_quality,
            "nakshatra_name": mr.nakshatra.name,
            "nakshatra_number": mr.nakshatra.number,
            "roek_name": mr.nakshatra.roek_name,
            "nakshatra_auspicious": mr.nakshatra.is_auspicious,
            "specials": [
                {"name": s.name, "matched": s.matched, "tone": s.tone, "detail": s.detail}
                for s in mr.special_criteria
            ],
            "vargottama": mr.vargottama_planets,
            "score": final_score,
            "base_score": mr.score,
            "event_extra_score": event_extra_score,
            "event_key": ek,
            "event_label": _MUHURTA_EVENTS[ek].label if ek else None,
            "grade": grade["grade"],
            "stars": stars,
            "tier": grade["tier"],
            "grade_summary": grade["summary"],
            "suggestions": mr.activity_suggestions,
            "cautions": mr.cautions,
            "personal_bhava": bhava_info,
        })
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"ผิดพลาด: {e}"}, status_code=500)


# ============================================================
# Forecast 7 วัน (เมื่อวาน−2 ถึง +3) — strip บน /muhurta
# ============================================================
def _format_be_date_short(d: _date) -> str:
    """13 มิ.ย."""
    months = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
              "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    return f"{d.day} {months[d.month]}"


def _wan_name_from_date(d: _date) -> str:
    names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    return names[d.weekday()]


_FORECAST_MIN_SCORE = 11    # ตรงกับ cutoff ของ scan ปกติ
_FORECAST_CACHE: Dict[tuple, dict] = {}     # (date_iso, province) → result


def _compute_forecast_day(d: _date, province: str) -> dict:
    """คำนวณข้อมูลฤกษ์ของวันเดียว สำหรับการ์ดใน strip
    Returns dict with: date, wan, score_avg, percent, stars, grade, tier,
        top_events (3), bad_alerts, hit_count, event_count
    """
    cache_key = (d.isoformat(), province)
    if cache_key in _FORECAST_CACHE:
        return _FORECAST_CACHE[cache_key]

    from thai_astro.muhurta import scan_range_multi_events as _scan
    start = datetime(d.year, d.month, d.day, 6, 0)
    end = datetime(d.year, d.month, d.day, 22, 0)
    event_keys = list(_MUHURTA_EVENTS.keys())

    try:
        # ใช้ max_per_day=15 ให้ตรงกับ /forecast/event-hits — count "N เวลา"
        # บน chip จะตรงกับจำนวนฤกษ์ที่ขยายออกมาจริง
        results = _scan(
            start=start, end=end, event_keys=event_keys,
            province=province, step_minutes=60,
            top_n_per_event=15, min_score=_FORECAST_MIN_SCORE,
            max_per_day=15,
        )
    except Exception:
        results = {}

    # รวมคะแนนทุก event
    all_scores = []
    event_stats: Dict[str, dict] = {}    # event_key → {best, count}
    for ek, hits in results.items():
        if not hits:
            continue
        scores = [h.score for h in hits]
        event_stats[ek] = {"best": max(scores), "count": len(scores)}
        all_scores.extend(scores)

    hit_count = len(all_scores)
    event_count = len(event_stats)
    avg_score = (sum(all_scores) / hit_count) if hit_count else 0

    # คะแนนการ์ด: เฉลี่ย hits ที่ผ่าน threshold; ถ้าไม่มี hit เลย → 0
    card_score = avg_score
    pct = _score_to_percent(int(round(card_score)))
    grade_info = _score_to_grade(int(round(card_score)))

    # top 3 events เรียงตาม best score
    top_sorted = sorted(event_stats.items(), key=lambda x: -x[1]["best"])[:3]
    top_events = []
    for ek, stats in top_sorted:
        ev = _MUHURTA_EVENTS[ek]
        ev_grade = _score_to_grade(stats["best"])
        top_events.append({
            "key": ek,
            "icon": ev.icon,
            "label": ev.label,
            "score": stats["best"],
            "time_count": stats["count"],
            "percent": _score_to_percent(stats["best"]),
            "grade": ev_grade["grade"],
            "tier": ev_grade["tier"],
        })

    # bad alerts: event taboo dithi ที่เกิดวันนี้ (strict_event_only ที่ตรง)
    # เช็คจาก base muhurta ของวันนั้น ตอนเที่ยง
    from thai_astro.muhurta import compute_muhurta
    from thai_astro.dithi_classifier import is_relevant_for
    bad_alerts = []
    try:
        base = compute_muhurta(
            datetime(d.year, d.month, d.day, 12, 0), province, event_key=None,
        )
        for dc in (base.dithi_classifications or []):
            if dc.strict_event_only and not dc.is_auspicious:
                # หา event ที่ตรง relevant_events
                for ek in (dc.relevant_events or ()):
                    if ek in _MUHURTA_EVENTS:
                        ev = _MUHURTA_EVENTS[ek]
                        bad_alerts.append({
                            "key": ek, "icon": ev.icon, "label": ev.label,
                            "reason": dc.name,
                        })
    except Exception:
        pass

    out = {
        "date": d.isoformat(),
        "be_year": d.year + 543,
        "be_date_short": _format_be_date_short(d),
        "wan": _wan_name_from_date(d),
        "score": int(round(card_score)),
        "percent": pct,
        "stars": _percent_to_stars(pct),
        "grade": grade_info["grade"],
        "tier": grade_info["tier"],
        "summary": grade_info["summary"],
        "hit_count": hit_count,
        "event_count": event_count,
        "top_events": top_events,
        "bad_alerts": bad_alerts,
    }
    _FORECAST_CACHE[cache_key] = out
    return out


@app.get("/muhurta/forecast")
async def muhurta_forecast(
    province: str = "กรุงเทพมหานคร",
    center: str = "",    # YYYY-MM-DD, default = today
) -> JSONResponse:
    """ฤกษ์ 7 วัน: center−3 ถึง center+3 (เมื่อวาน−2/เมื่อวาน/วันนี้/พรุ่งนี้/+1/+2/+3)"""
    if center:
        try:
            base = datetime.strptime(center, "%Y-%m-%d").date()
        except ValueError:
            base = datetime.now().date()
    else:
        base = datetime.now().date()
    # 7 การ์ด: -2, -1, 0, +1, +2, +3, +4 (อดีต 2 วัน + วันนี้ + อนาคต 4 วัน)
    days = [base + timedelta(days=offset) for offset in range(-2, 5)]
    forecast = []
    for d in days:
        info = _compute_forecast_day(d, province)
        info["offset"] = (d - base).days
        info["is_today"] = (d == base)
        forecast.append(info)
    return JSONResponse({"days": forecast, "center": base.isoformat(), "province": province})


@app.get("/muhurta/forecast/event-hits", response_class=HTMLResponse)
async def muhurta_forecast_event_hits(
    request: Request,
    date: str,            # YYYY-MM-DD
    event: str,           # event key
    province: str = "กรุงเทพมหานคร",
) -> HTMLResponse:
    """คืน HTML partial: รายการ hit-card สำหรับ event ที่เลือก ในวันที่กำหนด
    ใช้กับ inline expand ใน forecast strip"""
    from thai_astro.muhurta import scan_range_multi_events as _scan
    if event not in _MUHURTA_EVENTS:
        return HTMLResponse(
            f'<div class="forecast-empty-msg">⚠️ ไม่รู้จักกิจกรรม: {event}</div>',
            status_code=400,
        )
    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return HTMLResponse(
            f'<div class="forecast-empty-msg">⚠️ วันที่ไม่ถูกต้อง: {date}</div>',
            status_code=400,
        )
    ev = _MUHURTA_EVENTS[event]
    start = datetime(d.year, d.month, d.day, 6, 0)
    end = datetime(d.year, d.month, d.day, 22, 0)
    try:
        results = _scan(
            start=start, end=end, event_keys=[event],
            province=province, step_minutes=60,
            top_n_per_event=15, min_score=_FORECAST_MIN_SCORE,
            max_per_day=15,    # ทั้งวันเอาหมด
        )
    except Exception as e:
        return HTMLResponse(
            f'<div class="forecast-empty-msg">⚠️ คำนวณไม่สำเร็จ: {e}</div>',
            status_code=500,
        )
    hits = results.get(event, []) or []
    if not hits:
        return HTMLResponse(
            f'<div class="forecast-empty-msg">— ไม่มีฤกษ์ดีของ "{ev.label}" ในวันนี้ —</div>'
        )
    # Sort: best score first
    hits = sorted(hits, key=lambda h: -h.score)
    serialized = [_serialize_hit(h, event_label=ev.label) for h in hits]
    result_ctx = {
        "mode": "general",
        "event_keys": [event],
        "events_labels": {event: f"{ev.icon} {ev.label}"},
    }
    form_ctx = {"province": province}
    # render hit-card rows
    tpl = templates.env.get_template("_muhurta_hit_row.html")
    parts = []
    for i, h_dict in enumerate(serialized, start=1):
        parts.append(tpl.render(h=h_dict, rank=i, result=result_ctx, form=form_ctx))
    return HTMLResponse("".join(parts))


@app.get("/muhurta/detail")
async def muhurta_detail(
    iso: str,
    province: str = "กรุงเทพมหานคร",
    event_key: str = "",
    birth_date_th: str = "",
    birth_time: str = "",
    birth_province: str = "",
) -> JSONResponse:
    """รายละเอียดฤกษ์ 1 จุดเวลา (สำหรับ accordion โหร)"""
    try:
        when = datetime.strptime(iso, "%Y-%m-%dT%H:%M")
        ek = event_key if event_key in _MUHURTA_EVENTS else None
        mr = _compute_muhurta(when, province, ek)

        natal_extra = None
        if birth_date_th.strip() and birth_time.strip():
            try:
                natal_extra = _compute_personal_extras(
                    birth_date_th, birth_time,
                    birth_province or "กรุงเทพมหานคร",
                    mr.chart,
                )
            except Exception:
                pass

        view = _serialize_muhurta(mr, natal_extra=natal_extra)
        return JSONResponse(view)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"ผิดพลาด: {e}"}, status_code=500)


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
