"""ข้อมูลปฏิทินไทย — query helpers ที่อ่านจาก DB

หมายเหตุ Phase 8 (Stage 1):
    - ข้อมูลเดิม (hardcoded Python lists) ย้ายไป webapp/seed.py
    - หน้านี้เหลือเพียง query/lookup functions ที่ caller ใช้
    - Schema/source-of-truth: webapp/models.py
"""
from __future__ import annotations

from typing import Optional

from webapp.db import SessionLocal
from webapp.models import CalendarEpoch, HolyDay, NationalHoliday


# ============================================================
# Calendar Epochs
# ============================================================
def get_calendar_epochs() -> list[dict]:
    """ดึง timeline events ทั้งหมด เรียงตาม sort_order
    Fail-safe: ถ้า DB error → []
    """
    s = SessionLocal()
    try:
        rows = s.query(CalendarEpoch).order_by(CalendarEpoch.sort_order).all()
        return [r.to_dict() for r in rows]
    except Exception:
        return []
    finally:
        s.close()


# ============================================================
# Buddhist Holy Days (lunar-based)
# ============================================================
def get_holy_days() -> list[dict]:
    s = SessionLocal()
    try:
        rows = s.query(HolyDay).order_by(HolyDay.month, HolyDay.waxing.desc(), HolyDay.day).all()
        return [r.to_dict() for r in rows]
    except Exception:
        return []
    finally:
        s.close()


def find_holy_day(
    lunar_month: int,
    waxing: bool,
    day_in_phase: int,
    is_leap_month_year: bool = False,
    is_intercalary_month: bool = False,
) -> Optional[dict]:
    """หาว่าวันนี้เป็นวันสำคัญทางพุทธศาสนาหรือไม่

    HOLY_DAYS เก็บเลขเดือนสำหรับ "ปีปกติ" (ไม่ใช่อธิกมาส)
    ในปีอธิกมาส กรมการศาสนาเลื่อนเดือนวันสำคัญตามกฎ:
      - มาฆบูชา: เดือน 3 → 4
      - วิสาขบูชา: เดือน 6 → 7
      - อาสาฬหบูชา: เดือน 8 → 8 หลัง (intercalary)
      - เข้าพรรษา: แรม 1 ค่ำ เดือน 8 → เดือน 8 หลัง
      - ออกพรรษา / ลอยกระทง (เดือน 11, 12): ไม่ shift
    """
    if is_leap_month_year:
        if lunar_month == 8 and is_intercalary_month:
            original_month = 8
        elif lunar_month == 8 and not is_intercalary_month:
            return None
        elif lunar_month in (4, 5, 6, 7):
            original_month = lunar_month - 1
        else:
            original_month = lunar_month
    else:
        original_month = lunar_month

    s = SessionLocal()
    try:
        row = (
            s.query(HolyDay)
            .filter(
                HolyDay.month == original_month,
                HolyDay.waxing == waxing,
                HolyDay.day == day_in_phase,
            )
            .first()
        )
        return row.to_dict() if row else None
    except Exception:
        return None
    finally:
        s.close()


def is_buddhist_observance_day(day_in_phase: int) -> bool:
    """วันพระ = ขึ้น/แรม 8 หรือ 15 ค่ำ"""
    return day_in_phase in (8, 15)


# ============================================================
# National / Royal / Traditional Holidays (solar-based)
# ============================================================
def get_national_holidays() -> list[dict]:
    s = SessionLocal()
    try:
        rows = s.query(NationalHoliday).order_by(
            NationalHoliday.month, NationalHoliday.day
        ).all()
        return [r.to_dict() for r in rows]
    except Exception:
        return []
    finally:
        s.close()


def find_national_holiday(month: int, day: int) -> Optional[dict]:
    """หาวันสำคัญทางราชการตาม (เดือน, วัน) สุริยคติ"""
    s = SessionLocal()
    try:
        row = (
            s.query(NationalHoliday)
            .filter(NationalHoliday.month == month, NationalHoliday.day == day)
            .first()
        )
        return row.to_dict() if row else None
    except Exception:
        return None
    finally:
        s.close()


# ============================================================
# Backward-compat module-level lists (lazy-loaded)
# ============================================================
class _LazyList:
    """รายการที่โหลด on-demand จาก DB — เผื่อ caller เก่าใช้ list-style"""
    def __init__(self, loader):
        self._loader = loader
        self._cache: Optional[list] = None

    def _ensure(self):
        if self._cache is None:
            self._cache = self._loader()
        return self._cache

    def __iter__(self):
        return iter(self._ensure())

    def __len__(self):
        return len(self._ensure())

    def __getitem__(self, i):
        return self._ensure()[i]


CALENDAR_EPOCHS = _LazyList(get_calendar_epochs)
HOLY_DAYS = _LazyList(get_holy_days)
NATIONAL_HOLIDAYS = _LazyList(get_national_holidays)
