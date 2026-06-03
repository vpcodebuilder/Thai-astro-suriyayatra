"""Usage counter helpers — เก็บจำนวนการใช้งานแต่ละเมนู

นโยบาย:
    - เก็บแค่ counter (จำนวนครั้ง) ไม่เก็บข้อมูลดวง / IP / cookie
    - increment เมื่อ user submit form หรือถามคำถาม
    - get_counts() ใช้ render ตัวเลขในหน้าเว็บ
"""
from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

from webapp.db import SessionLocal, DATABASE_URL
from webapp.models import UsageStat


# canonical feature keys
FEATURE_SURIYAYATRA = "suriyayatra_chart"   # กดผูกดวงสุริยยาตร์
FEATURE_HORATHAYNU_SET = "horathaynu_chart"  # กดตั้งดวงโหรทายหนู
FEATURE_HORATHAYNU_ASK = "horathaynu_ask"    # กดถามคำถามโหรทายหนู


def increment(feature: str) -> None:
    """+1 counter ของ feature (idempotent — สร้าง row ถ้ายังไม่มี)
    Best-effort: ถ้า DB error จะ silently ignore ไม่ขัด user flow
    """
    s = SessionLocal()
    try:
        if DATABASE_URL.startswith("postgresql"):
            stmt = pg_insert(UsageStat).values(feature=feature, count=1)
            stmt = stmt.on_conflict_do_update(
                index_elements=["feature"],
                set_={"count": UsageStat.count + 1},
            )
        else:
            # SQLite
            stmt = sqlite_insert(UsageStat).values(feature=feature, count=1)
            stmt = stmt.on_conflict_do_update(
                index_elements=["feature"],
                set_={"count": UsageStat.count + 1},
            )
        s.execute(stmt)
        s.commit()
    except Exception:
        s.rollback()
    finally:
        s.close()


def get_counts() -> dict[str, int]:
    """คืน dict {feature: count} สำหรับทุก feature ที่มี
    Fail-safe: ถ้า DB error (เช่น table ยังไม่ migrate) → {}
    """
    s = SessionLocal()
    try:
        rows = s.query(UsageStat).all()
        return {r.feature: r.count for r in rows}
    except Exception:
        return {}
    finally:
        s.close()
