# thai_astro — ระบบคำนวณดวงชะตาโหราศาสตร์ไทย (วิธีสุริยยาตร์)

โปรแกรมคำนวณและผูกดวงตามคัมภีร์สุริยยาตร์ของไทย โดย port มาจาก
[Devtino.Astrology](https://github.com/devtino) (C#) เป็น Python ใช้เพียง standard library
ไม่พึ่ง Swiss Ephemeris หรือ library ดาราศาสตร์ตะวันตกใด ๆ

## โครงสร้างโปรเจกต์

```
thai_astro/
├── thai_astro/
│   ├── boonnak.py    # บูรณ์นาคทองเนียม: เถลิงศก, สุรทิน, หรคุณ, DesireFactory
│   ├── planets.py    # สมผุสดาวทั้ง 9 (Sun, Moon, MinorPlanets, Rahu, Ketu)
│   ├── lakkana.py    # ลัคนา (ใช้อันโตนาที)
│   ├── chart.py      # โครงสร้างดวงชะตา
│   ├── display.py    # ตาราง 4×3 แบบไทย
│   ├── prediction.py # คำพยากรณ์เบื้องต้น
│   └── calendar.py   # JDN utility
├── webapp/
│   ├── server.py     # FastAPI app
│   ├── templates/    # Jinja2 HTML
│   └── static/       # CSS ธีมไทย (ทอง × แดงเลือดหมู)
├── tests/            # 27 unit tests
├── thai_astro.py     # CLI
└── README.md
```

## ความต้องการ

- Python 3.10+
- ส่วน CLI ใช้ standard library อย่างเดียว
- ส่วน webapp ต้องการ `fastapi uvicorn jinja2 python-multipart`

## วิธีใช้งาน

### Web app (แนะนำ)

```bash
pip install fastapi uvicorn jinja2 python-multipart
python -m webapp.server
# เปิด browser ที่ http://127.0.0.1:8000
```

หน้าเว็บมี form กรอกชื่อ-วันเวลาเกิด-จังหวัด (รองรับครบ 77 จังหวัดของไทย)
แสดงผังดวงแบบไทย 4×3 พร้อมดาวพระเคราะห์ในแต่ละราศี และตำแหน่งสมผุสละเอียด

### CLI

```bash
python thai_astro.py --date 1990-05-15 --time 08:30 --province กรุงเทพมหานคร
python thai_astro.py                       # interactive
python thai_astro.py --list-provinces      # ดูจังหวัดทั้งหมด
```

### Options

| Option              | คำอธิบาย                       | Default            |
|---------------------|--------------------------------|---------------------|
| `--date`            | วันเกิด YYYY-MM-DD              | (ถาม)              |
| `--time`            | เวลาเกิด HH:MM                  | 12:00              |
| `--province`        | จังหวัด (ใช้ปรับเวลาท้องถิ่น)   | กรุงเทพมหานคร      |
| `--no-predict`      | ไม่แสดงคำพยากรณ์                | (แสดง)             |

## ทดสอบ

```bash
python -m unittest discover -s tests -v
```

## หลักการคำนวณ (สูตรหลัก)

### 1. บูรณ์นาคทองเนียม (boonnak.py)

**เถลิงศก** (วันปีใหม่สุริยยาตร์, เม.ย.) สำหรับ จ.ศ. ≥ 1115:
```
result = (จศ × 0.25875)
       − floor(จศ/4 + 0.5)
       + floor(จศ/100 + 0.38)
       − floor(จศ/400 + 0.595)
       − 5.53375
```

**หรคุณ** (จำนวนวันสะสม):
```
HorakhunThaloengsok = floor((292207 × จศ + 373) / 800) + 1
Horakhun = HorakhunThaloengsok + Surathin
```

**DesireFactory** คำนวณ:
- กรรมจุปา (Kammatchaphon), อุจจพล (Ujapon)
- มาส (Mas), อวมาน (Awaman), ดิถี (Dithi)

### 2. สมผุสดาว (planets.py)

แต่ละดาวคำนวณเป็นหน่วย **arcminute** (21600 = 360°):

- **อาทิตย์**: มัธยม = หาร KammatchaphonDesire ด้วย 24350/811/14
  ตามด้วยภุชพล (Phutchapon) ตาราง Kan 7 ค่า: `[0, 35, 67, 94, 116, 129, 134]`

- **จันทร์**: มัธยม = `Dithi×720 + floor(1.04×UjaponRem) − 40 + อาทิตย์มัธยม`
  ภุชพลด้วยตาราง Kan ของจันทร์: `[0, 77, 148, 209, 256, 286, 296]`

- **ดาวรอง** (พุธ ศุกร์ อังคาร พฤหัสบดี เสาร์): ใช้
  `PowerPlanet.ValueMinutes = Appa × 21600 + MattayomRawi`
  คำนวณ 2 ขั้น (มันทผล + สิงฆผล) ผ่านตาราง Chaya: `[0, 244, 427, 488]`

- **ราหู**: `Mattayom = ValueMinutes/20 + ValueMinutes/265`
  `Somput = 15150 − Mattayom`

- **เกตุ**: `Pon = (DesireAtMidnight − 344) mod 679`
  `Mattayom = floor((Pon + เวลา/24) × 21600/679)`
  `Somput = 21600 − Mattayom`

### 3. ลัคนา (lakkana.py)

ใช้ตาราง **อันโตนาที** (นาทีต่อราศี):

| ราศี | นาที | ราศี | นาที |
|------|------|------|------|
| เมษ | 120 | ตุลย์ | 168 |
| พฤษภ | 96  | พิจิก | 144 |
| เมถุน | 72  | ธนู | 120 |
| กรกฎ | 120 | มกร | 72  |
| สิงห์ | 144 | กุมภ์ | 96  |
| กันย์ | 168 | มีน | 120 |

รวม = 1440 นาที = 24 ชม. ✓

วิธีคำนวณ:
1. หาเวลาผ่านพระอาทิตย์ขึ้น (6:00 น.) − ค่าปรับท้องถิ่น (กรุงเทพฯ = 18:01 นาที:วินาที)
2. เริ่มจากราศีของอาทิตย์ ลบเวลาตามอันโตนาทีจนหมด แล้วเดินราศีถัดไป
3. เศษ → องศาในราศี

## หมายเหตุ

- ผลลัพธ์เป็น **sidereal** ตามตำราโหราศาสตร์ไทย ตรงกับปฏิทินสุริยยาตร์
  ที่พิมพ์ในประเทศไทย (ต่างจาก tropical ของฝรั่ง ~24°)
- ราหู-เกตุ ในสุริยยาตร์คำนวณจากสูตรต่างกัน จึง**ไม่ใช่**ตรงข้ามกัน 180° เป๊ะ
- เวลาอาทิตย์ขึ้น = 6:00 น. แบบคลาสสิก (SunriseType.SixAM) ไม่ใช่ดาราศาสตร์จริง

## เครดิตและอ้างอิง

- Source code อ้างอิง: **Devtino.Astrology** (C#)
- คัมภีร์สุริยสิทธานต์, ตำราโหราศาสตร์ไทยของ อ.เทพย์ สาริกบุตร
- ตำราพยากรณ์ของ พลตรี ประยูร พิศนาคะ
