"""Phase 3 — Binary verdict (โอกาส X%) สำหรับคำถาม yes/no

คะแนนรวมจาก:
    + dignity ของ sig (อุจน์/เกษตร/มูล = บวก, นิจ/ประ = ลบ)
    + ตำแหน่งภพ sig (กัมพ 1/4/7/10 = +1, ตรีโกณ 1/5/9 = +1, ทุกข์ 6/8/12 = -2)
    + house relation จากภพคำถาม (Phase 4 score)
    + ดาวมิตร (benefic) ใน same bhava กับ sig = +1
    + ดาวร้าย (malefic) ใน same bhava = -1
    + จันทร์อยู่ในภพดี (1/4/5/7/9/10/11) = +1
    + ดาวอ่อน (นิจ/ประ) ของจันทร์ในทุกข์ = -1

Output:
    Verdict(score, tier, label, text, factors)
    tier ∈ {"very_high", "high", "moderate", "low", "very_low"}
"""
from __future__ import annotations

from dataclasses import dataclass, field

from thai_astro.horathaynu.core.caster import Chart
from thai_astro.horathaynu.core.dignity_score import SigDignity, compute_sig_dignity


# ภพดี/ทุกข์
KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
GOOD_HOUSES = KENDRA | TRIKONA | {11}    # เกณฑ์+ตรีโกณ+ลาภะ

# ดาวมิตร (benefic) vs ดาวร้าย (malefic) ในโหราศาสตร์ไทย/พระเวท
BENEFICS = {"jupiter", "venus", "moon", "mercury"}
MALEFICS = {"saturn", "mars", "rahu", "ketu", "sun"}  # อาทิตย์เป็น malefic อ่อน


@dataclass
class Verdict:
    score: float                       # คะแนนรวม (อาจติดลบ)
    tier: str                          # very_high / high / moderate / low / very_low
    percentage: int                    # 5-95 (ค่าโดยประมาณ)
    label: str                         # "🎯 โอกาสสูง — น่าจะได้แน่"
    text: str                          # คำแนะนำต่อ
    factors: list[str] = field(default_factory=list)   # เหตุผลที่ทำให้คะแนนเป็นแบบนี้


def _tier_from_score(score: float) -> tuple[str, int, str, str]:
    """แปลงคะแนน → (tier, percentage, label, advice)"""
    if score >= 4:
        return ("very_high", 85,
                "🎯 โอกาสสูงมาก — แทบจะแน่นอน",
                "เดินหน้าได้เต็มที่ ดาวเข้าข้างคุณทุกทาง")
    if score >= 2:
        return ("high", 70,
                "🎯 โอกาสสูง — น่าจะได้",
                "ลงมือทำได้ มีปัจจัยหนุนหลายข้อ ระวังเรื่องเล็กน้อยพอ")
    if score >= 0:
        return ("moderate", 50,
                "🎯 ก้ำกึ่ง — 50/50",
                "ขึ้นกับความพยายามและจังหวะของคุณ ตัดสินใจให้ระมัดระวัง")
    if score >= -2:
        return ("low", 30,
                "🎯 โอกาสต่ำ — เสี่ยงพลาด",
                "ดาวไม่ค่อยเข้าข้าง เลื่อนเวลา/เปลี่ยนแผนได้ จะดีกว่า")
    return ("very_low", 15,
            "🎯 โอกาสต่ำมาก — ครั้งนี้ยังไม่ใช่",
            "ปัจจัยขัดเยอะ พักไว้ก่อน รอจังหวะใหม่ดีกว่า")


def compute_verdict(
    chart: Chart,
    sig_planet: str,
    sig_house: int,
    sig_rashi: int,
    asked_bhava: int = 0,
    house_relation_score: int = 0,
) -> Verdict:
    """คำนวณ verdict สำหรับคำถาม yes/no.

    Parameters:
        chart: ผังโหรทายหนู
        sig_planet: ดาว significator key
        sig_house: ภพที่ sig อยู่ (1-12)
        sig_rashi: ราศีที่ sig อยู่ (0-11)
        asked_bhava: ภพหลักของคำถาม (1-12) — 0 = ไม่ได้ระบุ
        house_relation_score: score จาก Phase 4 (ส่งเข้ามาจาก orchestrator)
    """
    score: float = 0.0
    factors: list[str] = []

    # ===== 1. Dignity ของ sig =====
    dignity = compute_sig_dignity(sig_planet, sig_rashi)
    if dignity.strength >= 2:
        score += 2
        factors.append(f"+2 sig อยู่ {dignity.label}")
    elif dignity.strength == 1:
        score += 1
        factors.append(f"+1 sig อยู่ {dignity.label}")
    elif dignity.strength <= -2:
        score -= 2
        factors.append(f"−2 sig ตก {dignity.label}")
    elif dignity.strength == -1:
        score -= 1
        factors.append(f"−1 sig อยู่ {dignity.label}")

    # ===== 2. ตำแหน่งภพ sig =====
    if sig_house in KENDRA:
        score += 1
        factors.append(f"+1 sig ในเกณฑ์ ({sig_house})")
    if sig_house in TRIKONA:
        score += 1
        factors.append(f"+1 sig ในตรีโกณ ({sig_house})")
    if sig_house == 11:
        score += 1
        factors.append("+1 sig ในลาภะ (สมหวัง)")
    if sig_house in DUSTHANA:
        score -= 2
        factors.append(f"−2 sig ในทุกข์ ({sig_house})")

    # ===== 3. House relation (จาก Phase 4) =====
    if asked_bhava >= 1:
        score += house_relation_score
        if house_relation_score != 0:
            factors.append(f"{'+' if house_relation_score > 0 else ''}{house_relation_score} ระยะห่างภพคำถาม→sig")

    # ===== 4. ดาวมิตร/ร้าย ในภพเดียวกับ sig =====
    same_bhava_planets = [
        k for k, p in chart.placements.items()
        if p.house == sig_house and k != sig_planet and k != "lagna"
    ]
    benefics_here = [p for p in same_bhava_planets if p in BENEFICS]
    malefics_here = [p for p in same_bhava_planets if p in MALEFICS]
    if benefics_here:
        score += len(benefics_here)
        factors.append(f"+{len(benefics_here)} ดาวมิตร ({', '.join(benefics_here)}) ในภพเดียวกัน")
    if malefics_here:
        score -= len(malefics_here)
        factors.append(f"−{len(malefics_here)} ดาวร้าย ({', '.join(malefics_here)}) ในภพเดียวกัน")

    # ===== 5. จันทร์ (อารมณ์/ความรู้สึกของผู้ถาม) =====
    if "moon" in chart.placements:
        moon_p = chart.placements["moon"]
        if moon_p.house in GOOD_HOUSES:
            score += 1
            factors.append(f"+1 จันทร์ในภพดี (ภพ {moon_p.house})")
        elif moon_p.house in DUSTHANA:
            score -= 1
            factors.append(f"−1 จันทร์ในทุกข์ (ภพ {moon_p.house})")

    # ===== สรุป tier =====
    tier, percentage, label, advice = _tier_from_score(score)
    return Verdict(
        score=score,
        tier=tier,
        percentage=percentage,
        label=label,
        text=advice,
        factors=factors,
    )


__all__ = ["Verdict", "compute_verdict", "BENEFICS", "MALEFICS"]
