"""Scraper: ดึงตารางปีอธิกมาส/อธิกวาร จาก myhora.com (BE 1181-3000)

URL pattern: https://myhora.com/calendar/thai-astro-{BE_YEAR}.aspx
หน้าแต่ละปีจะมีข้อความเช่น:
    "ปีปกติสุรทิน ปกติมาส ปกติวาร"     → normal
    "ปีปกติสุรทิน อธิกมาส ปกติวาร"      → adhikamasa
    "ปีปกติสุรทิน ปกติมาส อธิกวาร"      → adhikavara
    "ปีอธิกสุรทิน ปกติมาส ปกติวาร"      → solar leap (ไม่นับเป็น lunar adhikamasa)

Output: data/adhikamasa_scraped.json {be_year: {type, html_snippet}}

Usage:
    python -m scripts.scrape_adhikamasa --start 2500 --end 2600  # ทดสอบ
    python -m scripts.scrape_adhikamasa --start 1181 --end 3000  # full

มี checkpoint resume: ถ้าไฟล์ output มีอยู่แล้ว จะ skip ปีที่ scrape แล้ว
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

# Force UTF-8 stdout (Windows console = cp874)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_URL = "https://myhora.com/calendar/thai-astro-{be}.aspx"
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "adhikamasa_scraped.json"

# Pattern จับ classifications หลักของปี ใน "หัวข้อ" ของหน้า
# รูปแบบ HTML: "ปกติสุรทิน  <u>อธิกมาส</u> ปกติวาร" (หรือ "อธิกสุรทิน ปกติมาส อธิกวาร")
RX_STRIP_TAGS = re.compile(r"<[^>]+>")
RX_HEADER = re.compile(
    r"(ปกติสุรทิน|อธิกสุรทิน)\s*(ปกติมาส|อธิกมาส)\s*(ปกติวาร|อธิกวาร)"
)
# myhora.com title: "ปฏิทิน 100 ปี 2569 ปฏิทินร้อยปี ปีXXX - myhora.com"
RX_TITLE = re.compile(r"<title>[^<]*?(\d{4})[^<]*</title>")


def classify(html: str, expected_be: int) -> tuple[str, str]:
    """คืน (type, evidence_snippet)
        type: 'adhikamasa' | 'adhikavara' | 'both' | 'normal' | 'out_of_range' | 'unknown'

    out_of_range: ปีที่ขอ ≠ ปีที่ส่งกลับใน title — myhora.com ครอบคลุม BE 2300-2700
    ส่วนปีอื่นจะคืนหน้า default ของ 2569
    """
    # ตรวจ title — ถ้าปีไม่ตรง → out of range
    tm = RX_TITLE.search(html)
    if tm:
        try:
            shown_year = int(tm.group(1))
            if shown_year != expected_be:
                return "out_of_range", f"title shows {shown_year}, not {expected_be}"
        except ValueError:
            pass

    # ลบ HTML tags ก่อนค้น (เพื่อรองรับ <u>อธิกมาส</u>)
    clean = RX_STRIP_TAGS.sub("", html)

    # หา occurrence แรกของ classification header ในหน้า
    m = RX_HEADER.search(clean)
    if not m:
        return "unknown", "(no header found)"

    is_amasa = m.group(2) == "อธิกมาส"
    is_avara = m.group(3) == "อธิกวาร"
    evidence = m.group(0)
    if is_amasa and is_avara:
        return "both", evidence
    if is_amasa:
        return "adhikamasa", evidence
    if is_avara:
        return "adhikavara", evidence
    return "normal", evidence


def fetch_year(be_year: int, session: requests.Session, timeout: int = 15) -> str | None:
    """ดึง HTML ของหน้าปีนั้น ๆ — return None ถ้า error"""
    url = BASE_URL.format(be=be_year)
    try:
        r = session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  [error {be_year}] {e}", file=sys.stderr)
        return None


def load_checkpoint() -> dict[str, dict]:
    if OUTPUT_FILE.exists():
        try:
            return json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_checkpoint(data: dict[str, dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1181, help="ปี พ.ศ. เริ่มต้น")
    parser.add_argument("--end", type=int, default=3000, help="ปี พ.ศ. สิ้นสุด")
    parser.add_argument("--delay", type=float, default=0.4,
                        help="หน่วงระหว่าง request (วินาที)")
    parser.add_argument("--force", action="store_true",
                        help="ขูดซ้ำแม้มี checkpoint แล้ว")
    args = parser.parse_args()

    data = load_checkpoint() if not args.force else {}
    print(f"[start] {args.start}-{args.end} ({args.end - args.start + 1} years)")
    print(f"[checkpoint] มีอยู่ {len(data)} entries")

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
    })

    saved_at_count = 0
    for be in range(args.start, args.end + 1):
        key = str(be)
        if key in data and not args.force:
            continue

        html = fetch_year(be, session)
        if html is None:
            data[key] = {"type": "error", "evidence": None}
        else:
            kind, evidence = classify(html, expected_be=be)
            data[key] = {"type": kind, "evidence": evidence}
            print(f"  BE {be}: {kind:13s} | {evidence[:60]}")

        # save every 20 entries
        saved_at_count += 1
        if saved_at_count % 20 == 0:
            save_checkpoint(data)

        time.sleep(args.delay)

    save_checkpoint(data)
    # summary
    counts = {}
    for v in data.values():
        counts[v["type"]] = counts.get(v["type"], 0) + 1
    print(f"\n[done] saved → {OUTPUT_FILE}")
    print(f"[summary] {counts}")


if __name__ == "__main__":
    main()
