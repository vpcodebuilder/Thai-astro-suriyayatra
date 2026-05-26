"""โมดูลพื้นฐาน "บูรณ์นาคทองเนียม" (BoonnakThongniam)

Port จาก Devtino.Astrology/BoonnakThongniam/* และ Fraction/*

ค่าที่สำคัญ:
- จุลศักราช (จ.ศ.) = พ.ศ. - 1181 = ค.ศ. - 638
- เถลิงศก (Thaloengsok) = วันปีใหม่ทางสุริยยาตร์
- สุรทิน (Surathin) = จำนวนวันที่นับจากเถลิงศกถึงวันประสงค์
- หรคุณ (Horakhun) = เลขวันสะสมตั้งแต่ start of era
- กรรมจุปา (Kammatchaphon) = เศษกำลังของหรคุณ
- อุจจพล (Ujapon) = ตำแหน่งของจันทร์อุจจ์
- มาส (Mas), อวมาน (Awaman), ดิถี (Dithi) = ปัจจัยจันทรคติ
- DesireFactory = รวมค่าทั้งหมดสำหรับวันเวลาที่ต้องการ (Desire)

สูตรค่าคงที่:
- 292207 = chandrakala (กำลังจันทร์ต่อปีสุริยยาตร์)
- 800    = ตัวหารหรคุณ
- 373    = offset หรคุณ
- 703    = กำลังมาสต่อหรคุณ
- 650    = offset มาส
- 20760  = ตัวหารมาส
- 692    = ตัวหารอวมาน
- 3232   = ตัวหารอุจจพล
- 621    = offset อุจจพล
- 1181   = พ.ศ. - จ.ศ.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta


# ============================================================
# ค่าคงที่ Era
# ============================================================
BE_TO_CS_OFFSET = 1181      # จ.ศ. = พ.ศ. - 1181
BE_TO_CE_OFFSET = 543       # ค.ศ. = พ.ศ. - 543
CS_TO_CE_OFFSET = 638       # ค.ศ. = จ.ศ. + 638


def be_to_cs(be_year: int) -> int:
    """พ.ศ. -> จ.ศ."""
    return be_year - BE_TO_CS_OFFSET


def cs_to_be(cs_year: int) -> int:
    """จ.ศ. -> พ.ศ."""
    return cs_year + BE_TO_CS_OFFSET


def ce_to_be(ce_year: int) -> int:
    """ค.ศ. -> พ.ศ."""
    return ce_year + BE_TO_CE_OFFSET


def be_to_ce(be_year: int) -> int:
    """พ.ศ. -> ค.ศ."""
    return be_year - BE_TO_CE_OFFSET


# ============================================================
# Thaloengsok - วันเถลิงศก (ปีใหม่สุริยยาตร์)
# ============================================================

@dataclass
class ThaloengsokResult:
    """ผลการคำนวณวันเถลิงศก"""
    cs_year: int             # จ.ศ.
    be_year: int             # พ.ศ.
    month: int               # เดือน (เกรกอเรียน)
    day: int                 # วัน
    time_fraction: float     # เศษเวลาของวัน (0..1)

    @property
    def hour(self) -> int:
        return int(self.time_fraction * 24)

    @property
    def minute(self) -> int:
        return int((self.time_fraction * 24 - self.hour) * 60)

    @property
    def second(self) -> int:
        return int(((self.time_fraction * 24 - self.hour) * 60 - self.minute) * 60)

    def to_datetime(self) -> datetime:
        """แปลงเป็น datetime (ค.ศ.)"""
        ce_year = be_to_ce(self.be_year)
        return datetime(
            ce_year, self.month, self.day,
            self.hour, self.minute, self.second,
        )


def thaloengsok(cs_year: int) -> ThaloengsokResult:
    """คำนวณวันเถลิงศกของ จ.ศ. ที่กำหนด

    แบ่ง 3 ช่วงตามที่ Devtino.Astrology ทำ:
    - จ.ศ. -3739 ถึง -2398: เดือนกุมภาพันธ์
    - จ.ศ. -2397 ถึง 1114: เดือนมีนาคม
    - จ.ศ. 1115 ขึ้นไป (ยุคปัจจุบัน): เดือนเมษายน

    สูตรช่วงเมษายน (สำคัญที่สุดสำหรับยุคปัจจุบัน):
      result = (จศ × 0.25875)
             − floor(จศ/4 + 0.5)
             + floor(จศ/100 + 0.38)
             − floor(จศ/400 + 0.595)
             − 5.53375
      month = 4
      day = floor(result)
      time_fraction = result − floor(result)
    """
    from_factor = 0.25875 * cs_year

    if -3739 <= cs_year <= -2398:
        result = from_factor - math.floor(cs_year / 4.0 + 0.5) + 50.46625
        month = 2
    elif -2397 <= cs_year <= 1114:
        result = from_factor - math.floor(cs_year / 4.0 + 0.5) + 22.46625
        month = 3
    else:
        result = (
            from_factor
            - math.floor(cs_year / 4.0 + 0.5)
            + math.floor(cs_year / 100.0 + 0.38)
            - math.floor(cs_year / 400.0 + 0.595)
            - 5.53375
        )
        month = 4

    day = int(math.floor(result))
    time_fraction = result - math.floor(result)

    return ThaloengsokResult(
        cs_year=cs_year,
        be_year=cs_to_be(cs_year),
        month=month,
        day=day,
        time_fraction=time_fraction,
    )


# ============================================================
# Horakhun (หรคุณ)
# ============================================================

def horakhun_thaloengsok(cs_year: int) -> int:
    """หรคุณ ณ วันเถลิงศกของ จ.ศ. ที่กำหนด

    สูตร: floor((292207 × จ.ศ. + 373) / 800) + 1
    """
    return (292207 * cs_year + 373) // 800 + 1


# ============================================================
# Surathin (สุรทิน) - จำนวนวันจากเถลิงศก
# ============================================================

@dataclass
class SurathinResult:
    """ผลการคำนวณสุรทิน"""
    total_days: int                          # จำนวนวันจากเถลิงศก
    thaloengsok_cs_year: int                 # จ.ศ. ของเถลิงศกที่ใช้
    thaloengsok: ThaloengsokResult           # ข้อมูลเถลิงศก


def surathin(be_year: int, month: int, day: int) -> SurathinResult:
    """คำนวณสุรทิน (จำนวนวันจากเถลิงศก) ของวันประสงค์

    ถ้าวันเกิดอยู่ก่อนเถลิงศกในปีพ.ศ. ที่ระบุ ให้ใช้เถลิงศกของปีก่อนหน้า
    (เพราะปีใหม่สุริยยาตร์อยู่กลางเมษายน ไม่ตรงกับวันที่ 1 มกราคม)
    """
    ce_year = be_to_ce(be_year)
    target = date(ce_year, month, day)

    cs_year = be_to_cs(be_year)
    t = thaloengsok(cs_year)
    thaloengsok_date = date(be_to_ce(t.be_year), t.month, t.day)

    if target < thaloengsok_date:
        # เกิดก่อนเถลิงศกของปีนี้ -> ใช้เถลิงศกของปีก่อน
        cs_year -= 1
        t = thaloengsok(cs_year)
        thaloengsok_date = date(be_to_ce(t.be_year), t.month, t.day)

    total_days = (target - thaloengsok_date).days
    return SurathinResult(
        total_days=total_days,
        thaloengsok_cs_year=cs_year,
        thaloengsok=t,
    )


# ============================================================
# DesireFactory - รวมค่าทั้งหมดสำหรับการคำนวณตำแหน่งดาว
# ============================================================

@dataclass
class Desire:
    """รวมค่า "ปรารถนา" (Desire) สำหรับวันเวลาเกิดที่กำหนด

    เป็นพื้นฐานของการคำนวณตำแหน่งดาวเคราะห์ทุกดวงในสุริยยาตร์
    """
    be_year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    time_hours: float                # เวลาในวัน (ทศนิยม ชม., 0..24)

    horakhun: int                    # หรคุณรวม ณ วันเกิด
    horakhun_at_midnight: int        # = horakhun - 1 (ใช้ในสูตรหลายตัว)
    julian_date: int                 # = horakhun + 1954167

    thai_minor_era: int              # จ.ศ. ที่คำนวณใหม่ (อาจต่างจาก be-1181 เล็กน้อย)
    kammatchaphon: int               # เศษกรรมจุปา
    ujapon: int                      # เศษอุจจพล
    mas: int                         # quotient ของมาส
    awaman: int                      # remainder ของมาส (= เลขหลังหารมาสรอบเดียว)
    dithi: int                       # quotient ของอวมาน
    ujapon_remainder: int            # remainder สุดท้าย (UjaponRemainderDesire)

    surathin: SurathinResult         # ข้อมูลสุรทิน (เผื่อใช้ debug)


def build_desire(
    be_year: int, month: int, day: int,
    hour: int = 0, minute: int = 0, second: int = 0,
) -> Desire:
    """สร้าง Desire จาก พ.ศ./เดือน/วัน/เวลา

    ขั้นตอน (port มาจาก DesireFactory.Build() ของ Devtino):
    1. หาสุรทิน (TotalDays) จากวันเถลิงศก
    2. หรคุณ = หรคุณเถลิงศก + TotalDays
    3. คำนวณ KammatchaphonDesire, ThaiMinorEra ใหม่ผ่านสูตร v/292207
    4. คำนวณ Ujapon, Mas, Awaman, Dithi, UjaponRemainder
    """
    sr = surathin(be_year, month, day)
    h_thaloengsok = horakhun_thaloengsok(sr.thaloengsok_cs_year)
    horakhun = h_thaloengsok + sr.total_days
    horakhun_midnight = horakhun - 1

    time_hours = hour + minute / 60.0 + second / 3600.0

    # v = midnight*800 + floor(time_hours*800/24) - 373
    v = horakhun_midnight * 800 + int(math.floor(time_hours * 800 / 24.0)) - 373
    # ThaiMinorEra ใหม่ และ KammatchaphonDesire
    thai_minor_era = v // 292207
    kammatchaphon = v % 292207

    # อุจจพล: (DesireAtMidnight - 621) mod 3232
    ujapon = (horakhun_midnight - 621) % 3232

    # มาส/อวมาน
    v2 = horakhun_midnight * 703 + 650 + int(math.floor(time_hours * 703 / 24.0))
    mas = v2 // 20760
    awaman = v2 % 20760

    # ดิถี/อุจจพล remainder
    dithi = awaman // 692
    ujapon_remainder = awaman % 692

    return Desire(
        be_year=be_year, month=month, day=day,
        hour=hour, minute=minute, second=second,
        time_hours=time_hours,
        horakhun=horakhun,
        horakhun_at_midnight=horakhun_midnight,
        julian_date=horakhun + 1954167,
        thai_minor_era=thai_minor_era,
        kammatchaphon=kammatchaphon,
        ujapon=ujapon,
        mas=mas,
        awaman=awaman,
        dithi=dithi,
        ujapon_remainder=ujapon_remainder,
        surathin=sr,
    )
