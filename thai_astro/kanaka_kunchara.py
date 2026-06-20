"""เกณฑ์กนกกุญชร — ตามตำราอ.หลวงวุฒิรณพัศตุ์
(เก็บตารางอยู่ใน knowledge/ฤกษ์.xlsx sheet "กนกกุญชร")

หลักการ
-------
ตารางมีแกน 27 ฤกษ์ × 7 วาร — แต่ละช่องคือกฎ "ลัคนาราศีของฤกษ์"
ตัวอย่างกฎที่ปรากฏใน cell:
    "ห้ามกรกฎ"                         → ห้ามวางลัคนาราศีกรกฎ
    "ตุลย์พิจิกมังกรดี"                → ลัคนาเป็น ตุลย์/พิจิก/มกร = ดี
    "มิถุนดีนัก"                       → ลัคนาเป็น เมถุน = ดีนัก (เด่นมาก)
    "ห้ามราศีอื่น-ตุลย์ดีนัก"          → อนุญาตเฉพาะตุลย์เท่านั้น (ดีนัก)
    "ห้ามมิถุนธนู-กันย์ตุลย์พิจิกกุมภ์ดี" → ห้าม 2 + ดี 4
    "ธนูมังกรกันย์ดี-ห้ามปลูกเรือน"    → ดี 3 + หมายเหตุห้ามปลูกบ้าน

API
---
    parse_cell(text)     → ParsedCell
    check(lagna_rasi, nak_number, wan, lagna_rasi_name) → KKResult
"""
from dataclasses import dataclass, field
from typing import Set, Optional
from functools import lru_cache

from .kanaka_kunchara_table import KANAKA_KUNCHARA_RAW

# ============================================================
# ราศี (canonical = ตามที่ chart ใช้: เมถุน/มกร)
# ============================================================
RASI_CANONICAL = [
    "เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
    "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน",
]

# Aliases ที่ใช้ใน spreadsheet → canonical (chart format)
RASI_ALIAS = {
    "มิถุน": "เมถุน",   # spreadsheet ใช้ มิถุน
    "มังกร": "มกร",     # spreadsheet ใช้ มังกร
    "สิงห็": "สิงห์",   # typo ในตาราง
    "มิน": "มีน",       # typo "มิน" แทน "มีน"
    "กุม": "กุมภ์",     # ตัด "ภ์" ตกหล่นใน cell "ห้ามเมษสิงห์กุม"
}

# token ที่ใช้สแกน (ทั้ง canonical + alias) เรียงยาวก่อนเพื่อ greedy
_TOKENS = sorted(set(RASI_CANONICAL) | set(RASI_ALIAS.keys()), key=len, reverse=True)


def _extract_rasis(text: str) -> list:
    """Greedy: หาชื่อราศีในข้อความที่เรียงต่อกัน คืน list canonical names"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for tok in _TOKENS:
            if text.startswith(tok, i):
                canon = RASI_ALIAS.get(tok, tok)
                if canon in RASI_CANONICAL:
                    out.append(canon)
                i += len(tok)
                matched = True
                break
        if not matched:
            i += 1
    return out


# ============================================================
# Parsed cell
# ============================================================
@dataclass
class ParsedCell:
    forbidden: Set[str] = field(default_factory=set)        # ห้าม X
    good: Set[str] = field(default_factory=set)             # ดี
    very_good: Set[str] = field(default_factory=set)        # ดีนัก
    exclusive_listed: bool = False                          # "ห้ามราศีอื่น" → อนุญาตเฉพาะที่ระบุ
    extra_note: str = ""                                    # "ห้ามปลูกเรือน" ฯลฯ
    raw: str = ""


@lru_cache(maxsize=300)
def parse_cell(text: str) -> ParsedCell:
    """Parse cell text → ParsedCell. cache เพราะมีหลาย cell ซ้ำกัน"""
    result = ParsedCell(raw=text)
    if not text or not text.strip():
        return result
    segments = [s.strip() for s in text.split("-") if s.strip()]
    for seg in segments:
        if seg == "ห้ามราศีอื่น":
            result.exclusive_listed = True
            continue
        if seg == "ห้ามปลูกเรือน":
            result.extra_note = "ห้ามปลูกเรือน (ไม่เหมาะปลูกบ้าน/สร้างเรือน)"
            continue
        # "ห้าม..." ห้ามราศีเฉพาะ
        if seg.startswith("ห้าม"):
            rest = seg[len("ห้าม"):]
            for r in _extract_rasis(rest):
                result.forbidden.add(r)
            continue
        # "..ดีนัก" (เด่น)
        if seg.endswith("ดีนัก"):
            rest = seg[:-len("ดีนัก")]
            for r in _extract_rasis(rest):
                result.very_good.add(r)
            continue
        # "..ดี" (ดีทั่วไป)
        if seg.endswith("ดี"):
            rest = seg[:-len("ดี")]
            for r in _extract_rasis(rest):
                result.good.add(r)
            continue
        # ไม่ตรงรูปแบบ — เก็บไว้เป็น note
        if seg:
            result.extra_note = (result.extra_note + " | " + seg).strip(" |")
    return result


# ============================================================
# Lookup
# ============================================================
@dataclass
class KKResult:
    """ผลการตรวจกนกกุญชร"""
    tone: str           # "good" / "warning" / "neutral"
    matched: bool       # True = เข้าเกณฑ์ชัด (ดี/ห้าม); False = ไม่ระบุชัด
    label: str          # "ดีนัก" / "ดี" / "ห้าม" / "ไม่ระบุชัด"
    cell_text: str      # ข้อความ cell ดิบ
    rule_summary: str   # สรุปกฎใน cell (เช่น "ดี: ตุลย์,พิจิก,มกร | ห้าม: -")
    extra_note: str = ""


def _summarize(cell: ParsedCell) -> str:
    parts = []
    if cell.very_good:
        parts.append("ดีนัก: " + ", ".join(sorted(cell.very_good)))
    if cell.good:
        parts.append("ดี: " + ", ".join(sorted(cell.good)))
    if cell.forbidden:
        parts.append("ห้าม: " + ", ".join(sorted(cell.forbidden)))
    if cell.exclusive_listed:
        parts.append("(ห้ามราศีอื่น)")
    return " | ".join(parts) if parts else "ไม่ระบุชัด"


def check(lagna_rasi_name: str, nak_number: int, wan: int) -> KKResult:
    """ตรวจกนกกุญชร: ลัคนาที่ราศีนี้ใน (ฤกษ์, วาร) นี้ ผ่านหรือไม่

    Args:
        lagna_rasi_name: ชื่อราศีลัคนา (canonical: เมถุน/มกร ตามที่ chart ใช้)
        nak_number: 1-27 ตำแหน่งนักษัตรของจันทร์
        wan: 1=อา ... 7=ส
    """
    cell_text = KANAKA_KUNCHARA_RAW.get(nak_number, {}).get(wan, "")
    cell = parse_cell(cell_text)
    summary = _summarize(cell)

    if lagna_rasi_name in cell.very_good:
        return KKResult("good", True, "ดีนัก", cell_text, summary, cell.extra_note)
    if lagna_rasi_name in cell.good:
        return KKResult("good", True, "ดี", cell_text, summary, cell.extra_note)
    if lagna_rasi_name in cell.forbidden:
        return KKResult("warning", True, "ห้าม", cell_text, summary, cell.extra_note)
    if cell.exclusive_listed:
        # ไม่อยู่ในรายการอนุญาต → ห้ามอัตโนมัติ
        return KKResult("warning", True, "ห้าม (ราศีอื่น)", cell_text, summary, cell.extra_note)
    # ไม่ระบุชัด — neutral (ไม่ได้ห้าม แต่ก็ไม่ดีพิเศษ)
    return KKResult("neutral", False, "ไม่ระบุชัด", cell_text, summary, cell.extra_note)
