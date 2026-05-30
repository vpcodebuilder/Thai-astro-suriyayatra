"""Question mapping — แปลงคำถามเป็น (primary_bhava, significator, ดาวรอง, ภพรอง)

หลักการ 3 ชั้นจากตำราโหรทายหนู (อ.ประทีป อัครา 2528):
    ชั้น 1: คำถาม → ภพหลัก (primary_bhava) — ดูธีมของเรื่องที่ถาม
    ชั้น 2: เจ้าเรือนภพหลัก → ไปสถิตภพไหน (ภพผสมภพ — Phase 4)
    ชั้น 3: ดาว significator + ดาวครองร่วม (planet × bhava — Phase 3)

Phase 1: เตรียม mapping data ให้ครบ 25 categories
- ใช้ score-based matching แทน first-match (priority × len(keyword))
- เก็บ primary + secondary bhavas + significator + co-significators

References:
- ตำราโหรทายหนู โดย ประทีป อัครา (2528)
- baankhunyai.com — ความหมายภพเรือน
- horoscope.trueid.net — ภพ 12 โหราศาสตร์ไทย
- palachote.com — ดาว × เรือน
- horawej.com — ภพผสมภพ
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QuestionMapping:
    """ผูกระหว่างคำถามผู้ใช้กับ data point ในผังโหรทายหนู."""

    category: str                       # internal key
    label_th: str                       # ป้ายแสดงผล
    keywords: tuple[str, ...]           # คำที่ใช้ match ในคำถาม
    primary_bhava: int                  # 1-12: ภพหลักของเรื่องที่ถาม
    secondary_bhavas: tuple[int, ...]   # ภพรองที่มาประกอบ (1-3 ตัว)
    significator: str                   # ดาวตัวแทนหลัก (key ใน chart.placements)
    co_significators: tuple[str, ...]   # ดาวรอง (ใช้ตีความเสริม)
    tone_hint: str                      # "neutral" / "personal" / "urgent" / "material"
    priority: int                       # 1-10: สูง = ชนะใน score-based matching


# ===========================================================================
# 25 categories — ครอบคลุมคำถามยอดนิยมในวิชาโหรทายหนู
# ===========================================================================
QUESTION_MAPPINGS: tuple[QuestionMapping, ...] = (

    # ---------- กลุ่ม ของหาย / คนหาย / สัตว์หาย ----------
    QuestionMapping(
        category="lost_item",
        label_th="ของหาย / ของรัก",
        keywords=("ของหาย", "ของรัก", "ของรักหาย", "ทอง", "เครื่องประดับ",
                  "กระเป๋า", "ของสำคัญ", "ของมีค่า", "ลืม", "ของหล่น",
                  "ของหาไม่เจอ", "หาของ"),
        primary_bhava=2,                # กดุมภะ — ทรัพย์
        secondary_bhavas=(4, 12),       # พันธุ (ที่บ้าน) + วินาส (สูญถาวร)
        significator="venus",           # ของรัก/ของมีค่า
        co_significators=("mercury",),  # การติดต่อ ค้นหา
        tone_hint="urgent",
        priority=9,
    ),
    QuestionMapping(
        category="lost_animal",
        label_th="สัตว์เลี้ยงหาย",
        keywords=("หมาหาย", "แมวหาย", "สัตว์หาย", "สัตว์เลี้ยง", "หมา",
                  "แมว", "นกหาย"),
        primary_bhava=2,
        secondary_bhavas=(6, 12),       # อริ (บริวาร/สัตว์) + วินาส
        significator="moon",            # สิ่งมีชีวิตที่เลี้ยงดู
        co_significators=("venus",),
        tone_hint="urgent",
        priority=9,
    ),
    QuestionMapping(
        category="lost_person",
        label_th="คนหาย / ตามหาบุคคล",
        keywords=("คนหาย", "ใครหาย", "ตามหา", "หายตัว", "ติดต่อไม่ได้"),
        primary_bhava=1,                # ตนุ — ตัวบุคคล
        secondary_bhavas=(12, 8),       # วินาส (สูญหาย) + มรณะ (พลัดพราก)
        significator="moon",
        co_significators=("mercury",),
        tone_hint="urgent",
        priority=9,
    ),

    # ---------- กลุ่ม ความรัก / คู่ครอง ----------
    QuestionMapping(
        category="love",
        label_th="ความรัก",
        keywords=("ความรัก", "แอบรัก", "ชอบใคร", "ความสัมพันธ์",
                  "ปิ๊ง", "หวานใจ", "เริ่มรัก", "รัก", "คนรัก"),
        primary_bhava=7,                # ปัตนิ — คู่
        secondary_bhavas=(5, 11),       # ปุตตะ (สนุก/เสน่ห์) + ลาภะ (ได้)
        significator="venus",
        co_significators=("moon",),     # อารมณ์
        tone_hint="personal",
        priority=7,
    ),
    QuestionMapping(
        category="marriage",
        label_th="คู่ครอง / แต่งงาน",
        keywords=("แต่งงาน", "สามี", "ภรรยา", "เมีย", "ผัว", "คู่ครอง",
                  "คู่", "เนื้อคู่", "วิวาห์", "หมั้น"),
        primary_bhava=7,
        secondary_bhavas=(2, 8),        # กดุมภะ (สินสมรส) + มรณะ (เปลี่ยนผ่าน)
        significator="venus",
        co_significators=("jupiter",),  # บุญร่วม
        tone_hint="personal",
        priority=8,
    ),
    QuestionMapping(
        category="breakup",
        label_th="เลิกรา / ห่างเหิน",
        keywords=("เลิก", "เลิกกัน", "แยก", "แยกทาง", "ทะเลาะแฟน",
                  "ห่างเหิน", "หย่า", "นอกใจ", "ผิดใจ"),
        primary_bhava=7,
        secondary_bhavas=(8, 12),       # มรณะ (สิ้นสุด) + วินาส (พลัดพราก)
        significator="venus",
        co_significators=("saturn",),   # ความขัดข้อง/ระยะห่าง
        tone_hint="personal",
        priority=8,
    ),

    # ---------- กลุ่ม การงาน ----------
    QuestionMapping(
        category="career",
        label_th="การงาน / อาชีพ",
        keywords=("การงาน", "งาน", "อาชีพ", "ตำแหน่ง", "เลื่อนขั้น",
                  "เลื่อนตำแหน่ง", "หน้าที่", "เจ้านาย", "ลูกน้อง",
                  "ที่ทำงาน"),
        primary_bhava=10,               # กัมมะ
        secondary_bhavas=(6, 11),       # อริ (อุปสรรค) + ลาภะ (ผลตอบแทน)
        significator="sun",             # อำนาจ/ตำแหน่ง
        co_significators=("saturn",),   # ระยะยาว/อดทน
        tone_hint="material",
        priority=7,
    ),
    QuestionMapping(
        category="job_search",
        label_th="หางาน / สมัครงาน",
        keywords=("หางาน", "สมัครงาน", "สัมภาษณ์", "interview",
                  "งานใหม่", "ได้งาน"),
        primary_bhava=10,
        secondary_bhavas=(11, 7),       # ลาภะ (ผลรับ) + ปัตนิ (ทำกับใคร)
        significator="mercury",         # การติดต่อ
        co_significators=("jupiter",),  # โอกาส/บุญ
        tone_hint="material",
        priority=8,
    ),
    QuestionMapping(
        category="resign",
        label_th="ลาออก / ย้ายงาน",
        keywords=("ลาออก", "ย้ายงาน", "เปลี่ยนงาน", "ทิ้งงาน",
                  "อยากออก", "ออกจากงาน"),
        primary_bhava=10,
        secondary_bhavas=(12, 3),       # วินาส (จาก) + สหัชชะ (ย้าย)
        significator="saturn",          # การเปลี่ยน/ขัดข้อง
        co_significators=("mars",),     # ตัดสินใจเด็ดขาด
        tone_hint="material",
        priority=8,
    ),

    # ---------- กลุ่ม ทรัพย์ / โชค / หนี้ ----------
    QuestionMapping(
        category="wealth",
        label_th="ทรัพย์ / การเงิน",
        keywords=("ทรัพย์", "การเงิน", "เงิน", "รายได้", "ออม",
                  "เก็บเงิน", "ทรัพย์สิน"),
        primary_bhava=2,
        secondary_bhavas=(11, 8),       # ลาภะ (ลาภ) + มรณะ (มรดก)
        significator="jupiter",         # ลาภ/บุญ
        co_significators=("venus",),    # มูลค่า
        tone_hint="material",
        priority=7,
    ),
    QuestionMapping(
        category="luck_windfall",
        label_th="โชคลาภ",
        keywords=("โชค", "โชคลาภ", "ลาภลอย", "หวย", "lottery",
                  "ดวงโชค", "ฟลุค"),
        primary_bhava=11,               # ลาภะ
        secondary_bhavas=(5, 9),        # ปุตตะ (โชคไม่คาดฝัน) + ศุภะ (บุญ)
        significator="jupiter",
        co_significators=("rahu",),     # ลาภลอย/ไม่คาดฝัน
        tone_hint="material",
        priority=8,
    ),
    QuestionMapping(
        category="debt",
        label_th="หนี้สิน / ภาระจ่าย",
        keywords=("หนี้", "ค้างชำระ", "จ่าย", "ใช้คืน", "ติดหนี้",
                  "เงินกู้", "ภาระ"),
        primary_bhava=6,                # อริ — หนี้/ภาระ
        secondary_bhavas=(8, 12),       # มรณะ (ติดค้าง) + วินาส (รั่วไหล)
        significator="saturn",          # ภาระยาว
        co_significators=("mars",),     # บีบบังคับ
        tone_hint="material",
        priority=8,
    ),

    # ---------- กลุ่ม สุขภาพ ----------
    QuestionMapping(
        category="health",
        label_th="สุขภาพ",
        keywords=("สุขภาพ", "ป่วย", "โรค", "หมอ", "โรงพยาบาล",
                  "อาการ", "ไม่สบาย", "กินยา"),
        primary_bhava=1,                # ตนุ — ร่างกาย
        secondary_bhavas=(6, 8),        # อริ (โรค) + มรณะ (วิกฤต)
        significator="sun",             # พลังชีวิต
        co_significators=("moon",),     # ของเหลว/อารมณ์
        tone_hint="urgent",
        priority=7,
    ),

    # ---------- กลุ่ม การศึกษา / บุตร ----------
    QuestionMapping(
        category="study",
        label_th="การศึกษา / สอบ",
        keywords=("เรียน", "สอบ", "การศึกษา", "หนังสือ", "อ่านหนังสือ",
                  "คะแนน", "ผลสอบ", "มหาวิทยาลัย", "เข้าเรียน"),
        primary_bhava=4,                # พันธุ — การศึกษา (ตำราไทย)
        secondary_bhavas=(5, 9),        # ปุตตะ (สติปัญญา) + ศุภะ (สูงขึ้น)
        significator="mercury",         # ความรู้/การสื่อสาร
        co_significators=("jupiter",),  # ครู/บุญ
        tone_hint="personal",
        priority=7,
    ),
    QuestionMapping(
        category="child",
        label_th="บุตร / ทายาท",
        keywords=("ลูก", "บุตร", "มีลูก", "ตั้งครรภ์", "ท้อง",
                  "อยากมีลูก", "ทายาท"),
        primary_bhava=5,                # ปุตตะ
        secondary_bhavas=(2, 11),       # กดุมภะ (ครอบครัว) + ลาภะ (ได้รับ)
        significator="jupiter",
        co_significators=("moon",),     # มารดา/การคลอด
        tone_hint="personal",
        priority=8,
    ),

    # ---------- กลุ่ม ครอบครัว / พี่น้อง ----------
    QuestionMapping(
        category="parent",
        label_th="บิดามารดา",
        keywords=("พ่อ", "แม่", "บิดา", "มารดา", "ผู้ปกครอง",
                  "คุณพ่อ", "คุณแม่"),
        primary_bhava=4,                # พันธุ — สิ่งติดเนื่อง/พ่อแม่
        secondary_bhavas=(9, 1),        # ศุภะ (บิดา/ผู้ใหญ่) + ตนุ (ตัวเรา)
        significator="sun",             # บิดา
        co_significators=("moon",),     # มารดา
        tone_hint="personal",
        priority=8,
    ),
    QuestionMapping(
        category="sibling_friend",
        label_th="พี่น้อง / เพื่อน",
        keywords=("พี่น้อง", "เพื่อน", "พี่ชาย", "น้องชาย", "พี่สาว",
                  "น้องสาว", "มิตร", "เพื่อนสนิท"),
        primary_bhava=3,                # สหัชชะ
        secondary_bhavas=(11, 7),       # ลาภะ (เพื่อนช่วย) + ปัตนิ (หุ้นส่วน)
        significator="mars",            # พี่น้อง (ตำราไทย)
        co_significators=("mercury",),  # เพื่อน/เด็ก
        tone_hint="personal",
        priority=6,
    ),

    # ---------- กลุ่ม เดินทาง ----------
    QuestionMapping(
        category="travel_near",
        label_th="เดินทางใกล้",
        keywords=("เดินทาง", "ขับรถ", "ไป", "รถติด", "เที่ยว",
                  "ไปทำงาน", "ขับขี่"),
        primary_bhava=3,                # สหัชชะ — เดินทางใกล้
        secondary_bhavas=(12, 9),       # วินาส (อุปสรรค) + ศุภะ (โชค)
        significator="mercury",
        co_significators=("moon",),     # การเคลื่อนไหว
        tone_hint="neutral",
        priority=7,
    ),
    QuestionMapping(
        category="travel_far",
        label_th="เดินทางไกล / ต่างแดน",
        keywords=("ต่างประเทศ", "ไกล", "ย้ายถิ่น", "ทำงานต่างประเทศ",
                  "ต่างแดน", "ต่างเมือง", "ไปต่างจังหวัด", "ไกลบ้าน"),
        primary_bhava=9,                # ศุภะ — ต่างถิ่น
        secondary_bhavas=(12, 3),       # วินาส (พลัดบ้าน) + สหัชชะ (ย้าย)
        significator="jupiter",         # ต่างแดน/บุญ
        co_significators=("mercury",),  # การเคลื่อนไหว
        tone_hint="neutral",
        priority=8,
    ),

    # ---------- กลุ่ม คดี / ศัตรู ----------
    QuestionMapping(
        category="lawsuit",
        label_th="คดี / พิพาท",
        keywords=("คดี", "ฟ้องร้อง", "ทะเลาะ", "ความ", "พิพาท",
                  "ศาล", "ตำรวจ", "ขึ้นโรง", "ฟ้อง"),
        primary_bhava=6,                # อริ — ศัตรู/คดี
        secondary_bhavas=(12, 7),       # วินาส (พ่าย) + ปัตนิ (คู่กรณี)
        significator="mars",            # การต่อสู้
        co_significators=("saturn",),   # การยืดยาว
        tone_hint="urgent",
        priority=8,
    ),
    QuestionMapping(
        category="enemy",
        label_th="ศัตรู / คู่แข่ง",
        keywords=("ศัตรู", "คู่แข่ง", "ปะทะ", "ขัดขวาง", "เหยียบ",
                  "เกลียด", "เป็นศัตรู"),
        primary_bhava=6,
        secondary_bhavas=(7, 12),       # ปัตนิ (เปิดเผย) + วินาส (ลับ)
        significator="mars",
        co_significators=("rahu",),     # ของลึก/ไม่คาดฝัน
        tone_hint="urgent",
        priority=7,
    ),

    # ---------- กลุ่ม บ้าน / ธุรกิจ ----------
    QuestionMapping(
        category="property_home",
        label_th="บ้าน / ที่ดิน",
        keywords=("บ้าน", "ที่ดิน", "อสังหา", "ซื้อบ้าน", "ย้ายบ้าน",
                  "เช่าบ้าน", "ที่อยู่", "คอนโด"),
        primary_bhava=4,                # พันธุ
        secondary_bhavas=(2, 11),       # กดุมภะ (ทรัพย์) + ลาภะ (ได้)
        significator="saturn",          # โครงสร้าง/ที่ดิน
        co_significators=("moon",),     # ที่อยู่
        tone_hint="material",
        priority=7,
    ),
    QuestionMapping(
        category="business",
        label_th="ค้าขาย / ธุรกิจ",
        keywords=("ค้าขาย", "ธุรกิจ", "ลงทุน", "ขาย", "ซื้อขาย",
                  "หุ้นส่วน", "เปิดร้าน", "กิจการ"),
        primary_bhava=7,                # ปัตนิ — หุ้นส่วน/คู่ค้า
        secondary_bhavas=(10, 11),      # กัมมะ (อาชีพ) + ลาภะ (กำไร)
        significator="mercury",         # การค้า
        co_significators=("jupiter",),  # ลาภ
        tone_hint="material",
        priority=8,
    ),

    # ---------- กลุ่มทั่วไป ----------
    QuestionMapping(
        category="current_event",
        label_th="เหตุการณ์ปัจจุบัน",
        keywords=("เหตุการณ์", "จะเกิด", "สงสัย", "ตอนนี้", "อนาคต",
                  "ระยะสั้น", "วันนี้"),
        primary_bhava=1,                # ตนุ — ตัวเรา ณ ปัจจุบัน
        secondary_bhavas=(7, 10),       # ปัตนิ (ผู้อื่น) + กัมมะ (สิ่งที่ทำ)
        significator="lagna",
        co_significators=("sun",),
        tone_hint="neutral",
        priority=5,
    ),
    QuestionMapping(
        category="general",
        label_th="ดูดวงทั่วไป",
        keywords=(),                    # fallback — ไม่ match keyword ใดเลย
        primary_bhava=1,
        secondary_bhavas=(),
        significator="lagna",
        co_significators=(),
        tone_hint="neutral",
        priority=1,
    ),
)


# ===========================================================================
# Lookup helpers
# ===========================================================================
def get_mapping_by_category(category: str) -> QuestionMapping | None:
    """ค้น mapping จาก category key. คืน None ถ้าไม่พบ."""
    for m in QUESTION_MAPPINGS:
        if m.category == category:
            return m
    return None


def classify_question(question: str) -> tuple[QuestionMapping, list[str]]:
    """แปลงคำถาม → (mapping, matched_keywords).

    Algorithm: **score-based matching**
        score = Σ (mapping.priority × len(keyword)) ของทุก keyword ที่ match

    เหตุผลที่ใช้ score: คำถามอาจมีหลาย keyword พร้อมกัน
        เช่น "อยากเดินทางไปทำงานต่างประเทศ" — match ทั้ง "เดินทาง", "งาน",
        "ต่างประเทศ" — ต้องการให้ travel_far ชนะเพราะ priority สูงสุด
        + keyword "ต่างประเทศ" ยาวกว่า "งาน"

    ถ้าไม่ match ใดเลย → fallback "general"
    """
    q = question.strip().lower()
    if not q:
        fallback = get_mapping_by_category("general")
        assert fallback is not None, "general mapping ต้องมีเสมอ"
        return fallback, []

    best_mapping: QuestionMapping | None = None
    best_score = 0
    best_matched: list[str] = []

    for m in QUESTION_MAPPINGS:
        matched = [kw for kw in m.keywords if kw in q]
        if not matched:
            continue
        score = sum(m.priority * len(kw) for kw in matched)
        if score > best_score:
            best_score = score
            best_mapping = m
            best_matched = matched

    if best_mapping is None:
        fallback = get_mapping_by_category("general")
        assert fallback is not None
        return fallback, []

    return best_mapping, best_matched


__all__ = [
    "QuestionMapping",
    "QUESTION_MAPPINGS",
    "get_mapping_by_category",
    "classify_question",
]
