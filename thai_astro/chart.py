"""โครงสร้างข้อมูลดวงชะตา (Birth chart) - ใช้สูตรสุริยยาตร์ Devtino"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .boonnak import Desire, build_desire, ce_to_be
from .planets import (
    Planet, RASI_LORD, RASI_NAMES_TH, PLANET_ORDER, compute_all,
)
from .lakkana import (
    Lakkana, compute_lakkana, BANGKOK_LOCALITY_SECONDS, LOCALITY_ADJUST_SECONDS,
)


@dataclass
class Chart:
    """ดวงชะตา"""
    # ข้อมูลเกิด
    ce_year: int
    be_year: int
    month: int
    day: int
    hour: int
    minute: int
    province: str

    # ผลการคำนวณ
    desire: Desire
    ascendant: Lakkana
    planets: Dict[str, Planet]

    # บ้านที่ 1..12
    house_rasis: List[int] = field(init=False)
    house_lords: Dict[int, str] = field(init=False)
    chart_lord: str = field(init=False)
    house_planets: Dict[int, List[str]] = field(init=False)

    def __post_init__(self) -> None:
        asc_rasi = self.ascendant.zodiac.rasi
        self.house_rasis = [(asc_rasi + i) % 12 for i in range(12)]
        self.house_lords = {
            i + 1: RASI_LORD[self.house_rasis[i]] for i in range(12)
        }
        self.chart_lord = RASI_LORD[asc_rasi]

        self.house_planets = {i + 1: [] for i in range(12)}
        for name, planet in self.planets.items():
            house = self._rasi_to_house(planet.zodiac.rasi)
            self.house_planets[house].append(name)

    def _rasi_to_house(self, rasi: int) -> int:
        asc_rasi = self.ascendant.zodiac.rasi
        return ((rasi - asc_rasi) % 12) + 1

    @classmethod
    def calculate(
        cls,
        year: int, month: int, day: int,
        hour: int = 12, minute: int = 0,
        province: str = "กรุงเทพมหานคร",
    ) -> "Chart":
        """คำนวณดวงชะตาจาก ค.ศ./วัน/เวลา และจังหวัด

        เวลาที่ส่งเข้ามาเป็น Thai standard time (UTC+7) ตามนาฬิกาท้องถิ่น
        ค่าปรับเวลาท้องถิ่น (locality) จะถูกหักออกในการคำนวณลัคนา
        """
        be_year = ce_to_be(year)
        desire = build_desire(be_year, month, day, hour, minute)
        planets = compute_all(desire)
        sun = planets["อาทิตย์"]

        locality = LOCALITY_ADJUST_SECONDS.get(province, BANGKOK_LOCALITY_SECONDS)
        ascendant = compute_lakkana(
            desire, sun,
            sunrise_hours=6.0,
            locality_seconds=locality,
        )

        return cls(
            ce_year=year, be_year=be_year,
            month=month, day=day, hour=hour, minute=minute,
            province=province,
            desire=desire,
            ascendant=ascendant,
            planets=planets,
        )
