"""SQLAlchemy models สำหรับ Thai astrology calendar data

4 tables (Phase 8 Stage 1):
    - CalendarEpoch: เหตุการณ์สำคัญในประวัติศาสตร์ปฏิทินไทย (timeline)
    - HolyDay: วันสำคัญทางพุทธศาสนา (lunar-based)
    - NationalHoliday: วันสำคัญทางราชการ (solar-based)
    - AdhikamasaYear: ปีอธิกมาส / อธิกวาร / ปกติ (รายปี — ใช้แก้ off-by-1 ของสูตร)
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from webapp.db import Base


class CalendarEpoch(Base):
    """เหตุการณ์สำคัญในประวัติศาสตร์ปฏิทินไทย"""
    __tablename__ = "calendar_epochs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year_label = Column(String(50), nullable=False)   # "ค.ศ. 1782"
    ce_year = Column(Integer, nullable=False, index=True)
    be_year = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False, default="📅")
    type = Column(
        String(30), nullable=False, default="historical"
    )  # astronomical|buddhist|era|reform|historical
    image = Column(String(300), nullable=True)
    image_caption = Column(String(200), nullable=True)
    image_credit = Column(String(200), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)  # render order

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        d = {
            "year_label": self.year_label,
            "ce_year": self.ce_year,
            "be_year": self.be_year,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "type": self.type,
        }
        if self.image:
            d["image"] = self.image
            d["image_caption"] = self.image_caption
            d["image_credit"] = self.image_credit
        return d


class HolyDay(Base):
    """วันสำคัญทางพุทธศาสนา — เก็บเลขเดือนสำหรับปีปกติ
    (กฎ adhikamasa shift ทำที่ application layer)
    """
    __tablename__ = "holy_days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer, nullable=False)        # 1-12 (lunar)
    waxing = Column(Boolean, nullable=False)       # True = ขึ้น
    day = Column(Integer, nullable=False)          # 1-15
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False, default="🪷")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "waxing": self.waxing,
            "day": self.day,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
        }


class NationalHoliday(Base):
    """วันสำคัญทางราชการ/ประเพณีไทย (สุริยคติ — fixed solar date)"""
    __tablename__ = "national_holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer, nullable=False)        # 1-12 (solar)
    day = Column(Integer, nullable=False)          # 1-31
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False, default="🇹🇭")
    category = Column(
        String(30), nullable=False, default="holiday"
    )  # holiday|royal|national|tradition|memorial|international

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "day": self.day,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
        }


class AdhikamasaYear(Base):
    """ปีอธิกมาส / อธิกวาร / ปกติ — รายปีจุลศักราช (cs_year)

    ใช้แทน formula approximation ใน lunar.py:is_leap_month_year()
    - ถ้ามี entry ในตาราง → ใช้ค่านี้ (authoritative)
    - ถ้าไม่มี → fallback formula
    """
    __tablename__ = "adhikamasa_years"

    cs_year = Column(Integer, primary_key=True)    # จ.ศ.
    be_year = Column(Integer, nullable=False, index=True)
    ce_year = Column(Integer, nullable=False, index=True)
    type = Column(
        String(20), nullable=False
    )  # adhikamasa | adhikavara | both | normal
    source = Column(
        String(50), nullable=False, default="algorithm"
    )  # myhora | official | algorithm | user
    note = Column(Text, nullable=True)

    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    @property
    def is_adhikamasa(self) -> bool:
        return self.type in ("adhikamasa", "both")

    @property
    def is_adhikavara(self) -> bool:
        return self.type in ("adhikavara", "both")


class UsageStat(Base):
    """ตัวนับจำนวนการใช้งานเมนูต่างๆ
    เก็บแค่ counter ไม่เก็บข้อมูลดวงหรือ PII ของผู้ใช้
    """
    __tablename__ = "usage_stats"

    feature = Column(
        String(50), primary_key=True
    )  # 'suriyayatra_chart' | 'horathaynu_chart' | 'horathaynu_ask'
    count = Column(Integer, nullable=False, default=0)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

