"""Seed script — import current Python lists into DB

Usage:
    python -m webapp.seed [--reset]

--reset : clear tables before insert (idempotent re-seed)
"""
from __future__ import annotations

import sys

from sqlalchemy import delete

from webapp.db import SessionLocal
from webapp.models import CalendarEpoch, HolyDay, NationalHoliday, AdhikamasaYear

# ============================================================
# Source data (hardcoded — same as the original calendar_data.py)
# Once seeded, calendar_data.py functions will read from DB.
# ============================================================

EPOCHS_DATA = [
    {
        "year_label": "3102 ปีก่อน ค.ศ.", "ce_year": -3101, "be_year": None,
        "title": "เริ่มกาลียุค (Kali Yuga)",
        "description": "วันเริ่มต้นของยุคกาลีตามคัมภีร์ฮินดูโบราณ เป็น epoch ของสูตรสุริยยาตร์/สุริยสิทธานต์ที่ไทยใช้",
        "icon": "🌌", "type": "astronomical",
    },
    {
        "year_label": "543 ปีก่อน ค.ศ.", "ce_year": -542, "be_year": 1,
        "title": "ปรินิพพาน — เริ่ม พ.ศ. 1",
        "description": "ปีปรินิพพานของพระสัมมาสัมพุทธเจ้า ใช้เป็น epoch ของพุทธศักราช (พ.ศ.) วันแรกตามตำราอยู่ราว ขึ้น 1 ค่ำ เดือน 7 (มิถุนายน-กรกฎาคม)",
        "icon": "🪷", "type": "buddhist",
    },
    {
        "year_label": "ค.ศ. 78", "ce_year": 78, "be_year": 621,
        "title": "เริ่มมหาศักราช (ม.ศ.)",
        "description": "กษัตริย์ Shalivahana ของอินเดียใต้สถาปนา ตำราโบราณบางเล่มของไทยอ้างปีเป็น ม.ศ. โดยเฉพาะของช่วงสุโขทัย",
        "icon": "📜", "type": "era",
    },
    {
        "year_label": "ค.ศ. 638", "ce_year": 638, "be_year": 1181,
        "title": "เริ่มจุลศักราช (จ.ศ.)",
        "description": "สังฆราชโพธิสาตว์ของพม่าสถาปนาขึ้น เป็นจุดเริ่มต้นที่สูตรสุริยยาตร์ของไทยใช้คำนวณได้แม่นยำ (JDN epoch = 1954167)",
        "icon": "📐", "type": "era",
    },
    {
        "year_label": "ค.ศ. 1238", "ce_year": 1238, "be_year": 1781,
        "title": "สถาปนากรุงสุโขทัย",
        "description": "พ่อขุนศรีอินทราทิตย์ทรงสถาปนากรุงสุโขทัย — อาณาจักรไทยแห่งแรก มีศักราชใช้ทั้ง ม.ศ. (มหาศักราช) และจ.ศ. ในจารึก",
        "icon": "🛕", "type": "historical",
    },
    {
        "year_label": "ค.ศ. 1351", "ce_year": 1351, "be_year": 1894,
        "title": "สถาปนากรุงศรีอยุธยา",
        "description": "สมเด็จพระรามาธิบดีที่ 1 (พระเจ้าอู่ทอง) ทรงสถาปนากรุงศรีอยุธยาเป็นราชธานี — ยุคที่ปฏิทินจ.ศ. และโหราศาสตร์ไทยเฟื่องฟู",
        "icon": "🏛", "type": "historical",
    },
    {
        "year_label": "ค.ศ. 1767", "ce_year": 1767, "be_year": 2310,
        "title": "เสียกรุงศรีอยุธยาครั้งที่ 2",
        "description": "พม่ายึดและเผาทำลายกรุงศรีอยุธยา — ตำราโหราศาสตร์และปฏิทินจำนวนมากสูญหาย ก่อนสมเด็จพระเจ้าตากสินกอบกู้และก่อตั้งกรุงธนบุรี",
        "icon": "⚔", "type": "historical",
    },
    {
        "year_label": "ค.ศ. 1782", "ce_year": 1782, "be_year": 2325,
        "title": "สถาปนากรุงรัตนโกสินทร์",
        "description": "พระบาทสมเด็จพระพุทธยอดฟ้าฯ ทรงสถาปนาราชวงศ์จักรี 6 เมษายน เป็น \"วันจักรี\" จนถึงปัจจุบัน",
        "icon": "👑", "type": "historical",
        "image": "/static/timeline-images/rama1.jpg",
        "image_caption": "พระบาทสมเด็จพระพุทธยอดฟ้าจุฬาโลกมหาราช (ร.1)",
        "image_credit": "Wikimedia Commons · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1889", "ce_year": 1889, "be_year": 2432,
        "title": "ไทยรับปฏิทินสุริยคติแบบสากล",
        "description": "พระบาทสมเด็จพระจุลจอมเกล้าฯ (รัชกาลที่ 5) ทรงเปลี่ยนวันขึ้นปีใหม่ของไทยมาเป็น 1 เมษายน (จากเดิมที่ขึ้นตามจันทรคติ)",
        "icon": "📅", "type": "reform",
        "image": "/static/timeline-images/rama5.jpg",
        "image_caption": "พระบาทสมเด็จพระจุลจอมเกล้าเจ้าอยู่หัว (ร.5)",
        "image_credit": "Library of Congress · Wikimedia Commons · PD",
    },
    {
        "year_label": "ค.ศ. 1912", "ce_year": 1912, "be_year": 2455,
        "title": "ประกาศใช้ พ.ศ. อย่างเป็นทางการ",
        "description": "พระบาทสมเด็จพระมงกุฎเกล้าฯ (รัชกาลที่ 6) ทรงโปรดเกล้าฯ ให้เปลี่ยนจากรัตนโกสินทรศก (ร.ศ.) มาเป็นพุทธศักราช (พ.ศ.) ทั่วราชอาณาจักร",
        "icon": "🇹🇭", "type": "reform",
        "image": "/static/timeline-images/rama6.jpg",
        "image_caption": "พระบาทสมเด็จพระมงกุฎเกล้าเจ้าอยู่หัว (ร.6)",
        "image_credit": "Wikimedia Commons · Public Domain (c. 1920)",
    },
    {
        "year_label": "ค.ศ. 1941", "ce_year": 1941, "be_year": 2484,
        "title": "เปลี่ยนวันขึ้นปีใหม่ 1 เม.ย. → 1 ม.ค.",
        "description": "จอมพล ป.พิบูลสงคราม ประกาศให้ใช้วันขึ้นปีใหม่สากลแทนวันที่ 1 เมษายน พ.ศ. 2483 จึงเหลือเพียง 9 เดือน (เม.ย.-ธ.ค.) แล้วเริ่ม พ.ศ. 2484 ที่ 1 ม.ค.",
        "icon": "✂️", "type": "reform",
        "image": "/static/timeline-images/phibun.jpg",
        "image_caption": "จอมพล แปลก พิบูลสงคราม (นายกรัฐมนตรี พ.ศ. 2481-2487)",
        "image_credit": "Wikimedia Commons · PD (c. 1940s)",
    },
]


HOLY_DAYS_DATA = [
    {"month": 3, "waxing": True, "day": 15, "name": "วันมาฆบูชา",
     "description": "พระสงฆ์ 1,250 รูปมาประชุมพร้อมกันโดยมิได้นัดหมาย", "icon": "🪷"},
    {"month": 6, "waxing": True, "day": 15, "name": "วันวิสาขบูชา",
     "description": "ประสูติ ตรัสรู้ ปรินิพพาน ของพระสัมมาสัมพุทธเจ้า", "icon": "🪷"},
    {"month": 8, "waxing": True, "day": 15, "name": "วันอาสาฬหบูชา",
     "description": "พระพุทธเจ้าทรงแสดงปฐมเทศนาแก่ปัญจวัคคีย์ที่ป่าอิสิปตนมฤคทายวัน", "icon": "🪷"},
    {"month": 8, "waxing": False, "day": 1, "name": "วันเข้าพรรษา",
     "description": "พระภิกษุเริ่มจำพรรษา 3 เดือน", "icon": "🙏"},
    {"month": 11, "waxing": True, "day": 15, "name": "วันออกพรรษา",
     "description": "สิ้นสุดการจำพรรษา 3 เดือน", "icon": "🙏"},
    {"month": 12, "waxing": True, "day": 15, "name": "วันลอยกระทง",
     "description": "ขอบคุณพระแม่คงคาและขอขมาที่ใช้น้ำในการดำรงชีวิต", "icon": "🪷"},
]


NATIONAL_HOLIDAYS_DATA = [
    {"month": 1, "day": 1, "name": "วันขึ้นปีใหม่",
     "description": "วันขึ้นปีใหม่สากล (ใช้ตั้งแต่ พ.ศ. 2484)", "icon": "🎊", "category": "holiday"},
    {"month": 1, "day": 16, "name": "วันครู",
     "description": "ครบรอบการก่อตั้งคุรุสภา พ.ศ. 2488", "icon": "🧑‍🏫", "category": "memorial"},
    {"month": 2, "day": 14, "name": "วันวาเลนไทน์",
     "description": "วันแห่งความรักสากล", "icon": "💝", "category": "international"},
    {"month": 3, "day": 8, "name": "วันสตรีสากล",
     "description": "International Women's Day", "icon": "♀", "category": "international"},
    {"month": 4, "day": 1, "name": "วันข้าราชการพลเรือน",
     "description": "ครบรอบการประกาศใช้ พ.ร.บ. ระเบียบข้าราชการพลเรือน พ.ศ. 2471", "icon": "📋", "category": "memorial"},
    {"month": 4, "day": 6, "name": "วันจักรี",
     "description": "วันที่ ร.1 ทรงสถาปนาราชวงศ์จักรี (พ.ศ. 2325)", "icon": "👑", "category": "royal"},
    {"month": 4, "day": 13, "name": "วันสงกรานต์ (มหาสงกรานต์)",
     "description": "วันขึ้นปีใหม่ไทยตามประเพณี — วันแรกของเทศกาลสงกรานต์", "icon": "💦", "category": "tradition"},
    {"month": 4, "day": 14, "name": "วันสงกรานต์ (วันเนา)",
     "description": "วันกลางของเทศกาลสงกรานต์ — วันครอบครัว", "icon": "💦", "category": "tradition"},
    {"month": 4, "day": 15, "name": "วันสงกรานต์ (วันเถลิงศก)",
     "description": "วันเถลิงศกขึ้นจุลศักราชใหม่ — วันผู้สูงอายุแห่งชาติ", "icon": "💦", "category": "tradition"},
    {"month": 5, "day": 1, "name": "วันแรงงานแห่งชาติ",
     "description": "วันแรงงานสากล (May Day)", "icon": "🛠", "category": "holiday"},
    {"month": 5, "day": 4, "name": "วันฉัตรมงคล",
     "description": "วันบรมราชาภิเษก ร.10 (4 พ.ค. 2562)", "icon": "👑", "category": "royal"},
    {"month": 6, "day": 3, "name": "วันเฉลิมพระชนมพรรษา สมเด็จพระราชินี",
     "description": "วันคล้ายวันพระราชสมภพ สมเด็จพระนางเจ้าสุทิดาฯ พระบรมราชินี", "icon": "👑", "category": "royal"},
    {"month": 7, "day": 28, "name": "วันเฉลิมพระชนมพรรษา ร.10",
     "description": "วันคล้ายวันพระบรมราชสมภพ พระบาทสมเด็จพระวชิรเกล้าเจ้าอยู่หัว", "icon": "👑", "category": "royal"},
    {"month": 8, "day": 12, "name": "วันแม่แห่งชาติ",
     "description": "วันคล้ายวันพระบรมราชสมภพ สมเด็จพระบรมราชชนนีพันปีหลวง", "icon": "👑", "category": "royal"},
    {"month": 10, "day": 13, "name": "วันคล้ายวันสวรรคต ร.9",
     "description": "วันที่ ร.9 เสด็จสวรรคต (พ.ศ. 2559) — วันนวมินทรมหาราช", "icon": "🙏", "category": "royal"},
    {"month": 10, "day": 23, "name": "วันปิยมหาราช",
     "description": "วันคล้ายวันสวรรคต ร.5 (พ.ศ. 2453)", "icon": "🙏", "category": "royal"},
    {"month": 11, "day": 14, "name": "วันพระบิดาแห่งฝนหลวง",
     "description": "วันที่ ร.9 พระราชดำริโครงการฝนหลวง พ.ศ. 2498", "icon": "🌧", "category": "memorial"},
    {"month": 12, "day": 5, "name": "วันชาติ / วันพ่อแห่งชาติ / วันคล้ายวันพระบรมราชสมภพ ร.9",
     "description": "วันคล้ายวันพระบรมราชสมภพ พระบาทสมเด็จพระบรมชนกาธิเบศร (ร.9)", "icon": "👑", "category": "royal"},
    {"month": 12, "day": 10, "name": "วันรัฐธรรมนูญ",
     "description": "วันประกาศใช้รัฐธรรมนูญฉบับแรก (10 ธ.ค. 2475)", "icon": "📜", "category": "national"},
    {"month": 12, "day": 31, "name": "วันสิ้นปี",
     "description": "วันสิ้นปีปฏิทินสากล", "icon": "🎇", "category": "holiday"},
]


def seed_epochs(session, reset: bool):
    if reset:
        session.execute(delete(CalendarEpoch))
    if session.query(CalendarEpoch).count() > 0:
        print("[skip] calendar_epochs already populated")
        return
    for i, d in enumerate(EPOCHS_DATA):
        session.add(CalendarEpoch(sort_order=i, **d))
    print(f"[seed] calendar_epochs: {len(EPOCHS_DATA)} entries")


def seed_holy_days(session, reset: bool):
    if reset:
        session.execute(delete(HolyDay))
    if session.query(HolyDay).count() > 0:
        print("[skip] holy_days already populated")
        return
    for d in HOLY_DAYS_DATA:
        session.add(HolyDay(**d))
    print(f"[seed] holy_days: {len(HOLY_DAYS_DATA)} entries")


def seed_national_holidays(session, reset: bool):
    if reset:
        session.execute(delete(NationalHoliday))
    if session.query(NationalHoliday).count() > 0:
        print("[skip] national_holidays already populated")
        return
    for d in NATIONAL_HOLIDAYS_DATA:
        session.add(NationalHoliday(**d))
    print(f"[seed] national_holidays: {len(NATIONAL_HOLIDAYS_DATA)} entries")


def main():
    reset = "--reset" in sys.argv
    session = SessionLocal()
    try:
        seed_epochs(session, reset)
        seed_holy_days(session, reset)
        seed_national_holidays(session, reset)
        # adhikamasa_years: เว้นไว้ Stage 2 (scraper จะ populate)
        session.commit()
        print("[done] seed complete")
    except Exception as e:
        session.rollback()
        print(f"[error] {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
