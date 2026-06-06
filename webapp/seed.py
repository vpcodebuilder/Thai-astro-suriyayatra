"""Seed script — import current Python lists into DB

Usage:
    python -m webapp.seed [--reset]

--reset : clear tables before insert (idempotent re-seed)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import delete

from webapp.db import SessionLocal
from webapp.models import CalendarEpoch, HolyDay, NationalHoliday, AdhikamasaYear

ADHIKAMASA_JSON = Path(__file__).parent.parent / "data" / "adhikamasa_scraped.json"

# ============================================================
# Source data (hardcoded — same as the original calendar_data.py)
# Once seeded, calendar_data.py functions will read from DB.
# ============================================================

EPOCHS_DATA = [
    {
        "year_label": "3102 ปีก่อน ค.ศ.", "ce_year": -3101, "be_year": None,
        "title": "เริ่มกาลียุค (Kali Yuga)",
        "description": "ตามคติจักรวาลวิทยาของศาสนาฮินดู ยุคกาลีเริ่มต้นเมื่อดาวเคราะห์สำคัญเรียงตัว ณ จุดอ้างอิงทางดาราศาสตร์ ถือเป็น Epoch สำคัญของคัมภีร์สุริยสิทธานต์และระบบสุริยยาตร์ ซึ่งต่อมากลายเป็นรากฐานการคำนวณปฏิทินและโหราศาสตร์ไทย",
        "icon": "🌌", "type": "astronomical",
        "image": "/static/timeline-images/timeline01.png",
        "image_caption": "ฤาษีโบราณกับคัมภีร์ดาราศาสตร์อินเดีย — Kali Yuga epoch",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "543 ปีก่อน ค.ศ.", "ce_year": -542, "be_year": 1,
        "title": "พ.ศ. 1 : พระพุทธเจ้าปรินิพพาน",
        "description": "การปรินิพพานของพระสัมมาสัมพุทธเจ้าได้รับการกำหนดเป็นจุดเริ่มต้นของพุทธศักราช (พ.ศ.) ซึ่งภายหลังกลายเป็นระบบศักราชหลักของประเทศไทยและหลายประเทศในพุทธศาสนาเถรวาท",
        "icon": "🪷", "type": "buddhist",
        "image": "/static/timeline-images/timeline02.png",
        "image_caption": "ปรินิพพาน — Epoch ของพุทธศักราช",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 78", "ce_year": 78, "be_year": 621,
        "title": "เริ่มมหาศักราช (ม.ศ.)",
        "description": "มหาศักราชถือกำเนิดขึ้นในอินเดียและแพร่เข้าสู่เอเชียตะวันออกเฉียงใต้ กลายเป็นระบบศักราชสำคัญในยุคแรกของรัฐไทยโบราณ โดยเฉพาะในสมัยสุโขทัย",
        "icon": "📜", "type": "era",
        "image": "/static/timeline-images/timeline03.png",
        "image_caption": "มหาศักราช — กษัตริย์ Shalivahana แห่งอินเดียใต้",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 499", "ce_year": 499, "be_year": 1042,
        "title": "ยุคดาราศาสตร์อินเดียรุ่งเรือง",
        "description": "ผลงานของอารยภัฏและตำราสุริยสิทธานต์ได้พัฒนาระบบคำนวณการเคลื่อนที่ของดวงอาทิตย์ ดวงจันทร์ และดาวเคราะห์อย่างเป็นระบบ กลายเป็นรากฐานสำคัญของวิชาสุริยยาตร์ที่ไทยใช้มาจนถึงปัจจุบัน",
        "icon": "🔭", "type": "astronomical",
        "image": "/static/timeline-images/timeline04.png",
        "image_caption": "อารยภัฏ (Aryabhata) — บิดาแห่งดาราศาสตร์อินเดีย",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 638", "ce_year": 638, "be_year": 1181,
        "title": "เริ่มจุลศักราช (จ.ศ.)",
        "description": "จุลศักราชถือกำเนิดขึ้นในดินแดนพม่าและแพร่เข้าสู่รัฐต่าง ๆ ในเอเชียตะวันออกเฉียงใต้ ต่อมากลายเป็นศักราชหลักที่ใช้ในราชการไทยและเป็นฐานการคำนวณปฏิทินสุริยยาตร์",
        "icon": "📐", "type": "era",
        "image": "/static/timeline-images/timeline05.png",
        "image_caption": "จุลศักราช — กำเนิดในดินแดนพม่า (JDN epoch = 1954167)",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1283", "ce_year": 1283, "be_year": 1826,
        "title": "กำเนิดอักษรไทยและหลักฐานศักราชไทย",
        "description": "พ่อขุนรามคำแหงมหาราชทรงประดิษฐ์อักษรไทย ทำให้การบันทึกวัน เดือน ปี และศักราชต่าง ๆ ปรากฏในหลักฐานทางประวัติศาสตร์อย่างชัดเจนเป็นครั้งแรก",
        "icon": "🛕", "type": "sukhothai",
        "image": "/static/timeline-images/timeline06.png",
        "image_caption": "ศิลาจารึกพ่อขุนรามคำแหง — พ.ศ. 1826",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1455", "ce_year": 1455, "be_year": 1998,
        "title": "ระบบปฏิทินราชการอยุธยา",
        "description": "ราชสำนักอยุธยาพัฒนาการใช้จุลศักราชและปฏิทินจันทรคติอย่างเป็นระบบสำหรับการปกครอง พิธีกรรม และการกำหนดฤกษ์ยาม ส่งผลให้วิชาโหราศาสตร์และปฏิทินมีบทบาทสำคัญในราชการ",
        "icon": "🏛", "type": "ayutthaya",
        "image": "/static/timeline-images/timeline07.png",
        "image_caption": "ราชสำนักอยุธยา — ยุคทองของปฏิทินจุลศักราช",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1782", "ce_year": 1782, "be_year": 2325,
        "title": "สถาปนากรุงรัตนโกสินทร์",
        "description": "พระบาทสมเด็จพระพุทธยอดฟ้าจุฬาโลกมหาราชทรงสถาปนากรุงรัตนโกสินทร์และราชวงศ์จักรี ระบบปฏิทินและโหราศาสตร์ราชสำนักได้รับการสืบทอดและพัฒนาอย่างต่อเนื่อง",
        "icon": "👑", "type": "rattanakosin",
        "image": "/static/timeline-images/timeline08.png",
        "image_caption": "สถาปนากรุงรัตนโกสินทร์ — ราชวงศ์จักรี",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1855", "ce_year": 1855, "be_year": 2398,
        "title": "อิทธิพลปฏิทินตะวันตก",
        "description": "หลังการทำสนธิสัญญาเบาว์ริง ไทยมีความสัมพันธ์กับชาติตะวันตกมากขึ้น ระบบคริสต์ศักราชและปฏิทินสุริยคติสากลเริ่มเข้ามามีบทบาทในงานราชการและการค้าระหว่างประเทศ",
        "icon": "🌍", "type": "rattanakosin",
        "image": "/static/timeline-images/timeline09.png",
        "image_caption": "สนธิสัญญาเบาว์ริง — อิทธิพลปฏิทินตะวันตกในสยาม",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1889", "ce_year": 1889, "be_year": 2432,
        "title": "ปรับวันขึ้นปีใหม่เป็น 1 เมษายน",
        "description": "พระบาทสมเด็จพระจุลจอมเกล้าเจ้าอยู่หัวทรงปฏิรูประบบเวลาและการบริหารราชการ โดยกำหนดให้วันที่ 1 เมษายนเป็นวันขึ้นปีใหม่อย่างเป็นทางการ แทนการนับตามจันทรคติเดิม",
        "icon": "📅", "type": "reform",
        "image": "/static/timeline-images/timeline10.png",
        "image_caption": "พระบาทสมเด็จพระจุลจอมเกล้าเจ้าอยู่หัว (ร.5) — ปฏิรูประบบเวลา",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1912", "ce_year": 1912, "be_year": 2455,
        "title": "ประกาศใช้พุทธศักราชอย่างเป็นทางการ",
        "description": "พระบาทสมเด็จพระมงกุฎเกล้าเจ้าอยู่หัวทรงยกเลิกการใช้รัตนโกสินทรศกในราชการ และกำหนดให้พุทธศักราชเป็นระบบศักราชมาตรฐานของประเทศ",
        "icon": "🇹🇭", "type": "reform",
        "image": "/static/timeline-images/timeline11.png",
        "image_caption": "พระบาทสมเด็จพระมงกุฎเกล้าเจ้าอยู่หัว (ร.6) — ประกาศใช้ พ.ศ.",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 1941", "ce_year": 1941, "be_year": 2484,
        "title": "เปลี่ยนวันขึ้นปีใหม่เป็น 1 มกราคม",
        "description": "รัฐบาลจอมพล ป. พิบูลสงครามกำหนดให้ประเทศไทยใช้วันขึ้นปีใหม่ตามมาตรฐานสากลในวันที่ 1 มกราคม ส่งผลให้ปี พ.ศ. 2483 มีระยะเวลาเพียง 9 เดือน ก่อนเริ่ม พ.ศ. 2484 ในวันที่ 1 มกราคม",
        "icon": "✂️", "type": "reform",
        "image": "/static/timeline-images/timeline12.png",
        "image_caption": "จอมพล ป. พิบูลสงคราม — เปลี่ยนวันขึ้นปีใหม่เป็น 1 ม.ค.",
        "image_credit": "Illustration · Public Domain",
    },
    {
        "year_label": "ค.ศ. 2026", "ce_year": 2026, "be_year": 2569,
        "title": "ปฏิทินไทยในยุคดิจิทัล",
        "description": "แม้ประเทศไทยจะใช้ปฏิทินสากลในการดำเนินชีวิตประจำวัน แต่ยังคงรักษาพุทธศักราช ระบบจันทรคติ และองค์ความรู้สุริยยาตร์ไว้ควบคู่กัน สะท้อนมรดกทางวัฒนธรรมที่สืบทอดต่อเนื่องยาวนานกว่า 5,000 ปี",
        "icon": "📱", "type": "digital",
        "image": "/static/timeline-images/timeline13.png",
        "image_caption": "ปฏิทินไทยยุคดิจิทัล — มรดก 5,000 ปี",
        "image_credit": "Illustration · Public Domain",
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


def seed_adhikamasa(session, reset: bool):
    """Import ปีอธิกมาส/อธิกวาร 401 entries (BE 2300-2700) จาก myhora scrape.

    Idempotent: ถ้ามี row อยู่แล้ว → skip ทั้งหมด (ไม่ overwrite)
    ถ้ายังไม่มี → bulk insert จาก data/adhikamasa_scraped.json
    """
    if reset:
        session.execute(delete(AdhikamasaYear))
    if session.query(AdhikamasaYear).count() > 0:
        print("[skip] adhikamasa_years already populated")
        return
    if not ADHIKAMASA_JSON.exists():
        print(f"[warn] ไม่พบ {ADHIKAMASA_JSON.name} — ข้าม adhikamasa seeding")
        return

    data = json.loads(ADHIKAMASA_JSON.read_text(encoding="utf-8"))
    inserted = skipped = 0
    for be_str, info in data.items():
        be_year = int(be_str)
        kind = info["type"]
        if kind in ("error", "unknown"):
            skipped += 1
            continue
        cs_year = be_year - 1181
        ce_year = be_year - 543
        session.add(AdhikamasaYear(
            cs_year=cs_year,
            be_year=be_year,
            ce_year=ce_year,
            type=kind,
            source="myhora",
            note=info.get("evidence", ""),
        ))
        inserted += 1
    print(f"[seed] adhikamasa_years: {inserted} entries (skipped {skipped})")


def main():
    reset = "--reset" in sys.argv
    session = SessionLocal()
    try:
        seed_epochs(session, reset)
        seed_holy_days(session, reset)
        seed_national_holidays(session, reset)
        seed_adhikamasa(session, reset)
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
