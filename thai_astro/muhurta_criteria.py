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
    strength: int = 1   # 2 = ดีนัก (โดดเด่นเป็นพิเศษ); 1 = ปกติ (ดี / ห้าม)


# ============================================================
# ตารางเกณฑ์กนกนารี (อ.หลวงวุฒิรณพัศตุ์ — ปรมาจารย์ ณ.ร. รวบรวม)
# Lookup: KANAKA_NAREE_PASS[wan] = set ของ "ฤกษ์ที่" (1-27) ที่ "ทำได้"
# wan 1=อาทิตย์, 2=จันทร์, 3=อังคาร, 4=พุธ, 5=พฤหัสบดี, 6=ศุกร์, 7=เสาร์
# ============================================================
# Source: knowledge/ฤกษ์.xlsx (authoritative)
KANAKA_NAREE_PASS: dict = {
    1: frozenset({1, 3, 4, 7, 9, 10, 11, 13, 16, 19, 21, 22, 24, 26, 27}),    # อาทิตย์
    2: frozenset({1, 4, 7, 9, 11, 12, 13, 14, 15, 20, 22, 24, 25, 26, 27}),   # จันทร์
    3: frozenset({2, 7, 9, 10, 13, 16, 21, 22, 23, 25, 26, 27}),              # อังคาร
    4: frozenset({2, 4, 5, 7, 9, 10, 15, 17, 19, 21, 22, 23, 26, 27}),        # พุธ
    5: frozenset({2, 9, 11, 12, 15, 17, 18, 19, 22, 23, 25}),                 # พฤหัสบดี
    6: frozenset({1, 2, 5, 6, 7, 10, 11, 14, 17, 19, 21, 22, 24}),            # ศุกร์
    7: frozenset({8, 10, 11, 14, 15, 16, 17, 18, 20, 21, 22, 24}),            # เสาร์
}


def check_kanaka_naree(chart, wan: int = 0, nak_number: int = 0,
                       nak_name: str = "", roek_name: str = "") -> CriterionMatch:
    """**กนกนารี** — เกณฑ์เคลื่อนไหวสตรี (ตามตารางอ.หลวงวุฒิรณพัศตุ์)

    Lookup ตาราง 7 วาร × 27 ฤกษ์:
        - "ทำได้" → ผ่านเกณฑ์ (matched, tone=good) → +คะแนน
        - "ห้าม"  → ไม่ผ่านเกณฑ์ (matched, tone=warning) → -คะแนน

    Format detail: "วัน{X} × {roek_name} ฤกษ์ที่ {N} กลุ่มดาว{nak_name}"
    """
    wan_names = {1: "อาทิตย์", 2: "จันทร์", 3: "อังคาร", 4: "พุธ",
                 5: "พฤหัสบดี", 6: "ศุกร์", 7: "เสาร์"}
    if wan not in KANAKA_NAREE_PASS or not (1 <= nak_number <= 27):
        return CriterionMatch("กนกนารี", False, "neutral",
                              "ไม่สามารถตรวจสอบเกณฑ์ได้ (ข้อมูลไม่ครบ)")
    pass_ = nak_number in KANAKA_NAREE_PASS[wan]
    wan_name = wan_names[wan]
    roek_part = f"{roek_name} " if roek_name else ""
    nak_group = f"กลุ่มดาว{nak_name}" if nak_name else ""
    check_line = f"ตรงกับวัน{wan_name} เป็น{roek_part}ฤกษ์ที่ {nak_number} {nak_group}".strip()
    if pass_:
        detail = (
            f"✓ ผ่านเกณฑ์: คู่ \"วัน × ฤกษ์\" อยู่ในช่อง \"ทำได้\"\n"
            f"ตรวจสอบ: {check_line}\n"
            f"ตำราระบุ: คู่นี้อนุญาตให้ใช้ตั้งฤกษ์\n"
            f"ผลที่ได้: ฤกษ์หนุนเรื่องสตรี ความอ่อนหวาน ความสัมพันธ์ "
            f"เหมาะงานแต่ง/หมั้น/สู่ขอ\n"
            f"คะแนน: +2"
        )
        return CriterionMatch("กนกนารี", True, "good", detail)
    detail = (
        f"✗ ไม่ผ่านเกณฑ์: คู่ \"วัน × ฤกษ์\" อยู่ในช่อง \"ห้าม\"\n"
        f"ตรวจสอบ: {check_line}\n"
        f"ตำราระบุ: คู่นี้ห้ามใช้ตั้งฤกษ์เรื่องสตรี\n"
        f"ผลที่ได้: ขัดกับพลังเกณฑ์สตรี ไม่ควรใช้กับงานแต่ง/หมั้น/สู่ขอ\n"
        f"คะแนน: −1"
    )
    return CriterionMatch("กนกนารี", True, "warning", detail)


def check_kanaka_kunchara(chart, wan: int = 0, nak_number: int = 0,
                          nak_name: str = "", roek_name: str = "") -> CriterionMatch:
    """**กนกกุญชร** — เกณฑ์ลัคนาราศีของฤกษ์ (ตามตารางอ.หลวงวุฒิรณพัศตุ์)

    Lookup ตาราง 27 ฤกษ์ × 7 วาร (knowledge/ฤกษ์.xlsx sheet "กนกกุญชร")
    แต่ละช่องกำหนดราศี "ดีนัก/ดี/ห้าม" ของลัคนา ณ ฤกษ์นั้น
    - ลัคนาตรงราศี "ดีนัก" → ผ่าน (tone=good, label="ดีนัก")
    - ลัคนาตรงราศี "ดี"   → ผ่าน (tone=good, label="ดี")
    - ลัคนาตรงราศี "ห้าม" หรือ cell "ห้ามราศีอื่น" และไม่อยู่ในรายการ
      → ไม่ผ่าน (tone=warning, label="ห้าม")
    - ไม่ระบุชัด → neutral (ไม่มีผลต่อคะแนน)
    """
    from .kanaka_kunchara import check as kk_check

    lagna_name = chart.ascendant.zodiac.rasi_name
    if not (1 <= wan <= 7) or not (1 <= nak_number <= 27):
        return CriterionMatch("กนกกุญชร", False, "neutral",
                              "ไม่สามารถตรวจสอบเกณฑ์ได้ (ข้อมูลไม่ครบ)")

    res = kk_check(lagna_name, nak_number, wan)
    wan_names = {1: "อาทิตย์", 2: "จันทร์", 3: "อังคาร", 4: "พุธ",
                 5: "พฤหัสบดี", 6: "ศุกร์", 7: "เสาร์"}
    wan_name = wan_names.get(wan, "?")
    roek_part = f"{roek_name} " if roek_name else ""
    nak_group = f"กลุ่มดาว{nak_name}" if nak_name else ""
    check_line = f"ตรงกับวัน{wan_name} เป็น{roek_part}ฤกษ์ที่ {nak_number} {nak_group}".strip()
    note_tail = f"\nหมายเหตุ: {res.extra_note}" if res.extra_note else ""

    if res.tone == "good" and res.label == "ดีนัก":
        detail = (
            f"✨ ผ่านเกณฑ์ระดับ \"ดีนัก\": ลัคนา{lagna_name} เด่นเป็นพิเศษ\n"
            f"ตรวจสอบ: {check_line}\n"
            f"ตำราระบุ: {res.rule_summary}\n"
            f"ผลที่ได้: ฤกษ์นี้แรงเป็นพิเศษ พื้นฐานลัคนาเด่นมาก เหมาะงานสำคัญ\n"
            f"คะแนน: +3" + note_tail
        )
        return CriterionMatch("กนกกุญชร", True, "good", detail, strength=2)
    if res.tone == "good":
        detail = (
            f"✓ ผ่านเกณฑ์: ลัคนา{lagna_name} ตรงราศี \"ดี\" ของฤกษ์นี้\n"
            f"ตรวจสอบ: {check_line}\n"
            f"ตำราระบุ: {res.rule_summary}\n"
            f"ผลที่ได้: ลัคนาตกในราศีที่หนุนการเคลื่อนไหว ฤกษ์มั่นคง พื้นฐานแน่น\n"
            f"คะแนน: +2" + note_tail
        )
        return CriterionMatch("กนกกุญชร", True, "good", detail)
    if res.tone == "warning":
        if "ราศีอื่น" in res.label:
            head = f"✗ ไม่ผ่านเกณฑ์: ลัคนา{lagna_name} ไม่อยู่ในรายการอนุญาต"
            outcome = "ลัคนาไม่อยู่ในกลุ่มที่ตำรากำหนด ฤกษ์ไม่สนับสนุน"
        else:
            head = f"✗ ไม่ผ่านเกณฑ์: ลัคนา{lagna_name} ตรงราศี \"ห้าม\" ของฤกษ์นี้"
            outcome = "ลัคนาตกในราศีที่ขัดกับธาตุของฤกษ์ พลังฤกษ์ลด"
        detail = (
            f"{head}\n"
            f"ตรวจสอบ: {check_line}\n"
            f"ตำราระบุ: {res.rule_summary}\n"
            f"ผลที่ได้: {outcome}\n"
            f"คะแนน: −1" + note_tail
        )
        return CriterionMatch("กนกกุญชร", True, "warning", detail)
    # neutral — ลัคนาไม่อยู่ในรายการดี/ห้าม (ยังคืน matched=True เพื่อให้ tag แสดงเสมอ)
    detail = (
        f"○ ไม่ระบุชัด: ลัคนา{lagna_name} ไม่อยู่ในรายการดีหรือห้ามของฤกษ์นี้\n"
        f"ตรวจสอบ: {check_line}\n"
        f"ตำราระบุ: {res.rule_summary}\n"
        f"ผลที่ได้: เกณฑ์นี้ไม่กระทบฤกษ์ — ไม่หนุนและไม่ขัด\n"
        f"คะแนน: 0" + note_tail
    )
    return CriterionMatch("กนกกุญชร", True, "neutral", detail)


# ============================================================
# เกณฑ์จักขุมายา — สูตร (นักษัตร + เกณฑ์วัน) mod 7
# ============================================================
# เกณฑ์วัน (ตามตำราโบราณ — ระวิฉัฏโฐ/ทเวจันโท ฯลฯ)
JAKKHUMAYA_WAN_KANE = {
    1: 6,  # อาทิตย์ — ระวิฉัฏโฐ
    2: 2,  # จันทร์ — ทเวจันโท
    3: 5,  # อังคาร — ภุมโมปัญจ
    4: 1,  # พุธ — พุธเอโก
    5: 4,  # พฤหัสบดี — ชีโวจัตวา
    6: 0,  # ศุกร์ — ศุกราสูญญ (เกณฑ์ 0 หรือ 7)
    7: 3,  # เสาร์ — โสรตรีนิ
}

# เศษหารด้วย 7 → ชื่อโยค + tone + คำพยากรณ์
JAKKHUMAYA_REMAINDER = {
    0: {"name": "สรรพโยคอำพล", "tone": "good",
        "meaning": "เหมาะการสร้างวัด หล่อพระ ปลุกเสก ต่อเรือ ศิลปกรรม หัตถกรรม "
                   "พิธีศักดิ์สิทธิ์"},
    1: {"name": "อุบาทว์", "tone": "warning",
        "meaning": "ร้ายไม่ดี — ครูท่านห้ามทำการมงคล กิจจะอุบาทว์ ขัดข้อง"},
    2: {"name": "กาลกิณี", "tone": "warning",
        "meaning": "ร้ายไม่ดี — กาลกิณีเข้าครอบ กิจจะมีอุปสรรค สูญเสีย"},
    3: {"name": "มฤตยู", "tone": "warning",
        "meaning": "แสนเข็ญ — ครูท่านให้เว้นเด็ดขาด เป็นเศษที่อันตรายที่สุด"},
    4: {"name": "สาธุโยคบูชา", "tone": "good",
        "meaning": "เกิดสวัสดิมงคล พูลผล — เหมาะกิจมงคลทุกประเภท การบูชา ทำบุญ"},
    5: {"name": "สิทธิโชค", "tone": "good",
        "meaning": "สำเร็จทุกประการ — เหมาะกิจมงคลทั่วไป สมความปรารถนา"},
    6: {"name": "อำมฤคโชค", "tone": "good",
        "meaning": "โชคดีทุกสถาน — เหมาะทำสวนไร่นา หว่านพืชผล กิจมงคลทั่วไป"},
}


def check_chakkhumaya(chart, wan: int = 0, nak_number: int = 0,
                     nak_name: str = "", roek_name: str = "") -> CriterionMatch:
    """**จักขุมายาฤกษ์** — เกณฑ์สอบผลฤกษ์ตามสูตรโบราณ

    หลักการ: ตั้ง "ลำดับนักษัตรของจันทร์" บวกด้วย "เกณฑ์วัน"
              แล้วหารด้วย 7 พิจารณาจากเศษ
        - เศษ 0/4/5/6 → ผ่านเกณฑ์ (+2)
        - เศษ 1/2/3   → ไม่ผ่านเกณฑ์ (−3)
    """
    wan_names = {1: "อาทิตย์", 2: "จันทร์", 3: "อังคาร", 4: "พุธ",
                 5: "พฤหัสบดี", 6: "ศุกร์", 7: "เสาร์"}
    if wan not in JAKKHUMAYA_WAN_KANE or not (1 <= nak_number <= 27):
        return CriterionMatch("จักขุมายา", False, "neutral",
                              "ไม่สามารถตรวจสอบเกณฑ์ได้ (ข้อมูลไม่ครบ)")

    keisn = JAKKHUMAYA_WAN_KANE[wan]
    keisn_disp = "0 หรือ 7" if keisn == 0 else str(keisn)
    total = nak_number + keisn
    remainder = total % 7
    res = JAKKHUMAYA_REMAINDER[remainder]
    quotient = total // 7

    wan_name = wan_names[wan]
    roek_part = f"{roek_name} " if roek_name else ""
    nak_group = f"กลุ่มดาว{nak_name}" if nak_name else ""
    check_line = (f"ตรงกับวัน{wan_name} (เกณฑ์ {keisn_disp}) "
                  f"เป็น{roek_part}ฤกษ์ที่ {nak_number} {nak_group}").strip()
    formula = (f"({nak_number} + {keisn}) ÷ 7 = {quotient} เศษ {remainder} "
               f"→ \"{res['name']}\"")

    if res["tone"] == "good":
        detail = (
            f"✓ ผ่านเกณฑ์: ได้ \"{res['name']}\" (เศษ {remainder})\n"
            f"ตรวจสอบ: {check_line}\n"
            f"ตำราระบุ: {formula}\n"
            f"ผลที่ได้: {res['meaning']}\n"
            f"คะแนน: +2"
        )
        return CriterionMatch("จักขุมายา", True, "good", detail)

    # warning (เศษ 1/2/3)
    detail = (
        f"✗ ไม่ผ่านเกณฑ์: ได้ \"{res['name']}\" (เศษ {remainder})\n"
        f"ตรวจสอบ: {check_line}\n"
        f"ตำราระบุ: {formula}\n"
        f"ผลที่ได้: {res['meaning']}\n"
        f"คะแนน: −1"
    )
    return CriterionMatch("จักขุมายา", True, "warning", detail)


def _check_chakkhumaya_legacy(chart) -> CriterionMatch:
    """**(เลิกใช้)** เก็บไว้อ้างอิง — เกณฑ์จันทร์กุมราหู/เกตุเดิม"""
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


def evaluate_special_criteria(chart, wan: int = 0, nak_number: int = 0,
                              nak_name: str = "", roek_name: str = "") -> List[CriterionMatch]:
    """ตรวจเกณฑ์พิเศษ 3 อย่าง

    Args:
        chart: Chart object
        wan: 1-7 (ใช้ใน กนกนารี — ลำดับ 1=อาทิตย์)
        nak_number: 1-27 (ใช้ใน กนกนารี — ตำแหน่งนักษัตรของจันทร์)
        nak_name: ชื่อนักษัตร (กลุ่มดาว) เช่น "ภรณี"
        roek_name: ชื่อฤกษ์ใหญ่ (1 ใน 9) เช่น "มหัทธโนฤกษ์"
    """
    return [
        check_kanaka_naree(chart, wan=wan, nak_number=nak_number,
                           nak_name=nak_name, roek_name=roek_name),
        check_kanaka_kunchara(chart, wan=wan, nak_number=nak_number,
                              nak_name=nak_name, roek_name=roek_name),
        check_chakkhumaya(chart, wan=wan, nak_number=nak_number,
                          nak_name=nak_name, roek_name=roek_name),
    ]


# ============================================================
# คำอธิบาย + กิจกรรมที่เหมาะสม สำหรับ UI tag popover
# ============================================================
CRITERION_INFO = {
    "กนกนารี": {
        "long_desc": (
            "กนกนารี เป็นเกณฑ์มงคลในตำราโหรไทย ตรวจสอบจาก \"วาร × ฤกษ์\" "
            "(วันในสัปดาห์ × ตำแหน่งจันทร์ในนักษัตร 1-27) — แต่ละคู่ "
            "ตำรากำหนดเป็น \"ทำได้\" หรือ \"ห้าม\". "
            "ผ่านเกณฑ์ +2 คะแนน, ไม่ผ่าน −3 คะแนน. "
            "พลังของเกณฑ์นี้เกี่ยวกับสตรี ความอ่อนหวาน และความสัมพันธ์ "
            "เหมาะการแต่งงาน หมั้น สู่ขอ พบสตรี งานพิธีที่มีสตรีเป็นเจ้างาน"
        ),
        "relevant_events": (
            "wedding", "engagement_ask", "wedding_registration",
            "baby_naming", "first_haircut",
        ),
        "tone": "good",
    },
    "กนกกุญชร": {
        "long_desc": (
            "กนกกุญชร (\"ช้างทองคำ\") เป็นเกณฑ์ตรวจ \"ลัคนาราศีของฤกษ์\" "
            "— แต่ละคู่ \"วาร × ฤกษ์\" ตำราจะกำหนดราศีลัคนาที่ "
            "\"ดีนัก / ดี / ห้าม\" ของฤกษ์นั้น ๆ. "
            "ผ่านระดับ \"ดีนัก\" +3 คะแนน, ผ่านระดับ \"ดี\" +2 คะแนน, "
            "ลัคนาตรง \"ห้าม\" หรือ \"ห้ามราศีอื่น\" (อนุญาตเฉพาะที่ระบุ) → ไม่ผ่าน −3 คะแนน. "
            "เกณฑ์นี้ใช้ได้กับทุกกิจกรรม เพราะวัด \"ความเหมาะสมของลัคนา\" "
            "ซึ่งเป็นพื้นฐานของการตั้งฤกษ์"
        ),
        "relevant_events": (
            "wedding", "engagement_ask", "wedding_registration",
            "housewarming", "foundation_stone", "move_house", "land_purchase",
            "shop_opening", "office_opening", "investment", "contract",
            "product_launch", "interview_apply",
            "travel", "vehicle",
            "education", "exam",
            "ordination", "merit",
        ),
        "tone": "good",
    },
    "จักขุมายา": {
        "long_desc": (
            "จักขุมายาฤกษ์ — เกณฑ์สอบผลฤกษ์ที่โหราจารย์โบราณนับถือมาก "
            "หลักการ: ตั้ง \"ลำดับนักษัตรของจันทร์\" บวก \"เกณฑ์วัน\" "
            "(อา=6, จ=2, อ=5, พุธ=1, พฤ=4, ศ=0/7, ส=3) แล้วหารด้วย 7 "
            "พิจารณาจากเศษ — เศษ 0/4/5/6 ผ่านเกณฑ์ +2 คะแนน, "
            "เศษ 1/2/3 (อุบาทว์/กาลกิณี/มฤตยู) ไม่ผ่าน −3 คะแนน. "
            "เกณฑ์นี้ใช้ \"สอบผล\" ทุกฤกษ์ ใช้ได้กับกิจกรรมทุกประเภท"
        ),
        "relevant_events": (
            "wedding", "engagement_ask", "wedding_registration",
            "housewarming", "foundation_stone", "move_house", "land_purchase",
            "shop_opening", "office_opening", "investment", "contract",
            "product_launch", "interview_apply",
            "travel", "vehicle",
            "education", "exam",
            "ordination", "merit",
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
