"""27 นักษัตร (Nakshatra) + คุณภาพฤกษ์

นักษัตร = การแบ่งจักรราศี 360° ออกเป็น 27 ส่วน (13°20' ต่อนักษัตร = 800 arcmin)
แต่ละนักษัตรแบ่งเป็น 4 ปาทะ (3°20' = 200 arcmin)

ตำราโหราศาสตร์ไทยจัดกลุ่มนักษัตร 27 ดวงเป็น **9 ฤกษ์** กลุ่มละ 3:
    1. ทลิทโท         (ยากจน — อัปมงคล)        1, 10, 19
    2. มหัทธโน        (ทรัพย์ — มงคล ★)         2, 11, 20
    3. โจโร           (โจร — อัปมงคล)           3, 12, 21
    4. ภูมิปาโล        (ผู้ครองแผ่นดิน — มงคล ★) 4, 13, 22
    5. เทศาตรี        (เดินทาง — มงคล)          5, 14, 23
    6. เทวี           (เทพี — มงคล ★)            6, 15, 24
    7. เพชฌฆาต        (เพชฌฆาต — อัปมงคล)       7, 16, 25
    8. ราชา           (กษัตริย์ — มงคล ★)        8, 17, 26
    9. สมโณ           (สมณะ — มงคล/กลาง)        9, 18, 27

ตำราอ้างอิง:
    - อ.เทพย์ สาริกบุตร: ตำราโหราศาสตร์ภาคพยากรณ์
    - mahamongkol.com/m/content.php?id=491 — หลักการหาฤกษ์
"""
from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# ชื่อ 27 นักษัตร (index 0-26 → ลำดับที่ 1-27)
# ============================================================
NAKSHATRA_NAMES = [
    "อัศวินี", "ภรณี", "กฤติกา", "โรหิณี", "มฤคศิร",
    "อารทรา", "ปุนรวสุ", "ปุษยะ", "อาศเลษา",
    "มาฆะ", "ปุรพผลคุณี", "อุตรผลคุณี", "หัสตะ", "จิตรา",
    "สวาติ", "วิสาขะ", "อนุราธา", "เชษฐา",
    "มูละ", "ปุรพอาษาฒ", "อุตรอาษาฒ", "ศรวณะ", "ธนิษฐะ",
    "ศตภิษัช", "ปุรพภัทรบท", "อุตรภัทรบท", "เรวดี",
]


# ============================================================
# 9 ฤกษ์ (Roek group) — กลุ่มละ 3 นักษัตร
# (name, is_auspicious, meaning)
# ============================================================
ROEK_GROUPS = [
    ("ทลิทโทฤกษ์",   False, "ยากจน ขัดสน — ไม่เหมาะการเริ่มกิจมงคล"),
    ("มหัทธโนฤกษ์",  True,  "ทรัพย์มาก — เหมาะการลงทุน เปิดร้าน"),
    ("โจโรฤกษ์",     False, "โจร ลักทรัพย์ — เลี่ยงการมงคล"),
    ("ภูมิปาโลฤกษ์", True,  "ครองแผ่นดิน — เหมาะปลูกบ้าน ขึ้นบ้าน"),
    ("เทศาตรีฤกษ์",  True,  "เดินทางสะดวก — เหมาะออกเดินทาง"),
    ("เทวีฤกษ์",     True,  "เทพี เมตตา — เหมาะแต่งงาน หมั้น"),
    ("เพชฌฆาตฤกษ์",  False, "เพชฌฆาต — เลี่ยงการมงคลโดยเด็ดขาด"),
    ("ราชาฤกษ์",     True,  "ราชสมบัติ — เหมาะการรับตำแหน่ง สาบาน"),
    ("สมโณฤกษ์",     True,  "สมณะ สงบ — เหมาะการบวช ทำบุญ"),
]


# ============================================================
# ดาวเจ้านักษัตร (Lord) — ลำดับ Vimshottari (เริ่มที่เกตุ)
# 9 ดาว × 3 รอบ = 27
# ============================================================
NAKSHATRA_LORDS = [
    "เกตุ", "ศุกร์", "อาทิตย์",         # 1-3
    "จันทร์", "อังคาร", "ราหู",          # 4-6
    "พฤหัสบดี", "เสาร์", "พุธ",          # 7-9
    "เกตุ", "ศุกร์", "อาทิตย์",         # 10-12
    "จันทร์", "อังคาร", "ราหู",          # 13-15
    "พฤหัสบดี", "เสาร์", "พุธ",          # 16-18
    "เกตุ", "ศุกร์", "อาทิตย์",         # 19-21
    "จันทร์", "อังคาร", "ราหู",          # 22-24
    "พฤหัสบดี", "เสาร์", "พุธ",          # 25-27
]


ARCMIN_PER_NAKSHATRA = 800   # 13°20'
ARCMIN_PER_PADA = 200        # 3°20'
TOTAL_ARCMIN = 21600         # 360°


@dataclass(frozen=True)
class NakshatraPosition:
    """ตำแหน่งนักษัตรของจันทร์ (หรือดาวอื่น)"""
    index: int              # 0-26
    number: int             # 1-27 (= index + 1)
    name: str               # ชื่อนักษัตร
    pada: int               # 1-4
    lord: str               # ดาวเจ้านักษัตร
    roek_group_index: int   # 0-8 (= index % 9)
    roek_name: str          # ชื่อ 9 ฤกษ์
    is_auspicious: bool     # มงคล/อัปมงคล
    meaning: str            # ความหมายของฤกษ์
    arcmin_within: int      # arcmin ภายในนักษัตร (0-799)

    @property
    def degrees_within(self) -> float:
        return self.arcmin_within / 60.0


def compute_from_moon_position(moon_arcmin: int) -> NakshatraPosition:
    """คำนวณนักษัตรจากตำแหน่งจันทร์ใน arcmin (0-21599)

    moon_arcmin = chart.planets["จันทร์"].arcminute_position
    หรือ rasi*1800 + degree*60 + arcmin
    """
    m = moon_arcmin % TOTAL_ARCMIN
    idx = m // ARCMIN_PER_NAKSHATRA
    within = m - idx * ARCMIN_PER_NAKSHATRA
    pada = (within // ARCMIN_PER_PADA) + 1

    roek_idx = idx % 9
    roek_name, auspicious, meaning = ROEK_GROUPS[roek_idx]

    return NakshatraPosition(
        index=idx,
        number=idx + 1,
        name=NAKSHATRA_NAMES[idx],
        pada=pada,
        lord=NAKSHATRA_LORDS[idx],
        roek_group_index=roek_idx,
        roek_name=roek_name,
        is_auspicious=auspicious,
        meaning=meaning,
        arcmin_within=within,
    )


def compute_from_rasi_degree(rasi: int, degree: int, arcmin: int = 0) -> NakshatraPosition:
    """convenience wrapper จาก (rasi, degree, arcmin)"""
    total = rasi * 1800 + degree * 60 + arcmin
    return compute_from_moon_position(total)
