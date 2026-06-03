"""Import ผลจาก scrape_adhikamasa.py เข้า DB (adhikamasa_years table)

Usage:
    python -m scripts.import_adhikamasa

อ่านจาก data/adhikamasa_scraped.json → upsert adhikamasa_years
source = 'myhora' สำหรับทุก entry ที่ import จากที่นี่
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Force UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from webapp.db import SessionLocal, DATABASE_URL
from webapp.models import AdhikamasaYear

INPUT_FILE = Path(__file__).parent.parent / "data" / "adhikamasa_scraped.json"


def main():
    if not INPUT_FILE.exists():
        print(f"[error] ไม่พบไฟล์: {INPUT_FILE}")
        print("  รัน scripts.scrape_adhikamasa ก่อน")
        sys.exit(1)

    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    print(f"[load] {len(data)} entries จาก {INPUT_FILE.name}")

    s = SessionLocal()
    try:
        inserted = updated = skipped = 0
        for be_str, info in data.items():
            be_year = int(be_str)
            kind = info["type"]
            evidence = info.get("evidence", "")
            if kind in ("error", "unknown"):
                skipped += 1
                continue

            cs_year = be_year - 1181        # จ.ศ.
            ce_year = be_year - 543         # ค.ศ.

            existing = s.query(AdhikamasaYear).filter_by(cs_year=cs_year).first()
            if existing:
                # อัปเดตเฉพาะถ้า source เป็น algorithm (ไม่ overwrite manual entries)
                if existing.source in ("algorithm", "myhora"):
                    existing.type = kind
                    existing.be_year = be_year
                    existing.ce_year = ce_year
                    existing.source = "myhora"
                    existing.note = evidence
                    updated += 1
                else:
                    skipped += 1
            else:
                s.add(AdhikamasaYear(
                    cs_year=cs_year,
                    be_year=be_year,
                    ce_year=ce_year,
                    type=kind,
                    source="myhora",
                    note=evidence,
                ))
                inserted += 1

        s.commit()
        print(f"[done] inserted={inserted}, updated={updated}, skipped={skipped}")
        print(f"[db] {DATABASE_URL}")
    except Exception as e:
        s.rollback()
        print(f"[error] {e}")
        raise
    finally:
        s.close()


if __name__ == "__main__":
    main()
