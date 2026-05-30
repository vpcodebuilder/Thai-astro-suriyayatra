"""จุดลงเวลา — ระบุภพที่ "นาที" ของคำถามตก

ตามตำราหน้า 8:
- หาเจ้าเรือนลัคนา → ดาวนั้นสถิตในภพใด → cell แรกของเวลา
- แต่ละ cell = 7.5 นาที (90 นาที/12 cell = 1 ยาม)
- เดินไปข้างหน้าใน zodiac (= ภพถัดไป) cell ละ 7.5 นาที จนครบ 90 นาที

ตัวอย่าง: ลัคนา = พฤษภ → เจ้าเรือน = ศุกร์
         ศุกร์อยู่ตุล (ภพ 6 อริ)
         ยาม 4 = 10:30-12:00
         → cell 1 (อริ) = 10:30:00-10:37:30
            cell 2 (ปัตนิ) = 10:37:30-10:45:00
            ...
         เวลาคำถาม 10:32 → ตกใน cell 1 (อริ)
"""

from __future__ import annotations

from datetime import time, timedelta
from datetime import datetime, date

from thai_astro.horathaynu.core.time_to_yam import YAM_MINUTES, yam_range

CELL_MINUTES = 7.5
CELLS_PER_YAM = 12   # = YAM_MINUTES / CELL_MINUTES


def time_to_bhava_cell(asked_time: time, yam_index: int,
                       start_bhava: int) -> tuple[int, int]:
    """ระบุภพ + cell-index ที่เวลาคำถามตก

    Args:
        asked_time: เวลาที่ถาม
        yam_index: 1-16 ของยามที่เวลานี้ตก (ต้องคำนวณก่อนจาก time_to_yam)
        start_bhava: ภพที่เป็น cell แรก (= ภพที่เจ้าเรือนลัคนาอยู่)

    Returns:
        (bhava_at_time, cell_offset)
            bhava_at_time: ภพ 1-12 ที่เวลานี้ตก
            cell_offset:  0-11 (cell ที่เท่าไหร่ของยาม)
    """
    yam_start, _ = yam_range(yam_index)

    # คำนวณ minute offset ภายในยาม
    asked_minutes = asked_time.hour * 60 + asked_time.minute
    start_minutes = yam_start.hour * 60 + yam_start.minute
    offset = (asked_minutes - start_minutes) % (24 * 60)
    if offset >= YAM_MINUTES:
        raise ValueError(
            f"asked_time {asked_time} ไม่อยู่ในยาม {yam_index} "
            f"(เริ่ม {yam_start}, ยาว {YAM_MINUTES} นาที)"
        )

    cell_offset = int(offset // CELL_MINUTES)  # 0-11
    bhava = ((start_bhava - 1 + cell_offset) % 12) + 1
    return bhava, cell_offset


def cell_time_range(yam_index: int, cell_offset: int) -> tuple[time, time]:
    """คืนช่วงเวลา (start, end) ของ cell ที่ cell_offset ในยาม"""
    if not (0 <= cell_offset < CELLS_PER_YAM):
        raise ValueError(f"cell_offset ต้อง 0-{CELLS_PER_YAM-1} ได้รับ {cell_offset}")
    yam_start, _ = yam_range(yam_index)

    base = datetime.combine(date.today(), yam_start)
    start = base + timedelta(minutes=cell_offset * CELL_MINUTES)
    end = start + timedelta(minutes=CELL_MINUTES)
    return start.time(), end.time()
