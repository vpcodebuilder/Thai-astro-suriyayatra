"""โมดูลคำนวณลัคนา (Lakkana / Ascendant) แบบสุริยยาตร์

Port จาก Devtino.Astrology/Somput/Lakkana.cs + Common/Antonati.cs

หลักการ:
1. สมมติพระอาทิตย์ขึ้นเวลา 06:00 น. (วิธีคลาสสิก SunriseType.SixAM)
2. หาเวลาที่ผ่านจากพระอาทิตย์ขึ้น (intervalTimeBorn)
3. ลบเวลาท้องถิ่น (Locality adjust) - กรุงเทพฯ = 18:01 (นาที:วินาที)
4. ใช้ "อันโตนาที" (Antonati) - เวลาที่ลัคนาเคลื่อนผ่านแต่ละราศี (ต่างกัน):
   เมษ:120, พฤษภ:96, เมถุน:72, กรกฎ:120, สิงห์:144, กันย์:168,
   ตุลย์:168, พิจิก:144, ธนู:120, มกร:72, กุมภ์:96, มีน:120 (นาที)
   รวม = 1440 นาที = 24 ชั่วโมง ✓
5. เริ่มจากตำแหน่งอาทิตย์ในราศี ลบเวลาในราศีจนหมด แล้วเดินราศีถัดไป
6. เมื่อหมดเวลา -> คำนวณเศษเป็นองศาในราศี
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .planets import (
    Planet, Zodiac, compact_angle,
    RASI_ARCMIN, ZODIAC_ARCMIN, compute_sun,
)
from .boonnak import Desire


# อันโตนาที (นาทีต่อราศี) - จาก Antonati.cs
ANTONATI_MINUTES: Dict[int, int] = {
    0: 120,    # เมษ (Aries)
    1: 96,     # พฤษภ (Taurus)
    2: 72,     # เมถุน (Gemini)
    3: 120,    # กรกฎ (Cancer)
    4: 144,    # สิงห์ (Leo)
    5: 168,    # กันย์ (Virgo)
    6: 168,    # ตุลย์ (Libra)
    7: 144,    # พิจิก (Scorpius)
    8: 120,    # ธนู (Sagittarius)
    9: 72,     # มกร (Capricorn)
    10: 96,    # กุมภ์ (Aquarius)
    11: 120,   # มีน (Pisces)
}

# ค่าปรับเวลาท้องถิ่นทุกจังหวัด (วินาที) - port จาก Thailand.cs
# คือผลต่างของลองจิจูดจังหวัด เทียบกับเส้นแวงเวลา UTC+7 (105°E) เป็นเวลา
def _ms(minutes: int, seconds: int) -> int:
    return minutes * 60 + seconds


LOCALITY_ADJUST_SECONDS: Dict[str, int] = {
    "กระบี่": _ms(24, 21),
    "กรุงเทพมหานคร": _ms(18, 1),
    "กาญจนบุรี": _ms(21, 49),
    "กาฬสินธุ์": _ms(5, 57),
    "กำแพงเพชร": _ms(21, 53),
    "ขอนแก่น": _ms(8, 41),
    "จันทบุรี": _ms(11, 33),
    "ฉะเชิงเทรา": _ms(15, 41),
    "ชลบุรี": _ms(16, 5),
    "ชัยนาท": _ms(19, 29),
    "ชัยภูมิ": _ms(11, 53),
    "ชุมพร": _ms(23, 17),
    "เชียงราย": _ms(20, 41),
    "เชียงใหม่": _ms(24, 1),
    "ตรัง": _ms(21, 33),
    "ตราด": _ms(9, 57),
    "ตาก": _ms(23, 29),
    "นครนายก": _ms(15, 9),
    "นครปฐม": _ms(19, 45),
    "นครพนม": _ms(0, 53),
    "นครราชสีมา": _ms(11, 37),
    "นครศรีธรรมราช": _ms(20, 39),
    "นครสวรรค์": _ms(19, 29),
    "นนทบุรี": _ms(18, 1),
    "นราธิวาส": _ms(12, 41),
    "น่าน": _ms(16, 53),
    "บึงกาฬ": _ms(9, 21),
    "บุรีรัมย์": _ms(7, 37),
    "ปทุมธานี": _ms(17, 53),
    "ประจวบคีรีขันธ์": _ms(20, 49),
    "ปราจีนบุรี": _ms(14, 33),
    "ปัตตานี": _ms(14, 57),
    "พระนครศรีอยุธยา": _ms(17, 41),
    "พะเยา": _ms(20, 41),
    "พังงา": _ms(25, 53),
    "พัทลุง": _ms(19, 41),
    "พิจิตร": _ms(18, 37),
    "พิษณุโลก": _ms(18, 57),
    "เพชรบุรี": _ms(20, 14),
    "เพชรบูรณ์": _ms(15, 26),
    "แพร่": _ms(19, 24),
    "ภูเก็ต": _ms(26, 28),
    "มหาสารคาม": _ms(6, 49),
    "มุกดาหาร": _ms(0, 53),
    "แม่ฮ่องสอน": _ms(28, 9),
    "ยโสธร": _ms(0, 32),
    "ยะลา": _ms(14, 53),
    "ร้อยเอ็ด": _ms(5, 25),
    "ระนอง": _ms(25, 30),
    "ระยอง": _ms(14, 53),
    "ราชบุรี": _ms(20, 41),
    "ลพบุรี": _ms(17, 25),
    "ลำปาง": _ms(21, 53),
    "ลำพูน": _ms(23, 57),
    "เลย": _ms(13, 5),
    "ศรีสะเกษ": _ms(2, 41),
    "สกลนคร": _ms(3, 25),
    "สงขลา": _ms(17, 37),
    "สตูล": _ms(19, 49),
    "สมุทรปราการ": _ms(17, 37),
    "สมุทรสงคราม": _ms(20, 1),
    "สมุทรสาคร": _ms(18, 53),
    "สระแก้ว": _ms(14, 53),
    "สระบุรี": _ms(16, 21),
    "สิงห์บุรี": _ms(18, 25),
    "สุโขทัย": _ms(20, 41),
    "สุพรรณบุรี": _ms(19, 33),
    "สุราษฎร์ธานี": _ms(22, 45),
    "สุรินทร์": _ms(6, 1),
    "หนองคาย": _ms(9, 1),
    "หนองบัวลำภู": _ms(8, 49),
    "อ่างทอง": _ms(16, 13),
    "อำนาจเจริญ": _ms(0, 32),
    "อุดรธานี": _ms(8, 49),
    "อุตรดิตถ์": _ms(19, 37),
    "อุทัยธานี": _ms(19, 53),
    "อุบลราชธานี": _ms(0, 33),
}
BANGKOK_LOCALITY_SECONDS = LOCALITY_ADJUST_SECONDS["กรุงเทพมหานคร"]  # = 1081


@dataclass
class Lakkana:
    """ลัคนา"""
    somput: int                  # arcminute
    zodiac: Zodiac
    sunrise_hours: float         # ชั่วโมงที่ใช้เป็นพระอาทิตย์ขึ้น
    locality_seconds: int        # ค่าปรับเวลาท้องถิ่น (วินาที)

    @property
    def rasi(self) -> int:
        return self.zodiac.rasi

    @property
    def degree_in_rasi(self) -> float:
        return self.somput % RASI_ARCMIN / 60.0

    @property
    def longitude(self) -> float:
        return self.somput / 60.0

    def format_dms(self) -> str:
        return self.zodiac.format()


def compute_lakkana(
    desire: Desire,
    sun: Planet,
    sunrise_hours: float = 6.0,
    locality_seconds: int = BANGKOK_LOCALITY_SECONDS,
) -> Lakkana:
    """คำนวณลัคนาตามวิธีสุริยยาตร์ (port จาก Lakkana.cs)

    อาร์กิวเมนต์:
        desire: Desire จาก build_desire()
        sun: ตำแหน่งอาทิตย์จาก compute_sun()
        sunrise_hours: เวลาพระอาทิตย์ขึ้น (default 6.0)
        locality_seconds: ค่าปรับเวลาท้องถิ่นเป็นวินาที (default = กรุงเทพฯ 1081)
    """
    # เวลาเกิดเป็นวินาที
    time_seconds = desire.time_hours * 3600.0
    sunrise_seconds = sunrise_hours * 3600.0

    interval = time_seconds - sunrise_seconds
    if interval < 0:
        interval += 24 * 3600.0
    interval -= locality_seconds

    # เริ่มจากราศีของอาทิตย์
    rasi_position = sun.zodiac.rasi
    sun_deg = sun.zodiac.degree
    sun_min = sun.zodiac.arcminute

    # นาทีที่เหลือในราศีของอาทิตย์ (เป็น arcminute)
    remain_arcmin_in_rasi = RASI_ARCMIN - (sun_deg * 60 + sun_min)

    # วินาทีต่อ arcminute สำหรับราศีปัจจุบัน
    anto_min = ANTONATI_MINUTES[rasi_position]
    anto_sec = anto_min * 60
    seconds_per_arcmin = anto_sec / RASI_ARCMIN

    # วินาทีที่เหลือในราศีของอาทิตย์
    remain_seconds = seconds_per_arcmin * remain_arcmin_in_rasi
    remaining = interval - remain_seconds

    if remaining <= 0:
        # ยังอยู่ในราศีของอาทิตย์
        remaining += remain_seconds
    else:
        # เดินผ่านราศีถัดไปเรื่อย ๆ
        while remaining > 0:
            rasi_position = (rasi_position + 1) % 12
            anto_min = ANTONATI_MINUTES[rasi_position]
            anto_sec = anto_min * 60
            remaining -= anto_sec
            if remaining <= 0:
                remaining += anto_sec
                break

    # คำนวณเศษ arcminute ในราศีปัจจุบัน
    anto_min = ANTONATI_MINUTES[rasi_position]
    anto_sec = anto_min * 60
    seconds_per_arcmin = anto_sec / RASI_ARCMIN

    rasi_remain_arcmin = remaining / seconds_per_arcmin
    somput = compact_angle(int(rasi_position * RASI_ARCMIN + rasi_remain_arcmin))

    return Lakkana(
        somput=somput,
        zodiac=Zodiac.from_arcminutes(somput),
        sunrise_hours=sunrise_hours,
        locality_seconds=locality_seconds,
    )
