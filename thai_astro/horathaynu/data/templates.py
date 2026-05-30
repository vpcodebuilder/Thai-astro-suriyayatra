"""เทมเพลตประโยคคำพยากรณ์

แยกเป็นไฟล์เพื่อแก้ภาษา/น้ำเสียงได้โดยไม่แตะ logic
รูปแบบ: Python format string ที่ใช้ named placeholders
"""

# ใช้ใน relations 2 ชั้น
LORD_IN_HOUSE = (
    "{focus_name}เป็นเรือน{focus_house_name} ดาวเกษตรคือ{lord_name} "
    "ไปสถิตภพ{lord_house}({lord_house_name}) "
    "เกี่ยวกับเรื่อง{lord_house_themes}"
)

CHAIN_SECOND = (
    "เมื่อมอง{lord_name}เป็นเรือนต่อ ดาวเกษตรคือ{second_lord_name} "
    "ไปสถิตภพ{second_house}({second_house_name}) "
    "ผลสะท้อนถึงเรื่อง{second_house_themes}"
)

# ใช้ใน interpreter เมื่อ focus เป็นดาว (ไม่ใช่ลัคนา)
PLANET_IN_HOUSE = (
    "{planet_name}อยู่ภพ{house}({house_name}) "
    "ส่งผลถึง{house_themes} ในมุมของ{planet_themes}"
)

# คำเปิด/คำปิดของบทพยากรณ์รวม
OPENING = "ทายดวงยามวัน{day_name} ยามที่ {yam_index} ({yam_time_range})"
CLOSING = "— จบบทพยากรณ์ดวงยาม —"

WEEKDAY_NAMES_TH: tuple[str, ...] = (
    "อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์",
)
