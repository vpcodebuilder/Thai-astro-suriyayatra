# CLAUDE.md — thai_astro project memory

โปรเจกต์ระบบคำนวณและผูกดวงโหราศาสตร์ไทยตามวิธี **สุริยยาตร์** (Suriyayat)
ทั้ง CLI และ web app พร้อมระบบคำทำนายดาวจรกระทบดาวเดิม

> **กฎสำคัญ**: ห้ามใช้ library โหราศาสตร์/ดาราศาสตร์ตะวันตก (Swiss Ephemeris, Astropy ฯลฯ)
> สูตรทั้งหมด port มาจาก **Devtino.Astrology** (C#) ที่ใช้คัมภีร์สุริยสิทธานต์/สุริยยาตร์ไทยดั้งเดิม

---

## โครงสร้างไฟล์

```
D:\AI\claude code\thai_astro\
├── thai_astro/                       # Core astrology package
│   ├── __init__.py
│   ├── calendar.py                   # JDN, จ.ศ., ม.ศ., พ.ศ. utility
│   ├── boonnak.py                    # บูรณ์นาคทองเนียม: Thaloengsok, Surathin,
│   │                                 # Horakhun, DesireFactory (พื้นฐานสุริยยาตร์)
│   ├── planets.py                    # สมผุสดาว 9 ดวง (Sun, Moon, MinorPlanet,
│   │                                 # Rahu, Ketu) + Zodiac dataclass + Putchakoti
│   ├── lakkana.py                    # ลัคนา (อันโตนาที 12 ราศี + locality adjust 77 จังหวัด)
│   ├── chart.py                      # Chart dataclass รวมทุกอย่าง
│   ├── display.py                    # ASCII 4×3 grid (CLI)
│   ├── prediction.py                 # natal predictions เบื้องต้น
│   └── transit_prophecy.py           # คำทำนายดาวจรกระทบดาวเดิม + summary
├── webapp/                           # FastAPI web app
│   ├── __init__.py
│   ├── server.py                     # FastAPI routes + chart_to_view + circular layout
│   ├── templates/index.html          # Jinja2 (3-column layout + SVG zodiac)
│   └── static/
│       ├── styles.css                # ธีมไทย ทอง×แดงเลือดหมู
│       └── script.js                 # date picker sync + planet tooltip
├── tests/                            # 27 unit tests (รัน python -m unittest discover -s tests)
│   ├── test_calendar.py
│   ├── test_boonnak.py
│   ├── test_planets.py
│   └── test_chart.py
├── Devtino.Astrology/                # C# source (reference เท่านั้น ไม่ run)
├── thai_astro.py                     # CLI entry point
├── README.md
└── CLAUDE.md                         # ไฟล์นี้
```

**Reference C#**: `D:\AI\claude code\thai_astro\Devtino.Astrology\` — เปิดอ่านได้ ห้ามแก้

---

## วิธีรัน

```bash
# Web app (หลัก)
cd "D:/AI/claude code/thai_astro"
python -m uvicorn webapp.server:app --host 127.0.0.1 --port 8000 --reload
# เปิด http://127.0.0.1:8000

# CLI
python thai_astro.py --date 1990-05-15 --time 08:30 --province กรุงเทพมหานคร

# Tests
python -m unittest discover -s tests -v
```

**Dependencies**: fastapi, uvicorn, jinja2, python-multipart (ติดตั้งแล้ว)

**Windows console fix**: server.py และ thai_astro.py มี `sys.stdout.reconfigure("utf-8")`
เพราะ Windows cp874 พิมพ์ ° ไม่ได้

---

## สูตรสำคัญที่ port มาจาก Devtino (อย่าเปลี่ยน!)

### 1. ปฏิทิน / จ.ศ.
- จ.ศ. = พ.ศ. − 1181 = ค.ศ. − 638
- JDN ของ จ.ศ. 0 (21 มี.ค. 638 Julian = 24 มี.ค. 638 Gregorian) = **1954167**

### 2. เถลิงศก (Thaloengsok) สำหรับ จ.ศ. ≥ 1115 (เม.ย.)
```
result = (จศ × 0.25875)
       − floor(จศ/4 + 0.5)
       + floor(จศ/100 + 0.38)
       − floor(จศ/400 + 0.595)
       − 5.53375
month = 4
day = floor(result)
time_fraction = result − floor(result)
```

### 3. หรคุณ
```
HorakhunThaloengsok = floor((292207 × จศ + 373) / 800) + 1
Horakhun = HorakhunThaloengsok + Surathin (จำนวนวันจากเถลิงศก)
JDN = Horakhun + 1954167
```

### 4. DesireFactory (พื้นฐานของทุกการคำนวณ)
- `v = midnight_horakhun × 800 + floor(time_hours × 800/24) − 373`
- `thai_minor_era = v // 292207, kammatchaphon = v % 292207`
- `ujapon = (midnight_horakhun − 621) % 3232`
- `v2 = midnight_horakhun × 703 + 650 + floor(time_hours × 703/24)`
- `mas = v2 // 20760, awaman = v2 % 20760`
- `dithi = awaman // 692, ujapon_remainder = awaman % 692`

### 5. สมผุสดาว (เป็น arcminute, 21600 = 360°)
- **อาทิตย์**: หาร kammatchaphon ด้วย 24350/811/14 → arcmin offset −3
  - มันโทจจ์ = 4800 arcmin (80°), ตาราง Kan = `[0, 35, 67, 94, 116, 129, 134]`
- **จันทร์**: mattayom = `dithi×720 + floor(1.04×ujapon_rem) − 40 + sun_mattayom`
  - ตาราง Kan = `[0, 77, 148, 209, 256, 286, 296]`
- **ดาวรอง (5 ดวง)**: ใช้ PowerPlanet (Appa × 21600 + MattayomRawi) แล้ว 2-step manda + sighra
  - ตาราง Chaya = `[0, 244, 427, 488]`
  - MinorPlanet data 8 ค่า ต่อดาว — ดู `MINOR_PLANET_DATA` ใน planets.py
- **ราหู**: `BaseUp/20 + BaseDown/265`, Somput = `15150 − Mattayom`
- **เกตุ**: คำนวณจาก `(midnight − 344) % 679`, Somput = `21600 − Mattayom`

### 6. ลัคนา (อันโตนาที = นาทีต่อราศี)
```
เมษ:120, พฤษภ:96, เมถุน:72, กรกฎ:120, สิงห์:144, กันย์:168,
ตุลย์:168, พิจิก:144, ธนู:120, มกร:72, กุมภ์:96, มีน:120
รวม 1440 นาที = 24 ชม. ✓
```
- พระอาทิตย์ขึ้น = 06:00 (SunriseType.SixAM)
- locality offset (กรุงเทพฯ = 18:01 นาที:วินาที, ทุกจังหวัดอยู่ใน `LOCALITY_ADJUST_SECONDS`)
- เริ่มจากราศีของอาทิตย์ ลบเวลาตามอันโตนาทีจนหมด เดินไปราศีถัดไป
- เศษ → องศาในราศี

---

## หมายเหตุที่ต้องจำ

1. **ผลลัพธ์เป็น sidereal** (ระบบดาวฤกษ์) ตามตำราไทย ตรงกับปฏิทินสุริยยาตร์ที่พิมพ์ในไทย
   ต่างจาก tropical ฝรั่งราว 24° (ค่า ayanamsa ปัจจุบัน)
2. **ราหู-เกตุไม่ตรงข้ามกัน 180° เป๊ะ** เพราะ Devtino คำนวณแยกกัน
   (ราหูจาก PowerPlanet, เกตุจาก HorakhunMidnight) — เป็น feature ไม่ใช่บั๊ก
3. **arcsecond มักเป็น 0** เพราะสมผุสคำนวณเป็น integer arcminute ตามวิธีดั้งเดิม
4. **เวลาเกิดเป็น Thai standard time (UTC+7) ตามนาฬิกาท้องถิ่น** — locality offset
   จะถูกหักออกตอนคำนวณลัคนาตามจังหวัด
5. **HTML5 `<input type="date">` ให้ ISO YYYY-MM-DD (ค.ศ.)** แต่ user input ใช้
   `DD/MM/YYYY พ.ศ.` ผ่าน text + date picker icon (sync ด้วย JS ใน script.js)
6. **เลขดาว**: natal ใช้เลขไทย ๑-๙, transit ใช้เลขอารบิก 1-9
7. **ภพ 12** (ไม่ใช่ "บ้าน"): ตนุ กดุมภะ สหัชชะ พันธุ ปุตตะ อริ ปัตนิ มรณะ ศุภะ กัมมะ ลาภะ วินาส

---

## Web app — Features ที่ทำเสร็จแล้ว

### Layout 3 คอลัมน์ (จอ ≥ 1300px)
- **ซ้าย**: ฟอร์มข้อมูล (ชื่อ, วัน, เวลา, จังหวัด) + ฟอร์มดาวจร (optional)
- **กลาง**: จักรราศี SVG วงกลม + ตารางความหมายภพ 12
- **ขวา**: ตารางดาวกำเนิด + ดาวจร + ข้อมูลคำนวณ (collapsible)
- **ล่าง (เต็มแถว)**: สรุปคำทำนาย + ตารางคำทำนายเต็ม
- responsive: 1300px → 2 col, 900px → 1 col

### จักรราศี SVG
- **เมษอยู่ด้านบน** (มุม 90°) ทวนเข็มไป พฤษภ → เมถุน → ... → มีน
- ตำแหน่งราศี **fix ตลอด** ไม่หมุนตามลัคนา (Thai South-Indian style)
- เส้นแบ่ง 12 เส้นทุก 30° พอดี
- ขอบใน R=100, ขอบนอก R=260, ขอบนอกสุด (วงดาวจร) R=312
- **สัญลักษณ์ลัคนา "ลั"** วาดเป็นวงกลมสีครีมขอบแดงเลือดหมู ตำแหน่ง R=215
  ที่องศาเป๊ะภายในราศี (ไม่ใช่กลางราศี)
- **ดาวกำเนิด** chip ใหญ่ (r=14) เลขไทย ๑-๙ ที่ R=175
- **ดาวจร** chip เล็ก (r=11) เลขอารบิก 1-9 ที่ R=286 (ระหว่างขอบใน-ขอบนอกของวงดาวจร)
- chip layout: 1 ดวง=กลาง, 2-3=แถวเดียว, 4+=สองแถวซ้อน (in/out radius)
- **hover ดาว** → custom HTML tooltip แสดง ดาว/แหล่ง/ราศี/องศา/ลิปดา/ฟิลิปดา

### Form
- วันที่: text `DD/MM/YYYY (พ.ศ.)` + ปุ่ม 📅 date picker (sync 2 ทาง ผ่าน JS)
- เวลา: `<input type="time">` 24 ชั่วโมง
- จังหวัด: dropdown ครบ 77 จังหวัด (กรุงเทพฯ default)
- ดาวจร (optional): วันที่/เวลา/จังหวัด แยกต่างหาก
- Error handling: ทุก ValueError ถูก catch แสดง HTML error box (ไม่ใช่ JSON 422)

### คำทำนายดาวจรกระทบดาวเดิม
- module: `thai_astro/transit_prophecy.py`
- ใช้ **กุม** (ราศีเดียวกัน) + **เล็ง** (ตรงข้าม 6 ราศี) + optional ตรีโกณ/จัตุโกณ
- ตาราง CONJUNCTION_TEXT 81 entries (9×9) อ้างจาก อ.เทพย์ สาริกบุตร, พล.ต.ประยูร
- severity: 1-4 (สูง = ดาวจรเดินช้า + กุม)
- เรียงลำดับ: severity desc → slow planet first (เสาร์/ราหู/พฤหัส first)
- **`generate_summary()`** สร้างข้อความสรุปอ่านง่าย:
  - headline (1 ประโยค)
  - top 3 items พร้อม narrative + tone (good/heavy/warning/neutral)
  - good_items / warn_items list
  - conclusion (1 ประโยค)
- UI: card สรุปขึ้นบน → ตารางเต็มเรียงตามลำดับ + rank badges #1 #2 #3

---

## Tests สถานะ

27 tests ผ่านทั้งหมด ครอบคลุม:
- calendar.py (JDN conversion, era conversion)
- boonnak.py (Thaloengsok, Horakhun, Surathin, DesireFactory)
- planets.py (compact_angle, Putchakoti, ดาวทั้ง 9)
- chart.py (Chart.calculate, house lords, render)

ถ้าแก้สูตรใหม่ ต้องรัน `python -m unittest discover -s tests` ก่อน commit

---

## Workflow / Gotchas สำหรับการแก้ในอนาคต

1. **uvicorn --reload จับ .py แต่บางครั้งไม่ reload modules ที่ import ใหม่**
   → ถ้าเพิ่ม `import` ใหม่ใน server.py ให้ kill process แล้วรันใหม่:
   ```
   powershell -Command "Get-Process python* | Stop-Process -Force"
   ```

2. **Browser cache HTML form fields**
   → ผู้ใช้ที่เปิดหน้าค้างก่อนแก้ field name อาจ submit ด้วย field เก่า
   → ทุก Form() ใน server.py ใช้ default `""` แทน `...` (required) แล้ว validate manually
   → ส่งกลับเป็น HTML error box ไม่ใช่ 422 JSON

3. **Path "D:/AI/claude code/..."** มีช่องว่าง — ใช้ double quotes เมื่อ cd

4. **Thai chars ใน data-* attributes** ของ HTML ทำงานได้ปกติ ไม่ต้อง encode

5. **SVG dimension**: ถ้าจะขยายวงดาวจร ต้องปรับ
   `SVG_SIZE`, `R_OUTER_TRANSIT`, `R_TRANSIT` ใน server.py พร้อมกัน

---

## ไอเดียพัฒนาต่อ (ที่ยังไม่ทำ)

- เพิ่มคำพยากรณ์ตามทักษา (Taksa) ในตัว Chart
- เพิ่มกาลโยค (Kalayok)
- export PDF/PNG ผังดวง
- เก็บประวัติดวงผู้ใช้ (DB)
- เพิ่ม transit aspect แบบ orb (precise degree) นอกเหนือจาก rashi-based
- ราหู-เกตุให้ตรงข้ามกัน option (สำหรับคนที่ต้องการ)
- ตรวจอายุของผู้ขอดวง + เพิ่ม dasha prediction
- สูตรปรับ ayanamsa หากต้องการ tropical output

---

## Key files to reference quickly

| ต้องการแก้                | ไฟล์                              |
|---------------------------|-----------------------------------|
| สูตรสมผุสดาว             | `thai_astro/planets.py`           |
| สูตรลัคนา / locality      | `thai_astro/lakkana.py`           |
| Horakhun / DesireFactory  | `thai_astro/boonnak.py`           |
| คำทำนายดาวจร              | `thai_astro/transit_prophecy.py`  |
| ความหมายภพ 12             | `webapp/server.py` (BHAVA_MEANINGS) |
| layout / form / UI        | `webapp/templates/index.html`     |
| ธีม / สี / responsive     | `webapp/static/styles.css`        |
| tooltip / date sync       | `webapp/static/script.js`         |
| ค่าคงที่ SVG วงกลม        | `webapp/server.py` (R_OUTER, R_TRANSIT ฯลฯ) |
