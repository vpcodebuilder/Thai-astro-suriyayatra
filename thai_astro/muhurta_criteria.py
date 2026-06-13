"""เกณฑ์พิเศษและกิจกรรมในการหาฤกษ์

ประกอบด้วย:
    1. **เกณฑ์พิเศษ 3 อย่าง** (จาก horapayakorn.com id=539993303):
        - กนกนารี (Kanaka-naree)   — เคลื่อนไหวสตรี เหมาะการพบสตรี/แต่งงาน
        - กนกกุญชร (Kanaka-kunchara) — เคลื่อนไหวยานพาหนะ เหมาะออกรถ/เดินทาง
        - จักขุมายา (Chakkhumaya)   — ภาพลวงตา ระวังหลอกตา (เกณฑ์เตือน)
    2. **กิจกรรม pre-set 9 อย่าง** — กฎเฉพาะแต่ละกิจกรรม

ตำราอ้างอิง:
    - horapayakorn.com — ตำราหาฤกษ์ออนไลน์
    - mahamongkol.com/m/content.php?id=491 — หลักการหาฤกษ์
    - อ.เทพย์ สาริกบุตร: ตำราโหราศาสตร์ภาคพยากรณ์ — เกณฑ์ฤกษ์ดีตามกิจ

หมายเหตุ: เกณฑ์เหล่านี้เป็น MVP — ต้องการปรับให้ตรงตำราจริงในรอบถัดไป
        (โดยเฉพาะ จักขุมายา ที่ขึ้นกับ orb ของ ราหู/จันทร์ ซึ่งยังประมาณ)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# กลุ่มราศี (ใช้แยกประเภทในเกณฑ์)
# ============================================================
MOVABLE_SIGNS = {0, 3, 6, 9}              # จร: เมษ, กรกฎ, ตุล, มกร
FIXED_SIGNS = {1, 4, 7, 10}                # สถิร: พฤษภ, สิงห์, พิจิก, กุมภ์
DUAL_SIGNS = {2, 5, 8, 11}                 # อุภัย: เมถุน, กันย์, ธนู, มีน

FEMININE_SIGNS = {1, 3, 5, 7, 9, 11}       # ราศีคู่ (เพศหญิง)
MASCULINE_SIGNS = {0, 2, 4, 6, 8, 10}      # ราศีคี่ (เพศชาย)


@dataclass(frozen=True)
class CriterionMatch:
    """ผลการตรวจเกณฑ์พิเศษ 1 อย่าง"""
    name: str
    matched: bool
    tone: str           # "good" / "warning" / "neutral"
    detail: str         # อธิบายเหตุผล


def check_kanaka_naree(chart) -> CriterionMatch:
    """**กนกนารี** — เกณฑ์เคลื่อนไหวสตรี

    เข้าเกณฑ์เมื่อ:
        - จันทร์อยู่ในราศีเพศหญิง (1, 3, 5, 7, 9, 11) และ
        - ศุกร์อยู่ในราศีเพศหญิง
    เหมาะ: หาฤกษ์แต่งงาน หมั้น พบคู่ ทำการเกี่ยวเนื่องกับสตรี
    """
    moon = chart.planets["จันทร์"].zodiac.rasi
    venus = chart.planets["ศุกร์"].zodiac.rasi
    cond = moon in FEMININE_SIGNS and venus in FEMININE_SIGNS
    if cond:
        detail = f"จันทร์ใน{chart.planets['จันทร์'].zodiac.rasi_name} + ศุกร์ใน{chart.planets['ศุกร์'].zodiac.rasi_name} — เป็นราศีเพศหญิงทั้งสอง"
    else:
        detail = "จันทร์/ศุกร์ ไม่อยู่ในราศีเพศหญิงพร้อมกัน"
    return CriterionMatch("กนกนารี", cond, "good" if cond else "neutral", detail)


def check_kanaka_kunchara(chart) -> CriterionMatch:
    """**กนกกุญชร** — เกณฑ์เคลื่อนไหวยานพาหนะ/ช้าง

    เข้าเกณฑ์เมื่อ:
        - พฤหัสบดีอยู่ในราศีจร (movable: เมษ/กรกฎ/ตุล/มกร) หรือ
        - อังคารอยู่ในราศีจร
    เหมาะ: ออกรถใหม่ เดินทางไกล ขนส่ง พิธีเคลื่อนย้าย
    """
    jupiter = chart.planets["พฤหัสบดี"].zodiac.rasi
    mars = chart.planets["อังคาร"].zodiac.rasi
    cond = jupiter in MOVABLE_SIGNS or mars in MOVABLE_SIGNS
    parts = []
    if jupiter in MOVABLE_SIGNS:
        parts.append(f"พฤหัสฯ ใน{chart.planets['พฤหัสบดี'].zodiac.rasi_name} (ราศีจร)")
    if mars in MOVABLE_SIGNS:
        parts.append(f"อังคารใน{chart.planets['อังคาร'].zodiac.rasi_name} (ราศีจร)")
    detail = " + ".join(parts) if parts else "พฤหัสฯ/อังคาร ไม่อยู่ในราศีจร"
    return CriterionMatch("กนกกุญชร", cond, "good" if cond else "neutral", detail)


def check_chakkhumaya(chart) -> CriterionMatch:
    """**จักขุมายา** — เกณฑ์ภาพลวงตา (เตือน)

    เข้าเกณฑ์เมื่อ:
        - จันทร์อยู่ราศีเดียวกับราหูหรือเกตุ (กุมราหู/เกตุ)
    เตือน: ระวังการหลอกลวง สัญญา การมองเห็นไม่ชัด ไม่ควรเซ็นเอกสาร
    """
    moon = chart.planets["จันทร์"].zodiac.rasi
    rahu = chart.planets["ราหู"].zodiac.rasi
    ketu = chart.planets["เกตุ"].zodiac.rasi
    cond = moon == rahu or moon == ketu
    if cond:
        which = "ราหู" if moon == rahu else "เกตุ"
        detail = f"จันทร์กุม{which}ใน{chart.planets['จันทร์'].zodiac.rasi_name} — ระวังการหลอกลวง"
    else:
        detail = "จันทร์ไม่กุมราหู/เกตุ"
    return CriterionMatch("จักขุมายา", cond, "warning" if cond else "neutral", detail)


SPECIAL_CRITERIA_FNS = [check_kanaka_naree, check_kanaka_kunchara, check_chakkhumaya]


def evaluate_special_criteria(chart) -> List[CriterionMatch]:
    """ตรวจเกณฑ์พิเศษทั้ง 3 อย่าง"""
    return [fn(chart) for fn in SPECIAL_CRITERIA_FNS]


# ============================================================
# คำอธิบาย + กิจกรรมที่เหมาะสม สำหรับ UI tag popover
# ============================================================
CRITERION_INFO = {
    "กนกนารี": {
        "long_desc": (
            "กนกนารี เป็นเกณฑ์มงคลในตำราโหรไทย เกิดเมื่อจันทร์และศุกร์ "
            "อยู่ในราศีเพศหญิงทั้งสอง (พฤษภ/กรกฎ/กันย์/พิจิก/มกร/มีน) "
            "พลังของเกณฑ์นี้เกี่ยวกับสตรี ความอ่อนหวาน และความสัมพันธ์ "
            "เหมาะการแต่งงาน หมั้น สู่ขอ พบสตรี หรืองานพิธีที่มีสตรีเป็นเจ้างาน"
        ),
        "relevant_events": (
            "wedding", "engagement_ask", "wedding_registration",
            "baby_naming", "first_haircut",
        ),
        "tone": "good",
    },
    "กนกกุญชร": {
        "long_desc": (
            "กนกกุญชร (\"ช้างทองคำ\") เป็นเกณฑ์มงคลสำหรับการเคลื่อนไหว "
            "เกิดเมื่อพฤหัสบดีหรืออังคารอยู่ในราศีจร (เมษ/กรกฎ/ตุล/มกร) "
            "พลังของเกณฑ์นี้เหมาะกับการเดินทาง การออกรถ การขนย้าย "
            "พิธียกเสาเอก หรือการเริ่มต้นใหม่ที่ต้องการความคล่องตัว"
        ),
        "relevant_events": (
            "travel", "vehicle", "move_house",
            "foundation_stone", "shop_opening",
        ),
        "tone": "good",
    },
    "จักขุมายา": {
        "long_desc": (
            "จักขุมายา (\"ภาพลวงตา\") เป็นเกณฑ์เตือนภัยในตำราโหรไทย "
            "เกิดเมื่อจันทร์อยู่ราศีเดียวกับราหูหรือเกตุ พลังของเกณฑ์นี้ "
            "ทำให้การมองเห็นไม่ชัด ตัดสินใจผิดพลาด ถูกหลอกลวง "
            "ห้ามใช้กับการเซ็นสัญญา ทำเอกสารสำคัญ หรือกิจกรรมที่ต้องการ "
            "ความรอบคอบในการตัดสินใจ"
        ),
        "relevant_events": (
            "contract", "wedding_registration", "investment",
            "land_purchase", "interview_apply",
        ),
        "tone": "warning",
    },
}


def get_criterion_info(name: str) -> Optional[dict]:
    return CRITERION_INFO.get(name)


# ============================================================
# Pre-set events (กิจกรรม 9 อย่าง)
# ============================================================
@dataclass(frozen=True)
class EventCriteria:
    """กฎสำหรับกิจกรรมเฉพาะ"""
    key: str                    # short id (wedding, housewarming, ฯลฯ)
    icon: str                   # emoji
    label: str                  # ชื่อแสดงผล
    category: str               # หมวด: "มงคล/บ้าน" / "ธุรกิจ" / "เดินทาง" / "ศึกษา" / "สุขภาพ" / "ศาสนา"
    favored_planets: List[str]  # ดาวที่ต้องการให้แข็งแรง
    favored_bhavas: List[int]   # ภพ (จากลัคนา) ที่ดาว key ควรอยู่
    avoid_planets: List[str]    # ดาวที่ไม่ควรกุมจันทร์
    relevant_criterion: Optional[str]  # ชื่อเกณฑ์พิเศษที่เกี่ยวข้อง
    description: str


# ============================================================
# หมวดกิจกรรม (สำหรับ group ใน UI)
# ============================================================
EVENT_CATEGORIES = [
    ("ceremony",  "💍 งานมงคล/ครอบครัว"),
    ("home",      "🏠 บ้าน/อสังหา"),
    ("business",  "💼 ธุรกิจ/การเงิน"),
    ("travel",    "✈️ เดินทาง/ยานพาหนะ"),
    ("study",     "🎓 การศึกษา"),
    ("health",    "🩺 สุขภาพ/ความงาม"),
    ("religion",  "🙏 ศาสนา/พิธีกรรม"),
]


EVENTS: Dict[str, EventCriteria] = {
    # ===== งานมงคล/ครอบครัว =====
    "wedding": EventCriteria(
        key="wedding", icon="💍", label="แต่งงาน/หมั้น", category="ceremony",
        favored_planets=["ศุกร์", "พฤหัสบดี", "จันทร์"],
        favored_bhavas=[1, 5, 7, 11],
        avoid_planets=["เสาร์", "ราหู", "อังคาร"],
        relevant_criterion="กนกนารี",
        description="ฤกษ์ที่ศุกร์/พฤหัสฯ/จันทร์ แข็ง ตกตรีโกณ-เกณฑ์ (1/5/9) หรือ 7 (คู่)",
    ),
    "engagement_ask": EventCriteria(
        key="engagement_ask", icon="💐", label="สู่ขอ/หมั้น", category="ceremony",
        favored_planets=["ศุกร์", "พฤหัสบดี"],
        favored_bhavas=[5, 7, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion="กนกนารี",
        description="ศุกร์-พฤหัสฯ เด่น ภพ 7 (คู่) แข็ง — ระวังจักขุมายา (ถูกปฏิเสธ)",
    ),
    "wedding_registration": EventCriteria(
        key="wedding_registration", icon="📝", label="จดทะเบียนสมรส", category="ceremony",
        favored_planets=["พุธ", "ศุกร์", "พฤหัสบดี"],
        favored_bhavas=[1, 7, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion="จักขุมายา",
        description="พุธคือทะเบียน/เอกสาร + ศุกร์คือคู่ครอง — ห้ามจักขุมายา",
    ),
    "baby_naming": EventCriteria(
        key="baby_naming", icon="👶", label="ตั้งชื่อบุตร/รับขวัญ", category="ceremony",
        favored_planets=["จันทร์", "พฤหัสบดี", "พุธ"],
        favored_bhavas=[1, 5, 9],
        avoid_planets=["ราหู", "เสาร์", "อังคาร"],
        relevant_criterion=None,
        description="จันทร์ = แม่/ทารก, พฤหัสฯ = พรครูบาอาจารย์, ภพ 5 = บุตร",
    ),
    "first_haircut": EventCriteria(
        key="first_haircut", icon="✂️", label="โกนผมไฟ/ตัดผมครั้งแรก", category="ceremony",
        favored_planets=["จันทร์", "พฤหัสบดี"],
        favored_bhavas=[1, 5, 9],
        avoid_planets=["อังคาร", "ราหู", "เสาร์"],
        relevant_criterion=None,
        description="เป็นพิธีรับขวัญ — เน้นจันทร์ทรงอำนาจ และพฤหัสฯ คุ้มครอง",
    ),
    "name_change": EventCriteria(
        key="name_change", icon="🔤", label="เปลี่ยนชื่อ", category="ceremony",
        favored_planets=["พุธ", "พฤหัสบดี"],
        favored_bhavas=[1, 2, 10],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion=None,
        description="พุธ = นาม-คำพูด, ภพ 1 = ตัวตน, ภพ 10 = ชื่อเสียง",
    ),

    # ===== บ้าน/อสังหา =====
    "housewarming": EventCriteria(
        key="housewarming", icon="🏠", label="ขึ้นบ้านใหม่", category="home",
        favored_planets=["พฤหัสบดี", "ศุกร์", "เสาร์"],
        favored_bhavas=[4, 1, 9, 10],
        avoid_planets=["ราหู", "อังคาร"],
        relevant_criterion=None,
        description="เน้นภพ 4 (พันธุ-บ้าน) — เสาร์ภพ 4 ดี (รากฐาน), พฤหัสฯ ภพ 1 ดี",
    ),
    "foundation_stone": EventCriteria(
        key="foundation_stone", icon="🏗️", label="ยกเสาเอก/ลงเสาเอก", category="home",
        favored_planets=["เสาร์", "พฤหัสบดี", "อังคาร"],
        favored_bhavas=[4, 1, 10],
        avoid_planets=["ราหู"],
        relevant_criterion=None,
        description="เสาร์ = ความมั่นคง/รากฐาน + อังคารแข็งแรง = โครงสร้างทน",
    ),
    "move_house": EventCriteria(
        key="move_house", icon="📦", label="ย้ายบ้าน", category="home",
        favored_planets=["จันทร์", "ศุกร์", "พฤหัสบดี"],
        favored_bhavas=[3, 4, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion="กนกกุญชร",
        description="จันทร์ = บ้าน-แม่, ภพ 3 = ขนย้าย, ภพ 4 = ที่อยู่ใหม่",
    ),
    "land_purchase": EventCriteria(
        key="land_purchase", icon="🌳", label="ซื้อที่ดิน/อสังหา", category="home",
        favored_planets=["พฤหัสบดี", "เสาร์", "ศุกร์"],
        favored_bhavas=[2, 4, 11],
        avoid_planets=["ราหู", "อังคาร"],
        relevant_criterion=None,
        description="พฤหัสฯ ภพ 4 = อสังหาเจริญ, เสาร์ = ที่ดิน-รากฐาน",
    ),

    # ===== ธุรกิจ/การเงิน =====
    "shop_opening": EventCriteria(
        key="shop_opening", icon="🏪", label="เปิดร้าน/เปิดธุรกิจ", category="business",
        favored_planets=["พุธ", "ศุกร์", "พฤหัสบดี"],
        favored_bhavas=[2, 7, 10, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion=None,
        description="เน้นภพ 2 (กดุมภะ-ทรัพย์), 11 (ลาภะ-รายได้) และดาวพุธ/ศุกร์/พฤหัสฯ",
    ),
    "office_opening": EventCriteria(
        key="office_opening", icon="🏢", label="เปิดสำนักงาน/บริษัท", category="business",
        favored_planets=["พฤหัสบดี", "พุธ", "อาทิตย์"],
        favored_bhavas=[1, 10, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion=None,
        description="อาทิตย์ = ตำแหน่ง-อำนาจ, ภพ 10 = องค์กร, พฤหัสฯ = ความเจริญ",
    ),
    "investment": EventCriteria(
        key="investment", icon="💰", label="ลงทุน/เริ่มหุ้น", category="business",
        favored_planets=["พฤหัสบดี", "พุธ", "ศุกร์"],
        favored_bhavas=[2, 5, 11],
        avoid_planets=["ราหู", "เสาร์", "อังคาร"],
        relevant_criterion=None,
        description="พฤหัสฯ ภพ 2/11 = ทรัพย์เจริญ, พุธภพ 5 = ดวงโชค",
    ),
    "contract": EventCriteria(
        key="contract", icon="📋", label="เซ็นสัญญา", category="business",
        favored_planets=["พุธ", "พฤหัสบดี"],
        favored_bhavas=[3, 7, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion="จักขุมายา",
        description="พุธคือคำพูด-สัญญา ภพ 7 = พันธมิตร (ห้ามจักขุมายา เพราะถูกหลอก)",
    ),
    "product_launch": EventCriteria(
        key="product_launch", icon="🎉", label="เปิดตัวสินค้า/บริการ", category="business",
        favored_planets=["พุธ", "ศุกร์", "อาทิตย์"],
        favored_bhavas=[3, 10, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion=None,
        description="พุธ = โฆษณา/สื่อ, ศุกร์ = ความนิยม, ภพ 10 = ชื่อเสียง",
    ),
    "interview_apply": EventCriteria(
        key="interview_apply", icon="🤝", label="สัมภาษณ์งาน/สมัครงาน", category="business",
        favored_planets=["พุธ", "พฤหัสบดี", "อาทิตย์"],
        favored_bhavas=[1, 6, 10],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion=None,
        description="ภพ 6 = ลูกน้อง/การจ้าง, ภพ 10 = ตำแหน่ง, อาทิตย์ = อำนาจรับ",
    ),

    # ===== เดินทาง/ยานพาหนะ =====
    "travel": EventCriteria(
        key="travel", icon="✈️", label="เดินทางไกล", category="travel",
        favored_planets=["พุธ", "ศุกร์", "จันทร์"],
        favored_bhavas=[3, 9, 12],
        avoid_planets=["ราหู", "อังคาร"],
        relevant_criterion="กนกกุญชร",
        description="ภพ 3 (เดินทางใกล้), 9 (ไกล), 12 (ต่างถิ่น) — เน้น พุธ-ศุกร์",
    ),
    "vehicle": EventCriteria(
        key="vehicle", icon="🚗", label="ออกรถใหม่", category="travel",
        favored_planets=["ศุกร์", "พฤหัสบดี", "อังคาร"],
        favored_bhavas=[4, 9],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion="กนกกุญชร",
        description="ศุกร์ = ยานพาหนะ (ภพ 4), ภพ 9 = เดินทาง — ดู กนกกุญชร ประกอบ",
    ),

    # ===== การศึกษา =====
    "education": EventCriteria(
        key="education", icon="🎓", label="เริ่มเรียน/สมัครสอบ", category="study",
        favored_planets=["พุธ", "พฤหัสบดี", "อาทิตย์"],
        favored_bhavas=[1, 5, 9],
        avoid_planets=["ราหู"],
        relevant_criterion=None,
        description="พุธ = ปัญญา, พฤหัสฯ = ครู, ภพ 5 = บุตร/วิชา, ภพ 9 = ความรู้สูง",
    ),

    # ===== สุขภาพ/ความงาม =====
    "surgery": EventCriteria(
        key="surgery", icon="🩺", label="ผ่าตัด/ทำหัตถการ", category="health",
        favored_planets=["พฤหัสบดี", "ศุกร์"],
        favored_bhavas=[1, 11],
        avoid_planets=["อังคาร", "ราหู", "เสาร์"],
        relevant_criterion="จักขุมายา",
        description="เลี่ยงอังคาร (เลือดออก), ราหู (แทรกซ้อน) — เน้นพฤหัสฯ คุ้มครอง",
    ),
    "haircut_new_style": EventCriteria(
        key="haircut_new_style", icon="💇", label="ตัดผม/เปลี่ยนสไตล์", category="health",
        favored_planets=["ศุกร์", "จันทร์"],
        favored_bhavas=[1, 11],
        avoid_planets=["เสาร์", "ราหู"],
        relevant_criterion=None,
        description="ศุกร์ = ความงาม, จันทร์ภพ 1 = บุคลิกเด่น",
    ),

    # ===== ศาสนา/พิธีกรรม =====
    "merit": EventCriteria(
        key="merit", icon="🪔", label="ทำบุญ/พิธีกรรม", category="religion",
        favored_planets=["พฤหัสบดี", "จันทร์"],
        favored_bhavas=[1, 5, 9, 10],
        avoid_planets=["ราหู", "อังคาร"],
        relevant_criterion=None,
        description="พฤหัสฯ ครูบาอาจารย์ ภพ 9 = ศาสนา, สมโณฤกษ์/เทวีฤกษ์ ดีที่สุด",
    ),
    "ordination": EventCriteria(
        key="ordination", icon="🙏", label="บวชนาค/บวชชี", category="religion",
        favored_planets=["พฤหัสบดี", "เสาร์", "จันทร์"],
        favored_bhavas=[9, 12],
        avoid_planets=["ราหู", "อังคาร"],
        relevant_criterion=None,
        description="พฤหัสฯ = ครูบา, ภพ 9 = ศาสนา, ภพ 12 = สละ — สมโณฤกษ์เหมาะที่สุด",
    ),
    "kathin": EventCriteria(
        key="kathin", icon="🧡", label="ทอดกฐิน/ผ้าป่า", category="religion",
        favored_planets=["พฤหัสบดี", "ศุกร์"],
        favored_bhavas=[5, 9, 11],
        avoid_planets=["ราหู", "เสาร์"],
        relevant_criterion=None,
        description="พฤหัสฯ = บุญ, ภพ 5 = ทาน, ภพ 11 = ผลบุญ — เทวีฤกษ์ดี",
    ),
}


def get_event(key: str) -> Optional[EventCriteria]:
    return EVENTS.get(key)


def list_events() -> List[EventCriteria]:
    return list(EVENTS.values())


# ============================================================
# Scoring ดาวแข็ง/อ่อน + ภพดี (ใช้ใน muhurta.py)
# ============================================================
def planet_house_from_lakkana(chart, planet_name: str) -> int:
    """คืนภพ (1-12) ของดาวจาก ลัคนา"""
    asc_rasi = chart.ascendant.zodiac.rasi
    planet_rasi = chart.planets[planet_name].zodiac.rasi
    return ((planet_rasi - asc_rasi) % 12) + 1


def event_score(chart, event_key: str) -> Dict:
    """ให้คะแนนดวงตามกิจกรรม

    คืน {
        score: int (สูงสุด ~ +10),
        favored_hits: [(planet, house, in_favored)],
        avoid_hits: [planet],
        notes: [str]
    }
    """
    ev = EVENTS.get(event_key)
    if ev is None:
        return {"score": 0, "favored_hits": [], "avoid_hits": [], "notes": ["ไม่พบกิจกรรม"]}

    score = 0
    favored_hits = []
    notes = []

    for p in ev.favored_planets:
        if p not in chart.planets:
            continue
        h = planet_house_from_lakkana(chart, p)
        in_fav = h in ev.favored_bhavas
        favored_hits.append((p, h, in_fav))
        if in_fav:
            score += 2
            notes.append(f"✓ {p}ตกภพ {h} (ภพดีของกิจกรรมนี้)")

    avoid_hits = []
    moon_rasi = chart.planets["จันทร์"].zodiac.rasi
    for p in ev.avoid_planets:
        if p in chart.planets and chart.planets[p].zodiac.rasi == moon_rasi:
            avoid_hits.append(p)
            score -= 2
            notes.append(f"✗ จันทร์กุม{p} (ดาวห้ามของกิจกรรมนี้)")

    return {
        "score": score,
        "favored_hits": favored_hits,
        "avoid_hits": avoid_hits,
        "notes": notes,
    }
