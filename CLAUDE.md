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

---

# ===== Session 9 Updates =====
# เมนูใหม่ "เทียบปฏิทิน" + Timeline ประวัติศาสตร์ — 2026-06-02

## ภาพรวม
เพิ่มเมนูที่ 3 (`/calendar`) — เทียบจันทรคติ ⇄ สุริยคติ + แสดง Timeline ประวัติศาสตร์
ปฏิทินไทย 8 ยุค พร้อมภาพประวัติศาสตร์ Public Domain จาก Wikimedia Commons

## ไฟล์ใหม่
| ไฟล์ | บทบาท |
|------|--------|
| `thai_astro/calendar_convert.py` | `solar_to_lunar()` + `lunar_to_solar()` (search-based) + `round_trip_check()` |
| `webapp/calendar_data.py` | `CALENDAR_EPOCHS` (8 entries) + `HOLY_DAYS` (6 entries) + `find_holy_day()` |
| `webapp/templates/calendar.html` | หน้าเทียบปฏิทิน — 2 tabs + result + timeline + holy days |
| `webapp/static/timeline-images/{rama1,rama5,rama6,phibun}.jpg` | 4 ภาพ PD จาก Wikimedia (250×~320px, ~30KB ต่อภาพ) |

## ไฟล์ที่แก้
- `webapp/server.py` — เพิ่ม `GET /calendar` + `POST /calendar/convert` + `_pair_to_dict()`
- `webapp/static/styles.css` — เพิ่ม +600 บรรทัด (calendar UI + 2-col timeline + photo frames)
- `webapp/templates/{index,horathaynu,about}.html` — เพิ่ม nav link "เทียบปฏิทิน"
- `webapp/changelog.py` — entry `2026.06.02-a`

## Algorithm: Reverse Lookup (จันทรคติ → สุริยคติ)

```python
def lunar_to_solar(be_year, lunar_month, waxing, day_in_phase):
    # Window 2 ปี รอบปีที่ระบุ (ครอบคลุม edge case อธิกมาส + ขึ้นปีใหม่)
    start = date(ce_year - 1, 1, 1)
    end = date(ce_year + 1, 12, 31)
    matches = []
    for d in iter_days(start, end):
        desire = build_desire(d.year + 543, d.month, d.day)
        lunar = compute_lunar_date(desire, sun_rasi=0)
        if all match:
            matches.append(SolarLunarPair(d, lunar))
    return matches
```

**Complexity**: O(730) ต่อ query — เร็วพอ ไม่ต้อง pre-compute
**Range**: พ.ศ. 1181-3000 (CE 638-2457) ที่สูตรสุริยยาตร์ valid

## ขอบเขต / Known Limitations (Phase 1)
- **Off-by-1 จากปฏิทินทางการ**: สูตร approximation อวมาน/ดิถี ทำให้วันสำคัญ
  (วิสาขบูชา, ลอยกระทง) คลาดเคลื่อน ±1 วันบ้างครั้ง — note ใน UI
- **ปีอธิกมาส**: formula ปัจจุบันคืน 1 match + flag `is_leap_month_year` แสดง chip ⚠
  Phase 2 จะใส่ตารางอธิกมาส (เดือน 8/8) แยก
- **ไม่รองรับพุทธกาล** (พ.ศ. 1-1180): ก่อน จ.ศ. 0 สูตรไม่ valid
- **ไม่รองรับ ม.ศ. / ร.ศ.**: รับเฉพาะ พ.ศ./ค.ศ.

## Timeline 2-Column Alternating Layout

```
[Era 1 — left]──●──
                │
                ──●──[Era 2 — right]
                │
[Era 3 — left]──●──
```

- `.timeline-item:nth-child(odd)` → margin-right: auto (ฝั่งซ้าย)
- `.timeline-item:nth-child(even)` → margin-left: auto (ฝั่งขวา)
- Tile width 46%, gap each side 4% → dot offset `calc(-4% - 9px)`
- `::after` = dot (18px) สีตามยุค
- Mobile (<700px): collapse เป็น 1-col, เส้นซ้าย, tile ขวา

## Era-themed Backgrounds (5 types)
| Type | Gradient | SVG pattern (data URI inline) |
|------|---------|-------------------------------|
| `astronomical` | dark cosmos #1a0530→#0a0218 | stars (random circles) |
| `buddhist` | gold-cream #fff4d2→#ffe4a3 | lotus 6-petals rotation |
| `era` | gold #f6ecd2→#c9a24a | mandala 4-ring circles |
| `historical` | gold→deep #fff8e6→#d4b556 | temple/spire silhouette |
| `reform` | rose-gold #fde9c8→#b8336a | gear/clock with ticks |

## Photo Frames (ภาพประวัติศาสตร์ PD)

**4 ภาพ Public Domain**:
| Year | Person | Source URL pattern |
|------|--------|---------------------|
| 1782 | ร.1 | `commons.wikimedia.org/.../King_Rama_I_of_Siam_Portrait.jpg` |
| 1889 | ร.5 | `.../Chulalongkorn_LoC.jpg` (Library of Congress, c.1880) |
| 1912 | ร.6 | `.../Vajiravudh_of_Siam_cropped.jpg` (c.1920) |
| 1941 | จอมพล ป. | `.../Plaek_Phibunsongkhram_cropped.jpg` (c.1940s) |

**Photo frame design**:
- กรอบทอง 3px + shadow แดง ขนาด 100×130px
- Corner ornaments (gold-bright) ที่มุม top-left + bottom-right
- Caption ใต้กรอบ: ชื่อ + license credit
- Layout: flex 2-col (content | photo) บน desktop, stack vertical บน mobile

**License compliance**:
- ทุกภาพ public domain ตาม Wikimedia Commons
- ระบุ credit ใน `image_credit` field ของ `calendar_data.py`
- มี attribution footer ใต้ timeline:
  `"ภาพประวัติศาสตร์จาก Wikimedia Commons เป็น Public Domain
   (ลิขสิทธิ์หมดอายุตามกฎหมายไทย พ.ร.บ.ลิขสิทธิ์ 2537)"`

## Holy Days (6 entries)
- มาฆบูชา (ขึ้น 15 ค่ำ เดือน 3)
- วิสาขบูชา (ขึ้น 15 ค่ำ เดือน 6)
- อาสาฬหบูชา (ขึ้น 15 ค่ำ เดือน 8)
- เข้าพรรษา (แรม 1 ค่ำ เดือน 8)
- ออกพรรษา (ขึ้น 15 ค่ำ เดือน 11)
- ลอยกระทง (ขึ้น 15 ค่ำ เดือน 12)

`find_holy_day(lunar_month, waxing, day_in_phase)` — match → return dict, ไม่ match → None
UI: แสดง 🪷 badge + คำอธิบายเมื่อตรงวันสำคัญ
วันพระ (ขึ้น/แรม 8, 15) — แสดง 🙏 badge รอง (ถ้าไม่ใช่วันสำคัญ)

## Routes
| Method | Path | Action |
|--------|------|--------|
| GET | `/calendar` | render หน้าฟอร์ม + timeline + holy days |
| POST | `/calendar/convert` | JSON API — รับ direction + values → คืน matches |

## Gotchas สำคัญ
1. **`overflow: hidden` บน `.timeline-item`** จะ clip pseudo `::after` (dot) ที่อยู่นอกขอบ —
   ย้าย overflow hidden ไปที่ `.timeline-bg-pattern` (child) แทน
2. **Dot position** ใช้ `calc(-4% - 9px)` แทน `-46px` — รับ responsive width
3. **`compute_lunar_date(desire, sun_rasi=0)`** — `sun_rasi` ไม่ใช้ในสูตรใหม่ ส่ง 0 ได้
4. **Round-trip ผ่าน** (solar→lunar→solar = วันเดิม) — internal consistency
5. **JDN reference** = `1954167` (จ.ศ. 0 = 21 มี.ค. 638 Julian) — port จาก Devtino
6. **ภาพ Wikimedia ใช้ thumb URL** (`/250px-`) — เหมาะกับ photo frame ขนาด 100×130, ไม่ต้อง resize
7. **`<img loading="lazy">`** — กัน initial load lag (4 ภาพ ~125KB)

## ไอเดียพัฒนาต่อ (Phase 2-3) — ส่วนใหญ่ทำเสร็จใน Session 10 แล้ว
- ~~SQLite DB → DB-driven~~ ✓ (PostgreSQL/SQLite via SQLAlchemy)
- ~~ม.ศ. + ร.ศ. input/output~~ ✓
- ~~พุทธกาล (Meeus)~~ ✓
- ~~ตารางอธิกมาสจริง~~ ✓ (BE 2300-2700 จาก myhora.com)
- ~~Search by date วันสำคัญทางราชการ~~ ✓ (20 entries)
- ~~Auto-detect today widget~~ ✓
- ~~Round-trip warning~~ ✓
- **ภาพยุคโบราณ paintings** — ยังเหลือ (รอ user download Wikimedia paintings ตาม `data/timeline_image_urls.md`)
- Adhikamasa BE 1181-2299 + 2701-3000 — fallback formula (ขยายข้อมูลทีหลังถ้าหาตำราได้)

---

# ===== Session 10 Updates =====
# DB migration + ปีอธิกมาสจริง + ยุคพุทธกาล + Usage counter — 2026-06-03

## ภาพรวม
ยก calendar feature เข้า DB เต็มรูป + แก้ off-by-1 month ของปีอธิกมาส (สาเหตุที่
วันสำคัญในปี 2569 เคยแสดงเดือน 6 แทนที่จะเป็น 7) + รองรับยุคพุทธกาล (พ.ศ. 544-1180)
ผ่าน Meeus algorithm + เพิ่มวันสำคัญทางราชการ 20 entries + counter จำนวนผู้ใช้งาน

## ไฟล์ใหม่
| ไฟล์ | บทบาท |
|------|--------|
| `webapp/db.py` | SQLAlchemy engine + DATABASE_URL pattern (SQLite dev / PostgreSQL prod) |
| `webapp/models.py` | 5 models: CalendarEpoch, HolyDay, NationalHoliday, AdhikamasaYear, UsageStat |
| `webapp/seed.py` | idempotent seed script (Group A data) |
| `webapp/usage.py` | counter helpers — increment(feature), get_counts() — best-effort, ไม่เก็บ PII |
| `webapp/calendar_data.py` | **rewrite** — query functions แทน hardcoded lists + _LazyList compat |
| `thai_astro/ancient_lunar.py` | Meeus new-moon algorithm + compute_ancient_lunar_date() |
| `alembic/` + `alembic.ini` | migrations folder — initial + add_usage_stats |
| `scripts/scrape_adhikamasa.py` | ดึงปีอธิกมาส/อธิกวารจาก myhora.com (มี title-check) |
| `scripts/import_adhikamasa.py` | upsert JSON → adhikamasa_years table (source='myhora') |
| `data/adhikamasa_scraped.json` | 401 entries BE 2300-2700 (~37% อธิกมาส, ~19% อธิกวาร, ~44% ปกติ) |
| `data/timeline_image_urls.md` | curated Wikimedia paintings list (ยังไม่ download) |

## DB Schema (5 tables)
```
calendar_epochs       — 11 entries (timeline events; sort_order, image fields)
holy_days             — 6 entries (lunar; เก็บเลขเดือนสำหรับปีปกติ)
national_holidays     — 20 entries (solar; 6 categories)
adhikamasa_years      — pk=cs_year, type ∈ {adhikamasa, adhikavara, both, normal}
                        source ∈ {algorithm, myhora, official, user}
usage_stats           — pk=feature; counter + updated_at (no PII)
```

## DATABASE_URL pattern
```
# Dev (default ถ้าไม่ตั้ง)
sqlite:///./local.db

# Prod (Railway inject auto จาก PostgreSQL service)
postgresql://user:pass@host:5432/dbname
```
- `db.py` จัดการ `postgres://` legacy → `postgresql://` แล้ว
- `connect_args={"check_same_thread": False}` เฉพาะ SQLite

## Procfile (Railway deploy)
```
release: alembic upgrade head && python -m webapp.seed
web: uvicorn webapp.server:app --host 0.0.0.0 --port $PORT
```
ทุก deploy: migration + seed (idempotent — seed skip ถ้ามี data แล้ว)

## Adhikamasa fix (ที่สำคัญที่สุด)

### Shift rule ในปีอธิกมาส (lunar.py)
```python
if leap:
    if base_month in (5, 6, 7):
        lunar_month = base_month + 1
        is_intercalary = False
    elif base_month == 8:
        lunar_month = 8
        is_intercalary = True       # "เดือน 8 หลัง" (8/8)
    else:  # 1-4, 9-12
        lunar_month = base_month
```

### Lookup order
1. `_lookup_db_year_type(cs_year)` — query `adhikamasa_years` ก่อน (authoritative)
2. ถ้าไม่มี → fallback formula `(grate_year - 0.45222) % 2.7118886 < 1`

### Holy day match กฎใหม่
ใน adhikamasa year `find_holy_day()` reverse shift ก่อน lookup:
- lunar_month=8 + is_intercalary=True → match HOLY_DAYS month=8 (อาสาฬหบูชา ✓)
- lunar_month=8 + is_intercalary=False → return None (เดือน 8 ต้น ≠ วันพระใหญ่)
- lunar_month ∈ {4,5,6,7} → search HOLY_DAYS month=(lunar_month-1)
- อื่นๆ → search ปกติ

## Era support (ม.ศ. / ร.ศ.)
`thai_astro/calendar.py`:
- `RS_EPOCH_YEAR = 1781` (ร.ศ. 1 = ค.ศ. 1782)
- `convert_year_to_ce(year, era)` รองรับ {be, ce, ms, cs, rs}

Form `/calendar` มี dropdown era ข้างปีรับ — convert เป็น พ.ศ. ก่อน underlying

ผลลัพธ์แสดง 5 ศักราช: พ.ศ. + ค.ศ. + จ.ศ. + ม.ศ. + ร.ศ. (— ถ้าก่อนสถาปนากรุง)

## Ancient mode (พุทธกาล)
`thai_astro/ancient_lunar.py`:
- Meeus new-moon JDE formula (Ch 49)
- `find_k_for_jdn(jdn)` หา k (new moon number) แบบ walk
- `ancient_lunar_tithi(jdn)` = (jdn − new_moon_jdn) × 30 / 29.530588861
- `ancient_lunar_month(jdn, ce_year)` = นับ synodic months ตั้งแต่ ขึ้น 1 ค่ำ เดือน 5 ของปี

Routing (`calendar_convert.py`):
- `be_year >= 1181` → สูตรสุริยยาตร์ (แม่นยำ)
- `544 <= be_year < 1181` → Meeus (`is_ancient=True` flag)
- ก่อน 544 → ValueError

UI: chip "⚠ ประมาณ ±5-15 วัน" สีน้ำตาล + note "ศึกษาประวัติศาสตร์เท่านั้น"

## Usage counter
`webapp/usage.py`:
- 3 features: `suriyayatra_chart`, `horathaynu_chart`, `horathaynu_ask`
- `increment(feature)` — upsert (ON CONFLICT DO UPDATE) สำหรับทั้ง SQLite + PostgreSQL
- best-effort — fail silently ไม่ขัด user flow
- `get_counts()` → dict {feature: int} inject เข้า `_common_context`
- Trigger จุดที่ chart compute สำเร็จ (หลัง try) — fail → ไม่นับ
- Display: ใต้ปุ่ม "ผูกดวง" บนหน้า index + ใต้ปุ่ม "ตั้งดวงยาม" บนหน้า horathaynu

## National holidays (20 entries)
| Category | Examples |
|---|---|
| royal | จักรี, ฉัตรมงคล, ราชินี, ร.10, แม่, สวรรคต ร.9, ปิยมหาราช, พ่อ (ร.9) |
| national | รัฐธรรมนูญ |
| tradition | สงกรานต์ (3 วัน) |
| memorial | ครู, ข้าราชการพลเรือน, ฝนหลวง |
| holiday | ปีใหม่, แรงงาน, สิ้นปี |
| international | วาเลนไทน์, สตรีสากล |

## Form: เดือน 8 หลัง (Intercalary 8/8)
- Checkbox "เดือน 8 หลัง?" โผล่เฉพาะเมื่อเลือกเดือน 8
- เปลี่ยนเดือนอื่น → auto-uncheck
- Validate ที่ backend:
  - `is_intercalary_month=True` + `lunar_month != 8` → ValueError
  - `lunar_to_solar` คืน 0 matches + intercalary=True → hint "ปีอาจไม่ใช่ปีอธิกมาส"

## Today widget
`server.py:_today_widget()` คำนวณดวงวันนี้ (Thai TZ), inject เข้า `/` context.
- "📅 วันนี้ + วัน...ที่ DD เดือน พ.ศ. + 🌙 ค่ำ เดือน ปี + 🇹🇭 national + 🪷 holy"
- Pill style border-radius 999px, hover → translate-y(-1px) + shadow
- Click → ไปเมนู `/calendar`

## Bug ที่เคยเจอ
1. **scrape myhora ทั้งหมดเป็น "adhikamasa"** — เพราะปีนอกช่วง 2300-2700 myhora redirect ไปหน้า default (2569 = adhikamasa) → แก้ด้วย title-check (regex จับเลขปีใน `<title>`)
2. **Dataclass error** — `is_intercalary_month: bool = False` เป็น field ที่มี default ต้องอยู่ท้าย dataclass (ไม่ใช่กลาง field ที่ไม่มี default)
3. **Server cache** — `--reload` ของ uvicorn จับ Python file แต่บางที module-level imports cache → restart manually เมื่อแก้ตาราง/model
4. **Encoding crash บน Windows** — `sys.stdout.reconfigure(encoding="utf-8")` ที่ต้นทุก script (cp874 default พิมพ์ → ไม่ได้)
5. **Timeline dot misalignment** — `right: calc(-4% - 9px)` ใช้ % ของ item width (46%) ทำให้ dot offset แค่ 1.84% ของ container แทน 4% → แก้เป็น `calc(-100% * 4/46 - 9px)`
6. **"ทรง" ใช้ผิด** — ราชาศัพท์ใช้กับเชื้อพระวงศ์เท่านั้น, จอมพล ป. ไม่ใช่ราชวงศ์ → "ทรงนำเอา" → "ประกาศให้ใช้"

## ขอบเขตข้อมูลที่ scrape แล้ว
- BE 2300-2700 (401 ปี) — myhora.com
- distribution: adhikamasa 148 (~37%) | adhikavara 78 (~19%) | normal 175 (~44%)
- ตรงกับ Wikipedia ratio (~36.8%)

## ที่ยังเหลือ (Phase 11)
- Adhikamasa BE 1181-2299 + 2701-3000 (fallback formula ใช้งานได้)
- Timeline paintings — รอ user download Wikimedia paintings ตาม `data/timeline_image_urls.md`
- Chat + User (Session 2026-05-30 plan ใน CLAUDE.md เดิม) — ยังเก็บไว้

## ตำราอ้างอิงเพิ่ม
- Jean Meeus, "Astronomical Algorithms" 2nd ed (Ch 49: Phases of the Moon) — ใช้ใน ancient_lunar.py
- myhora.com — ตารางปีอธิกมาส scrape source
- กรมการศาสนา — กฎ shift วันสำคัญในปีอธิกมาส (แหล่งของ find_holy_day rule)

---

# ===== Session 11 Updates =====
# Timeline cinematic redesign — 13 scenes — 2026-06-03

## ภาพรวม
เปลี่ยน Timeline จาก 11 entries แบบ 2-column alternating cards → 13 entries
แบบ cinematic full-width hero scenes พร้อมภาพประกอบเฉพาะ (`timeline01-13.png`)
ที่ user เตรียมไว้ และเส้นเชื่อมสีทอง glow ระหว่าง scene

## เปลี่ยนแปลง
| เก่า | ใหม่ |
|---|---|
| 11 entries (Wikimedia photos 4 ภาพ) | 13 entries (ภาพประกอบเฉพาะ 13 ภาพ) |
| Layout 2-column alternating tiles + dot connectors | Full-width hero scenes + gold glowing connector |
| `.timeline-list/.timeline-item` (legacy เก็บไว้) | `.timeline-scenes > article.scene` |
| Era types: astronomical/buddhist/era/reform/historical | + sukhothai, ayutthaya, rattanakosin, digital |
| `description` สั้น พรรณนาเร็ว | ละเอียดเป็นทางการ (เนื้อหาจาก user spec) |

## 13 Scenes
1. 3102 BCE — กาลียุค (astronomical)
2. 543 BCE — ปรินิพพาน พ.ศ. 1 (buddhist)
3. 78 CE — มหาศักราช (era)
4. **499 CE — ดาราศาสตร์อินเดียรุ่งเรือง** ★ใหม่ (astronomical)
5. 638 CE — จุลศักราช (era)
6. **1283 CE — กำเนิดอักษรไทย พ่อขุนรามคำแหง** ★ใหม่ (sukhothai)
7. **1455 CE — ระบบปฏิทินราชการอยุธยา** ★ใหม่ (ayutthaya)
8. 1782 CE — สถาปนากรุงรัตนโกสินทร์ (rattanakosin)
9. **1855 CE — อิทธิพลปฏิทินตะวันตก (เบาว์ริง)** ★ใหม่ (rattanakosin)
10. 1889 CE — ปรับวันขึ้นปีใหม่เป็น 1 เมษายน (ร.5, reform)
11. 1912 CE — ประกาศใช้ พ.ศ. (ร.6, reform)
12. 1941 CE — เปลี่ยนวันขึ้นปีใหม่เป็น 1 ม.ค. (จอมพล ป., reform)
13. **2026 CE — ปฏิทินไทยในยุคดิจิทัล** ★ใหม่ (digital, บทสรุป)

## CSS layout ใหม่
- `.scene` — min-height 320px, full-width, overflow hidden
- `.scene-bg` — `background-size: cover` + hover scale 1.04 (transition 0.6s)
- `.scene-overlay` — linear-gradient ดำ→ใส (90deg) เพื่อความ legibility
- `.scene-content` — grid 280px / 1fr (year block ซ้าย, body ขวา) + padding 1.6rem 2rem
- `.scene-year-big` — Kanit 2rem gold gradient text (เปลี่ยนสีตาม era)
- `.scene-be` — pill chip รูปยา border ทอง
- `.scene-connector` — เส้นทอง 4px กลาง bottom, linear-gradient + box-shadow glow
- Responsive <760px: stack 1-col (year บน, body ล่าง)
- Cinema header — dark card สีน้ำตาลเข้ม + ขอบทอง + glow shadow (กัน text กลืนหลัง)

## Era tone (overlay gradient + year text color)
| Type | Tone | ใช้ใน scene |
|---|---|---|
| astronomical | น้ำเงิน-ทอง | 1, 4 |
| buddhist | ทองอุ่น | 2 |
| era | ทองเข้ม | 3, 5 |
| sukhothai | ทองแดง | 6 |
| ayutthaya | ทองแดงเข้ม | 7 |
| rattanakosin | ทอง-แดงเลือดหมู | 8, 9 |
| reform | ทอง | 10, 11, 12 |
| digital | น้ำเงิน-ทองดิจิทัล | 13 |

## ไฟล์ที่ user เตรียม
- `data/timeline01.png` ... `timeline13.png` — copy → `webapp/static/timeline-images/`
- `data/timeline_all.png` — ภาพรวมต้นฉบับ (ไม่ใช้ใน app — ใช้สำหรับ re-crop ถ้าต้องการ)

## ที่ทำไปแล้ว
1. Copy 13 ภาพ data/ → static/timeline-images/
2. Update seed.py: 11 → 13 entries (descriptions ใหม่ทั้งหมดจาก user spec)
3. Re-seed DB: ลบ calendar_epochs เดิม → insert 13 entries ใหม่
4. Rewrite HTML: `.timeline-scenes > article.scene`
5. Rewrite CSS: 8 era tones + connector + responsive
6. ลบ "SCENE 0X" label ตาม user feedback
7. ใส่ dark card บน header (กัน timeline-intro กลืน background)

## Legacy เก็บไว้
- CSS เก่าของ `.timeline-list/.timeline-item` ยังอยู่ใน styles.css (comment "LEGACY — kept for reference")
- HTML/template เก่าถูก replace แล้ว
- ภาพถ่ายเก่า (rama1/5/6/phibun.jpg) ยังอยู่ใน static/timeline-images/ ไม่ได้ลบ — เผื่อใช้ที่อื่น

---

# ===== Session 12 Updates =====
# Lunar month fix (mas-based) + Thai sunrise day convention — 2026-06-03

## ภาพรวม
2 patches สำคัญในวันเดียวกัน:
1. **แก้สูตรเดือนจันทรคติ** — เลิกใช้ floor(surathin/29.53) approximation ที่ off-by-1 ในปีอธิกมาส
2. **Thai sunrise day convention** — ผูกดวงตามตำราไทย (วันใหม่เริ่มที่พระอาทิตย์ขึ้น)

## Patch 1: Mas-based lunar month formula
### Bug report
User: "7 ก.พ. 2556 ระบบให้ แรม 12 ค่ำ **เดือน 3** ปีมะโรง — ที่ถูกคือ **เดือน 2**"

### Root cause
สูตรเก่า `floor((surathin + 7) / 29.530588)` เป็น approximation จากค่าเฉลี่ย
synodic month (29.53 วัน). มี off-by-1 error ในปีอธิกมาสช่วงปลายปี
(หลัง mas_diff = 4 = เดือน 8 หลัง)

### Fix
ใช้ `desire.mas - mas_at_thaloengsok` (synodic month count ที่ Devtino formula
คำนวณไว้แล้วเป็น integer arithmetic — ไม่มี rounding error)

```python
def _mas_at_thaloengsok(thaloengsok) -> int:
    """หา mas ณ วันเถลิงศก — cache ตาม cs_year"""
    cs = thaloengsok.cs_year
    if cs in _MAS_THALOENGSOK_CACHE:
        return _MAS_THALOENGSOK_CACHE[cs]
    d = build_desire(thaloengsok.be_year, thaloengsok.month, thaloengsok.day)
    _MAS_THALOENGSOK_CACHE[cs] = d.mas
    return d.mas

# ปีปกติ: mas_diff 0..11 → เดือน 5,6,7,8,9,10,11,12,1,2,3,4
# ปีอธิกมาส: mas_diff 0..12 → เดือน 5,6,7,8(ต้น),8(หลัง intercalary),9,10,...,4
```

### ทดสอบผ่าน
- 7 ก.พ. 2556 = แรม 12 ค่ำ เดือน 2 ปีมะโรง ✓
- 31 พ.ค. 2569 (Visakha) = ขึ้น 15 ค่ำ เดือน 7 ✓
- 29 ก.ค. 2569 (Asalha) = ขึ้น 15 ค่ำ เดือน 8 หลัง ✓
- 30 ก.ค. 2569 (เข้าพรรษา) = แรม 1 ค่ำ เดือน 8 หลัง ✓

---

## Patch 2: Thai sunrise day convention

### หลักการ
ตำราไทย: วันใหม่เริ่มที่พระอาทิตย์ขึ้น (~06:00) ไม่ใช่เที่ยงคืน
- เกิด 3 มิ.ย. 02:00 (สากล) → ตำราไทยถือเป็น 2 มิ.ย. (ยังก่อนพระอาทิตย์ขึ้น)

### 2 โหมด
| Mode | Description |
|---|---|
| `real_sunrise` (default) | คำนวณ sunrise จริงตาม (date, จังหวัด) ผ่าน NOAA formula |
| `six_am` | ใช้ 06:00 ตรง (Thai standard time) ตำราคลาสสิก SunriseType.SixAM |

### ไฟล์ใหม่
- `thai_astro/sunrise.py`:
  - `LATITUDE_BY_PROVINCE` — 77 จังหวัด (≈ ศูนย์กลางจังหวัด, accuracy ±0.3°)
  - `sunrise_hours_at(date, province)` — NOAA simplified formula
    - Solar declination, EOT, hour angle at sunrise
    - Accuracy ±5-10 min (พอเพียงสำหรับโหราศาสตร์)
  - `thai_birth_day_adjust(birth_dt, province, mode)`
    - คืน (adjusted_date, sunrise_hours_used, hour_decimal)
    - ถ้า time < sunrise → adjusted = date - 1

### Integration
- `server.py POST /`: รับ form field `sunrise_mode` + apply adjustment ก่อน `Chart.calculate`
- `_today_widget()`: ใช้ Thai sunrise convention (real_sunrise, กรุงเทพ)
- UI: 
  - Info note ในฟอร์ม — อธิบายว่ากรอกเวลาสากล ระบบปรับให้
  - Banner หลังตั้งดวง — 🌅 ถ้า shift / ☀ ถ้าไม่ shift
  - Toggle button: สลับ real_sunrise ⇄ six_am

### Sunrise computed examples (Thai standard time)
| Province | 21 มี.ค. | 21 มิ.ย. | 21 ก.ย. | 21 ธ.ค. |
|---|---|---|---|---|
| กรุงเทพ | 06:26 | 05:55 | 06:11 | 06:41 |
| เชียงใหม่ | 06:32 | 05:52 | 06:17 | 06:57 |
| ภูเก็ต | 06:35 | 06:14 | 06:19 | 06:39 |
| นราธิวาส | 06:21 | 06:03 | 06:05 | 06:23 |

### Implementation notes
1. **Banner placement**: ต้องอยู่ใน `chart-section` (col 2) ไม่ใช่ `<section>` ระดับ
   เดียวกัน — เพราะ grid auto-flow จะทำให้ chart ตกแถวล่าง user complained
   "หน้าพัง" ครั้งแรกที่วาง section นอก chart-section
2. **Time accuracy**: ลัคนา/สมผุสดาว ใช้เวลาเกิดจริง (ไม่ shift) เพราะ build_desire
   รับ (adjusted_date, original_hour) → moment ใน sky อาจคลาดเคลื่อน ~24h เมื่อ shift
   (acceptable approximation ตามที่ Thai practitioners ใช้กัน)
3. **parse_thai_date** คืน **CE year** (ไม่ใช่ BE) — เคย bug ตอน integrate
4. **_format_thai_date_ce(ce_y, m, d)** = "DD MONTH พ.ศ. {ce+543}"

---

# ===== Roadmap Updates =====
# (เปลี่ยนแปลงสถานะของ Phase 11 เดิม)

## ที่ทำเสร็จเพิ่มแล้ว (ตั้งแต่ Session 11)
- ✓ Mas-based lunar month (แก้ adhikamasa ครึ่งปีหลัง)
- ✓ Thai sunrise day convention (ผูกดวง + today widget)
- ✓ Timeline 13 cinematic scenes (replaced 11 2-col tiles)

## ที่ยังเหลือ
- Adhikamasa BE 1181-2299 + 2701-3000 — fallback formula (ไม่ใช่ตำราจริง)
- Timeline paintings — รอ user download Wikimedia paintings (data/timeline_image_urls.md)
- Chat + User system (Session 2026-05-30 plan)
- Off-by-1 day ใน ดิถี formula (rare cases) — Devtino approximation

## Reference for future devs
- ดูประวัติแก้ที่ webapp/changelog.py (เวอร์ชั่น 2026.06.03-a ถึง -d)
- DB schema: webapp/models.py (5 tables)
- Adhikamasa data: data/adhikamasa_scraped.json (401 entries BE 2300-2700)



# ===== Session 13 Updates =====
# ดาวเกษตรกุมภ์ = ราหู + คำพยากรณ์โหรขยาย dignity context — 2026-06-05

## ภาพรวม
แก้ 4 จุดในระบบ "คำพยากรณ์จากโหร" ตามคำขอ user (วันเกิด 2/9/2522 14:18, ดาวจร 5/7/2569 9:55):
1. **RASI_LORD[กุมภ์] เปลี่ยนจากเสาร์ → ราหู** (ตามเลขเกษตรกุมภ์ = 8)
2. **คำทำนายดาวจรปรากฏในทุก section** (เดิมหายเงียบเมื่อ tone=neutral)
3. **แยก "ดวงเดิม" / "ดาวจร" + เส้นคั่น + label วันที่ดาวจร**
4. **ผนวก dignity** (เกษตร/อุจน์/นิจ/ประ ฯลฯ) เข้าทุกคำทำนายเจ้าเรือนภพ

## ไฟล์ที่แก้
| ไฟล์ | การแก้ |
|------|--------|
| `thai_astro/planets.py` | `RASI_LORD[10] = "ราหู"` (เดิมเสาร์) |
| `thai_astro/dignities.py` | `SWAKSHETRA`: เสาร์={9}, ราหู={10} (sync ตาม RASI_LORD) |
| `thai_astro/bhava_lord_prophecy.py` | + `Optional dignities` param, `BhavaLordPrediction.dignity*` 3 field, `_DIGNITY_SUFFIX` ผนวกท้ายคำทำนาย, auto-flip tone (อุจน์/เกษตรพลิกเตือน→กลาง, นิจ/ประพลิกดี→เตือน) |
| `thai_astro/oracle_narrative.py` | `_build_life_area_section` แยก natal/transit dict, รับประกัน transit ≥1 line (ใช้ neutral fallback), `compose_oracle_reading` รับ/คืน `transit_date_label` |
| `webapp/server.py` | compute `transit_dignities = compute_all_dignities(transit_chart.planets)`, ส่งเข้า `predict_*_lords`, ตั้ง `transit_date_label = "DD MONTH พ.ศ. YYYY เวลา HH:MM น."` |
| `webapp/templates/index.html` | life area renders 2 blocks: `📜 ดวงเดิม` → `<hr class="oracle-divider">` → `🌠 ดาวจร (วันที่)`, การ์ดหัวมี `.oracle-transit-window` |
| `webapp/static/styles.css` | `.oracle-source-label`, `.oracle-divider`, `.oracle-transit-window` |

## หมายเหตุสำคัญ

### ผลกระทบจากการเปลี่ยน RASI_LORD[10]
**ระบบทั้งระบบเปลี่ยนหมด** เมื่อกุมภ์เกี่ยวข้อง:
- `chart.py`: `house_lords[X]` / `chart_lord` เปลี่ยนเป็นราหู (ลัคนาที่ทำให้กุมภ์เป็นภพไหน)
- `dignities.py`: ดาวที่ตกกุมภ์ → ราหู = เกษตร, เสาร์ที่กุมภ์ ≠ swakshetra อีกต่อไป
- `triyangka.py:164`: ปฐมตรียางค์ของกุมภ์ = ราหู (เดิมเสาร์ ตาม Parashara ดั้งเดิม)
- `chart.py:43-45`, `dignities.py:329` (nicchabhanga), `server.py:722` ใช้ RASI_LORD[X] ทั้งหมด

`HORATHAYNU_LORD_NUMBERS = [3,6,4,2,1,4,6,3,5,7,8,5]` (โหรทายหนู) มี กุมภ์=8 อยู่แล้ว — sync กันแล้ว

### Dignity suffix pattern
ใน `bhava_lord_prophecy._DIGNITY_SUFFIX`:
```
อุจน์   → " — ดาวเจ้าเรือนได้ §อุจน์§ พลังเต็มที่..."
มูล     → " — ดาวเจ้าเรือนอยู่ §มูลตรีโกณ§..."
เกษตร  → " — ดาวเจ้าเรือนอยู่ §เกษตร§ (บ้านตัวเอง) แสดงพลังเต็ม..."
มิตร    → " — ดาวเจ้าเรือนอยู่ราศี §มิตร§ มีคนหนุนหลัง..."
ประ     → " — ดาวเจ้าเรือนตก §ประ§ (ราศีศัตรู) เรื่องนี้ติดขัด..."
ศัตรู   → " — ดาวเจ้าเรือนตก §ศัตรู§ มีอุปสรรค..."
นิจ     → " — ดาวเจ้าเรือนตก §นิจ§ (มหานิจ) อ่อนกำลังที่สุด..."
สมพล    → "" (ไม่เสริม)
```
`§...§` = marker ที่ template strip ออกตอน render (`| replace('§', '')`). คงไว้
เพื่ออนาคต — ถ้าจะ bold ก็ render เป็น `<strong>...</strong>` แทน

### Auto-flip tone logic
ใน `_predict()`:
- `tone == "good"` + ดาวกำลังอ่อน (นิจ/ประ) → `tone = "warning"`, label = "ปะปน (ดาวอ่อน)"
- `tone == "warning"` + ดาวกำลังแข็ง (อุจน์/เกษตร/มูล) → `tone = "neutral"`, label = "บรรเทา (ดาวแรง)"
ทำให้ดาวที่แข็งมาก "พลิกร้ายเป็นดี" สอดคล้องตำราโหรไทย

### _build_life_area_section (ใหม่)
- bucket แยก: natal (good/warn/neutral), transit (good/warn/neutral)
- natal: เก็บ good[:2] + warn[:2], ถ้าว่างทั้งคู่ใช้ neutral[0]
- transit: เก็บ good[:2] + warn[:2], ถ้าว่างทั้งคู่ใช้ neutral[0] (รับประกันมี ≥1 line)
- คืน dict ใหม่: `natal: {good, warn}`, `transit: {good, warn}`, `has_natal`, `has_transit`,
  + keep flat `good`/`warn` backward-compat

### Template structure ใหม่
```jinja
{% for area in o.life_areas %}
  <h3>{{ area.title }}</h3>
  {% if area.has_natal %}
    <div class="oracle-source oracle-source-natal">
      <div class="oracle-source-label">📜 ดวงเดิม</div>
      <ul>...</ul>
    </div>
  {% endif %}
  {% if area.has_transit %}
    {% if area.has_natal %}<hr class="oracle-divider"/>{% endif %}
    <div class="oracle-source oracle-source-transit">
      <div class="oracle-source-label">🌠 ดาวจร ({{ o.transit_date_label }})</div>
      <ul>...</ul>
    </div>
  {% endif %}
{% endfor %}
```

## ทดสอบที่ผ่าน
วันเกิด 2/9/2522 14:18 (ลัคนาพิจิก) + ดาวจร 5/7/2569 9:55 — ตรวจ "ครอบครัวและบ้าน":
- **ก่อนแก้**: "เจ้าเรือนพันธุไปอยู่ปุตตะ" (RASI_LORD[10]=เสาร์เก่า, เสาร์จรอยู่มีน)
- **หลังแก้**: "เจ้าเรือนพันธุ**อยู่พันธุ** — ดาวเจ้าเรือนอยู่ **เกษตร** (บ้านตัวเอง)" ✓
  (ราหูจรอยู่ในราศีกุมภ์ = ภพพันธุ = swakshetra ของราหูใหม่)

## Gotchas
1. **uvicorn ไม่มี --reload ใน launch.json** — ต้อง preview_stop + preview_start เมื่อแก้ Python
2. **§...§ marker** ใน prediction text ต้อง template strip ออกด้วย `| replace('§', '')` ไม่งั้นโผล่บนหน้าจอ
3. **dignity_strength** เก็บไว้ใน BhavaLordPrediction แต่ยังไม่ใช้ — เผื่ออนาคต sort/rank
4. **local.db ห้ามทับ** — มี usage_stats counter จริงในนั้น (user เน้น)

## Cache version
`v=20260605a` — bump เมื่อแก้ HTML/CSS/JS


# ===== Session 14 Updates =====
# โหรทายหนู ลึก 5 ชั้น — Intent + Dignity + Verdict + House relation + Sub-intents — 2026-06-05

## ภาพรวม
ขยายความลึกของระบบคำพยากรณ์โหรทายหนูจาก 4 ชั้น (lens / planet×bhava /
combo / lord×bhava) เป็น **5 ชั้น + binary verdict** ตามแนว prashna จริง

## 5 Phase ที่ทำเสร็จ

### Phase 1 — Intent detection ([intent.py](thai_astro/horathaynu/core/intent.py))
แตกคำถามเป็น 3 มิติ:
- `intent_type` ∈ {yes_no, when, where, who, why, how, outcome}
- `polarity` ∈ {hope, worry, neutral}
- `topic` (จาก category mapping)

ตัวอย่าง:
- "จะได้งานไหม" → (yes_no, neutral, "หางาน")
- "เมื่อไหร่จะได้แฟน" → (when, neutral, "เนื้อคู่")
- "อยากย้ายงาน กลัวพลาด" → (outcome, worry, "ลาออก")

### Phase 2 — Dignity ([dignity_score.py](thai_astro/horathaynu/core/dignity_score.py))
Port `EXALTATION/SWAKSHETRA/MULATRIKONA/PLANET_RELATIONS` จาก
`thai_astro/dignities.py` มาใช้ key อังกฤษของ horathaynu (sun/moon/...)

`compute_sig_dignity(planet, rashi)` → `SigDignity(dignity, label, strength, suffix)`
- อุจน์/เกษตร/มูล = is_strong → suffix "พลังเต็มที่..."
- นิจ/ประ/ศัตรู = is_weak → suffix "ติดขัด..."

### Phase 3 — Binary verdict ([verdict.py](thai_astro/horathaynu/core/verdict.py))
คะแนนรวม:
| Factor | ±score |
|--------|--------|
| sig dignity (อุจน์/เกษตร/มูล) | +2 |
| sig dignity (นิจ/ประ) | −2 |
| sig in kendra (1/4/7/10) | +1 |
| sig in trikona (1/5/9) | +1 |
| sig in 11 (ลาภะ) | +1 |
| sig in dusthana (6/8/12) | −2 |
| house_relation_score (Phase 4) | ±2 |
| ดาวมิตร (benefic) same bhava | +1/ดวง |
| ดาวร้าย (malefic) same bhava | −1/ดวง |
| จันทร์ในภพดี | +1 |
| จันทร์ในทุกข์ | −1 |

Tier mapping:
- score ≥ +4 → very_high (85%) — "แทบจะแน่นอน"
- ≥ +2 → high (70%) — "น่าจะได้"
- ≥ 0 → moderate (50%) — "ก้ำกึ่ง"
- ≥ −2 → low (30%) — "เสี่ยงพลาด"
- < −2 → very_low (15%) — "ครั้งนี้ยังไม่ใช่"

Benefics = {jupiter, venus, moon, mercury}
Malefics = {saturn, mars, rahu, ketu, sun}

### Phase 4 — House relation ([house_relation.py](thai_astro/horathaynu/core/house_relation.py))
12 ระยะจากภพคำถามไปถึง sig:
- 1 = ภพเดิม (มั่นคง, +2)
- 5, 9 = ตรีโกณ (+2)
- 11 = ลาภะ ✓ (สมหวัง +2)
- 6, 8, 12 = ทุกข์ (−2)
- 3 = สหัชชะ (เคลื่อนไหว, 0)
- 4, 10 = เกณฑ์ (+1)

`compute_house_relation(asked_bhava, sig_house, topic)` → text formatted กับ topic

### Phase 5 — Sub-intents (+18 categories ใน [question_mapping.py](thai_astro/horathaynu/data/question_mapping.py))
| Parent | Sub-intents เพิ่ม |
|--------|-------------------|
| career | promotion, boss_conflict, freelance |
| love | love_loyalty, love_reconcile, love_new, love_thirdparty |
| wealth | investment, loan, bonus, repay |
| health | health_recover, health_surgery |
| study | exam_pass, scholarship |
| home | buy_house, move_home |

แต่ละ sub-intent มี:
- keywords เฉพาะ
- primary_bhava + secondary_bhavas เฉพาะ
- significator + co_significators เฉพาะ
- priority สูง (8-9) เพื่อชนะ parent category

career parent priority ลด 7→6 เพื่อให้ sub-intents (8-9) ชนะใน score-based matching

## Orchestration ใน prophecy.predict()

```
1. classify_question(q) → (mapping, matched)         [Phase 5]
2. parse_intent(q, topic=mapping.label_th) → intent  [Phase 1]
3. compute_sig_dignity(sig, sig_rashi) → dignity     [Phase 2]
4. compute_house_relation(primary_bhava, sig_house)  [Phase 4]
5. compute_verdict(chart, sig, sig_house, ...)       [Phase 3]
6. Render text:
   - บรรทัด 1: intent_headline
   - บรรทัด 2: verdict.label + "(โอกาส ~X%)"
   - บรรทัด 3+: category renderer + dignity suffix + combos + house_relation + lord×bhava
```

## ProphecyResult — 13 fields ใหม่
```
intent_type, polarity, intent_headline,
dignity_kind, dignity_label, dignity_strength,
house_relation_distance, house_relation_name, house_relation_text,
verdict_tier, verdict_percentage, verdict_label, verdict_factors
```

## JSON response /horathaynu/ask
เพิ่ม 13 field ใหม่ส่งกลับ → frontend ใช้ได้ทันที (แสดงเป็น chip/badge)

## Tests ผ่าน
5 ประโยคทดสอบ (date 5/6/2569 10:30):
- "สัมภาษณ์งานจะได้ไหม" → cat=job_search, intent=yes_no, verdict=30% (sig วินาส)
- "เมื่อไหร่จะได้แฟน" → cat=love_new, intent=when, verdict=85% (sig=ศุกร์อุจน์)
- "คนรักจริงใจไหม" → cat=love, intent=yes_no, verdict=85%
- "ของรักหายอยู่ที่ไหน" → cat=lost_item, intent=where, verdict=50%
- "ลงทุนหุ้นได้ไหม" → cat=investment, intent=yes_no, verdict=70%

## Gotchas
1. **`lordship.py` กุมภ์เคยเป็นเสาร์** — Session 13 แก้ใน planets.py แล้วแต่ไม่ sync มาที่นี่
   → Session 14 แก้ให้ตรงกัน (กุมภ์ = ราหู)
2. **career parent priority ต้องต่ำกว่า sub-intents** — ไม่งั้น "สัมภาษณ์งาน" จะ match career
   ก่อน job_search เพราะ career มี keyword "งาน" ซึ่งสั้นกว่า "สัมภาษณ์" แต่ priority สูง
3. **polarity=neutral เป็น default** — คำถามที่ไม่มี อยาก/หวัง/กลัว/ห่วง = neutral
4. **horathaynu chart กระจายดาว** — same-house dignity & combo อาจไม่เจอ → fine

## Cache version
`v=20260605b` — bump เมื่อแก้ HTML/CSS/JS


# ===== Session 14b Updates =====
# Fix: หลาย sub-intent ให้คำตอบซ้ำ — 2026-06-05

## ปัญหา
หลัง Session 14 ครบ 5 phase แล้ว user พบว่า "จะได้เลื่อนตำแหน่งไหม" กับ
"อุปสรรคเรื่องงานเกี่ยวกับคนมั้ย" → คำตอบเกือบเหมือนกันทั้งหมด

**Root cause**: หลาย sub-category ใช้ `significator + primary_bhava` เดียวกัน:
- career, promotion, boss_conflict ทั้งหมดมี sig=sun, bhava=10
- ผัง chart เดียวกัน → ตำแหน่งดาวเดียวกัน → text ออกมาเกือบเหมือนกัน
- generic renderer `_make_text_generic_category` แตกต่างเฉพาะ `cat_label` ที่ swap แล้ว

## วิธีแก้

### 1. เพิ่ม [category_intros.py](thai_astro/horathaynu/data/category_intros.py)
- 33 categories × 3 tier (good/warn/neutral) = 99 บทเปิด
- Token: `{sig}`, `{bhava}`, `{rashi}` substitute ตอน render
- `get_category_intro(cat, tier, sig, bhava, rashi)` → text หรือ None (fallback)
- Tier mapping: very_high/high → idx 0 (good), low/very_low → idx 1 (warn), moderate → idx 2

### 2. เพิ่ม category `work_conflict`
- keywords: อุปสรรคเรื่องงาน, ปัญหาที่ทำงาน, ขัดแย้งที่ทำงาน, เพื่อนร่วมงาน
- primary_bhava=6 (อริ ทุกข์) — แทน 10 ที่ใช้ใน career
- sig=mars (การกระทบกระทั่ง) แทน sun
- **priority=10** — สูงสุด เพื่อชนะ career (priority=6)

### 3. Orchestrate ใน prophecy.predict()
- เพิ่มบรรทัด 3 ใน header_lines: `cat_intro` (intent_headline → verdict → intro → body)
- ถ้า `get_category_intro` คืน None → ไม่ใส่ (backward compat)

## ผลลัพธ์ (ทดสอบ 5/6/2569 10:30)

```
Q1: "จะได้เลื่อนตำแหน่งไหม"
   cat=promotion | sig=อาทิตย์/พิจิก/ภพ3 | verdict=50%
   intro: "📈 เรื่องเลื่อนตำแหน่ง — ก้ำกึ่ง ขึ้นกับว่าคุณจะ proactive แค่ไหน..."

Q2: "อุปสรรคเรื่องงานเกี่ยวกับคนมั้ย"
   cat=work_conflict | sig=อังคาร/พฤษภ/ภพ9 | verdict=70%
   intro: "⚔️ เรื่องอุปสรรค/ปัญหาที่ทำงาน — อังคารอยู่ภพศุภะ (อริ-ทุกข์)..."
```

ทุกชั้นต่างกันหมด — category, sig, bhava, intro, verdict, house relation, lord×bhava

## Pattern สำหรับเพิ่ม sub-intent ใหม่
1. เพิ่ม QuestionMapping entry ใน `question_mapping.py` พร้อม keywords + priority สูงพอ
2. **เพิ่ม entry ใน `CATEGORY_INTROS`** — 3 บรรทัด (good/warn/neutral)
   ⚠️ ถ้าไม่เพิ่ม จะตกไป fallback generic ที่อาจซ้ำกับ category อื่นที่ sig+bhava เดียวกัน
3. ถ้าต้องใช้ renderer เฉพาะ (เช่น lost_item) → เพิ่ม branch ใน `predict()` orchestrator

## Cache version
`v=20260605c`


# ===== Session 15 Updates =====
# Production migration + UI polish — 2026-06-05

## ภาพรวม
1. **Railway PostgreSQL migration** — counter ที่ห่ายทุก deploy แก้แล้ว
2. **adhikamasa_years auto-seed** — 401 ปี (BE 2300-2700) ทุก deploy
3. **Checkbox toggles → collapsible button** — ไม่บัง chip กุมภ์/พฤษภ/มีน

## 1. Railway PostgreSQL migration

### ปัญหาเดิม
- `db.py` มี fallback: ถ้า `DATABASE_URL` env ไม่ตั้ง → ใช้ `sqlite:///./local.db`
- Railway container = ephemeral filesystem → ทุก deploy = local.db ใหม่ว่าง → counter reset

### วิธีแก้ (Manual ใน Railway dashboard)
1. Add PostgreSQL service ใน Railway project
2. Add Variable Reference ใน web service → `DATABASE_URL` ชี้ไป Postgres
3. Postgres service มี `postgres-volume` (persistent) → ข้อมูลคงอยู่ข้าม deploy
4. กด Deploy → release phase รัน `alembic upgrade head && python -m webapp.seed`

### ผลลัพธ์
- counter ใน `usage_stats` ตอนนี้อยู่ใน PostgreSQL → ไม่หายอีก
- 5 tables seed สำเร็จ: calendar_epochs(13), holy_days(6), national_holidays(20), usage_stats, adhikamasa_years(401)

### Gotchas
- Railway PostgreSQL ให้ 2 URL: internal (`*.railway.internal`) สำหรับ web service ใช้,
  public (`*.proxy.rlwy.net`) สำหรับ DBeaver/pgAdmin ต่อจากภายนอก
- PostgreSQL log ที่ Railway แสดง = log ของ DB เอง (startup/checkpoint) ไม่ใช่ deploy log
- Deploy log อยู่ที่ Web service → Deployments → คลิก deployment ล่าสุด

## 2. seed_adhikamasa() — auto-import 401 ปี

### Pattern (เพิ่มใน `webapp/seed.py`)
```python
ADHIKAMASA_JSON = Path(__file__).parent.parent / "data" / "adhikamasa_scraped.json"

def seed_adhikamasa(session, reset: bool):
    if reset:
        session.execute(delete(AdhikamasaYear))
    if session.query(AdhikamasaYear).count() > 0:
        print("[skip] adhikamasa_years already populated")
        return
    if not ADHIKAMASA_JSON.exists():
        print(f"[warn] ไม่พบ {ADHIKAMASA_JSON.name} — ข้าม adhikamasa seeding")
        return
    data = json.loads(ADHIKAMASA_JSON.read_text(encoding="utf-8"))
    for be_str, info in data.items():
        if info["type"] in ("error", "unknown"):
            continue
        session.add(AdhikamasaYear(
            cs_year=int(be_str) - 1181,
            be_year=int(be_str),
            ce_year=int(be_str) - 543,
            type=info["type"],
            source="myhora",
            note=info.get("evidence", ""),
        ))
```

### Idempotent
- ครั้งแรก: insert 401 entries
- ครั้งถัดไป: count > 0 → skip
- ถ้าจะ override ใช้ `python -m webapp.seed --reset`

## 3. Checkbox toggles → collapsible button

### ปัญหา
- 5 checkboxes (ราศี/ธาตุ/ภพ/ตรียางค์/Orbit) อยู่ `position: absolute; top: 6px; right: 6px`
- บัง chip ดาวจรในราศีกุมภ์ + เลขเกษตร 8 + พิษ + chip natal/transit ทั้งหลาย
- Mobile: ยิ่งกินพื้นที่มาก

### วิธีแก้ (Session 15)
Wrap 5 checkboxes ใน `<div class="chart-cb-list">` ที่ default `display: none`
+ เพิ่มปุ่ม `<button class="chart-cb-toggle">⚙ ชั้น</button>`

```html
<div class="chart-cb-stack" data-open="false">
  <button class="chart-cb-toggle" aria-expanded="false">⚙ ชั้น</button>
  <div class="chart-cb-list">
    [5 labels with checkboxes]
  </div>
</div>
```

### CSS
- ปุ่ม: rounded pill, gold-deep border, สีครีม bg
- `.chart-cb-stack[data-open="true"] .chart-cb-list { display: flex }`
- Mobile (≤600px): `.cb-toggle-text { display: none }` — เหลือแค่ ⚙

### JS (`setupTriyangkaToggle()` ใน script.js)
- Click ปุ่ม → toggle `data-open` + บันทึก localStorage `chart_cb_open`
- Click outside stack → close (เฉพาะตอน open)
- localStorage persist → จำสถานะ open/closed ระหว่าง session

### Gotchas
1. `document.write()` หลัง POST **ไม่ refire DOMContentLoaded** → click handler ไม่ bind
   → ใช้ form.submit() ปกติให้ browser navigate จริง ๆ
2. Original page ไม่มี `.zodiac-stage` (form-only) → setupTriyangkaToggle returns early
   ก่อน result มา — ปกติแล้ว เพราะหลัง submit แล้ว page reload จึง setup
3. animation `cbFadeIn` 0.18s — เร็วพอไม่หน่วง UX

## Cache version
`v=20260605d` — bump เมื่อแก้ HTML/CSS/JS

## ไอเดียถัดไป (ยังไม่ทำ)
- Banner deploy "PostgreSQL connected ✓" หลัง migration แรก (ตอนนี้เห็นแค่ counter เพิ่มขึ้นจริง)
- Guard `db.py`: ถ้า env Railway/prod แต่ DATABASE_URL=sqlite → raise warning (กันพลาดในอนาคต)
- adhikamasa_years ขยาย BE 1181-2299 + 2701-3000 (ตอนนี้ครอบ 2300-2700)

