"""ตารางสูตรยามอัฐุกาล (โหรทายหนู — ฉบับ อ.กานดา)

★ 14 ชุดสูตรประจำวัน (7 วัน × กลางวัน/กลางคืน) ยามละ 8 ช่อง
★ ตัวเลข 1-7 = หมายเลขดาว (1=อาทิตย์ 2=จันทร์ 3=อังคาร 4=พุธ 5=พฤหัส 6=ศุกร์ 7=เสาร์)

ใช้คู่กับ caster แบบ "chain walking":
    counts = derive_counts(day, asked_yam, n_stars)
    chart  = caster.cast_chain(asked_yam, counts)

หมายเหตุ:
- "หัวใจยามกลางวัน" = แถวอาทิตย์ = 1-6-4-2-7-5-3-1
- "หัวใจยามกลางคืน" = แถวอาทิตย์ = 1-5-2-6-3-7-4-1
- วันถัดไปเลื่อน +1 มอด 7
"""

from __future__ import annotations

YAM_PER_HALF = 8        # 8 ยาม/ครึ่งวัน
DAY_COUNT = 7

# ตารางหัวใจ — แถวอาทิตย์ (day index 0)
HEART_DAY:   tuple[int, ...] = (1, 6, 4, 2, 7, 5, 3, 1)
HEART_NIGHT: tuple[int, ...] = (1, 5, 2, 6, 3, 7, 4, 1)


def _build(heart: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """สร้างตารางครบ 7 วันจาก heart โดยเลื่อน +1 mod 7 ในแต่ละค่า

    เช่น heart_day อาทิตย์ = (1,6,4,2,7,5,3,1)
         จันทร์            = (2,7,5,3,1,6,4,2)
         อังคาร            = (3,1,6,4,2,7,5,3)
         ...
    """
    rows: list[tuple[int, ...]] = []
    for d in range(DAY_COUNT):
        row = tuple(((v - 1 + d) % 7) + 1 for v in heart)
        rows.append(row)
    return tuple(rows)


# YAM_TABLE_DAY[day_index] = (8 ค่า สำหรับยาม 1-8 กลางวัน)
YAM_TABLE_DAY:   tuple[tuple[int, ...], ...] = _build(HEART_DAY)
YAM_TABLE_NIGHT: tuple[tuple[int, ...], ...] = _build(HEART_NIGHT)


def yam_value(day: int, yam_index: int, is_night: bool = False) -> int:
    """คืนค่าในตารางสูตร

    Args:
        day: 0=อาทิตย์ ... 6=เสาร์
        yam_index: 1-8 (ภายในครึ่งวัน)
        is_night: True ถ้าใช้ตารางกลางคืน
    """
    if not (0 <= day <= 6):
        raise ValueError(f"day ต้อง 0-6 ได้รับ {day}")
    if not (1 <= yam_index <= YAM_PER_HALF):
        raise ValueError(f"yam_index ต้อง 1-{YAM_PER_HALF} ได้รับ {yam_index}")
    table = YAM_TABLE_NIGHT if is_night else YAM_TABLE_DAY
    return table[day][yam_index - 1]


def yam_index_global_to_local(yam_index: int) -> tuple[int, bool]:
    """แปลง yam_index 1-16 (รวมวัน+คืน) → (local 1-8, is_night)"""
    if not (1 <= yam_index <= 16):
        raise ValueError(f"yam_index ต้อง 1-16 ได้รับ {yam_index}")
    if yam_index <= 8:
        return yam_index, False
    return yam_index - 8, True


# ====================================================================
# Counts derivation — สำหรับ chain walking
# ====================================================================

N_STARS_DEFAULT = 11
"""ดาวลอย 9 ดวง (1,2,3,4,6,7,5,9,0) + ลัคนา + 1 reserved = 11 placements"""


def derive_counts(day: int, yam_index: int,
                  n_stars: int = N_STARS_DEFAULT,
                  overrides: dict[int, int] | None = None) -> list[int]:
    """หาค่า "นับ N ช่อง" สำหรับดาวลอยแต่ละตัว — ping-pong walking

    กฎ (ฉบับ อ.กานดา):
    - เริ่มอ่านที่ตำแหน่ง asked_yam ของแถวประจำวัน (กลางวัน/กลางคืน ตาม yam_index)
    - อ่านค่าให้ดาว 1 ตำแหน่งปัจจุบัน → เดิน +1 ตำแหน่ง → ดาว 2 → ...
    - **เคล็ดลับ:** เมื่อถึงสุดแถว (ตำแหน่ง 1 หรือ 8) → "ย้ำ" ค่านั้นอีกครั้ง (ใช้ซ้ำ)
      แล้วเด้งกลับทิศตรงข้าม → เดินไปจนสุดอีกฝั่ง → ย้ำ → เด้งกลับอีก ...
    - ทำจนได้ครบ n_stars ค่า

    ตัวอย่าง วันพุธ ยาม 4 (แถว = 4 2 7 5 3 1 6 4):
        pos: 4→5→6→7→8 ┐ 8(ย้ำ) ┐ 7→6→5→4→3
        ค่า: 5 3 1 6 4   4         6 1 3 5 7
        → counts = [5, 3, 1, 6, 4, 4, 6, 1, 3, 5, 7]

    ตัวอย่าง คืนวันจันทร์ ยาม 8 (แถว = 2 6 3 7 4 1 5 2):
        pos: 8 ┐ 8(ย้ำ) ┐ 7→6→5→4→3→2→1 ┐ 1(ย้ำ) ┐ 2
        ค่า: 2   2         5 1 4 7 3 6 2   2         6
        → counts = [2, 2, 5, 1, 4, 7, 3, 6, 2, 2, 6]
    """
    overrides = overrides or {}
    local_yam, is_night = yam_index_global_to_local(yam_index)
    row = (YAM_TABLE_NIGHT if is_night else YAM_TABLE_DAY)[day]

    counts: list[int] = []
    pos = local_yam        # ตำแหน่งปัจจุบันใน row (1-8)
    direction = +1         # +1 = เดินไป (ค่ามากขึ้น), -1 = ถอยหลัง

    for star_idx in range(n_stars):
        if star_idx in overrides:
            counts.append(overrides[star_idx])
        else:
            counts.append(row[pos - 1])

        # คำนวณตำแหน่งถัดไป
        next_pos = pos + direction
        if next_pos > YAM_PER_HALF or next_pos < 1:
            # ชนขอบ → ย้ำที่เดิม (pos ไม่เปลี่ยน) + กลับทิศ
            direction = -direction
        else:
            pos = next_pos

    return counts
