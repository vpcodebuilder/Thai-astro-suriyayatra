"""ความหมายภพ 12 — น้ำเสียง prashna (คำถามเฉพาะหน้า) ไม่ใช่ natal

ใน webapp/server.py มี BHAVA_MEANINGS อยู่แล้ว แต่เป็นน้ำเสียงดูดวงตลอดชีวิต
ของไฟล์นี้เป็นน้ำเสียงที่เหมาะกับการตอบคำถามเฉพาะหน้า เช่น:
- "ของอยู่ที่ไหน" → ใช้ objects_places
- "บุคคลนั้นเป็นใคร" → ใช้ people
- "เรื่องจะเป็นยังไง" → ใช้ event_phrases

References:
- ตำราโหรทายหนู โดย ประทีป อัครา (2528)
- horoscope.trueid.net (12 ภพ)
- baankhunyai.com (ความหมายภพเรือน)
- horawej.com (ภพเรือน)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BhavaMeaning:
    """ความหมายภพแบบ prashna — เน้นใช้ตอบคำถาม."""

    house: int                      # 1-12
    name: str                       # ตนุ / กดุมภะ / ...
    theme: str                      # ธีมหลัก 1 ประโยค ขึ้นต้นคำตอบ
    objects_places: str             # สิ่งของ / สถานที่ (ของหายอยู่ไหน)
    people: str                     # บุคคลที่เกี่ยวข้อง (ใครเป็นคน...)
    event_tone: str                 # น้ำเสียงเหตุการณ์ในภพนี้
    default_tone: str               # "good" / "warning" / "neutral"
    affirmative_phrase: str         # "ใช่/บวก" — สำหรับคำถาม yes/no เชิงดี
    negative_phrase: str            # "ไม่/ลบ" — สำหรับคำถาม yes/no เชิงร้าย
    timeframe_hint: str             # เวลาที่เกี่ยวข้อง (เร็ว/ช้า/นาน)


# ===========================================================================
# 12 ภพ — เนื้อหาแยกตามมุมการใช้งาน
# ===========================================================================
BHAVA_MEANINGS_PRASHNA: dict[int, BhavaMeaning] = {

    1: BhavaMeaning(
        house=1,
        name="ตนุ",
        theme="เรื่องนี้เริ่มและจบที่ตัวเจ้าชะตา — ขึ้นกับการตัดสินใจของตนเอง",
        objects_places="ติดกายอยู่/อยู่บนตัว/ใกล้ตัวมาก/ในเสื้อผ้า กระเป๋าที่ถือ",
        people="ตัวผู้ถามเอง หรือคนที่มาแทนตัวผู้ถาม (ตัวแทน)",
        event_tone="เริ่มต้น ตั้งต้น ลงมือ — เป็นจุดเริ่มของเหตุการณ์",
        default_tone="good",
        affirmative_phrase="ใช่ เรื่องจะเริ่มจากตัวคุณก่อน",
        negative_phrase="แต่ระวัง — ตัวคุณเองอาจเป็นเหตุของปัญหา",
        timeframe_hint="ทันที / ปัจจุบัน / วันนี้-สัปดาห์นี้",
    ),

    2: BhavaMeaning(
        house=2,
        name="กดุมภะ",
        theme="เรื่องนี้เกี่ยวกับทรัพย์ การเก็บออม สิ่งของมีค่า การพูดและการกิน",
        objects_places=("ในที่เก็บทรัพย์/กระเป๋าเงิน/ตู้นิรภัย/ตู้เก็บของ/"
                        "ใกล้ที่กินที่ใช้ในชีวิตประจำวัน"),
        people="คนในครอบครัว ผู้ที่ดูแลทรัพย์ คนใกล้ตัวที่กินอยู่ด้วยกัน",
        event_tone="สะสม เก็บกัก รวบรวม ขายซื้อ การพูดการเจรจา",
        default_tone="good",
        affirmative_phrase="ใช่ มีโอกาสได้/สะสม/เพิ่มพูน",
        negative_phrase="ระวังจะเสียทรัพย์ หรือมีปัญหาเรื่องเงิน",
        timeframe_hint="ระยะสั้น-กลาง / เป็นเดือน",
    ),

    3: BhavaMeaning(
        house=3,
        name="สหัชชะ",
        theme="เรื่องนี้เกี่ยวกับการสื่อสาร เดินทางใกล้ พี่น้อง เพื่อนบ้าน",
        objects_places=("ที่พี่น้องหรือเพื่อนใกล้ตัว/บนเส้นทางที่เดินบ่อย/"
                        "ใกล้บ้านในระยะที่เดินไปได้/ในรถ ในกระเป๋าเดินทาง"),
        people="พี่น้อง เพื่อนบ้าน เพื่อนสนิทใกล้ตัว ผู้ที่ติดต่อด้วยบ่อย",
        event_tone="เคลื่อนไหว ติดต่อ สื่อสาร เดินทางไม่ไกล",
        default_tone="neutral",
        affirmative_phrase="ใช่ มีการเคลื่อนไหว / มีคนช่วยสื่อสาร",
        negative_phrase="แต่อาจติดขัดเรื่องการสื่อสาร / เดินทางไม่สะดวก",
        timeframe_hint="เร็ว / เป็นวัน / สัปดาห์",
    ),

    4: BhavaMeaning(
        house=4,
        name="พันธุ",
        theme="เรื่องนี้เกี่ยวกับบ้าน ที่อยู่ บิดามารดา ความมั่นคงในชีวิต การศึกษา",
        objects_places=("ในบ้าน/ที่อยู่อาศัย/ใกล้พ่อแม่/ใต้ของในบ้าน/"
                        "ในห้องนอนหรือห้องเก็บของในบ้าน"),
        people="บิดามารดา ผู้ปกครอง คนในบ้าน เจ้าของที่อยู่อาศัย",
        event_tone="ฝังราก มั่นคง ลึก เป็นรากฐาน — เปลี่ยนแปลงช้า",
        default_tone="good",
        affirmative_phrase="ใช่ — เป็นเรื่องที่มีรากฐานแข็งแรง",
        negative_phrase="แต่เปลี่ยนยาก / เรื่องในบ้านมีปัญหา",
        timeframe_hint="กลาง-ยาว / เป็นเดือน-ปี",
    ),

    5: BhavaMeaning(
        house=5,
        name="ปุตตะ",
        theme="เรื่องนี้เกี่ยวกับความสุข ความสนุก ลูกหลาน เสน่ห์ โชคที่ไม่คาดฝัน",
        objects_places=("ที่นั่งเล่น/ที่อ่านหนังสือ/สวนสนุก/บริเวณที่"
                        "เคยใช้พักผ่อน/ที่ลูก คนรัก หรือสัตว์เลี้ยงอยู่"),
        people="ลูก คนรัก คนที่ทำให้เพลิดเพลิน นักเรียน ลูกศิษย์",
        event_tone="หวานชื่น เพลิดเพลิน สร้างสรรค์ ลาภไม่คาดฝัน",
        default_tone="good",
        affirmative_phrase="ใช่ — มีความสุข มีโชคไม่คาดฝัน",
        negative_phrase="ระวังเพราะรักจนเสีย / ลูกหรือคนรักเป็นเหตุ",
        timeframe_hint="ระยะกลาง / เป็นสัปดาห์-เดือน",
    ),

    6: BhavaMeaning(
        house=6,
        name="อริ",
        theme="เรื่องนี้เกี่ยวกับศัตรู คู่แข่ง อุปสรรค โรคภัย หนี้สิน บริวาร",
        objects_places=("ที่คู่แข่ง/ศัตรู/บริวารหรือผู้ใต้บังคับ/ถูกผู้ที่"
                        "ไม่เป็นมิตรเก็บไว้/อยู่ในที่ทำงานในแผนกที่ขัดแย้ง"),
        people="ศัตรู คู่แข่ง ลูกน้องที่ไม่ซื่อ เจ้าหนี้ คนที่เป็นโรคหรือสร้างปัญหา",
        event_tone="ขัดขวาง ปะทะ ติดขัด หนัก ต้องอดทน",
        default_tone="warning",
        affirmative_phrase="ใช่ — มีอุปสรรค/มีคนขัดขวางจริง",
        negative_phrase="หนักหน่อย ต้องเตรียมรับมือ / มีศัตรูชัดเจน",
        timeframe_hint="ลากยาว / ค่อย ๆ คลี่คลาย",
    ),

    7: BhavaMeaning(
        house=7,
        name="ปัตนิ",
        theme="เรื่องนี้เกี่ยวกับคู่ครอง หุ้นส่วน คู่ตรงข้าม ผู้ทำธุรกิจร่วม",
        objects_places=("ที่คู่ครอง/หุ้นส่วน/คนที่ทำธุรกิจด้วย/อยู่ฝั่งตรงข้าม"
                        "กับผู้ถาม/ในที่ที่ทั้งสองฝ่ายเคยไปร่วมกัน"),
        people="คู่ครอง สามี/ภรรยา หุ้นส่วน คู่กรณี คู่ค้า คนที่อยู่ฝ่ายตรงข้าม",
        event_tone="ปฏิสัมพันธ์ ตกลง ผูกพัน หรือ ปะทะแบบเปิดเผย",
        default_tone="neutral",
        affirmative_phrase="ใช่ — มีคู่ มีอีกฝ่ายเข้ามาเกี่ยวข้องชัดเจน",
        negative_phrase="แต่ฝ่ายตรงข้ามอาจไม่เป็นมิตร / ตกลงไม่ลงตัว",
        timeframe_hint="ระยะกลาง / ต้องรอตอบจากอีกฝ่าย",
    ),

    8: BhavaMeaning(
        house=8,
        name="มรณะ",
        theme="เรื่องนี้เกี่ยวกับการสิ้นสุด การเปลี่ยนแปลงใหญ่ มรดก สิ่งที่ซ่อน",
        objects_places=("ที่ลับ/ของซ่อนอยู่/ในที่ปิดมิดชิด/ของที่อาจ"
                        "สูญหายโดยไม่กลับมา/ในที่เก็บมรดก"),
        people="คนที่จากไป ผู้ทิ้งมรดก คนที่เก็บความลับ คนที่ใกล้สูญเสีย",
        event_tone="พลิกผัน เปลี่ยนแปลงลึก เริ่มใหม่จากการสิ้นสุด",
        default_tone="warning",
        affirmative_phrase="ใช่ — เรื่องนี้กำลังพลิกผันใหญ่",
        negative_phrase="ระวังการสูญเสีย / เรื่องจะจบไม่สวย",
        timeframe_hint="ยาว / ต้องรอวันใหม่",
    ),

    9: BhavaMeaning(
        house=9,
        name="ศุภะ",
        theme="เรื่องนี้เกี่ยวกับบุญ บารมี ผู้ใหญ่ ครู ต่างถิ่น ต่างประเทศ",
        objects_places=("ที่ผู้ใหญ่/ครู/วัด/ต่างจังหวัด/ต่างประเทศ/"
                        "ในที่ที่ต้องเดินทางไปไกล/ของถูกพาไปไกลบ้าน"),
        people="ผู้ใหญ่ ครูบาอาจารย์ พระ ผู้ที่อยู่ไกล คนจากต่างถิ่น",
        event_tone="เปิดทาง เจริญ ขึ้นสูง เดินทางไกล มีบุญหนุน",
        default_tone="good",
        affirmative_phrase="ใช่ — มีบุญหนุน มีผู้ใหญ่ช่วย ขยายขอบเขต",
        negative_phrase="แต่ต้องเดินทาง / ขึ้นกับโชควาสนาเก่า",
        timeframe_hint="ค่อยเป็นค่อยไป / เป็นเดือน-ปี",
    ),

    10: BhavaMeaning(
        house=10,
        name="กัมมะ",
        theme="เรื่องนี้เกี่ยวกับการงาน อาชีพ ตำแหน่ง เกียรติยศ ผลของการกระทำ",
        objects_places=("ที่ทำงาน/ในตำแหน่งหน้าที่/ที่กลางแจ้ง/บนตึก"
                        "หรือสถานที่ที่สาธารณะเห็น/ในเอกสารราชการ"),
        people="เจ้านาย หัวหน้า ผู้บังคับบัญชา คนที่มีอำนาจในการงาน",
        event_tone="ทำงาน เลื่อนขั้น ยกระดับ ปรากฏต่อสาธารณะ",
        default_tone="good",
        affirmative_phrase="ใช่ — มีโอกาสก้าวหน้าในการงาน",
        negative_phrase="แต่ต้องรับภาระหนัก / มีคนจับตา",
        timeframe_hint="ระยะกลาง / เป็นเดือน",
    ),

    11: BhavaMeaning(
        house=11,
        name="ลาภะ",
        theme="เรื่องนี้เกี่ยวกับลาภ ผลตอบแทน มิตร เพื่อนช่วย ความปรารถนาที่หวัง",
        objects_places=("ที่มิตรสหาย/กับเพื่อนที่ช่วยเหลือ/ในกลุ่ม/"
                        "ของจะกลับมาในรูปลาภ/อาจมีคนพากลับมาให้"),
        people="มิตรสหาย ผู้ให้ความช่วยเหลือ กลุ่มเพื่อน คนที่นำลาภมาให้",
        event_tone="ได้รับ สมหวัง สำเร็จ ลาภเข้า",
        default_tone="good",
        affirmative_phrase="ใช่ — สมหวัง ได้ในสิ่งที่หวัง",
        negative_phrase="แต่อาจน้อยกว่าที่คาด / ต้องพึ่งเพื่อน",
        timeframe_hint="เร็ว-กลาง / ภายในไม่กี่สัปดาห์",
    ),

    12: BhavaMeaning(
        house=12,
        name="วินาส",
        theme="เรื่องนี้เกี่ยวกับการสูญเสีย รายจ่าย ที่ลับ การไปไกล สิ่งที่หลุดมือ",
        objects_places=("ที่ลับ/ในที่มืด/ใต้ของ/นอกบ้าน/ที่ไกล/"
                        "มีโอกาสสูญหายถาวร/พลัดออกไปไกลแล้ว"),
        people="คนที่อยู่ไกล คนที่กำลังจะจากไป ผู้ที่อยู่หลังฉาก",
        event_tone="สูญหาย รั่วไหล ปล่อยมือ ไกลออกไป",
        default_tone="warning",
        affirmative_phrase="ใช่ — เรื่องไปไกลแล้ว / กำลังเปลี่ยนผ่าน",
        negative_phrase="ระวังสูญหายถาวร / เสียทรัพย์ / พลัดพราก",
        timeframe_hint="ยาวมาก หรือ จบโดยไม่กลับ",
    ),
}


# ===========================================================================
# Helpers
# ===========================================================================
def get_bhava(house: int) -> BhavaMeaning:
    """ดึง BhavaMeaning ของภพ 1-12. raise ValueError ถ้านอกช่วง."""
    if house not in BHAVA_MEANINGS_PRASHNA:
        raise ValueError(f"house ต้องอยู่ในช่วง 1-12 ได้ {house}")
    return BHAVA_MEANINGS_PRASHNA[house]


def get_theme(house: int) -> str:
    """shortcut — คืนเฉพาะ theme ของภพนั้น."""
    return get_bhava(house).theme


def get_location(house: int) -> str:
    """shortcut — คืนเฉพาะ objects_places (สำหรับของหาย)."""
    return get_bhava(house).objects_places


def get_people(house: int) -> str:
    """shortcut — คืนเฉพาะคำอธิบายบุคคลในภพ."""
    return get_bhava(house).people


def render_yes_no(house: int, expecting_good: bool) -> str:
    """ตอบคำถามเชิง yes/no ตามภพและความคาดหวัง.

    expecting_good=True : ผู้ถามอยากให้เป็นบวก (เช่น "จะได้งานไหม")
    expecting_good=False : ผู้ถามกลัวเหตุการณ์ร้าย (เช่น "จะเสียงานไหม")

    คืนวลีพร้อมใช้ตามโทนของภพ.
    """
    b = get_bhava(house)
    if b.default_tone == "good":
        return b.affirmative_phrase if expecting_good else b.negative_phrase
    if b.default_tone == "warning":
        return b.negative_phrase if expecting_good else b.affirmative_phrase
    # neutral
    return b.affirmative_phrase if expecting_good else b.negative_phrase


__all__ = [
    "BhavaMeaning",
    "BHAVA_MEANINGS_PRASHNA",
    "get_bhava",
    "get_theme",
    "get_location",
    "get_people",
    "render_yes_no",
]
