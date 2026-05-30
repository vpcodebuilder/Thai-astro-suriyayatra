"""ขับดาวเข้าจักร — chain walking (ตำราอ.กานดา)

หลักการ:
1. ดาว 1 (อาทิตย์) เริ่มจากราศีพฤษภเสมอ
2. ดาว n (n≥2) เริ่มจากราศีของดาว n−1 (cell ล่าสุดที่วางไป)
3. "นับ N ช่อง" = นับโดยรวมเซลล์ต้นทางเป็น 1 → เดินไปข้างหน้าใน zodiac (N−1 cells)
4. ลัคนา ถือเป็นดาวลำดับหนึ่งใน chain (ตามตัวอย่างอ.กานดา อยู่ระหว่างดาว 8 และดาว 9)

ลำดับการวาง (เริ่มจากดาว 1):
    1, 2, 3, 4, 5, 6, 7, 8, ลัคนา, 9, 0   (= 11 placements)

planet_key สำหรับแต่ละลำดับ — กำหนดผ่าน PLACEMENT_ORDER
"""

from __future__ import annotations

from dataclasses import dataclass, field

from thai_astro.horathaynu.data.yam_table import (
    N_STARS_DEFAULT,
    derive_counts,
)


# ราศีของพฤษภ (taurus) — ลัคนาเริ่มที่นี่เสมอตามตำราอ.กานดา
START_SIGN = 1   # 0=เมษ, 1=พฤษภ


# ลำดับการวาง 11 ตำแหน่ง (index 0-10)
# planet_key อ้างถึง slot ของ Chart.placements
PLACEMENT_ORDER: tuple[str, ...] = (
    "sun",      # ดาว 1
    "moon",     # ดาว 2
    "mars",     # ดาว 3
    "mercury",  # ดาว 4
    "jupiter",  # ดาว 5
    "venus",    # ดาว 6
    "saturn",   # ดาว 7
    "rahu",     # ดาว 8
    "lagna",    # ลัคนา
    "ketu",     # ดาว 9
    "uranus",   # ดาว 0 (มฤตยู)
)


@dataclass(frozen=True)
class Placement:
    sign: int   # 0-11
    house: int  # 1-12


@dataclass
class Chart:
    day: int
    yam_index: int          # 1-16 (global)
    ascendant_sign: int     # = ราศีของ lagna
    placements: dict[str, Placement] = field(default_factory=dict)
    counts: list[int] = field(default_factory=list)
    """counts ที่ใช้ในการเดิน chain — เก็บไว้ debug/inspect"""

    def sign_of(self, planet_key: str) -> int:
        return self.placements[planet_key].sign

    def house_of(self, planet_key: str) -> int:
        return self.placements[planet_key].house

    def planets_in_house(self, house: int) -> list[str]:
        return [k for k, p in self.placements.items() if p.house == house]

    def planets_in_sign(self, sign: int) -> list[str]:
        return [k for k, p in self.placements.items() if p.sign == sign]


def walk(start_sign: int, count: int) -> int:
    """เดิน N ช่องจากราศี start_sign (รวมต้นทางเป็น 1, ไปข้างหน้าใน zodiac)

    Args:
        start_sign: 0-11
        count: ≥1; count=1 → อยู่ที่ start_sign, count=2 → ราศีถัดไป, ...

    Returns:
        ราศีปลายทาง 0-11
    """
    if count < 1:
        raise ValueError(f"count ต้อง ≥1 ได้รับ {count}")
    return (start_sign + count - 1) % 12


def cast_chain(day: int, yam_index: int,
               counts: list[int] | None = None,
               overrides: dict[int, int] | None = None) -> Chart:
    """ขับดาวเข้าจักรด้วย chain walking

    Args:
        day: 0-6 (อาทิตย์-เสาร์)
        yam_index: 1-16 (1-8 กลางวัน, 9-16 กลางคืน)
        counts: ถ้าระบุมา ใช้ตรงๆ (length ต้อง = len(PLACEMENT_ORDER))
        overrides: ถ้าไม่ได้ระบุ counts จะใช้ derive_counts() พร้อม overrides

    Raises:
        NotImplementedError: ถ้า derive_counts หา count ของบาง star ไม่ได้
                             และไม่มี override
    """
    if not (0 <= day <= 6):
        raise ValueError(f"day ต้อง 0-6 ได้รับ {day}")
    if not (1 <= yam_index <= 16):
        raise ValueError(f"yam_index ต้อง 1-16 ได้รับ {yam_index}")

    n = len(PLACEMENT_ORDER)
    if counts is None:
        counts = derive_counts(day, yam_index, n_stars=n, overrides=overrides)
    elif len(counts) != n:
        raise ValueError(
            f"counts ต้องมี {n} ค่า (= len(PLACEMENT_ORDER)) ได้รับ {len(counts)}"
        )

    chart = Chart(day=day, yam_index=yam_index, ascendant_sign=START_SIGN,
                  counts=list(counts))

    current_sign = START_SIGN
    placed: dict[str, Placement] = {}
    for key, c in zip(PLACEMENT_ORDER, counts):
        current_sign = walk(current_sign, c)
        # house จะคำนวณภายหลังเมื่อรู้ ascendant_sign จริง (= sign ของ lagna)
        placed[key] = Placement(sign=current_sign, house=0)  # placeholder

    if "lagna" not in placed:
        raise RuntimeError("PLACEMENT_ORDER ต้องมี 'lagna' อย่างน้อยหนึ่งครั้ง")

    asc = placed["lagna"].sign
    chart.ascendant_sign = asc

    # คำนวณ house ของทุกดาวจาก asc ที่แท้จริง
    for key, p in placed.items():
        house = ((p.sign - asc) % 12) + 1
        chart.placements[key] = Placement(sign=p.sign, house=house)

    return chart


# ========== Backward-compat (legacy lookup API) ==========
# ฟังก์ชันเดิมก่อน refactor — ยังคงไว้สำหรับ tests ที่ใช้ yam_table แบบเก่า
# จะเลิกใช้ในเวอร์ชันถัดไป

def cast(day: int, yam_index: int) -> Chart:
    """legacy alias → cast_chain (ไม่รับ counts override)"""
    return cast_chain(day, yam_index)


def sign_to_house(sign: int, ascendant_sign: int) -> int:
    return ((sign - ascendant_sign) % 12) + 1


def house_to_sign(house: int, ascendant_sign: int) -> int:
    return (ascendant_sign + house - 1) % 12
