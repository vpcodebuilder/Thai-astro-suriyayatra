"""โมดูล 1: แปลงปฏิทินและคำนวณ Julian Day Number

- แปลง ค.ศ. <-> Julian Day Number (JDN)
- แปลง ค.ศ. -> จ.ศ. (จุลศักราช), ม.ศ. (มหาศักราช), พ.ศ. (พุทธศักราช)

ค่าคงที่อ้างอิง:
- จุดเริ่มต้นจุลศักราช = 21 มีนาคม ค.ศ. 638 (JDN 1954167)
- มหาศักราช เริ่ม ค.ศ. 78
- พุทธศักราช = ค.ศ. + 543
- ปีสุริยะไทย (สุริยยาตร์) = 365.25875 วัน
"""
from __future__ import annotations

from dataclasses import dataclass

# ---- ค่าคงที่ ----
JDN_CS_EPOCH = 1954167          # 21 มีนาคม ค.ศ. 638 = จ.ศ. 0 (จุดเริ่มต้น)
MS_EPOCH_YEAR = 78              # มหาศักราชเริ่มต้นปี ค.ศ. 78
CS_EPOCH_YEAR = 638             # จุลศักราชเริ่มต้นปี ค.ศ. 638
BE_OFFSET = 543                 # พ.ศ. = ค.ศ. + 543
THAI_SOLAR_YEAR = 365.25875     # วันต่อปีสุริยะไทย


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """แปลง ค.ศ. (ปฏิทินเกรกอเรียน) เป็น Julian Day Number
    สูตรมาตรฐานของ Fliegel & Van Flandern (1968)
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn


def jdn_to_gregorian(jdn: int) -> tuple[int, int, int]:
    """แปลง Julian Day Number กลับเป็น ค.ศ. (year, month, day)"""
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


def ce_to_chulasakarat(ce_year: int) -> int:
    """ค.ศ. -> จ.ศ. (จุลศักราช) อย่างง่าย
    หมายเหตุ: ขึ้นปี จ.ศ. ใหม่ราว 13-15 เมษายน (สงกรานต์)
    ฟังก์ชันนี้ใช้รูปแบบง่าย จ.ศ. = ค.ศ. - 638
    หากต้องการความแม่นยำในช่วงต้นปี ให้ใช้ jdn_to_chulasakarat แทน
    """
    return ce_year - CS_EPOCH_YEAR


def ce_to_mahasakarat(ce_year: int) -> int:
    """ค.ศ. -> ม.ศ. (มหาศักราช)"""
    return ce_year - MS_EPOCH_YEAR


def ce_to_buddhist(ce_year: int) -> int:
    """ค.ศ. -> พ.ศ. (พุทธศักราช)"""
    return ce_year + BE_OFFSET


def jdn_to_chulasakarat(jdn: int) -> int:
    """คำนวณ จ.ศ. จาก JDN โดยอ้างอิงปีสุริยะไทย (365.25875 วัน)
    คืนค่าปี จ.ศ. ที่นับจาก 21 มี.ค. 638 (JDN 1954167) เป็นปีที่ 0
    """
    days_since_epoch = jdn - JDN_CS_EPOCH
    return int(days_since_epoch // THAI_SOLAR_YEAR)


def ahargana(jdn: int) -> int:
    """อหรคณ = จำนวนวันที่นับจากจุดเริ่มต้นจุลศักราช
    ใช้เป็นตัวตั้งในการคำนวณตำแหน่งดาวเคราะห์แบบสุริยยาตร์
    """
    return jdn - JDN_CS_EPOCH


@dataclass
class ThaiDate:
    """ข้อมูลวันที่แบบไทย"""
    ce_year: int
    month: int
    day: int
    jdn: int
    chulasakarat: int
    mahasakarat: int
    buddhist: int

    @classmethod
    def from_gregorian(cls, year: int, month: int, day: int) -> "ThaiDate":
        jdn = gregorian_to_jdn(year, month, day)
        return cls(
            ce_year=year,
            month=month,
            day=day,
            jdn=jdn,
            chulasakarat=ce_to_chulasakarat(year),
            mahasakarat=ce_to_mahasakarat(year),
            buddhist=ce_to_buddhist(year),
        )

    def __str__(self) -> str:
        return (
            f"{self.day:02d}/{self.month:02d}/{self.ce_year} "
            f"(พ.ศ. {self.buddhist}, จ.ศ. {self.chulasakarat}, "
            f"ม.ศ. {self.mahasakarat}, JDN {self.jdn})"
        )
