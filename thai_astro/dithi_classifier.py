"""ดิถีจำแนกประเภทตามตำราโหรไทย

จัดประเภทดิถี (วันทางจันทรคติ ขึ้น/แรม X ค่ำ) ตาม **วาร** (วันในสัปดาห์)
แบ่งเป็น:
    1. ดิถีมงคล 5 ประการ — อมฤตโชค / มหาสิทธิโชค / สิทธิโชค / ชัยโชค / ราชาโชค
    2. ดิถีร้าย — อัคนิโรธ / มหาสูญ
    3. ดิถีพรหมประสิทธิ์ — สากล (ไม่ขึ้นกับวาร)

ตารางหลักใช้ pattern ของ "เลื่อนเลขดิถีตามวาร" — แต่ละวารดิถีจะเลื่อน 1 ตำแหน่ง
ในตำราโบราณ (พรหมชาติ/อ.เทพย์ สาริกบุตร)

หมายเหตุ:
    - ตำรามีหลายเวอร์ชัน — ตารางนี้ใช้ pattern ที่พบบ่อยที่สุด
    - day_in_phase (1-15) ใช้เหมือนกันทั้งข้างขึ้นและข้างแรม
      (เช่น "ขึ้น 5 ค่ำ" และ "แรม 5 ค่ำ" ถือเป็นดิถี 5 เหมือนกัน)
    - แต่ละจุดเวลา อาจเข้าได้หลายดิถี (เช่น ทั้งอมฤตโชค + เพิ่มเงื่อนไขมงคลอื่น)

อ้างอิง:
    - palungjit.org/ฤกษ์อมฤตโชคตามตำราฤกษ์พรหมประสิทธิ์
    - mahamodo.com/tamnai/good_time_other_isan.aspx
    - astroneemo.net (ตำราดิถีร้าย)
    - theluckyname.com/ดิถีอัคนิโรธ
    - 10luc.com (ดิถีมงคล 5 ประการ)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


# ============================================================
# ตารางวาร × ดิถี
# Index: WAN 1-7 (1=อาทิตย์, 2=จันทร์, ..., 7=เสาร์)
# Values: list of day_in_phase (1-15)
# ============================================================

# ดิถีอมฤตโชค — มงคลที่สุด ดีทุกการ ความราบรื่นและสบาย
DITHI_AMRITACHOK = {
    1: [5, 12],     # อาทิตย์
    2: [6, 13],     # จันทร์
    3: [7, 14],     # อังคาร
    4: [1, 8],      # พุธ
    5: [2, 9],      # พฤหัสบดี
    6: [3, 10],     # ศุกร์
    7: [4, 11],     # เสาร์
}

# ดิถีมหาสิทธิโชค — สำเร็จยิ่งใหญ่ ดีรองอมฤตโชค (โครงการระยะสั้น)
DITHI_MAHA_SIDDHICHOK = {
    1: [4, 11],
    2: [5, 12],
    3: [6, 13],
    4: [7, 14],
    5: [1, 8],
    6: [2, 9],
    7: [3, 10],
}

# ดิถีสิทธิโชค — สำเร็จสมปรารถนา (โครงการระยะยาว)
DITHI_SIDDHICHOK = {
    1: [3, 10],
    2: [4, 11],
    3: [5, 12],
    4: [6, 13],
    5: [7, 14],
    6: [1, 8],
    7: [2, 9],
}

# ดิถีชัยโชค — ชัยชนะ
DITHI_CHAICHOK = {
    1: [6, 13],
    2: [7, 14],
    3: [1, 8],
    4: [2, 9],
    5: [3, 10],
    6: [4, 11],
    7: [5, 12],
}

# ดิถีราชาโชค — โชคจากผู้ใหญ่/ราชสมบัติ
DITHI_RACHACHOK = {
    1: [1, 8],
    2: [2, 9],
    3: [3, 10],
    4: [4, 11],
    5: [5, 12],
    6: [6, 13],
    7: [7, 14],
}


# ============================================================
# ดิถีร้าย
# ============================================================

# ดิถีอัคนิโรธ — วันที่เหมือนอยู่ในกองไฟ ห้ามมงคล
# Pattern: วารคี่ → 12 ลด, วารคู่ → 6 ขึ้น
# อาทิตย์(1)=12, จันทร์(2)=11, อังคาร(3)=10, พุธ(4)=9, พฤหัส(5)=8, ศุกร์(6)=7, เสาร์(7)=6
DITHI_AKKHANIROT = {
    1: [12],
    2: [11],
    3: [10],
    4: [9],
    5: [8],
    6: [7],
    7: [6],
}

# ดิถีมหาสูญ — วันสูญเสีย ห้ามมงคลเด็ดขาด
# ตามตำราหลายเล่ม — pattern วาร × ดิถี
DITHI_MAHASOON = {
    1: [6, 12],
    2: [4, 11],
    3: [5, 13],
    4: [6, 14],
    5: [8, 15],
    6: [5, 11],
    7: [4, 12],
}

# ดิถีพิฆาต — วันห้ามมงคล อีกตำราหนึ่ง (mahamongkol)
# pattern: เลื่อน 1 ตำแหน่งต่อวาร เริ่มที่ ขึ้น/แรม 12 ของวันอาทิตย์
DITHI_PHIKHAT = {
    1: [12],
    2: [11],
    3: [10],
    4: [9],
    5: [8],
    6: [7],
    7: [6],
}

# ดิถีทรธึก — วันอันตราย ห้ามมงคลเด็ดขาด
# ตำรามาตรฐาน วาร × ค่ำ
DITHI_TARATHUK = {
    1: [10, 13],
    2: [11, 14],
    3: [12, 15],
    4: [1, 13],
    5: [2, 14],
    6: [3, 15],
    7: [4, 11],
}

# ดิถีอายกรรมพลาย (ภาณฤกษ์/ดาวกำพลาย) — วันที่ผีปีศาจมีกำลังแรง
# ตามตำรา: ขึ้น 13 ค่ำ และ แรม 13 ค่ำ (universal — ไม่ขึ้นกับวาร)
DITHI_AAYAKAMPHLAY = {13}    # day_in_phase 13 (both waxing/waning)

# ดิถีเรียงหมอน — สำหรับ "แต่งงาน" (wedding) เท่านั้น
DITHI_RIANG_MON_WAXING = {7, 10, 13}    # ขึ้น 7, 10, 13 ค่ำ
DITHI_RIANG_MON_WANING = {4, 8, 10, 14}  # แรม 4, 8, 10, 14 ค่ำ

# วันห้ามเฉพาะดิถี (phase day taboo) — phrase "สงฆ์ 14 นารี 11 แต่งงาน 7 เผาศพ 15"
# - day_in_phase 14 → ห้ามบวช
# - day_in_phase 11 (ขึ้น) → ห้ามงานสตรี
# - day_in_phase 7  → ห้ามแต่งงาน
# - day_in_phase 15 (ขึ้น) → ห้ามเผาศพ

# วันห้ามเฉพาะวาร (wan taboo)
WAN_TABOO = {
    # wan 7 (เสาร์) → ห้ามขึ้นบ้านใหม่
    7: {"category": "home", "label": "ขึ้นบ้านใหม่"},
    # wan 4 (พุธ) → ห้ามแต่งงาน
    4: {"category": "wedding", "label": "แต่งงาน"},
    # wan 3 (อังคาร) → ห้ามโกนจุก
    3: {"category": "first_haircut", "label": "โกนจุก/โกนผมไฟ"},
}

# ดิถีพรหมประสิทธิ์ — ทำการใดสำเร็จง่าย (สากล)
# ขึ้น 8 ค่ำ และ แรม 14 ค่ำ ตามที่พบบ่อย
# day_in_phase=8 (ทั้งข้างขึ้น) และ day_in_phase=14 (ข้างแรม)
DITHI_PHROM_PRASIT_WAXING = {8}      # เฉพาะข้างขึ้น 8 ค่ำ
DITHI_PHROM_PRASIT_WANING = {14}     # เฉพาะข้างแรม 14 ค่ำ


# ============================================================
# Result class
# ============================================================
@dataclass(frozen=True)
class DithiClassification:
    """1 ประเภทดิถีที่ตรง"""
    name: str               # ชื่อ เช่น "ดิถีอมฤตโชค"
    is_auspicious: bool     # True = มงคล, False = ร้าย
    short_desc: str         # คำอธิบายสั้น
    long_desc: str          # คำอธิบายยาวสำหรับคนทั่วไป
    severity: int           # 1-3 (ความสำคัญ — มงคล: 3=สูงสุด, ร้าย: 3=ร้ายแรงที่สุด)
    # หมวดกิจกรรมที่เกี่ยวข้อง (ตรงกับ EVENT_CATEGORIES ใน muhurta_criteria)
    # ค่าพิเศษ:
    #   ()           — neutral (ดิถีปกติ)
    #   ("universal",) — เหมาะกับทุกกิจกรรม
    #   tuple ของ category keys — เหมาะเฉพาะหมวดที่ระบุ
    relevant_categories: tuple = ()
    # event keys เฉพาะ (override categories — สำหรับ taboo ที่เจาะจง)
    # เช่น "ห้ามขึ้นบ้านใหม่วันเสาร์" → ("housewarming", "move_house") เท่านั้น
    # ไม่ใช่ทั้ง home category
    relevant_events: tuple = ()
    # ถ้า True → กรองออกเลยถ้า event ไม่อยู่ใน relevant_events
    # (สำหรับดิถีที่เฉพาะกิจกรรมเฉพาะอย่างเช่น เรียงหมอน, สงฆ์ 14, ห้ามวันเสาร์_บ้าน)
    # ถ้า False → แสดงเป็น "ดิถีอื่นในวันเดียวกัน" (informational)
    strict_event_only: bool = False
    suitable_for: str = ""    # คำอธิบายว่าเหมาะกับอะไร (สำหรับ UI)


# ============================================================
# Definitions
# ============================================================
DITHI_INFO = {
    "อมฤตโชค": DithiClassification(
        name="ดิถีอมฤตโชค",
        is_auspicious=True, severity=3,
        short_desc="วันมงคลสูงสุด — ทำการใดสำเร็จราบรื่น",
        long_desc=(
            "ดิถีมงคลที่ดีที่สุดในตำราโหรไทย เปรียบเสมือน \"น้ำอมฤต\" "
            "ที่ทำให้ทุกสิ่งสำเร็จลุล่วงด้วยดี เหมาะแก่งานมงคลทั่วไป "
            "เช่น แต่งงาน ขึ้นบ้านใหม่ เปิดกิจการ — ใช้ได้ทั้งข้างขึ้นและข้างแรม"
        ),
        relevant_categories=("universal",),
        suitable_for="เหมาะกับทุกกิจกรรมมงคล",
    ),
    "มหาสิทธิโชค": DithiClassification(
        name="ดิถีมหาสิทธิโชค",
        is_auspicious=True, severity=3,
        short_desc="วันสำเร็จยิ่งใหญ่ — เหมาะธุรกิจ/โครงการระยะสั้น",
        long_desc=(
            "ดิถีให้ความสำเร็จอันยิ่งใหญ่ เหมาะแก่งานสำคัญที่เป็นโครงการ"
            "ระยะสั้น เช่น เปิดร้าน เปิดตัวสินค้า เซ็นสัญญา ลงทุน "
            "ดีรองจากอมฤตโชค ใช้ได้ทั้งข้างขึ้นและข้างแรม"
        ),
        relevant_categories=("business", "ceremony"),
        suitable_for="เหมาะกับธุรกิจ/โครงการระยะสั้น/พิธีมงคล",
    ),
    "สิทธิโชค": DithiClassification(
        name="ดิถีสิทธิโชค",
        is_auspicious=True, severity=2,
        short_desc="วันสำเร็จสมปรารถนา — เหมาะงานระยะยาว",
        long_desc=(
            "ดิถีให้ความสำเร็จสมปรารถนา เหมาะแก่งานที่เป็นโครงการระยะยาว "
            "เช่น ขึ้นบ้านใหม่ ลงทุน ก่อตั้งธุรกิจ ปลูกบ้าน "
            "ใช้ได้ทั้งข้างขึ้นและข้างแรม"
        ),
        relevant_categories=("home", "business", "ceremony"),
        suitable_for="เหมาะกับบ้าน/ธุรกิจระยะยาว/พิธีมงคล",
    ),
    "ชัยโชค": DithiClassification(
        name="ดิถีชัยโชค",
        is_auspicious=True, severity=2,
        short_desc="วันชัยชนะ — เหมาะการแข่งขัน สอบ สมัครงาน",
        long_desc=(
            "ดิถีแห่งชัยชนะ เหมาะกับกิจการที่ต้องเอาชนะ เช่น "
            "การแข่งขัน สมัครงาน สอบ เลือกตั้ง หรืองานที่ต้องการชนะคู่แข่ง "
            "ไม่เหมาะกับงานสงบหรืองานครอบครัว"
        ),
        relevant_categories=("business", "study"),
        suitable_for="เหมาะกับการแข่งขัน/สอบ/สมัครงาน",
    ),
    "ราชาโชค": DithiClassification(
        name="ดิถีราชาโชค",
        is_auspicious=True, severity=2,
        short_desc="วันโชคจากผู้ใหญ่ — เหมาะตำแหน่ง พบผู้ใหญ่",
        long_desc=(
            "ดิถีแห่งโชคจากผู้ใหญ่/ผู้มีอำนาจ เหมาะการรับตำแหน่ง สมัครงาน "
            "เข้าเฝ้าผู้ใหญ่ ขอความช่วยเหลือจากบุคคลสำคัญ "
            "เปิดสำนักงาน/บริษัทที่ต้องการการสนับสนุนจากผู้ใหญ่"
        ),
        relevant_categories=("business", "ceremony"),
        suitable_for="เหมาะกับตำแหน่ง/สมัครงาน/เปิดสำนักงาน",
    ),
    "พรหมประสิทธิ์": DithiClassification(
        name="ดิถีพรหมประสิทธิ์",
        is_auspicious=True, severity=3,
        short_desc="วันพรหมประทาน — ทำการใดสำเร็จง่าย",
        long_desc=(
            "ดิถีแห่งการได้รับพรจากสิ่งศักดิ์สิทธิ์ ทำสิ่งใดจะสำเร็จง่าย "
            "เหมาะการมงคลทุกประเภท โดยเฉพาะการบวช ทำบุญ พิธีกรรมศาสนา "
            "(ใช้กับ ขึ้น 8 ค่ำ และ แรม 14 ค่ำ ทั้งหมด ไม่ขึ้นกับวาร)"
        ),
        relevant_categories=("universal",),
        suitable_for="เหมาะกับทุกกิจกรรม (โดยเฉพาะศาสนา/พิธี)",
    ),
    "อัคนิโรธ": DithiClassification(
        name="ดิถีอัคนิโรธ",
        is_auspicious=False, severity=3,
        short_desc="วันร้าย — เหมือนอยู่ในกองไฟ ห้ามมงคล",
        long_desc=(
            "ดิถีที่เปรียบเสมือนอยู่ในกองไฟ มีอุปสรรคและอันตราย "
            "ห้ามทำการมงคลในวันนี้เด็ดขาด แม้ฤกษ์อื่นจะดีก็ตาม "
            "เพราะจะทำให้เกิดความเดือดร้อน เร่าร้อน วุ่นวาย"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลทุกประเภท",
    ),
    "มหาสูญ": DithiClassification(
        name="ดิถีมหาสูญ",
        is_auspicious=False, severity=3,
        short_desc="วันสูญเสีย — ห้ามมงคลเด็ดขาด",
        long_desc=(
            "ดิถีแห่งความสูญเสีย เป็นวันที่ห้ามทำการมงคลโดยเด็ดขาด "
            "ไม่ว่าฤกษ์อื่นจะดีเพียงใด เพราะจะทำให้สิ่งที่เริ่มต้น "
            "สูญเสีย ขาดทุน หรือล้มเหลว"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลทุกประเภท",
    ),
    "ปกติ": DithiClassification(
        name="ดิถีปกติ",
        is_auspicious=True, severity=0,    # neutral — ไม่นับคะแนน
        short_desc="วันปกติ — ไม่ตรงดิถีพิเศษ แต่ยังใช้ได้",
        long_desc=(
            "วันนี้ไม่ตรงกับดิถีมงคลที่มีชื่อเฉพาะในตำรา "
            "(เช่น อมฤตโชค สิทธิโชค) และก็ไม่ตรงดิถีร้าย "
            "ถือเป็น \"วันธรรมดา\" ที่ยังคงใช้งานได้ตามปัจจัยอื่น "
            "เช่น วาร นักษัตร กาลโยค หรือเกณฑ์พิเศษ"
        ),
        relevant_categories=(),
        suitable_for="วันธรรมดา ใช้งานทั่วไปได้",
    ),
    # === ดิถีร้ายเพิ่มจาก mahamongkol ===
    "พิฆาต": DithiClassification(
        name="ดิถีพิฆาต",
        is_auspicious=False, severity=2,
        short_desc="วันอัปมงคล — ห้ามมงคล",
        long_desc=(
            "ดิถีพิฆาต เป็นวันห้ามทำการมงคลตามตำราโบราณอีกตำราหนึ่ง "
            "เป็นวันอัปมงคล แม้ตรงกับดิถีดีอื่นก็ตาม จะทำให้กิจการเริ่มต้น"
            "ติดขัด ไม่ราบรื่น"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลทุกประเภท",
    ),
    "ทรธึก": DithiClassification(
        name="ดิถีทรธึก",
        is_auspicious=False, severity=3,
        short_desc="วันอันตราย — ห้ามมงคลเด็ดขาด",
        long_desc=(
            "ดิถีทรธึก เป็นวันอันตราย ห้ามทำการมงคลโดยเด็ดขาด "
            "แม้ตรงกับดิถีดีอื่นก็ตาม โบราณถือว่าเป็นวันที่ทำให้เกิด"
            "ความเสียหาย ความสูญเสีย และอันตรายต่อชีวิตได้"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลทุกประเภท",
    ),
    "อายกรรมพลาย": DithiClassification(
        name="ดิถีอายกรรมพลาย",
        is_auspicious=False, severity=2,
        short_desc="วันภาณฤกษ์ — ภูตผีมีกำลังแรง ห้ามมงคล",
        long_desc=(
            "ดิถีอายกรรมพลาย หรือ \"วันภาณฤกษ์/วันดาวกำพลาย/วันภาน\" "
            "เป็นวันที่ภูตผีปีศาจ (พลาย) มีกำลังแรง โบราณถือว่าเป็นวัน"
            "ห้ามทำการมงคล เนื่องจากจะทำให้ผีร้ายเข้าแทรกแซง "
            "(ตรงกับ ขึ้น 13 ค่ำ และ แรม 13 ค่ำ ทุกเดือน)"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลทุกประเภท",
    ),
    "กทิงวันแท้": DithiClassification(
        name="กทิงวันแท้",
        is_auspicious=False, severity=3,
        short_desc="วันแรงสูงสุด — วาร + ดิถี + เดือน ตรงกัน 3 ส่วน",
        long_desc=(
            "กทิงวันแท้ (ระดับสูงสุด) คือวันที่เลขของ \"วาร-ดิถี-เดือน\" "
            "ตรงกันครบทั้ง 3 ส่วน เช่น วันอาทิตย์ ขึ้น 1 ค่ำ เดือน 1 (อ้าย), "
            "วันอังคาร ขึ้น 3 ค่ำ เดือน 3, วันพฤหัส ขึ้น 12 ค่ำ เดือน 12 "
            "เป็นวันที่พลังจักรวาลขัดแย้งและแตกหัก ห้ามใช้กับงานมงคลเด็ดขาด "
            "แม้ฤกษ์อื่นจะดีก็ตาม — เหมาะเฉพาะพิธีปลุกเสก/คาถาอาคม"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลเด็ดขาด (เหมาะเฉพาะปลุกเสก/อาคม)",
    ),
    "กทิงวันไม่เต็ม": DithiClassification(
        name="กทิงวันไม่เต็ม",
        is_auspicious=False, severity=2,
        short_desc="วันแรงปานกลาง — ตรงเพียง 2 ใน 3 ส่วน",
        long_desc=(
            "กทิงวันไม่เต็มรูปแบบ คือมีคู่เลขตรงกัน 2 ส่วน เช่น "
            "\"วัน-ดิถี\" (วันอาทิตย์ ขึ้น 1 ค่ำ — แต่เดือนไม่ตรง) "
            "หรือ \"ดิถี-เดือน\" (ขึ้น 5 ค่ำ เดือน 5 — แต่ไม่ใช่วันพฤหัส) "
            "ระดับความแรงเบากว่ากทิงวันแท้ แต่ยังคงห้ามมงคลตามตำราโบราณ"
        ),
        relevant_categories=("universal_bad",),
        suitable_for="ห้ามมงคลทั่วไป",
    ),
    # === ดิถีมงคล เฉพาะกิจกรรม ===
    "เรียงหมอน": DithiClassification(
        name="ดิถีเรียงหมอน",
        is_auspicious=True, severity=3,
        short_desc="วันเฉพาะแต่งงาน — ดิถีแมลงปอ",
        long_desc=(
            "ดิถีเรียงหมอน (หรือดิถีแมลงปอ) เป็นดิถีเฉพาะสำหรับ"
            "ฤกษ์แต่งงาน คนโบราณถือว่าหากหาฤกษ์ได้ดีแล้ว แต่ไม่ตรง"
            "กับดิถีเรียงหมอน จะต้องเลื่อนวันส่งตัวเจ้าสาวออกไป "
            "(ขึ้น 7, 10, 13 ค่ำ หรือ แรม 4, 8, 10, 14 ค่ำ)"
        ),
        relevant_events=("wedding", "engagement_ask", "wedding_registration"),
        strict_event_only=True,    # filter ออกถ้าไม่ใช่งานแต่งงาน
        suitable_for="เหมาะกับแต่งงาน/หมั้นโดยเฉพาะ",
    ),
    # === วันห้ามเฉพาะดิถี (universal phase taboo) ===
    "สงฆ์14": DithiClassification(
        name="ห้ามบวช (สงฆ์ 14)",
        is_auspicious=False, severity=2,
        short_desc="ห้ามบวช — ขึ้น/แรม 14 ค่ำ",
        long_desc=(
            "ตามตำราโบราณ ขึ้น 14 ค่ำ หรือ แรม 14 ค่ำ "
            "เป็นวันห้ามบวชนาค/บวชชี/อุปสมบท เพราะถือว่าเป็นวันคับขัน "
            "ใกล้วันพระใหญ่ ไม่เหมาะการเริ่มต้นชีวิตสมณะ"
        ),
        relevant_events=("ordination",),
        strict_event_only=True,
        suitable_for="ห้ามบวช",
    ),
    "นารี11": DithiClassification(
        name="ห้ามงานสตรี (นารี 11)",
        is_auspicious=False, severity=2,
        short_desc="ห้ามงานเกี่ยวสตรี — ขึ้น 11 ค่ำ",
        long_desc=(
            "ตามตำราโบราณ ขึ้น 11 ค่ำ ห้ามทำกิจการเกี่ยวกับสตรี "
            "เช่น สู่ขอ หมั้น แต่งงาน รับขวัญ "
            "ถือเป็นวันไม่เหมาะกับงานครอบครัวที่มีสตรีเป็นเจ้างาน"
        ),
        relevant_events=("wedding", "engagement_ask", "wedding_registration", "baby_naming"),
        strict_event_only=True,
        suitable_for="ห้ามแต่งงาน/หมั้น/สู่ขอ/รับขวัญ",
    ),
    "แต่งงาน7": DithiClassification(
        name="ห้ามแต่งงาน (7 ค่ำ)",
        is_auspicious=False, severity=2,
        short_desc="ห้ามแต่งงาน — ขึ้น/แรม 7 ค่ำ",
        long_desc=(
            "ตามตำราโบราณ ขึ้น 7 ค่ำ หรือ แรม 7 ค่ำ เป็นวันห้ามแต่งงาน "
            "หากแต่งในวันนี้ คู่ครองจะมีปัญหากันบ่อย"
        ),
        relevant_events=("wedding", "engagement_ask", "wedding_registration"),
        strict_event_only=True,
        suitable_for="ห้ามแต่งงาน",
    ),
    # === วันห้ามเฉพาะวาร (wan taboo) — เจาะจง event เฉพาะ ===
    "ห้ามวันเสาร์_บ้าน": DithiClassification(
        name="ห้ามขึ้นบ้านใหม่วันเสาร์",
        is_auspicious=False, severity=2,
        short_desc="วันเสาร์ห้ามขึ้นบ้านใหม่",
        long_desc=(
            "ตามตำราโบราณ ห้ามขึ้นบ้านใหม่ในวันเสาร์ เพราะเสาร์เป็น"
            "ดาวบาปเคราะห์ ทำให้บ้านมีบรรยากาศหนัก ผู้อยู่อาศัยจะมี"
            "เรื่องทุกข์ใจ ปัญหาในครอบครัวบ่อย"
        ),
        relevant_events=("housewarming", "move_house"),
        strict_event_only=True,
        suitable_for="ห้ามขึ้นบ้านใหม่/ย้ายเข้า",
    ),
    "ห้ามวันพุธ_แต่งงาน": DithiClassification(
        name="ห้ามแต่งงานวันพุธ",
        is_auspicious=False, severity=2,
        short_desc="วันพุธห้ามแต่งงาน",
        long_desc=(
            "ตามตำราโบราณ ห้ามแต่งงานในวันพุธ เพราะพุธเป็นดาวพูดมาก "
            "คู่ครองจะมีปากเสียงกัน เถียงกัน ไม่ลงรอย"
        ),
        relevant_events=("wedding", "engagement_ask", "wedding_registration"),
        strict_event_only=True,
        suitable_for="ห้ามแต่งงาน/หมั้น/จดทะเบียน",
    ),
    "ห้ามวันอังคาร_โกนจุก": DithiClassification(
        name="ห้ามโกนจุกวันอังคาร",
        is_auspicious=False, severity=2,
        short_desc="วันอังคารห้ามโกนจุก/โกนผมไฟ",
        long_desc=(
            "ตามตำราโบราณ ห้ามโกนจุก/โกนผมไฟในวันอังคาร เพราะ"
            "อังคารเป็นดาวรุนแรง เด็กจะมีนิสัยฉุนเฉียว ดุร้าย"
        ),
        relevant_events=("first_haircut",),
        strict_event_only=True,
        suitable_for="ห้ามโกนจุก/โกนผมไฟ",
    ),
}


def is_relevant_for(
    dithi: DithiClassification,
    event_category: str,
    event_key: Optional[str] = None,
) -> bool:
    """ดิถีนี้เหมาะกับ event ที่ผู้ใช้เลือกไหม
    ตรวจ relevant_events (เจาะจง) ก่อน — ถ้าไม่ระบุ จะใช้ relevant_categories
    """
    # ตรวจ event_key เฉพาะก่อน
    if dithi.relevant_events and event_key:
        return event_key in dithi.relevant_events
    if dithi.relevant_events and not event_key:
        return False  # มี events เฉพาะแต่ไม่รู้ event ที่เลือก
    # fallback ไป categories
    cats = dithi.relevant_categories
    if not cats:
        return False
    if "universal" in cats or "universal_bad" in cats:
        return True
    return event_category in cats


def should_show_for_event(
    dithi: DithiClassification,
    event_category: Optional[str],
    event_key: Optional[str],
) -> bool:
    """ตัดสินว่าจะ "แสดง" ดิถีนี้ใน hit ของ event ที่เลือกหรือไม่
    - universal good/bad → แสดงเสมอ
    - neutral (ดิถีปกติ) → แสดงเสมอ (fallback)
    - strict_event_only=True → แสดงเฉพาะถ้า event ตรง
    - มี categories/events (non-strict) → แสดงเสมอ (เป็น informational)
    """
    cats = dithi.relevant_categories
    if "universal" in cats or "universal_bad" in cats:
        return True
    if dithi.severity == 0:    # ดิถีปกติ
        return True
    if dithi.strict_event_only:
        if not event_key and not event_category:
            return False
        return is_relevant_for(dithi, event_category or "", event_key=event_key)
    # informational dithi (non-strict) → show always
    return True


# ============================================================
# Public API
# ============================================================
def classify_dithi(
    wan: int, day_in_phase: int, is_waxing: bool,
    lunar_month: Optional[int] = None,
) -> List[DithiClassification]:
    """จำแนกดิถีจาก (วาร, ดิถี ขึ้น/แรม X ค่ำ)

    Args:
        wan: 1-7 (1=อาทิตย์, ..., 7=เสาร์)
        day_in_phase: 1-15 (เลขค่ำ)
        is_waxing: True=ขึ้น, False=แรม
        lunar_month: 1-12 (สำหรับตรวจกระทิงวัน — optional)

    Returns:
        list ของ DithiClassification ที่ตรงกับ moment นี้ (อาจมีหลาย)
    """
    matches: List[DithiClassification] = []

    # ดิถีมงคล 5 ประการ
    if day_in_phase in DITHI_AMRITACHOK.get(wan, []):
        matches.append(DITHI_INFO["อมฤตโชค"])
    if day_in_phase in DITHI_MAHA_SIDDHICHOK.get(wan, []):
        matches.append(DITHI_INFO["มหาสิทธิโชค"])
    if day_in_phase in DITHI_SIDDHICHOK.get(wan, []):
        matches.append(DITHI_INFO["สิทธิโชค"])
    if day_in_phase in DITHI_CHAICHOK.get(wan, []):
        matches.append(DITHI_INFO["ชัยโชค"])
    if day_in_phase in DITHI_RACHACHOK.get(wan, []):
        matches.append(DITHI_INFO["ราชาโชค"])

    # ดิถีพรหมประสิทธิ์ (ไม่ขึ้นกับวาร)
    if is_waxing and day_in_phase in DITHI_PHROM_PRASIT_WAXING:
        matches.append(DITHI_INFO["พรหมประสิทธิ์"])
    elif (not is_waxing) and day_in_phase in DITHI_PHROM_PRASIT_WANING:
        matches.append(DITHI_INFO["พรหมประสิทธิ์"])

    # ดิถีเรียงหมอน — แต่งงาน
    if is_waxing and day_in_phase in DITHI_RIANG_MON_WAXING:
        matches.append(DITHI_INFO["เรียงหมอน"])
    elif (not is_waxing) and day_in_phase in DITHI_RIANG_MON_WANING:
        matches.append(DITHI_INFO["เรียงหมอน"])

    # ดิถีร้าย
    if day_in_phase in DITHI_AKKHANIROT.get(wan, []):
        matches.append(DITHI_INFO["อัคนิโรธ"])
    if day_in_phase in DITHI_MAHASOON.get(wan, []):
        matches.append(DITHI_INFO["มหาสูญ"])
    if day_in_phase in DITHI_PHIKHAT.get(wan, []):
        matches.append(DITHI_INFO["พิฆาต"])
    if day_in_phase in DITHI_TARATHUK.get(wan, []):
        matches.append(DITHI_INFO["ทรธึก"])
    if day_in_phase in DITHI_AAYAKAMPHLAY:
        matches.append(DITHI_INFO["อายกรรมพลาย"])

    # กทิงวัน (กระทิงวัน) — ตาม mahamongkol:
    #   pattern: วัน-ดิถี-เดือน ตรงกันตามตาราง
    #   day_in_phase 1-7 → wan ตรงกับ day_in_phase
    #   day_in_phase 8-12 → wan = ((day-1) mod 7) + 1
    #     (8→อา, 9→จ, 10→อ, 11→พ, 12→พฤ)
    #   เดือน = day_in_phase (1-12)
    #   day 13-15 ไม่เข้ากทิงวัน (เพราะเดือนมีแค่ 1-12)
    #
    # กทิงวันแท้  = ทั้ง 3 ส่วน (วาร+ดิถี+เดือน) ตรงกันครบ → severity 3
    # กทิงวันไม่เต็ม = ตรงแค่ 2 ส่วน (วาร-ดิถี หรือ ดิถี-เดือน) → severity 2
    if 1 <= day_in_phase <= 12:
        expected_wan = ((day_in_phase - 1) % 7) + 1
        wan_dithi_match = (wan == expected_wan)
        dithi_month_match = (lunar_month is not None and lunar_month == day_in_phase)
        if wan_dithi_match and dithi_month_match:
            matches.append(DITHI_INFO["กทิงวันแท้"])
        elif wan_dithi_match or dithi_month_match:
            matches.append(DITHI_INFO["กทิงวันไม่เต็ม"])

    # วันห้ามเฉพาะดิถี (universal phase taboo)
    if day_in_phase == 14:
        matches.append(DITHI_INFO["สงฆ์14"])
    if is_waxing and day_in_phase == 11:
        matches.append(DITHI_INFO["นารี11"])
    if day_in_phase == 7:
        matches.append(DITHI_INFO["แต่งงาน7"])

    # วันห้ามเฉพาะวาร (wan taboo)
    if wan == 7:    # เสาร์
        matches.append(DITHI_INFO["ห้ามวันเสาร์_บ้าน"])
    elif wan == 4:  # พุธ
        matches.append(DITHI_INFO["ห้ามวันพุธ_แต่งงาน"])
    elif wan == 3:  # อังคาร
        matches.append(DITHI_INFO["ห้ามวันอังคาร_โกนจุก"])

    # ถ้าไม่ตรงดิถีไหนเลย → ใส่ "ดิถีปกติ" เพื่ออธิบายให้ user
    if not matches:
        matches.append(DITHI_INFO["ปกติ"])

    return matches


def classify_from_lunar(wan: int, lunar) -> List[DithiClassification]:
    """convenience wrapper จาก LunarDate"""
    return classify_dithi(
        wan, lunar.day_in_phase, lunar.waxing,
        lunar_month=getattr(lunar, "lunar_month", None),
    )
