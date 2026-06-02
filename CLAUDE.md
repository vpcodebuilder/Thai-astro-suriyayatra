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

- เพิ่มกาลโยค (Kalayok)
- export PDF/PNG ผังดวง
- เก็บประวัติดวงผู้ใช้ (DB)
- เพิ่ม transit aspect แบบ orb (precise degree) นอกเหนือจาก rashi-based
- ราหู-เกตุให้ตรงข้ามกัน option (สำหรับคนที่ต้องการ)
- สูตรปรับ ayanamsa หากต้องการ tropical output
- ตำราจันทรคติแม่นยำสุด: ใส่ตารางอธิกวาร (8/8 vs 7-30) แทน approximation จาก synodic
- ดาวเคราะห์ทั้ง 10 ให้ออก arc-second จริง (ต้องเขียนสูตรใหม่ไม่ใช้ truncate)

---

## Key files to reference quickly

| ต้องการแก้                                | ไฟล์                                     |
|-------------------------------------------|------------------------------------------|
| สูตรสมผุสดาว 10 ดวง (รวมมฤตยู)            | `thai_astro/planets.py`                  |
| สูตรลัคนา + arc-second + locality 77 จว.   | `thai_astro/lakkana.py`                  |
| Horakhun / DesireFactory                  | `thai_astro/boonnak.py`                  |
| คำทำนายดาวจรกระทบดาวเดิม                 | `thai_astro/transit_prophecy.py`         |
| **เจ้าเรือนครองภพ (natal + transit)**     | `thai_astro/bhava_lord_prophecy.py`      |
| **ตำแหน่งกำลังดาว + เกณฑ์โยค**            | `thai_astro/dignities.py`                |
| **ทักษา (natal + transit + overlay)**     | `thai_astro/taksa.py`                    |
| **บทพูดของโหร (oracle synthesis)**        | `thai_astro/oracle_narrative.py`         |
| **ปฏิทินจันทรคติไทย**                     | `thai_astro/lunar.py`                    |
| ความหมายภพ 12                             | `webapp/server.py` (BHAVA_MEANINGS)      |
| layout / form / view tabs / UI            | `webapp/templates/index.html`            |
| ธีม / สี / responsive / view rules        | `webapp/static/styles.css`               |
| tooltip / date sync / tab switching       | `webapp/static/script.js`                |
| Deploy config (Railway)                   | `Procfile`, `requirements.txt`, `runtime.txt` |

---

# ===== Session 2 Updates =====
# ฟีเจอร์ที่เพิ่มหลังจาก Initial commit ทั้งหมด

## โมดูลใหม่ใน `thai_astro/`

### `bhava_lord_prophecy.py` — เจ้าเรือนครองภพ
- **หลักการ**: เจ้าเรือนภพ X (ดาวเจ้าราศีที่ครองภพ) ไปสถิตภพ Y → ทาย "เรื่อง X เกิดผ่าน Y"
- 144 combinations (12×12) — 80+ override (เฉพาะคู่สำคัญ) + template generic ตาม tone
- **2 มุมมอง**:
  1. `predict_natal_lords()` — ดูดวงพื้นฐาน (ตลอดชีวิต)
  2. `predict_transit_lords()` — เจ้าเรือนเดิม ขณะนี้ดาวจรอยู่ภพไหน
- จำแนกโทน: good / warning / neutral พร้อมตรวจ **วิปริต-ราชโยค** (ทุกข์ชนทุกข์ = ดี)

### `dignities.py` — ตำแหน่งกำลังดาว + เกณฑ์โยค
- **Dignities รายดวง**: อุจน์ / นิจ / มูลตรีโกณ / เกษตร / มิตร / ประ (ศัตรู) / สมพล
  - Strength score: -3 ถึง +3
  - `EXALTATION_RASI`, `DEBILITATION_RASI`, `SWAKSHETRA`, `MULATRIKONA`, `PLANET_RELATIONS`
- **เกณฑ์โยค auto-detect**:
  - **ปทุมเกณฑ์** (Padma) — ดาวหลัก ≥ 4 ดวงในเกณฑ์ (1,4,7,10)
  - **มหาภูตเกณฑ์** — ดาวหลัก ≥ 3 ดวงในตรีโกณ (1,5,9)
  - **อุดมเกณฑ์** — ดาวอุจน์ ≥ 2 ดวง
  - **องค์เกณฑ์** — ดาวกำลังแข็ง (อุจน์/เกษตร/มูล) ≥ 3 ดวง
  - **นิจภังคราชโยค** — ดาวนิจ แต่เจ้าราศีที่รับได้ตำแหน่งดี → พลิกร้ายเป็นดี
  - **<ดาว>ได้อุจน์** — โยคย่อยรายดวง

### `taksa.py` — ทักษา (ดาวประจำวันเกิด 8 ดวง 8 ทิศ)
- **ดาวประจำวันเกิด** จาก weekday() + กฎพิเศษ: พุธหลัง 18:00 = ราหู
- **ลำดับ 8 ดาวทักษา (อัฏฐดาว)**: `TAKSA_CYCLE = อาทิตย์→จันทร์→อังคาร→พุธ→เสาร์→พฤหัสบดี→ราหู→ศุกร์`
- **8 ตำแหน่งบริวาร**: บริวาร / อายุ / เดช / ศรี / มูละ / อุตสาหะ / มนตรี / กาลกิณี
- **8 ทิศ (FIX, ตำราไทยมาตรฐาน)**: ศุกร์-อุดร(N) / อาทิตย์-อีสาน(NE) / จันทร์-บูรพา(E) / อังคาร-อาคเนย์(SE) / พุธ-ทักษิณ(S) / เสาร์-หรดี(SW) / พฤหัสบดี-ประจิม(W) / ราหู-พายัพ(NW)
- **มหาทักษาดาษา 96 ปี**: 8 ดาว × 12 ปีต่อดาว (`DASA_YEARS_PER_PLANET = 12`)
- **คำทำนาย 64 cells** (`PREDICTION`): ดาว × ตำแหน่งบริวาร เขียนเฉพาะแต่ละบท
- **ทักษาจร (Transit Taksa)** — `TRANSIT_CYCLE_9 = 8 ทิศ + ตากลาง` (= พฤหัสบดี)
  - เดิน 1 ตา/ปี เริ่มจากดาวบริวาร, เมื่อถึงอาทิตย์→แวะตากลาง→ต่อจันทร์
  - แสดงเลขอารบิกในแต่ละช่อง = ปีอายุที่ทักษาจรตก
- **Overlay × Natal combos** (เมื่อทักษาจรตกตากลาง):
  - ตั้งภพใหม่ใช้พฤหัสบดีเป็นบริวาร → จับคู่ overlay×natal ผ่านดาวเดียวกัน
  - ตัวอย่าง: เกิดอาทิตย์, ปีตากลาง → บริวารจร(พฤหัส) + อุตสาหะเดิม(พฤหัส) = ตัวคุณ × การงาน
  - 40+ overrides เฉพาะคู่สำคัญใน `OVERLAY_NATAL_OVERRIDES`
- **ดาวจรกระทบดาวทักษา (transit_aspects_on_taksa)**:
  - `TRANSIT_PLANET_X_BHAVA` 9 ดาว × 8 ภพ = 72 entries
  - กระจายตามคุณสมบัติของดาวจร (ไม่ใช่แค่ธีมภพ) ป้องกันคำซ้ำ

### `oracle_narrative.py` — บทพูดของโหร (Oracle Reading)
- สังเคราะห์ทุก source: transit aspects + bhava lord (natal+transit) + dignities + yogas
- โครงสร้าง: greeting → yoga callouts → headline → life_areas → opportunities/warnings → closing
- **คำศัพท์ร่วมสมัย** (`MODERN_NATAL_THEME`, `LIFE_AREAS`): แปลภพโบราณ→คำคนยุคนี้
- **กลไกพลิกร้ายเป็นดี**: ถ้ามี ปทุม/อุดม/นิจภังค → ทุกคำเตือนเติมท้าย "แต่ด้วยเกณฑ์ดวงพื้นฐาน เรื่องนี้จะไม่หนักเท่าที่ควรเป็น"
- **Deterministic randomness**: seed จาก birth date/time → บทพูดของคนเดียวกันคงที่
- 4 tone classes: good / heavy / mixed / neutral

### `lunar.py` — ปฏิทินจันทรคติไทย
- **ดิถี → ขึ้น/แรม X ค่ำ** จาก `desire.dithi` (0-29)
  - 0-14 = ขึ้น 1-15 ค่ำ (waxing)
  - 15-29 = แรม 1-15 ค่ำ (waning)
- **เดือนจันทรคติ** (1-12: อ้าย ยี่ สาม ... สิบสอง)
  - สูตร: `((floor((surathin_days + 7) / 29.530588) + 4) % 12) + 1`
  - offset 7 + synodic month 29.530588 — verified กับวันสำคัญพุทธ 10/10 ผ่าน
- **ปีอธิกมาส** (port `ThaiLunarYear.cs`): `(grate_year - 0.45222) % 2.7118886 < 1`
- **ปีนักษัตร 12 ตัว**: ชวด ฉลู ขาล ... กุน. CE 1972 = ปีชวด (`(ce - 1972) % 12`)
- ใช้ `desire.surathin.thaloengsok_cs_year` เป็น CS อ้างอิง (ครอบคลุม Songkran boundary)

## โมดูลเดิมที่ปรับ

### `planets.py`
- **เพิ่ม "มฤตยู" (Uranus)** เป็นดาวที่ 10 ใน `compute_all()`
  - ใช้ `MINOR_PLANET_DATA_URANUS = (1, 84, 1, 7224, 16277, 7440, 38640, 3/7)` (port จาก Devtino)
  - `PLANET_ORDER` มี 10 ดวง: + "มฤตยู" ท้าย
- `Zodiac.from_arcminutes()` มี field `arcsecond` (default 0)

### `lakkana.py`
- **คำนวณ arc-second จริงสำหรับลัคนา**: เก็บ fractional arcmin → `arcsecond = (frac × 60)`
- ดาวเคราะห์ทั่วไปยัง 00″ (เพราะ Devtino formula = integer arcmin)

## UI ใน `webapp/`

### View Tabs (`templates/index.html` + `static/script.js`)
- **2 tabs sticky บนแถวล่าง**: 📖 ดูดวง / 🔬 ศึกษาโหราศาสตร์
- HTML class system: `view-general` / `view-student` / `view-both`
- CSS: `body.view-X .view-Y { display: none }` (specificity-based)
- **Body default**: `class="view-general"` ตั้งใน HTML (JS overrides จาก localStorage)
- **Layout เป็น 2-col เสมอ** (form 340 | chart 1fr): กลายเป็น 1-col ที่ <900px
  - แถวบน (chart-section) **อยู่ทั้ง 2 view** เพราะเป็น "หัวใจ" ของผัง
  - view-tabs sticky ใต้แถวบน
  - detail-section ลงไปใต้ tabs (full width ด้วย `grid-column: 1/-1`)

### การ์ดเนื้อหา (เรียงตาม DOM)
| Card | view | หมายเหตุ |
|------|------|---------|
| Birth header + lakkana badge + zodiac SVG | both | แถวบนสุด |
| ตารางดาวกำเนิด 10 ดวง + ดาวจร + calc info | student | full width ใต้ tabs |
| ความหมายภพ 12 | student | full width |
| **เรื่องสำคัญในชีวิตคุณ (top 5 highlights)** | general | bhava 2/7/10/11 + 1 warn |
| เจ้าเรือนครองภพ ครบ 12 (natal) | student | |
| สรุปดาวจร (top 3 + good/warn) | both | |
| เจ้าเรือนเดิม ณ ดาวจรครบ 12 | student | |
| ตารางคำทำนายดาวจรเต็ม | student | |
| ทักษา: summary bar + headline + ทักษาจร bar | both | |
| ทักษา: 3×3 grid + 8 บริวาร + overlay + combos | student | |
| คำพยากรณ์จากโหร 🔮 | both | การ์ดท้ายสุด, ธีมแดง-ทอง |

### ดวงชะตา banner
- "เกิด**วันอาทิตย์**ที่ 2 กันยายน พ.ศ. 2522 เวลา 14:18 น."
- 🌙 จันทรคติ chip: "ขึ้น 11 ค่ำ เดือน 9 ปีมะแม"
- ลัคนา badge: "พิจิก 15°14'47″" (มี arcsec แล้ว)

### Mobile fixes
- ลบ `inputmode="numeric"` ที่ block พิมพ์ `/`
- ลบ `pattern` attribute ที่บางมือถือ reject
- เปลี่ยน date picker จาก CSS-overlay เป็น `<button>` + JS `showPicker()`
- `font-size: 16px` บน inputs/selects ที่ <768px กัน iOS auto-zoom
- `appearance: menulist` บังคับ native dropdown
- 44px+ touch targets

### Form
- **Transit pre-fill**: วันเวลาปัจจุบัน (Thai TZ) + กรุงเทพฯ เป็น default
- ทำเป็น `required` (ไม่ใช่ optional แล้ว)

### ข้อมูลการคำนวณ (สำหรับผู้ศึกษา)
- แก้ "กรรมจุปา" → **"กัมมัชพล"** ✓
- เพิ่ม 5 ฟิลด์: หรคุณกึ่งคืน / ศักราชใหม่ / มาสเกณฑ์ / อวมาน / เศษอุจจพล
- เพิ่ม **จันทรคติ** บรรทัดสุดท้าย (เต็มรูปแบบ "ขึ้น 11 ค่ำ เดือน 9 (เก้า) ปีมะแม จ.ศ. 1341")

## Deploy (Railway)
- **Repo**: `https://github.com/vpcodebuilder/Thai-astro-suriyayatra.git`
- ไฟล์ที่ต้องมีสำหรับ Railway:
  - `requirements.txt`: fastapi, uvicorn[standard], jinja2, python-multipart
  - `Procfile`: `web: uvicorn webapp.server:app --host 0.0.0.0 --port $PORT`
  - `runtime.txt`: `python-3.11`
- **`.gitignore`** ignore `Devtino.Astrology/` (เป็น C# ของบุคคลที่สาม ห้าม redistribute)

### Bug ที่เคยเจอ + วิธีแก้
1. **Railway "Internal Server Error"** จาก `TypeError: unhashable type: 'dict'`
   - สาเหตุ: Starlette ≥ 0.40 เปลี่ยน API ของ `TemplateResponse`
   - แก้: ส่ง `request` เป็น argument แรก: `templates.TemplateResponse(request, "index.html", {...})`
2. **CSS/JS cache เก่าใน browser** หลัง deploy
   - แก้: ใส่ `?v=YYYYMMDDx` ใน `<link href>` และ `<script src>`
3. **Layout เปลี่ยน tab แล้ว grid column 3 ยังกินที่**
   - สาเหตุ: `display: none` ลบ item แต่ track ยังสงวน width
   - แก้: ใช้ 2-col grid เสมอ, ของ student ใส่ `grid-column: 1/-1` ให้ flow ลงแถวล่าง

## หลักการแสดงผล Arc-second
- **ลัคนา**: คำนวณจริงจาก fractional arcmin (แสดงได้ 0-59 sec)
- **ดาวเคราะห์ 10 ดวง**: 00″ เสมอ — เป็น by-design ของ Devtino formula
- ใน template: ทุก label `{{ degree }}°{{ arcminute }}′{{ arcsecond }}″` (default 0)

## Cycle versioning ของ static assets
ถ้าจะเปลี่ยน CSS/JS ให้บังคับ browser โหลดใหม่ ปรับ query version ใน `index.html`:
- ปัจจุบัน: `?v=20260528d`
- format: `YYYYMMDDx` ที่ `x` = a/b/c/... bump เรื่อย ๆ

## ตำราที่ใช้อ้างอิง (ระบุใน docstring แต่ละโมดูล)
- อ.เทพย์ สาริกบุตร: โหราศาสตร์ภาคพยากรณ์ / ตำราทักษา 8 ดาว
- พล.ต.ประยูร พลอารีย์: โหราศาสตร์ไทยมาตรฐาน / ทักษา-พยากรณ์
- อ.จรัญ พิกุล: คัมภีร์โหราศาสตร์ไทย
- หลวงพรหมโยธี: ตำราทักษา
- Loy Chunpongthong: สูตรอธิกมาส (port ใน ThaiLunarYear.cs)
- B.V. Raman: Three Hundred Important Combinations (แปลไทย)

## หมายเหตุสำคัญสำหรับการแก้ครั้งต่อไป
1. **ดาว 10 ดวง** ทำให้ test เก่าที่ assert `len(planets) == 9` ต้อง update เป็น 10
2. **มฤตยูใช้ชื่อไทย "มฤตยู" ในผลลัพธ์** แต่ตอน compute ใน `compute_minor_planet()` ส่งเป็น `"ยูเรนัส"` (เพราะ formula key) แล้ว rename ใน `compute_all()`
3. **PLANET_INFO ใน server.py มี 10 entries** — abbr เป็น `๐` (ศูนย์ไทย) / `0`
4. **CSS planet color**: ต้องมี `.planet-uranus` (เพิ่งเพิ่ม สีน้ำเงิน gradient)
5. **Taksa cycle เริ่มที่ N (ศุกร์)** ไม่ใช่ E (อาทิตย์) — เปลี่ยนตามตำราไทยมาตรฐาน
6. **สูตรเดือนจันทรคติใหม่**: ใช้ surathin + 7 / 29.53 — ไม่ใช่ sun_rasi เก่า (มี off-by-1)
7. **อย่าใช้ library ดาราศาสตร์ตะวันตก** (Swiss Ephemeris, Astropy ฯลฯ) — ต้อง port จาก Devtino ทุกอย่าง
| ค่าคงที่ SVG วงกลม        | `webapp/server.py` (R_OUTER, R_TRANSIT ฯลฯ) |

---

# ===== Session 3 Updates =====
# โมดูล "โหรทายหนู" (ดวงยามอัฐุกาล) ตามตำราอ.กานดา
# Commit: 63db515

## ภาพรวม
ระบบดูดวงจากเวลา (prashna/horary astrology) — ผู้ถามตั้งคำถาม + ระบบ
คำนวณตำแหน่งดาวจาก (วัน, ยาม) แล้วตีคำพยากรณ์โดยใช้ significator
+ bhava ตามแบบโหราศาสตร์ไทย

**ต่างจากผูกดวงสุริยยาตร์ตรงไหน**:
- ไม่ใช้ ephemeris จริง / ไม่คำนวณ astronomy
- ใช้ "ตารางขับดาว" ตามวันและยาม (16 ยาม/วัน)
- เหมาะกับคำถามเฉพาะหน้า (ของหาย, ความรัก, การงาน) ไม่ใช่ดูดวงตลอดชีวิต

## โครงไฟล์ใหม่
```
thai_astro/horathaynu/
├── __init__.py
├── api.py                       # predict() + predict_from_datetime()
├── data/
│   ├── lordship.py              # ดาวเกษตร 12 ราศี (มาตรฐานไทย 7 ดาว)
│   ├── houses.py                # ภพ 1-12 + QUESTION_TO_HOUSE
│   ├── planet_meanings.py       # 11 ดาว (รวมเกตุ+มฤตยู)
│   ├── templates.py             # เทมเพลตประโยค
│   └── yam_table.py             # ★ ตาราง 14 ชุด + derive_counts() ping-pong
└── core/
    ├── time_to_yam.py           # datetime → yam_index 1-16
    ├── caster.py                # ★ chain walking algorithm
    ├── bhava.py                 # ภพ 1-12 จากลัคนา (วนซ้าย)
    ├── time_precision.py        # 7.5 นาที/cell precision
    ├── relations.py             # เรือนสัมพันธ์ 2 ชั้น (เผื่อใช้)
    ├── interpreter.py           # เผื่อใช้
    └── prophecy.py              # ★ significator + 6 category renderers
```

## หัวใจของ algorithm

### 1. ตาราง 14 ชุด (yam_table.py)
แต่ละวัน × กลางวัน/กลางคืน × 8 ยาม = 7×2×8 = 112 ค่า
- หัวใจกลางวัน อาทิตย์ = `(1, 6, 4, 2, 7, 5, 3, 1)`  step +5 mod 7
- หัวใจกลางคืน อาทิตย์ = `(1, 5, 2, 6, 3, 7, 4, 1)`  step +4 mod 7
- วันถัดไปเลื่อน +1 mod 7
- ตัวเลข 1-7 = หมายเลขดาว (1=อา 2=จ 3=อ 4=พ 5=พฤ 6=ศ 7=ส)

### 2. Ping-pong walking (★หัวใจ★)
อ่านค่า "นับ N ช่อง" สำหรับ 11 ดาว จาก row ของวัน+ครึ่งวันที่ asked:
- ดาว 1: เริ่ม pos = asked_yam → อ่านค่า → เดิน +1 ทิศทาง
- ถึงสุด (pos 8 หรือ 1) → **ย้ำค่าเดิม** + กลับทิศ
- ทำจนได้ 11 ค่า

### 3. Chain walking ลงจักร (caster.py)
- ดาว 1 เริ่มที่ราศีพฤษภเสมอ
- ดาว n (n≥2) เริ่มที่ราศีของดาว n-1
- "นับ N" = นับโดยรวม start cell เป็น 1 → เดินไปข้างหน้าใน zodiac
- ลำดับ: 1.อา 2.จ 3.อ 4.พ 5.พฤ 6.ศ 7.ส 8.ราหู 9.ลัคนา 10.เกตุ 11.มฤตยู

### 4. ภพ 12 จากลัคนา (bhava.py)
- ตนุ = ราศีลัคนา; กดุมภะ = ราศีถัดไป (zodiac forward = "วนซ้าย" ในผัง)
- จนถึงวินาศ = ราศีก่อนลัคนา

### 5. จุดลงเวลา (time_precision.py)
- 7.5 นาที/cell × 12 cell = 90 นาที = 1 ยาม
- cell แรก = ภพที่เจ้าเรือนลัคนาอยู่ (เช่น ลัคนาพฤษภ → เจ้าเรือน=ศุกร์ → ศุกร์ที่ภพไหนก็ cell แรก)

### 6. ระบบพยากรณ์ (prophecy.py)
- **15+ keyword categories** จับคำถาม → significator planet
  - ของหาย → ศุกร์ (lost_item) — มี location map ทุกภพ 1-12
  - รัก → ศุกร์ (love)
  - ทรัพย์/โชค → พฤหัส (wealth)
  - งาน → อาทิตย์ (career)
  - บุตร → พฤหัส (person)
  - สุขภาพ → อาทิตย์ (health)
  - เดินทาง → พุธ (travel)
  - คดี/พิพาท → อังคาร (enemy)
  - เหตุการณ์/สงสัย → ลัคนา (current_event)
- **6 renderer** เฉพาะ + 1 generic fallback
- **ดูเงื่อนไขพิเศษ**: เกษตรของตน, ดาวครองร่วม, tone (good/warning/neutral)

## ค่าคงที่สำคัญ
- `START_SIGN = 1` (พฤษภ) ในเชน
- ลำดับ placement 11 ดาวใน `PLACEMENT_ORDER`
- เลขดาวเกษตรประจำราศี: `HORATHAYNU_LORD_NUMBERS = [3,6,4,2,1,4,6,3,5,7,8,5]`
  (เมษ→มีน) — **กุมภ์=8 (ราหู) ไม่ใช่เสาร์** ตามตำราโหรทายหนู

## Web app — หน้า /horathaynu

### Routes
- `GET /horathaynu` — render ฟอร์ม
- `POST /horathaynu` — ตั้งดวง (re-render เต็มหน้า)
- `POST /horathaynu/ask` — **JSON API** สำหรับ AJAX ถาม-ทำนาย

### Layout 3-col 20/50/30
- ซ้าย (20%): ฟอร์ม date/time
- กลาง (50%): summary card + ผังจักรราศี SVG + ถาม-ทำนาย (AJAX)
- ขวา (30%): ตารางดาวลอย 11 ตำแหน่ง

### ผังจักรราศี SVG
- **ใช้ class จาก styles.css เดิม** (rim-line, asc-sector, planet-chip-svg ฯลฯ)
- **เพิ่ม 2 อย่างเฉพาะ horathaynu**:
  - `lord-num-bg/text` — เลขดาวเกษตรในวงกลมเล็กทุกราศี (R=138)
  - `time-ring` + `time-label-text` — วงนอก 2 วง (R=268, R=305) +
    เวลา 12 cell เริ่มจากภพของเจ้าเรือนลัคนา (R_label=288)
- เส้นแบ่ง 12 เส้นยาวออกไปถึง R_TIME_OUTER

### ถาม-ทำนาย (AJAX)
- `<form>` capture submit ด้วย JS → `fetch("/horathaynu/ask")` → render บนสุด
- ผลล่าสุดอยู่บน, มี timestamp `HH:MM:SS`
- ไม่เก็บประวัติ — refresh = clear
- มี tone-good/warning/neutral border สี
- **Suggestion chips 8 หัวข้อ** (auto-submit เมื่อคลิก):
  ตามหาของหาย, เหตุการณ์ปัจจุบัน, การเดินทาง, คดีความ, สุขภาพ, โชคลาภ, ความรัก, การงาน

### nav menu
- เพิ่ม `.nav-links` ทั้งใน index.html + horathaynu.html
- 2 ลิงค์: "ผูกดวงสุริยยาตร์" / "โหรทายหนู"

## ตัวอย่างยืนยัน (ตำราอ.กานดา หน้า 8)
- **วันพุธ ยาม 4 (10:32)**: ลัคนา=พฤษภ, ศุกร์ที่ตุล=ภพ 6 (อริ), จุดลงเวลา 10:30-10:37:30 ที่อริ
- **คืนวันอังคาร ยาม 6**: ลัคนา=เมษ, ดาว 5=สิงห์, ดาว 0=ธนู
- **คืนวันจันทร์ ยาม 8**: ลัคนา=เมษ, counts = [2, 2, 5, 1, 4, 7, 3, 6, 2, 2, 6]
  (ตัวอย่าง ping-pong ที่เด้งทั้ง 2 ฝั่ง)

## Tests สถานะ
**81/81 ผ่าน** (เพิ่ม 17 tests ใหม่)
- `test_horathaynu_time.py` (10) — yam range/time conversion
- `test_horathaynu_caster.py` (15) — chain walking + ตำแหน่งครบทั้ง 11 ดาว Wed yam4
- `test_horathaynu_derive_counts.py` (8) — ping-pong กับ 3 ตัวอย่าง
- `test_horathaynu_relations.py` (8) — เรือนสัมพันธ์ + predict flow

## ตำราอ้างอิงเพิ่ม
- **อ.กานดา** (เอกสาร 8 หน้า): วิธีตั้งดวงยามอัฐุกาล + ตาราง 14 ชุด +
  ping-pong walking + จุดลงภพ + จุดลงเวลา (★ตำราหลักของโมดูลนี้)
- อ.ประทีป อัครา: หลักการเดียวกัน (อ้างในสเปก user)
- บล็อก khojorn (2011), exguitarhora (2020) — reference อิเล็กทรอนิกส์

## หมายเหตุสำคัญสำหรับการแก้ครั้งต่อไป
1. **ตำแหน่งทุกดาวขึ้นกับ counts** — ถ้าแก้ ping-pong rule ผังจะเปลี่ยนหมด
2. **lord_house ใช้ key 'lagna'** ใน `chart.placements` (ไม่ใช่ดาวเกษตร) — ระวังสับสน
3. **กุมภ์ = ราหู (8) ไม่ใช่เสาร์** ใน `HORATHAYNU_LORD_NUMBERS`
4. **วันใหม่ 06:00 น.** — ก่อนนั้นถือเป็นวันก่อนหน้า (ยาม 13-16 = night yam 5-8)
5. **AJAX endpoint คืน JSON** — อย่าเปลี่ยนเป็น HTML (JS frontend depend on shape)
6. **กฎพยากรณ์** (prophecy.py) เป็นแบบ template-based เบื้องต้น — ผู้ใช้สามารถ
   ขยาย QUESTION_KEYWORDS, BHAVA_LOCATIONS, _make_text_* ได้
7. **CSS class นาม `time-ring`, `lord-num-bg/text`, `qa-chip`** อยู่ inline ใน
   horathaynu.html ไม่ใช่ styles.css — เพราะใช้เฉพาะหน้านี้

---

# ===== Planned Feature (ยังไม่ทำ — รอผู้ใช้เรียก) =====
# Chat กับ Claude (โหราจารย์ AI) + ระบบสมาชิก
# วันที่คุย: 2026-05-30

## สถานะ
**เก็บไว้ก่อน** — ผู้ใช้จะเรียกมาทำเมื่อพร้อม อย่าเริ่มเขียนโค้ดจนกว่าจะสั่ง

## แนวคิด
เพิ่มกล่อง chat ใน 2 หน้า (`/` สุริยยาตร์ + `/horathaynu` โหรทายหนู)
ให้ผู้ใช้คุยกับ Claude ที่สวมบทบาท "โหราจารย์ผู้เชี่ยวชาญ" โดยใช้ข้อมูล
ดวงที่คำนวณแล้วเป็น context อ้างอิงตำราไทย (อ.เทพย์ / อ.ประยูร / อ.กานดา)
ห้ามผสมโหราศาสตร์ตะวันตก

## เทคโนโลยีที่เลือก
- **Anthropic API (Claude Sonnet 4.6)** + prompt caching
- ไม่ใช้ฟรี tier (ไม่มี) / ไม่ embed claude.ai (ไม่ได้)
- ประเมินค่าใช้จ่าย: ~0.6 บาท/ข้อความ (cache hit)
- เริ่มเติม $20 → ใช้ Sonnet ได้ ~1,200 ข้อความ

## ระบบสมาชิก (กันค่าใช้จ่ายบาน)
- **Guest**: ใช้ผูกดวงทุกอย่างได้ฟรี แต่ chat ล็อค 🔒
- **Member**: chat ได้ 5 ข้อความ/วัน (reset เที่ยงคืน Asia/Bangkok)
- **Premium** (อนาคต): ไม่จำกัด — เตรียม field `tier: free|premium` ไว้

## OAuth
- เฟส 1: **Google เท่านั้น** (ง่ายสุด ครอบคลุมคนไทย)
- เฟส 2: เพิ่ม LINE / Facebook ถ้ามีคนขอ
- ใช้ Authlib + cookie session (FastAPI SessionMiddleware) ไม่ใช้ JWT

## DB Schema (PostgreSQL บน Railway)
```
User              { id, provider, provider_user_id, email, display_name,
                    avatar_url, tier, created_at, last_login_at }
DailyQuota        { user_id, date, used }  -- PK (user_id, date)
ChatSession       { id, user_id, chart_type, chart_snapshot(JSON), created_at }
ChatMessage       { id, session_id, role, content, tokens_in, tokens_out, created_at }
```
- ORM: SQLAlchemy + Alembic migrations
- Chart snapshot **pin ตอนสร้าง session** (เปลี่ยนดวง = session ใหม่)
- History retention: ผู้ใช้ลบเอง + auto cleanup >90 วัน

## หน้าที่ต้องเพิ่ม/แก้
| Path | สถานะ | หมายเหตุ |
|---|---|---|
| `/` | **ใหม่** | Landing page (hero + 2 CTA + feature comparison) |
| `/chart` | **ย้ายจาก /** | ผูกดวงสุริยยาตร์ (เดิม) — chat ล็อคถ้า guest |
| `/horathaynu` | แก้ | เพิ่ม chat (ล็อคถ้า guest) |
| `/login` | **ใหม่** | ปุ่ม OAuth |
| `/auth/google/{start,callback}` | **ใหม่** | OAuth flow |
| `/logout`, `/account` | **ใหม่** | session mgmt + quota display + history |
| `/privacy`, `/terms` | **ใหม่** | จำเป็นตาม OAuth ToS |

## Routes API
```
POST /chat/start                สร้าง ChatSession จากดวงปัจจุบัน
POST /chat/send                 ส่งข้อความ → consume quota → Claude
GET  /chat/history/{session_id} ดึงข้อความเก่า
DELETE /chat/{session_id}       ลบ
GET  /api/quota                 quota เหลือสำหรับ UI badge
```

## Env Vars ที่ต้องเพิ่มบน Railway
```
ANTHROPIC_API_KEY
DATABASE_URL
SESSION_SECRET
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
```

## Phases (โดยประมาณ 4-5 สัปดาห์)
1. Foundation: landing + ย้าย route + DB + session middleware
2. Auth: Google OAuth + User CRUD + /account
3. Chat + Quota: Anthropic SDK + ChatSession/Message + quota enforcement + UI
4. Polish: history view + rate limit + (optional) LINE OAuth

## ประเด็นที่ตัดสินแล้ว (default ถ้าผู้ใช้ไม่บอกเป็นอื่น)
1. OAuth เฟสแรก: **Google เท่านั้น**
2. DB: **Railway PostgreSQL**
3. Chart snapshot: **pin ตอนสร้าง session**
4. History: **ผู้ใช้ลบเอง + auto >90 วัน**
5. Quota reset: **เที่ยงคืน Asia/Bangkok**
6. Guest trial: **ไม่ให้ลอง** (force signup conversion)
7. Premium tier: **เตรียม field ไว้ แต่ยังไม่ implement**
8. Domain: **ยังไม่ได้คุย** — ถามผู้ใช้ตอนเริ่มทำ (OAuth ต้อง redirect URI ที่แน่นอน)

## System prompt (โครง draft)
```
คุณคือ "อาจารย์โหร" ผู้เชี่ยวชาญโหราศาสตร์ไทยสายสุริยยาตร์
- ตอบเป็นภาษาไทย น้ำเสียงสุภาพแบบโหรอาวุโส
- อ้างตำรา: อ.เทพย์ สาริกบุตร / อ.ประยูร / อ.กานดา (โหรทายหนู)
- ห้ามใช้ศัพท์โหราศาสตร์ตะวันตก (ใช้ภพไทย ราศีไทย)
- ตอบตามดวงที่ให้เท่านั้น ห้ามแต่งดาวเพิ่ม
- คำถามนอกขอบเขตโหราศาสตร์ → ปฏิเสธอ่อนๆ
## ข้อมูลดวงของผู้ถาม
{chart_summary จาก context builder}
```

## กลยุทธ์ลดต้นทุน (รวมในแผนแล้ว)
- Prompt caching system+chart context (ลด ~40%)
- จำกัด history 3-5 รอบล่าสุด
- `max_tokens=800`
- Quota แข็ง 5/วัน
- Spending limit บนแดชบอร์ด Anthropic
- Log token count ทุก request

## ไฟล์ที่จะแตะ (เมื่อเริ่มทำจริง)
- `requirements.txt` — เพิ่ม anthropic, sqlalchemy, alembic, psycopg2-binary, authlib, itsdangerous
- `webapp/server.py` — routes ใหม่ + auth middleware
- `webapp/chat.py` **(ใหม่)** — context builders + Anthropic client
- `webapp/auth.py` **(ใหม่)** — OAuth flow
- `webapp/db.py` **(ใหม่)** — SQLAlchemy session + models
- `webapp/templates/` — landing.html, login.html, account.html, privacy.html, terms.html
- `webapp/templates/index.html` + `horathaynu.html` — chat UI + auth gate
- `webapp/static/styles.css` — chat bubbles + landing
- `alembic/` **(ใหม่)** — migrations folder

---

# ===== Feature 2 — ขยายคำทำนายโหรทายหนูให้ลึก (เสร็จแล้ว) =====
# วันที่คุย: 2026-05-30
# สถานะ: ✅ ทำเสร็จครบทั้ง 7 Phase

## ปัญหาเดิม
`thai_astro/horathaynu/core/prophecy.py` ปัจจุบันทำได้แค่
"ดาว X อยู่ภพ Y + ครองร่วม Z" — ไม่ตีความความหมายจริง
ทุกคำถามที่ map ไปดาวเดียวกันได้คำตอบเหมือนกัน

## หลักการ 3 ชั้น (จากตำรา อ.ประทีป อัครา 2528)
1. **ชั้น 1**: คำถาม → ภพหลัก (significator bhava)
2. **ชั้น 2**: เจ้าเรือนภพหลักไปสถิตภพไหน (ภพผสมภพ 12×12 = 144 combos)
3. **ชั้น 3**: ดาวที่อยู่ในภพหลัก + ดาวครองร่วม (ดาว×ภพ 11×12 = 132)

โค้ดเดิมทำชั้น 3 แบบจำกัด ขาดชั้น 1+2 ทั้งดุ้น

## โครงสร้างที่จะเพิ่มใน `thai_astro/horathaynu/data/`
- `question_mapping.py`        — keyword → (bhava, significator, category)
- `bhava_meanings_prashna.py`  — 12 ภพ น้ำเสียง prashna (ไม่ใช่ natal)
- `planet_in_bhava.py`         — 132 entries (11×12)
- `lord_in_bhava.py`           — 144 entries (port จาก `bhava_lord_prophecy.py`
                                  ปรับภาษาเป็น prashna)
- `planet_combo.py`            — ดาวครองร่วมที่มีนัยพิเศษ ~20 คู่

## Phases
| # | งาน | entries | เวลา |
|---|---|---|---|
| 1 | question→bhava mapping (ขยาย 20 cat) | 20 | 1 วัน |
| 2 | bhava_meanings_prashna 12 ภพ | 12 | 1 วัน |
| 3 | planet_in_bhava (เริ่ม 7 ดาว × 12) | 84 | 3-4 วัน |
| 4 | lord_in_bhava port + ปรับภาษา | 144 | 2 วัน |
| 5 | planet_combo | ~20 | 1 วัน |
| 6 | rewrite prophecy.py 3-layer render | — | 1 วัน |
| 7 | test + tune | — | 1 วัน |

**คำแนะนำที่ user approve:** เริ่ม Phase 1+2 (ชั้น 1+2 ครอบ 80% insight)
ขยาย 8 categories ที่มี chips อยู่แล้ว → Phase 3-5 ทำทีหลัง

## แหล่งอ้างอิง
- **ตำราหลัก**: ตำราโหรทายหนู โดย ประทีป อัครา (2528, 241 หน้า) — ★
- **ตำราอ.กานดา** (8 หน้า, ใช้แล้ว) — เฉพาะวิธีตั้งดวง
- **เว็บฟรี** (อ้างได้):
  - palachote.com — ดาว 7 ดวง × 12 ภพ
  - horawej.com — "วิธีพยากรณ์แบบภพผสมภพ"
  - horoscope.trueid.net — ความหมายภพ 12
  - baankhunyai.com — คำทำนายภพ
  - tandhava.in.th — ดาวเกษตร + เจ้าเรือน
  - YouTube อ.เซิน — demo หาของหาย
- **ใช้ของในโปรเจกต์ซ้ำได้**: `thai_astro/bhava_lord_prophecy.py` (80+ override
  natal — port มา prashna ได้)

## ประเด็นที่ตัดสินแล้ว (Phase 1 scope)
1. เริ่มจาก 8 categories ที่มี chips อยู่แล้วก่อน
2. ใช้ template + override pattern (เหมือน bhava_lord_prophecy เดิม)
3. ไม่ต้องหาตำราจริง — เว็บฟรี + การ port จากโมดูลเดิมพอ
4. คำเขียนเป็น original ของเรา ไม่ copy ตำรา (กัน copyright)

---

## ผลการทำจริง (Session 2026-05-30/31)

### ไฟล์ที่สร้าง/แก้
```
thai_astro/horathaynu/
├── data/
│   ├── question_mapping.py           ✅ ใหม่ — 25 categories (ขยายจาก 8 เดิม)
│   ├── bhava_meanings_prashna.py     ✅ ใหม่ — 12 ภพ × 8 field/ภพ
│   ├── planet_in_bhava.py            ✅ ใหม่ — 84 entries (7 ดาว × 12 ภพ)
│   ├── lord_in_bhava.py              ✅ ใหม่ — wrapper reuse bhava_lord_prophecy
│   └── planet_combo.py               ✅ ใหม่ — 35 คู่ดาวพิเศษ
└── core/
    └── prophecy.py                   ✅ แก้ — เพิ่ม verdict + lens + on-topic
webapp/
├── server.py                         ✅ แก้ — gibberish guard + warning field
└── templates/horathaynu.html         ✅ แก้ — accordion + warning box + maxlen
```

### Architecture สุดท้าย — 4 ชั้นในคำตอบ

```
🎯 Verdict          ← Phase C: synthesize tone จากทุกชั้น
📌 Headline         ← ที่อยู่ของ significator
🌌 Category lens    ← Phase A: frame ดาว×ภพ ในบริบทคำถาม (เสมอ)
✨ Planet × Bhava   ← Phase 3: 84 entries (เฉพาะเมื่อ on-topic)
🤝 Combo            ← Phase 5: 35 คู่ — filter ตาม category
🌟 Lord × Bhava     ← Phase 4: 144 entries (ภพผสมภพ — chart-derived)
```

### Question handling pipeline
1. **Length check** — max 200 chars
2. **Gibberish guard** — 5 heuristics:
   - อักษรซ้ำติดกัน ≥ 4 ตัว
   - สระ > พยัญชนะ + 2
   - พยัญชนะที่ใช้ ≤ 2 ชนิดในข้อความ ≥ 8 ตัว
   - ≥ 8 อักษรไทย แต่ไม่มีสระเลย
   - Pattern ซ้ำ 3 ครั้ง+ และครอบคลุม ≥ 60%
3. **Keyword classify** — score-based matching (`priority × len(keyword)`)
4. **Fallback** — ถ้าไม่ match + Thai ≥ 5 → general + warning banner UI
5. **Reject** — อื่น ๆ → 400 พร้อมข้อความแนะนำ

### Verdict synthesis logic
- รวบ tone จาก 3 source: planet×bhava, lord×bhava, combos (×0.5)
- ถ้า good มากกว่า warning + 0.3 → "แนวโน้มดี — เดินหน้าได้"
- ถ้า warning มากกว่า good + 0.3 → "ต้องระวัง"
- อื่น → "ก้ำกึ่ง"

### On-topic detection (กัน text หลุดบริบท)
`CATEGORY_RELEVANT_BHAVAS` — 25 entries map category → set of relevant houses
ถ้า `sig_house` ไม่อยู่ใน set → ซ่อน generic planet×bhava text
(เช่น เสาร์อยู่ภพ 7 สำหรับคำถาม "ลาออก" — ไม่แสดง "คู่ครองอายุห่าง" เพราะ off-topic)

### UI ปรับ
- **Accordion 9 groups** ใน suggestion panel (`<details>` native HTML)
- คำถามตัวอย่างเป็น **ประโยคเต็ม** (เช่น "สัมภาษณ์งานมาจะได้งานมั้ย?")
- **Warning box สีเหลือง** (background #fff3cd, border-left #d49100)
  แสดงก่อน answer เมื่อ category=general
- ปุ่ม "ทำนาย" align กับ input (เปลี่ยน flex-start → stretch)
- input `maxlength="200"`

### Tests
- 81/81 unit tests ผ่านตลอดทั้ง 7 Phase
- ไม่มี test ใหม่สำหรับ data files (ค่อยทำเพิ่มถ้าจำเป็น) — manual integration test เพียงพอ

### Key learnings / gotchas
1. **Horathaynu chart กระจายดาวมาก** — co-planets ใน same rashi น้อย
   ต้องใช้ same-bhava ด้วยใน combo finder
2. **Generic planet×bhava text หลุดบริบทง่าย** — entry เดียวต่อคู่ (planet, bhava)
   แต่ดาวคู่เดียวกันตีความต่างตามเรื่องที่ถาม → ใช้ on-topic filter
3. **Keyword "ยา" / "หาย" สั้นเกิน** — false positive กับคำในประโยคเช่น "อยาก"
   → ลบออก/แทนด้วย compound keyword
4. **Cache version** ต้อง bump ทุกครั้งที่แก้ HTML/CSS (ตอนนี้ `?v=20260530c`)
5. **uvicorn --reload ไม่ pickup data file ใหม่** — ต้อง kill process แล้วรันใหม่
6. **Pre-existing `bhava_lord_prophecy.py`** ที่ port natal ใช้ได้กับ prashna ด้วย
   — ประหยัดเขียน 144 entries ใหม่

---

# ===== Feature 3 — ตรียางค์ (Drekkana) + ธาตุของราศี (เสร็จแล้ว) =====
# วันที่: 2026-05-31

## ภาพรวม
แสดงตรียางค์และธาตุบนผังจักรราศีหน้าผูกดวงสุริยยาตร์ (`/`)
- ราศี 30° แบ่ง 3 ช่อง × 10° แต่ละช่องมี "ดาวเจ้าตรียางค์" (Drekkana lord)
- ตรียางค์พิษ 3 ชนิด: 🐍 พิษนาค / 🦅 พิษครุฑ / 🐕 พิษสุนัข
- ระบุพิษหนัก/เบาตาม offset ในช่อง 10° (กลางช่อง = หนัก)
- แสดงธาตุของแต่ละราศี (ไฟ/ดิน/ลม/น้ำ)

## โมดูลใหม่: `thai_astro/triyangka.py`
```python
ELEMENT_INFO = { fire / earth / air / water }
RASHI_ELEMENT[12]                  # ราศี → ธาตุ
POISON_MAP[12]                     # ราศี → (poison_type, decanate)
POISON_INFO                        # ชื่อ + icon + ความหมาย
DECANATE_NAMES_TH = ["ปฐม", "ทุติย", "ตติย"]

# Core functions
triyangka_lord(rashi, decanate)            # คืนดาวเกษตร
get_triyangka_info(rashi, deg, arcmin)     # คืน TriyangkaInfo เต็ม
all_decanate_lords()                       # คืน list 36 ช่อง สำหรับ render
poison_severity_at(offset)                 # heavy/light
```

## กฎตรียางค์ (ตำราโหรไทย/พระเวท)
- ปฐมตรียางค์ (0°-10°): เจ้าราศีเดิม
- ทุติยตรียางค์ (10°-20°): เจ้าราศีตรีโกณ 5 = (rashi+4) % 12
- ตติยตรียางค์ (20°-30°): เจ้าราศีตรีโกณ 9 = (rashi+8) % 12

## ตำแหน่งตรียางค์พิษ
- 🐍 พิษนาค → ปฐมของ เมษ/กันย์/ธนู/มีน
- 🦅 พิษครุฑ → ทุติยของ พฤษภ/สิงห์/ตุล/กุมภ์
- 🐕 พิษสุนัข → ตติยของ เมถุน/กรกฎ/พิจิก/มกร
- ระดับ: heavy (3.20-6.39°) / light (ส่วนที่เหลือ)

## UI (index.html + styles.css + script.js)
### บนผัง SVG (ทับ layer "triyangka-layer")
- 24 เส้นแบ่งตรียางค์ (dashed บาง) ที่ 10° และ 20° ในแต่ละราศี
- 36 markers ดาวตรียางค์ — เลขอารบิก 1-7 ในช่วง R=240-258
  (1=อาทิตย์ 2=จันทร์ 3=อังคาร 4=พุธ 5=พฤหัสบดี 6=ศุกร์ 7=เสาร์)
- 2 rim circles ที่ R=240/258 → ทำให้เห็นเป็น "วงตรียางค์"
- 12 element markers (▲■〰▼) สีตามธาตุ ที่ R=110 ใกล้ขอบใน
- Poison shadow + icon บน chip ดาวกำเนิด/ลัคนาที่ตกพิษ
- ดาวกำเนิดวางตามตรียางค์ที่ตน (chip_layout_by_decanate)

### Toggle checkbox
- มุมขวาบนของ `.zodiac-stage` (absolute position, ขนาดเล็ก)
- จำสถานะใน localStorage (`triyangka_visible`)
- ซ่อน/แสดงทั้ง `triyangka-layer` พร้อมกัน

### Hover tooltips
- ตรียางค์ marker → tooltip "ตรียางค์ X/3 (ราศี)" + ดาวครอง + ช่วงองศา + พิษ
- ดาวกำเนิด/ลัคนาที่ตกพิษ → tooltip เพิ่ม "⚠️ พิษ" + ชนิด + ระดับ + ความหมาย

### ตารางดาวกำเนิด (โหมดศึกษา)
- เพิ่มคอลัมน์: chip ธาตุ + ตรียางค์ + พิษ (ถ้ามี)
- Row poisoned มี border-left สี (เขียว/ทอง/แดง)

## R constants (server.py SVG layout)
```
R_INNER = 100
R_ELEMENT_MARKER = 110      # ใหม่
R_BHAVA = 118
R_PLANET = 175
R_LAGNA_MARKER = 215
R_LABEL = 232
R_TRIYANGKA_RING_INNER = 240   # ใหม่
R_TRIYANGKA_LORD = 248         # ใหม่ (centerring)
R_TRIYANGKA_RING_OUTER = 258   # ใหม่
R_OUTER = 260
R_TRANSIT = 286
```

## Bug fix สำคัญ
**Lagna marker hover bounce** — `transform: scale(1.18)` ไม่มี `transform-origin`
ทำให้ scale รอบจุด SVG origin (0,0) → วงกลมกระเด็น
แก้ด้วย `transform-origin: center; transform-box: fill-box;`
ใน `.lagna-marker-circle` — fix ใช้ได้ทั้ง 2 หน้า (สุริยยาตร์ + โหรทายหนู)

## References
- horapayakorn.com — Drekkana rule
- mahaplee.blogspot.com — ตรียางค์พิษ 3 ชนิด
- astroneemo.net — ตรียางค์ในโหราศาสตร์พระเวท
- baankhunyai.com — ธาตุในโหราศาสตร์ไทย

---

# ===== Feature 4 — UX overhaul + About page (เสร็จแล้ว) =====
# วันที่: 2026-05-31

## ภาพรวม
ปรับ UX หลายจุด + เพิ่มหน้า `/about` พร้อม version history

## หน้า /about (ใหม่)
- ไฟล์: `webapp/changelog.py` (รายการเวอร์ชั่น) + `webapp/templates/about.html`
- Route: `GET /about`
- Layout: hero card + changelog accordion (`<details>`)
- เวอร์ชั่นใหม่อยู่บนสุด + เปิด default
- Categories ใน details: เพิ่ม (เขียว) / แก้ (ส้ม) / ปรับ (ม่วง)
- Nav link "เกี่ยวกับ" ใส่ทั้งหน้าหลัก + โหรทายหนู
- มี `<header class="site-header">` + ❀ เหมือนหน้าอื่น

## UX revisions ที่ทำเสร็จ
1. **Toggle ตรียางค์ + ธาตุ แยก checkbox** (มุมขวาบนของผัง, stacked)
2. **ตาราง dasso จร**: เพิ่มคอลัมน์ธาตุ/ตรียางค์/พิษ
3. **ภพ 12**: แสดง chip ดาวกำเนิดที่ตกในแต่ละภพ (ใช้ `result.planets_by_bhava`)
4. **ข้อมูลการคำนวณ**: เปิดตลอด + `calc-info-single` 1 column
5. **Overlay (ภพทักษาซ้อน)**: ย้ายไปข้างขวา grid 50/50 (เมื่อมี overlay)
6. **ดาวจรกระทบดาวทักษา**: เพิ่ม chip + ลูกศร ⊕ (กุม) / ⚔ (เล็ง) + label
7. **Tooltip** สีพิษ contrast: bg ทอง + cream text บน maroon
8. **Mobile tap**: click ติด stuck mode + tap นอก/ESC ปิด
9. **ฟอร์มข้อมูลผู้ขอดวง**: ตอนยังไม่ผูกดวง max-width 340px (เท่ากับตอนผูกดวงเสร็จ) + จัดกลาง

## Horathaynu fix
- ดาวกองที่เส้นเริ่มราศี (เพราะ `_chip_layout_by_decanate` ใช้ degree=0 สำหรับโหรทายหนู)
- แก้ด้วยพารามิเตอร์ `position_by_degree=True/False` ใน `build_circular_layout`
- Horathaynu ใช้ `False` → กลับไปใช้ legacy `_chip_layout` (กระจายในเซกเตอร์)

## Tip
เพิ่ม entry ใหม่ใน `webapp/changelog.py` ที่ index 0 (บนสุด) — ใส่ version, date,
title, highlights (4-5 จุด), details (categories with items)

---

# ===== Session 5 Updates =====
# Mobile layout fixes — 2026-06-01

## ปัญหาที่แก้ (2 commits)

### Commit a557962 — Mobile layout balance (v=20260601a)
แก้ 4 จุดหลักที่ทำให้ layout มือถือเบี้ยว/ล้น:

1. **`.nav-links` → flex system**: รวม nav-links CSS เข้า `styles.css` ใช้
   `display: flex; flex-wrap: wrap; justify-content: center; gap: 8px`
   ลบ duplicate inline `<style>` block จาก index.html, horathaynu.html, about.html
   — ก่อนหน้าใช้ `display: inline-block` ซึ่งตัดบรรทัดแบบเบี้ยวบนจอแคบ

2. **`.prophecy-list` overflow**: `minmax(420px, 1fr)` เกินความกว้าง content
   ของมือถือ (~327px) → เพิ่ม `@media (max-width: 600px) { grid-template-columns: 1fr }`

3. **`.container` mobile padding**: ลด padding LR จาก 1.5rem → 1rem ที่ ≤600px
   ทำให้ `.view-tabs` negative margin (`-1rem -1rem 0`) ตรงกับ container padding พอดี

4. **`.result-header` mobile**: เพิ่ม `flex-direction: column; align-items: center`
   ที่ ≤600px เพื่อให้ lakkana-badge wrap ลงมาแบบจัดกลาง ไม่ชิดซ้าย

### Commit 6157171 — Taksa mobile fixes (v=20260601b)

1. **`.taksa-grid-row.has-overlay` specificity bug**:
   media query `@media (max-width: 900px)` override แค่ `.taksa-grid-row` แต่
   `.taksa-grid-row.has-overlay` มี specificity สูงกว่า → overlay ไม่ยอมลงแถวล่าง
   **แก้**: เพิ่ม `.taksa-grid-row.has-overlay` เข้า media query selector ด้วย

2. **`.dasa-tag` word-wrap**: "🌟 เสวยอยู่" แตกบรรทัดระหว่าง "เสวย" กับ "อยู่"
   **แก้**: เพิ่ม `white-space: nowrap` ใน `.dasa-tag`

## CSS version history
| version | เนื้อหา |
|---------|---------|
| `v=20260531d` | ก่อน session นี้ (session 4) |
| `v=20260601a` | mobile layout balance (nav-links, prophecy-list, container padding, result-header) |
| `v=20260601b` | taksa overlay stacking + dasa-tag nowrap |

## Gotchas ที่ค้นพบ
- **CSS specificity + media query**: `.class.modifier { ... }` ใน non-media context
  จะ override `.class` ใน media query — ต้องระบุ `.class.modifier` ใน media query ด้วย
- **`.nav-links` styles เดิมกระจายอยู่ใน inline `<style>` แต่ละหน้า** — ตอนนี้ consolidate
  เข้า `styles.css` หมดแล้ว ถ้าเพิ่มหน้าใหม่ไม่ต้องเพิ่ม nav-links style อีก

---

# ===== Session 6 Updates =====
# Transit Scrubber + ตัดฟอร์มดาวจร — 2026-06-01

## ภาพรวม
ลด friction ของการดูดวง: ตัดช่อง "ดาวจร" 3 field ออกจากฟอร์ม
+ เพิ่ม Scrubber เลื่อนเวลาดาวจรแบบ inline ใต้ผังจักรราศี

## Workflow ใหม่
1. ผู้ใช้กรอก **แค่ชื่อ/วันเกิด/เวลาเกิด/จังหวัด** (3 field เดียว)
2. กด "ผูกดวง" → ดาวจร auto = วันนี้/เวลานี้/กรุงเทพฯ
3. ที่การ์ดดาวจรใต้ผัง → กดปุ่ม ±1/±7/±30 วัน หรือเลือก date/time
4. ฟอร์มหลัก re-submit ด้วย hidden field → ทุก section (ผัง+คำทำนาย+ภพ+oracle+ฯลฯ) update พร้อมกัน
5. Scroll position คงเดิม (sessionStorage)

## Architecture
- **Strategy**: Full-page form submit (ไม่ใช่ AJAX) — เพราะคำทำนายมีหลาย section ที่ depend transit
- **State**: hidden inputs `transit_date_iso` + `transit_time_24` ใน birth-form
- **Default**: ถ้า hidden ว่าง → server ใช้ `datetime.now(THAI_TZ)`
- **Scroll restore**: `sessionStorage["transit_scroll_y"]` + `history.scrollRestoration = manual`

## Layout การ์ด
ทั้ง 2 cards ใช้ structure เดียวกัน (`.info-card`):
```
[info-card-head]    ← icon + h2 + dashed border bottom
[info-card-body-grid] ← grid 2-col: วันที่/เวลา/สถานที่/จันทรคติ
[lakkana row หรือ scrubber-block]
```

- **การ์ดดาวกำเนิด** (`.natal-info-card`) — อยู่บนผัง: วันเกิด/เวลาเกิด/สถานที่เกิด/จันทรคติ/ลัคนา
- **การ์ดดาวจร** (`.transit-info-card`) — อยู่ใต้ผัง: วันที่/เวลา/สถานที่ + scrubber-block

## ไฟล์ที่แก้
| ไฟล์ | การแก้ |
|------|--------|
| `webapp/server.py` | ลบ 3 transit form fields, รับ `transit_date_iso`+`transit_time_24` hidden, `scroll_to_transit` flag, ส่ง `birth_month_num/birth_day_num/birth_hour/birth_minute` ไป template (สำหรับ JS), `transit_meta` มี `date_iso`+`time_24` |
| `webapp/templates/index.html` | ลบ `<fieldset class="transit-fieldset">`, เพิ่ม `natal-info-card` (บนผัง) + `transit-info-card` (ใต้ผัง), hidden inputs ในฟอร์มหลัก, `body data-scroll-target` |
| `webapp/static/script.js` | `setupTransitScrubber()` — ปุ่ม±delta+date+time → set hidden+submit, `setupScrollRestore()` — restore `window.scrollY` จาก sessionStorage หลัง load |
| `webapp/static/styles.css` | `.info-card` + `.info-card-body-grid` (grid 2-col, responsive 1-col ที่ ≤700px), `.scrubber-block`+`.scrub-btn`+`.scrubber-busy` |
| `webapp/changelog.py` | entry `2026.06.01-c` |

## CSS version
- `v=20260601c/d/e` — bump ทุกครั้งที่แก้ HTML/CSS/JS

## Gotchas สำคัญ
1. **`generate_summary()` คืน dict ไม่ใช่ object** — ถ้าจะ serialize ต้องใช้ `.get()` ไม่ใช่ `getattr()` (เคยมีบั๊ก headline ว่าง)
2. **`history.scrollRestoration = "manual"`** — ต้องตั้งก่อน restore เอง ไม่งั้น browser เด้ง scroll ตามตำแหน่งที่จำไว้
3. **`requestAnimationFrame` + `setTimeout` double restore** — กัน SVG/font ที่ delay layout ทำให้ scroll ที่ตั้งครั้งแรกผิดตำแหน่ง
4. **uvicorn --reload ไม่ pickup logic change ใน function body บางครั้ง** — restart manual ถ้า test แล้วยังเห็นพฤติกรรมเก่า
5. **กดปุ่ม scrub แล้วต้อง `e.preventDefault()`** — ไม่งั้น button type=button ใน form อาจถูกเข้าใจเป็น submit ตามค่า default
6. **ฟอร์มหลักต้อง `id="birth-form"`** — JS scrubber ใช้ id หา form เพื่อ submit
7. **Layout cards** — ไม่ใช้ grid 2-col แล้ว, การ์ด natal บน + การ์ด transit ล่าง (vertical stack เต็มความกว้าง) เพราะดูง่ายกว่าและ flow การอ่านเป็นบนลงล่าง

## Routes & params
- `POST /` รับเพิ่ม:
  - `transit_date_iso` (YYYY-MM-DD, optional) — ถ้าว่าง = now
  - `transit_time_24` (HH:MM, optional) — ถ้าว่าง = now
  - `scroll_to_transit` ("1" = restore scroll, อื่นๆ = ปกติ)

## ไอเดียพัฒนาต่อ (transit scrubber)
- Animation transition ของ chip ดาวจร (smooth slide ไประหว่างราศี)
- Auto-play timeline mode (กด ▶ แล้วเล่นเดินทีละวัน)
- Bookmark วันสำคัญ (ดาวเปลี่ยนราศี, ราหู-เกตุ retrograde)
- Compare 2 transit dates side-by-side

---

# ===== Session 7 Updates =====
# Transit chips by degree + Version badge + กล่องวิธีใช้ — 2026-06-01

## ภาพรวม
หลัง session 6 (scrubber) มีการปรับ UX เพิ่ม 6 จุด:

| # | งาน | ที่แก้ |
|---|------|--------|
| 1 | Transit chips position by degree (เหมือน natal) | `_chip_layout_by_decanate(R_TRANSIT)` |
| 2 | การ์ดดาวกำเนิด (โหมดศึกษา) มี subtitle วันที่/เวลา/สถานที่ | `index.html` `transit-meta` |
| 3 | Overlay ภพทักษาซ้อน ขอบบนเสมอตารางทักษา | `.taksa-overlay-side { align-self: stretch; margin-top: 0 !important }` |
| 4 | Version badge ติด "เกี่ยวกับ" ใน nav ทุกหน้า | `_common_context()` ส่ง `latest_version` |
| 5 | ลบ "ฉบับ อ.กานดา" จาก header โหรทายหนู | `horathaynu.html` |
| 6 | กล่องวิธีใช้ในหน้าผูกดวง (แสดงเฉพาะตอนยังไม่ผูกดวง) | `.howto-card` ใน `.howto-section` |

## Bug ที่เคยติด
- **R_LABEL ใกล้ R_TRIYANGKA_LORD เกินไป** → ขยับ R_LABEL 232→222, R_BHAVA 118→110, R_ELEMENT 110→130 — ลดการบังกัน
- **R_LAGNA_MARKER=215 ทับ R_LABEL=222** → ย้ายเป็น R_LAGNA_MARKER=200

---

# ===== Session 8 Updates =====
# Orbit View + Checkbox ราศี/ภพ + Bug fixes — 2026-06-01

## ภาพรวม
เพิ่ม **โหมด Orbit** (geocentric solar-system view) สลับกับจักรราศีเดิม
+ checkbox toggle ใหม่ 2 อัน (ราศี, ภพ)

User request เดิม = "2.5D bird-eye view" → ลอง CSS perspective rotateX แต่ user
ไม่ชอบ → เปลี่ยนเป็น **proper orbit view** (วงรี geocentric, ดาวบน orbit
ของตัวเอง — เหมือนภาพ solar system จาก top-down)

## โมดูล/ฟังก์ชันใหม่

### `webapp/server.py`
```python
ORBIT_PARAMS = {                            # 9 ดวง: ry/rx ratio ≈ 0.78 (เอียง eccentric)
    "จันทร์":   {"rx": 45,  "ry": 36,  "rot": 8,   "level": 0},
    "อาทิตย์":  {"rx": 72,  "ry": 56,  "rot": 22,  "level": 1},
    ...
    "ราหู":    {"rx": 250, "ry": 195, "rot": -32, "level": 8},
    "เกตุ":    {"rx": 250, "ry": 195, "rot": -32, "level": 8},  # ใช้ ring เดียวกับราหู
}
ORBIT_RASI_RING = 295           # outer compass radius
ORBIT_DIVIDER_INNER = 28
ORBIT_DIVIDER_OUTER = 278

def _orbit_point(rx, ry, rot_deg, angle_deg):                    # parametric (เก็บไว้)
def _orbit_point_at_ray_angle(rx, ry, rot_deg, angle_deg):       # ★ ใช้สำหรับ chip
def build_orbit_layout(natal_planets, transit_planets, ascendant) -> dict
```

### CSS class structure (`.zodiac-stage`)
- เพิ่ม `.orbit-on` / `.orbit-off`
- `.orbit-on .zodiac-svg > *:not(defs):not(.orbit-mode-layer) { display: none }`
- `.orbit-on .zodiac-center { display: none }`
- `.orbit-on { background: radial-gradient dark space }`

## ★ Bug สำคัญที่ user catch ได้

### Bug 1: chip position ใช้ parametric angle แทน geometric
**อาการ**: ดาวมฤตยูจรอยู่ราศีพฤษภ (longitude ~35°) แต่บนผัง orbit
แสดงในเซกเตอร์ราศีกรกฎ (เลื่อนไป ~28° ตาม rotation ของ ring มฤตยู)

**สาเหตุ**: ใช้ `_orbit_point()` ที่คำนวณ:
```
x_local = rx * cos(t)      # t = parametric angle (ตามการเคลื่อนรอบ ellipse)
y_local = ry * sin(t)
# rotate (x_local, y_local) ด้วย rot_deg → chip rotate ตามทั้ง ring
```
ผลคือ chip ที่ longitude 135° บน ring rotation 28° → ถูกย้ายไป angular 135-28 = 107°
บนหน้าจอ → เลื่อนไปอีกราศี

**แก้**: เพิ่ม `_orbit_point_at_ray_angle()`:
```
# หาจุดตัดของ ray จาก center ที่มุม θ_screen กับ rotated ellipse
# สูตร: t² · (cos²(θ−rot)/rx² + sin²(θ−rot)/ry²) = 1
# → จุดบน ring จริง + angular position บนหน้าจอตรงตาม longitude
```
ผลลัพธ์: dropdown 20/20 chips ตรง screen rasi = natal rasi ✓

### Bug 2: `_angle_from_zodiac` offset ผิด
**อาการ**: ทุก chip เลื่อนไป 15° จาก sector ที่ถูกต้อง

**สาเหตุ**: ใช้สูตร `90 + 30*rasi + deg` — แต่ degree 0 ของราศีคือ
**ขอบเริ่ม** ไม่ใช่ **กลาง sector**

**แก้**: `75 + 30*rasi + deg`
- เมษ deg 0 → angle 75° (ขอบ มีน/เมษ)
- เมษ deg 15 → angle 90° (กลาง = บนสุด)
- เมษ deg 30 → angle 105° (ขอบ เมษ/พฤษภ)

## Checkbox layers (เรียงตามลำดับ)
```
ราศี (rasi-label)       — default ON
ธาตุ (element-layer)    — default ON
ภพ (bhava-label)        — default ON
ตรียางค์ (triyangka)    — default ON
🌌 Orbit                — default OFF
```

`bindToggle(cbId, layerClass, storageKey, defaultOn)` — เพิ่ม param `defaultOn`
ที่ใช้กับ localStorage check (`v === null ? def : v`)

## Orbit layout template (HTML)
```html
<g class="orbit-mode-layer">
  <circle class="orbit-bg-disk"/>           <!-- dark space bg -->
  <line class="orbit-rasi-divider"/> x12    <!-- เส้นแบ่งราศี radial -->
  <circle class="orbit-zodiac-rim"/>        <!-- ขอบจักรราศี dashed -->
  <ellipse class="orbit-ring orbit-ring-N"/> x9   <!-- 9 วงรี -->
  <text class="orbit-rasi-label"/> x12      <!-- ชื่อราศี รอบนอก -->
  <circle class="orbit-earth-marker"/>      <!-- Earth ⊕ center -->
  <g class="orbit-chip-group"/> x10         <!-- natal chips -->
  <g class="orbit-chip-group orbit-transit-chip"/> x10  <!-- transit chips -->
</g>
```

## Color scheme ของ orbit rings (ตามภาพอ้างอิง solar system)
| Level | Planet | Color |
|-------|--------|-------|
| 0 | จันทร์ | ฟ้าอ่อน (#a8d8ea) |
| 1 | อาทิตย์ | ทอง (#ffd166) |
| 2 | พุธ | ฟ้า (#87ceeb) |
| 3 | ศุกร์ | เขียวอ่อน (#aef0c5) |
| 4 | อังคาร | แดง (#ff6b6b) |
| 5 | พฤหัสบดี | ส้ม (#ffa94d) |
| 6 | เสาร์ | ม่วงอ่อน (#d9b7e8) |
| 7 | มฤตยู | ฟ้าเข้ม (#6ec5ff) |
| 8 | ราหู/เกตุ | ม่วง (#c39bd3) + dashed 5-5 |

## ดาวจรพิษ
ตอนนี้ transit chip แสดง poison shadow + icon เหมือน natal chip:
- `.poison-shadow` วงเงา (r=16)
- `.poison-badge-svg.poison-badge-transit` icon เล็ก (font-size 10px แทน 13px)

## กล่องวิธีใช้
- `.howto-card` ใน `.howto-section` (grid-column: 2)
- แสดงเฉพาะตอน `not result` (ก่อนผูกดวง)
- Container `.container` เป็น 2-col เสมอ (form 340 | content 1fr)
- ที่ <900px → stack vertical (form บน, howto/chart ล่าง)

## CSS version
- `v=20260601f/g/h` — bump เมื่อแก้ HTML/CSS/JS

## Gotchas สำคัญ
1. **ray-intersection กับ rotated ellipse** — สูตร `t² · (cos²(θ−rot)/rx² + sin²(θ−rot)/ry²) = 1` ต้องใช้ทุกครั้งที่วาง chip บน rotated ring (ห้ามใช้ parametric)
2. **degree 0 ของราศี = ขอบเริ่ม** ไม่ใช่ center → ใช้ `75 + 30i` ไม่ใช่ `90 + 30i`
3. **`bindToggle` default หาย localStorage check** — ถ้า `localStorage.getItem(key) === null` ต้องใช้ default ไม่ใช่ `"1"` (กัน toggle-orbit default ON ผิด)
4. **ดาว 10 ดวงแต่ orbit 9 ring** — เพราะ ราหู/เกตุ ใช้ ring เดียวกัน (เป็น lunar nodes)
5. **chip ดาวต้องอยู่ใน group `.orbit-mode-layer`** — ถ้าวางนอก group จะแสดงตลอด ทั้งใน zodiac mode

## ไอเดียพัฒนาต่อ (orbit view)
- Animation: chip ดาว slide ตาม orbit เมื่อกด Scrubber
- Speed indicator: ดาวเร็ว (จันทร์) เคลื่อน chip เร็วกว่า ดาวช้า (เสาร์)
- Tooltip ใน orbit mode แสดง longitude + retrograde icon
- Constellation lines: ลากเส้นจาก chip ของดาวที่เป็น aspect คู่กัน
- Toggle "Show natal+transit aspects" — เส้นเชื่อม chip กุม/เล็ง
