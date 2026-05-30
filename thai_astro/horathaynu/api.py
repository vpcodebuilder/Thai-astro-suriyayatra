"""Entry หลักของโมดูลโหรทายหนู (ฉบับ อ.กานดา — chain walking)

ตัวอย่างใช้งาน:
    from thai_astro.horathaynu import predict
    result = predict(day=3, yam_index=4, question="love")  # วันพุธ ยาม 4

ถ้ามี datetime จริง:
    from thai_astro.horathaynu.api import predict_from_datetime
    result = predict_from_datetime(datetime.now(), question="money")

ถ้ารู้ counts จากตำราแล้ว (เพราะกฎ derive ของดาว 6+ ยังไม่ implement):
    result = predict(day=3, yam_index=4, counts=[5,3,1,6,4,4,6,1,3,5,7])
"""

from __future__ import annotations

from datetime import datetime

from thai_astro.horathaynu.core.caster import cast_chain
from thai_astro.horathaynu.core.interpreter import interpret
from thai_astro.horathaynu.core.time_precision import time_to_bhava_cell
from thai_astro.horathaynu.core.time_to_yam import datetime_to_day_yam
from thai_astro.horathaynu.core.bhava import bhava_name
from thai_astro.horathaynu.data.lordship import lord_of


def predict(day: int, yam_index: int,
            question: str | None = None,
            focus_override: str | None = None,
            counts: list[int] | None = None,
            count_overrides: dict[int, int] | None = None) -> dict:
    """พยากรณ์จาก (วัน, ยาม)

    Args:
        day: 0=อาทิตย์ ... 6=เสาร์
        yam_index: 1-16 (1-8 กลางวัน, 9-16 กลางคืน)
        question: keyword ("love", "money", ...) — optional
        focus_override: planet_key สำหรับบังคับ focus — optional
        counts: counts ครบทุกดาว (ข้าม derive_counts)
        count_overrides: {star_index_0based: count} สำหรับ override บางตัว
    """
    chart = cast_chain(day, yam_index, counts=counts, overrides=count_overrides)
    return interpret(chart, question=question, focus_override=focus_override)


def predict_from_datetime(dt: datetime,
                          question: str | None = None,
                          focus_override: str | None = None,
                          counts: list[int] | None = None,
                          count_overrides: dict[int, int] | None = None) -> dict:
    """รับ datetime → แปลงเป็น (day, yam_index) → predict + เพิ่ม time_cell"""
    day, yam_index = datetime_to_day_yam(dt)
    result = predict(day, yam_index, question=question,
                     focus_override=focus_override,
                     counts=counts, count_overrides=count_overrides)

    # เพิ่ม time precision: หา bhava ที่นาทีถามตก
    asc = result["chart"]["ascendant_sign"]
    lagna_lord = lord_of(asc)
    placements = result["chart"]["placements"]
    if lagna_lord in placements:
        lord_house = placements[lagna_lord]["house"]
        bhava_at_time, cell_offset = time_to_bhava_cell(
            dt.time(), yam_index, lord_house
        )
        result["time_precision"] = {
            "asked_time": dt.time().isoformat(timespec="minutes"),
            "lagna_lord": lagna_lord,
            "lord_house": lord_house,
            "lord_bhava_name": bhava_name(lord_house),
            "bhava_at_time": bhava_at_time,
            "bhava_at_time_name": bhava_name(bhava_at_time),
            "cell_offset": cell_offset,
        }
    return result
