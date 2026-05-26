"""แสดงผลตารางดวงชะตาแบบไทย (4×3)"""
from __future__ import annotations

from typing import List

from .chart import Chart
from .planets import RASI_NAMES_TH, PLANET_ORDER


PLANET_ABBR = {
    "อาทิตย์": "อา",
    "จันทร์": "จ",
    "อังคาร": "อ",
    "พุธ": "พ",
    "พฤหัสบดี": "พฤ",
    "ศุกร์": "ศ",
    "เสาร์": "ส",
    "ราหู": "รา",
    "เกตุ": "เก",
}

LAYOUT = [
    [12, 1, 2, 3],
    [11, 0, 0, 4],
    [10, 0, 0, 5],
    [9, 8, 7, 6],
]
CELL_WIDTH = 12


def _is_combining(ch: str) -> bool:
    code = ord(ch)
    return (
        0x0E31 <= code <= 0x0E31
        or 0x0E34 <= code <= 0x0E3A
        or 0x0E47 <= code <= 0x0E4E
    )


def _pad_thai(text: str, width: int) -> str:
    display_len = sum(1 for ch in text if not _is_combining(ch))
    pad = width - display_len
    if pad < 0:
        return text[:width]
    return text + " " * pad


def _house_cell_lines(chart: Chart, house: int) -> List[str]:
    rasi = chart.house_rasis[house - 1]
    rasi_name = RASI_NAMES_TH[rasi]
    asc_marker = " ลค." if house == 1 else ""
    line1 = f"บ้าน{house}{asc_marker}"
    line2 = rasi_name

    planets_here = chart.house_planets[house]
    abbrevs = [PLANET_ABBR.get(p, p) for p in planets_here]
    if len(abbrevs) <= 3:
        line3 = " ".join(abbrevs)
        line4 = ""
    else:
        mid = (len(abbrevs) + 1) // 2
        line3 = " ".join(abbrevs[:mid])
        line4 = " ".join(abbrevs[mid:])
    return [line1, line2, line3, line4]


def _center_info_lines(chart: Chart) -> List[str]:
    return [
        f"เกิด: {chart.day:02d}/{chart.month:02d}/{chart.ce_year}",
        f"พ.ศ. {chart.be_year}",
        f"เวลา: {chart.hour:02d}:{chart.minute:02d} น.",
        f"ลัคนา: {chart.ascendant.format_dms()}",
        f"เจ้าชะตา: {chart.chart_lord}",
        f"จังหวัด: {chart.province}",
    ]


def render_chart(chart: Chart) -> str:
    lines: List[str] = []
    width = CELL_WIDTH * 4 + 5

    lines.append("=" * width)
    lines.append("ดวงชะตา (Thai Astrology Chart - Suriyayat)")
    lines.append("=" * width)

    center_lines = _center_info_lines(chart)
    border = "+" + ("-" * CELL_WIDTH + "+") * 4
    lines.append(border)

    for row in range(4):
        for sub in range(4):
            row_text = "|"
            for col in range(4):
                house = LAYOUT[row][col]
                if house == 0:
                    if col == 1 and row in (1, 2):
                        idx = (row - 1) * 4 + sub
                        text = center_lines[idx] if idx < len(center_lines) else ""
                        row_text += _pad_thai(text, CELL_WIDTH * 2 + 1) + "|"
                    else:
                        continue
                else:
                    cell = _house_cell_lines(chart, house)
                    text = cell[sub] if sub < len(cell) else ""
                    row_text += _pad_thai(text, CELL_WIDTH) + "|"
            lines.append(row_text)
        lines.append(border)

    lines.append("")
    lines.append("ตำแหน่งดาว (สมผุส):")
    lines.append("-" * 56)
    for name in PLANET_ORDER:
        if name in chart.planets:
            p = chart.planets[name]
            retro = " (พักร์)" if p.retrograde else ""
            house = chart._rasi_to_house(p.zodiac.rasi)
            lines.append(
                f"  {name:<10} {p.format_dms():<22} บ้านที่ {house:<2}{retro}"
            )

    lines.append("")
    lines.append("ดาวเจ้าเรือนแต่ละบ้าน:")
    lines.append("-" * 56)
    for h in range(1, 13):
        rasi = chart.house_rasis[h - 1]
        lines.append(
            f"  บ้านที่ {h:<2} ({RASI_NAMES_TH[rasi]:<5}) -> {chart.house_lords[h]}"
        )

    # debug info: หรคุณ, จศ, ฯลฯ
    d = chart.desire
    sr = d.surathin
    lines.append("")
    lines.append("ข้อมูลคำนวณ:")
    lines.append("-" * 56)
    lines.append(f"  จ.ศ.: {sr.thaloengsok_cs_year}  เถลิงศก: {sr.thaloengsok.day}/{sr.thaloengsok.month}/{sr.thaloengsok.be_year}")
    lines.append(f"  สุรทิน: {sr.total_days} วัน")
    lines.append(f"  หรคุณ: {d.horakhun}  JDN: {d.julian_date}")
    lines.append(f"  กรรมจุปา: {d.kammatchaphon}  อุจจพล: {d.ujapon}")
    lines.append(f"  มาส: {d.mas}  อวมาน: {d.awaman}  ดิถี: {d.dithi}  อุจ.เศษ: {d.ujapon_remainder}")

    return "\n".join(lines)
