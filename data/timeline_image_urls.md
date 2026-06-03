# Timeline images — Curated Wikimedia URLs (เน้นภาพวาด)

ดาวน์โหลดภาพ → save เป็นไฟล์ตามคอลัมน์ "Local filename"
ใส่ไว้ที่ `webapp/static/timeline-images/` แล้วบอกผมจะ update DB ให้

ทุกภาพเป็น **Public Domain** (อายุลิขสิทธิ์หมดแล้วตาม พ.ร.บ. ลิขสิทธิ์ ๒๕๓๗)

---

## 👑 บุคคล — เปลี่ยนจากภาพถ่าย → ภาพวาด (พระบรมสาทิสลักษณ์)

| Entry | Local filename | Wikimedia file page | Direct download |
|---|---|---|---|
| **ร.1** (ค.ศ. 1782) | `rama1.jpg` | [King_Rama_I_of_Siam_(Yodfa_Chulalok)_Portrait.jpg](https://commons.wikimedia.org/wiki/File:King_Rama_I_of_Siam_(Yodfa_Chulalok)_Portrait.jpg) | คลิกหน้า File → ปุ่ม "Original file" |
| **ร.5** (ค.ศ. 1889) | `rama5.jpg` | [King_Rama_V_of_Siam_(Chulalongkorn)_Portrait.jpg](https://commons.wikimedia.org/wiki/File:King_Rama_V_of_Siam_(Chulalongkorn)_Portrait.jpg) | คลิกหน้า File → "Original file" |
| **ร.6** (ค.ศ. 1912) | `rama6.jpg` | [Vajiravudh_Portrait_(King_Rama_VI_of_Siam).jpg](https://commons.wikimedia.org/wiki/File:Vajiravudh_Portrait_(King_Rama_VI_of_Siam).jpg) | คลิกหน้า File → "Original file" |
| **จอมพล ป.** (ค.ศ. 1941) | `phibun.jpg` | ⚠ Wikimedia มีแต่ภาพถ่าย ไม่มีภาพวาดสาธารณะ — แนะนำคงภาพถ่ายเดิม หรือใช้ภาพสีพื้นหลังประวัติศาสตร์แทน | (skip) |

---

## 🏛 อาณาจักร / สถานที่ / ยุค — ภาพประวัติศาสตร์

| Entry | Local filename | แนะนำ Wikimedia categories |
|---|---|---|
| **กาลียุค** (3102 BCE) | `kali-yuga.jpg` (ใหม่) | [Category:Vishnu_in_paintings](https://commons.wikimedia.org/wiki/Category:Vishnu_in_paintings) (ภาพ Hindu cosmology / Dashavatara) |
| **ปรินิพพาน** (543 BCE) | `parinirvana.jpg` (ใหม่) | [Category:Parinirvana_in_painting](https://commons.wikimedia.org/wiki/Category:Parinirvana_in_painting) — มีภาพไทย/พม่า/ลาว |
| **มหาศักราช** (78 CE) | `shalivahana.jpg` (ใหม่) | [Category:Shalivahana](https://commons.wikimedia.org/wiki/Category:Shalivahana) (เหรียญ/รูปสลัก/ภาพคัมภีร์) |
| **จุลศักราช** (638 CE) | `chulasakarat.jpg` (ใหม่) | [Category:Pyu_city-states](https://commons.wikimedia.org/wiki/Category:Pyu_city-states) (พม่าตอนสถาปนา จ.ศ.) |
| **สุโขทัย** (1238) | `sukhothai.jpg` (ใหม่) | [Category:Wat_Mahathat_(Sukhothai)](https://commons.wikimedia.org/wiki/Category:Wat_Mahathat_(Sukhothai)) — เลือกภาพสีโทนภาพวาดได้ |
| **อยุธยา** (1351) | `ayutthaya.jpg` (ใหม่) | [Category:Wat_Phra_Si_Sanphet](https://commons.wikimedia.org/wiki/Category:Wat_Phra_Si_Sanphet) หรือ [Category:Old_paintings_of_Ayutthaya](https://commons.wikimedia.org/wiki/Category:Old_paintings_of_Ayutthaya) |
| **เสียกรุง** (1767) | `fall-ayutthaya.jpg` (ใหม่) | [Category:Burmese-Siamese_War_(1765–1767)](https://commons.wikimedia.org/wiki/Category:Burmese%E2%80%93Siamese_War_(1765%E2%80%931767)) — มีภาพประวัติศาสตร์ |

---

## วิธีดาวน์โหลดจาก Wikimedia

1. คลิกลิงก์ "Wikimedia file page" → เข้าสู่หน้า File:
2. คลิกที่ภาพ → ปุ่ม "Original file" หรือ "Download" ด้านล่าง
3. Save as → ใช้ชื่อตาม "Local filename" (เช่น `rama1.jpg`)
4. วางใน `webapp/static/timeline-images/`
5. แจ้งผมว่า upload เสร็จ — ผม update DB description/credit ให้

## เกณฑ์เลือกภาพ
- ❤ ภาพวาด / illustration > ภาพถ่าย
- 🎨 โทนสีเข้ากับ era theme ของ entry (โบราณ-ทอง / โบราณ-ขาวดำ)
- 📐 อัตราส่วน 3:4 (portrait) ขนาด ≥ 400×533 px
- ✅ Public Domain เท่านั้น

## หมายเหตุ Credit
ภาพใหม่ทุกภาพแนะนำลง credit format เดิม:
```
Wikimedia Commons · Public Domain
```
หรือถ้ามีศิลปิน → `<ชื่อศิลปิน> · Wikimedia Commons · PD`
