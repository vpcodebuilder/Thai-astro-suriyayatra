"""ภพ 12 — ตามตำราอ.กานดา

ภพ 1 (ตนุ) = ราศีของลัคนา
ภพ 2 (กดุมภะ), 3 (สหัชชะ), ... → เดินไปข้างหน้าใน zodiac ("วนซ้าย" ในผัง)
ภพ 12 (วินาศ) = ราศีก่อนหน้าลัคนา

ตัวอย่าง: ลัคนา = พฤษภ → ภพ 2 = เมถุน, ภพ 12 = เมษ
"""

from __future__ import annotations

BHAVA_NAMES_TH: tuple[str, ...] = (
    "ตนุ", "กดุมภะ", "สหัชชะ", "พันธุ",
    "ปุตตะ", "อริ", "ปัตนิ", "มรณะ",
    "ศุภะ", "กัมมะ", "ลาภะ", "วินาศ",
)


def bhava_of(sign: int, lagna_sign: int) -> int:
    """ราศี (0-11) อยู่ในภพใด (1-12) เมื่อรู้ราศีลัคนา"""
    if not (0 <= sign <= 11):
        raise ValueError(f"sign ต้อง 0-11 ได้รับ {sign}")
    if not (0 <= lagna_sign <= 11):
        raise ValueError(f"lagna_sign ต้อง 0-11 ได้รับ {lagna_sign}")
    return ((sign - lagna_sign) % 12) + 1


def sign_of_bhava(bhava: int, lagna_sign: int) -> int:
    """ภพ X อยู่ราศีใด (0-11)"""
    if not (1 <= bhava <= 12):
        raise ValueError(f"bhava ต้อง 1-12 ได้รับ {bhava}")
    if not (0 <= lagna_sign <= 11):
        raise ValueError(f"lagna_sign ต้อง 0-11 ได้รับ {lagna_sign}")
    return (lagna_sign + bhava - 1) % 12


def bhava_name(bhava: int) -> str:
    if not (1 <= bhava <= 12):
        raise ValueError(f"bhava ต้อง 1-12 ได้รับ {bhava}")
    return BHAVA_NAMES_TH[bhava - 1]
