"""แปลง (วันในสัปดาห์, เวลา) → yam_index 1-16

หลัก:
- วันใหม่เริ่ม 06:00 (พระอาทิตย์ขึ้น — ตรงกับ SunriseType.SixAM ของโปรเจคเดิม)
- กลางวัน 1-8: 06:00-07:30, 07:30-09:00, ..., 16:30-18:00 (ยามละ 90 นาที)
- กลางคืน 9-16: 18:00-19:30, ..., 04:30-06:00

ช่วงเวลา [start, end) — start inclusive, end exclusive
ยกเว้นยาม 16 ที่ end = 06:00 ของวันถัดไป (ปิดท้ายวัน)
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

YAM_COUNT = 16
YAM_MINUTES = 90  # 24×60 / 16
SUNRISE_HOUR = 6


def yam_range(yam_index: int) -> tuple[time, time]:
    """คืน (start, end) ของยาม"""
    if not (1 <= yam_index <= YAM_COUNT):
        raise ValueError(f"yam_index ต้อง 1-{YAM_COUNT} ได้รับ {yam_index}")
    total_start = SUNRISE_HOUR * 60 + (yam_index - 1) * YAM_MINUTES
    total_end = total_start + YAM_MINUTES
    start = time((total_start // 60) % 24, total_start % 60)
    end = time((total_end // 60) % 24, total_end % 60)
    return start, end


def time_to_yam(t: time) -> int:
    """เวลา → yam_index 1-16 (ไม่สนใจวัน)"""
    minutes = t.hour * 60 + t.minute
    offset = (minutes - SUNRISE_HOUR * 60) % (24 * 60)
    return offset // YAM_MINUTES + 1


def datetime_to_day_yam(dt: datetime) -> tuple[int, int]:
    """datetime → (day_of_week 0-6, yam_index 1-16)

    วันใหม่เริ่ม 06:00 → ถ้าเวลา < 06:00 ถือเป็นวันก่อนหน้า
    เช่น เสาร์ 03:00 → ถือเป็นยาม 14 ของวันศุกร์
    """
    effective = dt
    if dt.time() < time(SUNRISE_HOUR, 0):
        effective = dt - timedelta(days=1)
    # Python weekday: 0=Monday ... 6=Sunday
    # โหรไทย: 0=Sunday ... 6=Saturday
    day = (effective.weekday() + 1) % 7
    yam = time_to_yam(dt.time())
    return day, yam


def date_time_to_day_yam(d: date, t: time) -> tuple[int, int]:
    """convenience: รับ date + time แยกกัน"""
    return datetime_to_day_yam(datetime.combine(d, t))
