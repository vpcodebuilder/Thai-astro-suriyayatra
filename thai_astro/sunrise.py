"""พระอาทิตย์ขึ้นและการนับวันแบบโหราศาสตร์ไทย

ในตำราโหราศาสตร์ไทย "วันใหม่เริ่มที่พระอาทิตย์ขึ้น" ไม่ใช่เที่ยงคืน
- เกิด 3 มิ.ย. 02:00 (สากล) → ก่อนพระอาทิตย์ขึ้น → ถือเป็น 2 มิ.ย. (ตำราไทย)

2 โหมดให้เลือก:
1. `real_sunrise` (default) — คำนวณพระอาทิตย์ขึ้นตามจริงจาก (วัน, ละติจูด, ลองจิจูด)
2. `six_am` — ใช้ 06:00 น. (Thai standard time) ตามตำราคลาสสิก (SunriseType.SixAM)

Source:
- NOAA solar calculator (simplified):
  https://gml.noaa.gov/grad/solcalc/solareqns.PDF
- Accuracy ±5-10 นาที (ดีพอสำหรับโหราศาสตร์ ที่ใช้ระดับนาทีอยู่แล้ว)
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Literal, Dict

from .lakkana import LOCALITY_ADJUST_SECONDS


# ============================================================
# Province latitude (≈ จังหวัดศูนย์กลาง — accuracy ±0.3°)
# ลองจิจูด derive จาก LOCALITY_ADJUST_SECONDS (= 105° − local lon)
# ============================================================
LATITUDE_BY_PROVINCE: Dict[str, float] = {
    "กระบี่": 8.08, "กรุงเทพมหานคร": 13.75, "กาญจนบุรี": 14.02,
    "กาฬสินธุ์": 16.43, "กำแพงเพชร": 16.48, "ขอนแก่น": 16.44,
    "จันทบุรี": 12.61, "ฉะเชิงเทรา": 13.69, "ชลบุรี": 13.36,
    "ชัยนาท": 15.19, "ชัยภูมิ": 15.81, "ชุมพร": 10.49,
    "เชียงราย": 19.91, "เชียงใหม่": 18.79, "ตรัง": 7.56,
    "ตราด": 12.24, "ตาก": 16.87, "นครนายก": 14.21,
    "นครปฐม": 13.82, "นครพนม": 17.41, "นครราชสีมา": 14.97,
    "นครศรีธรรมราช": 8.43, "นครสวรรค์": 15.70, "นนทบุรี": 13.86,
    "นราธิวาส": 6.43, "น่าน": 18.78, "บึงกาฬ": 18.36,
    "บุรีรัมย์": 14.99, "ปทุมธานี": 14.02, "ประจวบคีรีขันธ์": 11.81,
    "ปราจีนบุรี": 14.05, "ปัตตานี": 6.87, "พระนครศรีอยุธยา": 14.36,
    "พะเยา": 19.17, "พังงา": 8.45, "พัทลุง": 7.62,
    "พิจิตร": 16.44, "พิษณุโลก": 16.82, "เพชรบุรี": 13.11,
    "เพชรบูรณ์": 16.42, "แพร่": 18.14, "ภูเก็ต": 7.88,
    "มหาสารคาม": 16.18, "มุกดาหาร": 16.54, "แม่ฮ่องสอน": 19.30,
    "ยโสธร": 15.79, "ยะลา": 6.54, "ร้อยเอ็ด": 16.05,
    "ระนอง": 9.97, "ระยอง": 12.68, "ราชบุรี": 13.53,
    "ลพบุรี": 14.80, "ลำปาง": 18.29, "ลำพูน": 18.58,
    "เลย": 17.49, "ศรีสะเกษ": 15.12, "สกลนคร": 17.16,
    "สงขลา": 7.20, "สตูล": 6.62, "สมุทรปราการ": 13.60,
    "สมุทรสงคราม": 13.41, "สมุทรสาคร": 13.55, "สระแก้ว": 13.82,
    "สระบุรี": 14.53, "สิงห์บุรี": 14.89, "สุโขทัย": 17.01,
    "สุพรรณบุรี": 14.47, "สุราษฎร์ธานี": 9.14, "สุรินทร์": 14.88,
    "หนองคาย": 17.88, "หนองบัวลำภู": 17.20, "อ่างทอง": 14.59,
    "อำนาจเจริญ": 15.86, "อุดรธานี": 17.41, "อุตรดิตถ์": 17.62,
    "อุทัยธานี": 15.38, "อุบลราชธานี": 15.23,
}


SunriseMode = Literal["real_sunrise", "six_am"]

THAI_TZ_HOURS = 7.0


def _longitude_from_locality(province: str) -> float:
    """คืน longitude (degrees east) จาก LOCALITY_ADJUST_SECONDS
    locality_seconds = (105° − lon) × 240 sec/degree
    → lon = 105 − locality_sec / 240
    """
    sec = LOCALITY_ADJUST_SECONDS.get(province, LOCALITY_ADJUST_SECONDS["กรุงเทพมหานคร"])
    return 105.0 - sec / 240.0


def sunrise_hours_at(d: date, province: str = "กรุงเทพมหานคร") -> float:
    """พระอาทิตย์ขึ้น (ชั่วโมง Thai standard time, ทศนิยม)

    Args:
        d: วันที่ (สุริยคติสากล)
        province: ชื่อจังหวัดไทย

    Returns:
        ชั่วโมงในรูปทศนิยม เช่น 5.92 = 05:55 น.
    """
    latitude = LATITUDE_BY_PROVINCE.get(province, 13.75)  # default กทม.
    longitude = _longitude_from_locality(province)

    # Day of year (1-365/366)
    n = d.toordinal() - date(d.year, 1, 1).toordinal() + 1

    # Solar declination (degrees) — approximation
    decl_deg = 23.45 * math.sin(math.radians(360 * (284 + n) / 365))

    # Equation of Time (minutes)
    B = math.radians(360 * (n - 81) / 365)
    eot_min = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

    # Hour angle at sunrise (degrees)
    lat_r = math.radians(latitude)
    decl_r = math.radians(decl_deg)
    cos_h = -math.tan(lat_r) * math.tan(decl_r)
    cos_h = max(-1.0, min(1.0, cos_h))  # clamp (กันที่ขั้วโลก)
    h_deg = math.degrees(math.acos(cos_h))

    # Solar noon ในเวลา Thai standard
    solar_noon_local = 12.0 - longitude / 15.0 - eot_min / 60.0 + THAI_TZ_HOURS

    # Sunrise = solar noon - (h_deg / 15) hours
    return solar_noon_local - h_deg / 15.0


def thai_birth_day_adjust(
    birth_dt: datetime,
    province: str = "กรุงเทพมหานคร",
    mode: SunriseMode = "real_sunrise",
) -> tuple[date, float, float]:
    """ปรับวันเกิดให้สอดคล้องกับการนับวันแบบโหราศาสตร์ไทย

    Args:
        birth_dt: เวลาเกิดจริง (สุริยคติ + นาฬิกาตามจังหวัด)
        province: จังหวัดเกิด
        mode:
            - "real_sunrise": ใช้เวลาพระอาทิตย์ขึ้นจริงตาม (วัน, จังหวัด)
            - "six_am": ใช้ 06:00 น. (Thai standard) ตามตำราคลาสสิก

    Returns:
        (adjusted_date, sunrise_hours_used, hour_decimal_of_birth)
        - adjusted_date: วันสำหรับ build_desire (อาจเป็นวันก่อนหน้า)
        - sunrise_hours_used: ค่า sunrise ที่ใช้ตัดสิน
        - hour_decimal_of_birth: เวลาเกิดในรูป hours.fraction
    """
    if mode == "six_am":
        sunrise_h = 6.0
    else:
        sunrise_h = sunrise_hours_at(birth_dt.date(), province)

    hour_dec = birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
    if hour_dec < sunrise_h:
        adjusted = birth_dt.date() - timedelta(days=1)
    else:
        adjusted = birth_dt.date()
    return adjusted, sunrise_h, hour_dec


def format_sunrise(h: float) -> str:
    """3.916 → '03:55'  /  6.0 → '06:00'"""
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm == 60:
        hh += 1
        mm = 0
    return f"{hh:02d}:{mm:02d}"
