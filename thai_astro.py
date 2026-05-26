"""CLI: ระบบคำนวณดวงชะตาโหราศาสตร์ไทย (สุริยยาตร์)

ใช้งาน:
    python thai_astro.py --date 1990-05-15 --time 08:30 --province กรุงเทพมหานคร
    python thai_astro.py
"""
from __future__ import annotations

import argparse
import io
import sys
from datetime import date

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass

from thai_astro.chart import Chart
from thai_astro.display import render_chart
from thai_astro.prediction import predict
from thai_astro.lakkana import LOCALITY_ADJUST_SECONDS


def parse_date(s: str) -> tuple[int, int, int]:
    try:
        d = date.fromisoformat(s)
        return d.year, d.month, d.day
    except ValueError as e:
        raise SystemExit(f"รูปแบบวันที่ไม่ถูกต้อง: {s} (ต้องเป็น YYYY-MM-DD)") from e


def parse_time(s: str) -> tuple[int, int]:
    try:
        h, m = s.split(":")
        return int(h), int(m)
    except (ValueError, AttributeError) as e:
        raise SystemExit(f"รูปแบบเวลาไม่ถูกต้อง: {s} (ต้องเป็น HH:MM)") from e


def prompt(message: str, default: str | None = None) -> str:
    full = f"{message} [{default}]: " if default else f"{message}: "
    val = input(full).strip()
    return val if val else (default or "")


def interactive() -> tuple[int, int, int, int, int, str]:
    print("== ระบบคำนวณดวงชะตาโหราศาสตร์ไทย (สุริยยาตร์) ==")
    print()
    date_str = prompt("วันเกิด (YYYY-MM-DD)")
    time_str = prompt("เวลาเกิด (HH:MM)", "12:00")
    province = prompt("จังหวัด", "กรุงเทพมหานคร")
    y, mo, d = parse_date(date_str)
    h, mi = parse_time(time_str)
    return y, mo, d, h, mi, province


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="คำนวณดวงชะตาโหราศาสตร์ไทย (Suriyayat)")
    parser.add_argument("--date", help="วันเกิด YYYY-MM-DD")
    parser.add_argument("--time", default="12:00", help="เวลาเกิด HH:MM (default 12:00)")
    parser.add_argument("--province", default="กรุงเทพมหานคร",
                        help="จังหวัด (default กรุงเทพมหานคร)")
    parser.add_argument("--no-predict", action="store_true", help="ไม่แสดงคำพยากรณ์")
    parser.add_argument("--list-provinces", action="store_true",
                        help="แสดงรายชื่อจังหวัดที่รองรับ")
    args = parser.parse_args(argv)

    if args.list_provinces:
        for p in LOCALITY_ADJUST_SECONDS:
            print(p)
        return 0

    if args.date is None:
        y, mo, d, h, mi, province = interactive()
    else:
        y, mo, d = parse_date(args.date)
        h, mi = parse_time(args.time)
        province = args.province

    chart = Chart.calculate(y, mo, d, h, mi, province=province)
    print()
    print(render_chart(chart))
    if not args.no_predict:
        print()
        print(predict(chart))
    return 0


if __name__ == "__main__":
    sys.exit(main())
