"""ความหมายดาว 11 ดวง (โหรทายหนู — ดวงยาม)

เก็บเป็น keyword สั้นๆ ใช้เติมในเทมเพลต
ค่าเหล่านี้เป็น default จากความหมายไทยมาตรฐาน — ถ้าตำราโหรทายหนูของสำนัก
ที่คุณใช้ให้ความหมายต่าง ให้ override ในไฟล์นี้
"""

# planet_key ต้องตรงกับที่ caster ใช้
PLANET_KEYS = (
    "lagna", "sun", "moon", "mars", "mercury",
    "jupiter", "venus", "saturn", "rahu", "ketu", "uranus",
)

PLANET_NAME_TH: dict[str, str] = {
    "lagna":   "ลัคนา",
    "sun":     "อาทิตย์",
    "moon":    "จันทร์",
    "mars":    "อังคาร",
    "mercury": "พุธ",
    "jupiter": "พฤหัสบดี",
    "venus":   "ศุกร์",
    "saturn":  "เสาร์",
    "rahu":    "ราหู",
    "ketu":    "เกตุ",
    "uranus":  "มฤตยู",
}

PLANET_MEANINGS: dict[str, dict] = {
    "lagna":   {"themes": ["เจ้าชะตา", "ตัวผู้ถาม", "เรื่องเฉพาะหน้า"]},
    "sun":     {"themes": ["ผู้ใหญ่", "อำนาจ", "เกียรติยศ", "บิดา"]},
    "moon":    {"themes": ["มารดา", "อารมณ์", "ผู้หญิง", "ความเปลี่ยนแปลง"]},
    "mars":    {"themes": ["พลัง", "การต่อสู้", "ความขัดแย้ง", "นักรบ"]},
    "mercury": {"themes": ["การพูด", "การค้า", "ปัญญา", "เด็ก"]},
    "jupiter": {"themes": ["ครูบาอาจารย์", "บุญ", "ความรู้", "ที่พึ่ง"]},
    "venus":   {"themes": ["ความรัก", "ศิลปะ", "ความหวาน", "หญิงสาว"]},
    "saturn":  {"themes": ["อุปสรรค", "ความเก่าแก่", "ทุกข์", "ผู้สูงวัย"]},
    "rahu":    {"themes": ["ลาภลอย", "เรื่องลึกลับ", "ของหาย", "สิ่งคาดไม่ถึง"]},
    "ketu":    {"themes": ["การพลัดพราก", "ของเก่า", "การหลุดพ้น", "ความสงบ"]},
    "uranus":  {"themes": ["การพลิกผัน", "สิ่งใหม่", "ความรวดเร็ว", "เทคโนโลยี"]},
}


def planet_name(key: str) -> str:
    return PLANET_NAME_TH[key]


def planet_themes(key: str) -> list[str]:
    return PLANET_MEANINGS[key]["themes"]
