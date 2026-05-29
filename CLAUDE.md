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
