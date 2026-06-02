"""Version history — แสดงในหน้า /about

ใหม่สุดอยู่บนสุดของ list. แต่ละ entry มี:
    version: string (semver/date code)
    date: ISO date string
    title: หัวข้อสั้น
    highlights: list of strings (สิ่งที่เพิ่ม/แก้สั้นๆ)
    details: list of {category, items} — category = "เพิ่ม"/"แก้"/"ปรับ"

เพิ่ม entry ใหม่ด้านบน (index 0) เสมอ
"""

CHANGELOG = [
    {
        "version": "2026.06.01-e",
        "date": "2026-06-01",
        "title": "Orbit View + Checkbox ราศี/ภพ + UI polish",
        "highlights": [
            "เพิ่มโหมด 🌌 Orbit view (geocentric, วงรีเอียงต่างมุม) สลับกับผังจักรราศี",
            "ดาวทุกดวงอยู่ถูก sector ราศีบน orbit (ray-intersection algorithm)",
            "เพิ่ม checkbox ราศี + ภพ แสดง/ซ่อน (เรียง: ราศี/ธาตุ/ภพ/ตรียางค์/Orbit)",
            "ดาวจรพิษมีสัญลักษณ์ 🐍🦅🐕 เหมือนดาวกำเนิด",
            "เส้นแบ่งราศี + zodiac rim ใน Orbit mode",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "Orbit view: 9 วงรี geocentric (จันทร์→อาทิตย์→…→ราหู/เกตุ), Earth ⊕ center",
                    "build_orbit_layout() + _orbit_point_at_ray_angle() ใน server.py",
                    "12 เส้นแบ่งราศี (radial dashed) + zodiac rim ใน orbit mode",
                    "Checkbox toggle-rasi (ราศี) + toggle-bhava (ภพ) พร้อม localStorage persist",
                    "Transit chips ใน orbit mode — ring ขยาย +8 จาก natal ring",
                    "ดาวจรที่ตกตรียางค์พิษแสดง shadow + icon เหมือน natal chips",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "Bug: orbit chip position — เปลี่ยนจาก parametric angle เป็น ray-intersection บน rotated ellipse",
                    "Bug: _angle_from_zodiac 90+30i+deg → 75+30i+deg (degree 0 = ขอบราศี ไม่ใช่กลาง)",
                    "2.5D toggle เปลี่ยนเป็น Orbit toggle (ลบ CSS tilt ออก)",
                    "R_LABEL=222, R_BHAVA=110, R_ELEMENT=130 — ลดการบังกัน",
                    "R_LAGNA_MARKER=200 — ขยับลัคนา marker ให้ไม่ชนดาว",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "Orbit ring rotation: เอียงเด่นขึ้น (ราหู -32°, มฤตยู +28°, อังคาร -18°)",
                    "Orbit eccentricity เพิ่ม (ry/rx ratio ~0.78) — ดูเหมือน orbit จริงมากขึ้น",
                    "Cache version → v=20260601g",
                ],
            },
        ],
    },
    {
        "version": "2026.06.01-d",
        "date": "2026-06-01",
        "title": "ดาวจรตามองศา + UI polish + กล่องวิธีใช้",
        "highlights": [
            "ดาวจรบนผังวางตามองศา/ตรียางค์ที่ถูกต้อง (เหมือนดาวกำเนิด)",
            "การ์ดดาวกำเนิด (โหมดศึกษา) มี subtitle วันที่/เวลา/สถานที่ เหมือนการ์ดดาวจร",
            "Overlay ภพทักษาซ้อน ขอบบนเสมอตารางทักษา 3×3 แล้ว",
            "Version badge ติด \"เกี่ยวกับ\" ในเมนู — เห็นเวอร์ชั่นล่าสุดได้เลย",
            "เพิ่มกล่องวิธีใช้ในหน้าผูกดวงสุริยยาตร์",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "Transit chips position by degree — ใช้ `_chip_layout_by_decanate` ที่ R_TRANSIT (286)",
                    "Subtitle ใต้ \"ดาวกำเนิด\" ในตาราง — เกิด/วันที่/เวลา/จังหวัด",
                    "Version badge `.version-badge` ใน nav-link \"เกี่ยวกับ\" ทั้ง 3 หน้า — อ่านจาก CHANGELOG[0]",
                    "กล่องวิธีใช้ `.howto-card` ในหน้า / (แสดงเฉพาะตอนยังไม่ผูกดวง) อธิบาย Scrubber/โหมด/Hover/Toggle",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "Overlay ภพทักษาซ้อนเริ่มต่ำกว่าตาราง 3×3 → `.taksa-overlay-side` ตั้ง `margin-top: 0 !important; align-self: stretch`",
                    "Header โหรทายหนู: ตัด \"— ฉบับ อ.กานดา\" ออกจาก subtitle",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "`_common_context()` ส่ง `latest_version` อัตโนมัติทุกหน้า (อ่านจาก CHANGELOG[0])",
                    "Cache version → v=20260601f",
                ],
            },
        ],
    },
    {
        "version": "2026.06.01-c",
        "date": "2026-06-01",
        "title": "ดาวจรเลื่อนเวลาได้ + ตัดฟอร์มดาวจรออก",
        "highlights": [
            "ตัดช่องกรอกวันเวลา/จังหวัดดาวจรออกจากฟอร์ม — ใช้ \"วันนี้/ปัจจุบัน/กรุงเทพฯ\" auto",
            "เพิ่มแถบ Scrubber ใต้ผังจักรราศี — เลื่อนวัน ±1/±7/±30 หรือเลือกวันที่/เวลาเฉพาะ",
            "เลื่อนเวลาแล้วทุกส่วน (ผังดวง + คำทำนาย + สรุป + ภพ + oracle) อัพเดทพร้อมกัน",
            "ปุ่ม Scrubber ไม่กระโดด scroll กลับบน — อยู่ที่เดิม",
            "การ์ดดวงชะตา + ดาวจร ใช้ layout เดียวกัน (วันที่/เวลา/สถานที่ grid)",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "Transit Scrubber: ปุ่ม -30/-7/-1/วันนี้/+1/+7/+30 + date+time picker",
                    "การ์ดดวงชะตา (natal-info-card) — แสดงวันเกิด/เวลา/สถานที่/จันทรคติ/ลัคนา แบบ grid 2 column",
                    "การ์ดดาวจร (transit-info-card) — โครงสร้างเดียวกับการ์ดดวงชะตา + scrubber ใต้",
                    "Scroll position restore ผ่าน sessionStorage — กดปุ่มเลื่อนเวลาแล้วอยู่จุดเดิม",
                    "history.scrollRestoration = manual — กันเบราว์เซอร์เด้ง scroll เอง",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "ฟอร์มเดิมต้องกรอก 3 field สำหรับดาวจร (วันที่/เวลา/จังหวัด) → ตัดออกหมด ใช้ default",
                    "Transit chart calc ทำทุกครั้งหลังกดผูกดวง (ไม่ optional แล้ว)",
                    "การ์ด result-header-card → เปลี่ยนเป็น natal-info-card layout เดียวกับ transit",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "ย้าย transit card จากบนผังลงไปใต้ผังจักรราศี — อ่าน flow ดูดาว → เลื่อนเวลาง่าย",
                    "เพิ่ม API endpoint POST / รับ transit_date_iso + transit_time_24 (hidden form)",
                    "scrubber-busy state — disable button ชั่วคราวระหว่างคำนวณ",
                ],
            },
        ],
    },
    {
        "version": "2026.05.31-d",
        "date": "2026-05-31",
        "title": "ปรับหน้าเกี่ยวกับ + ขนาดฟอร์มหน้าแรก",
        "highlights": [
            "หน้าเกี่ยวกับมี header ❀ เหมือนหน้าผูกดวง",
            "ฟอร์มข้อมูลผู้ขอดวง: ขนาดเท่ากันก่อน/หลังผูกดวง",
        ],
        "details": [
            {
                "category": "แก้",
                "items": [
                    "หน้า /about ชิดด้านบนเกินไป → เพิ่ม site-header + ❀ ออรนาเมนต์",
                    "ฟอร์ม 'ข้อมูลผู้ขอดวง' ตอนยังไม่ผูกดวงกินเต็มหน้า → ปรับ max-width: 340px (เท่ากับตอนผูกดวงเสร็จ) + จัดกลาง",
                ],
            },
        ],
    },
    {
        "version": "2026.05.31-c",
        "date": "2026-05-31",
        "title": "ปรับ UX รอบใหญ่: ตารางสมบูรณ์ + เปิดภพ 12 + เกี่ยวกับ",
        "highlights": [
            "ตาราง dasso จร เพิ่มธาตุ/ตรียางค์/พิษ เหมือนตารางดาวกำเนิด",
            "ภพ 12 แสดงดาวกำเนิดที่อยู่ในแต่ละภพ",
            "Toggle แยก ตรียางค์ / ธาตุ",
            "หน้าเกี่ยวกับ (เวอร์ชั่นไฮ้สตอรี่)",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "ตารางดาวจร: เพิ่มคอลัมน์ธาตุ + ตรียางค์ + พิษ (เหมือนดาวกำเนิด)",
                    "ภพ 12 ในตารางความหมาย — แสดงดาวกำเนิดที่ตกในแต่ละภพ",
                    "Toggle ธาตุ แยกออกจาก ตรียางค์ (เปิด/ปิดอิสระกัน)",
                    "หน้า /about — ประวัติเวอร์ชั่น + รายการแก้ไข accordion",
                    "ดาวจรกระทบดาวทักษา — แสดง chip ดาว + ลูกศรกุม/เล็ง",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "Tooltip อ่านยาก (text มืดบน bg มืด) → ปรับสีเป็นทอง bg + cream text",
                    "Mobile tap ดาว/ตรียางค์ → tap ค้าง + tap นอก/ESC ปิด",
                    "ข้อมูลการคำนวณ — เปิดตลอด + ยาวลงเป็น single column",
                    "ภพทักษาซ้อน Overlay ย้ายไปข้างขวาตาราง — แบ่ง 50/50",
                    "Horathaynu: ดาวกองที่เส้นเริ่ม → กระจายในเซกเตอร์เหมือนเดิม",
                    "ดาวกำเนิดวางตามตรียางค์ที่ตน (ไม่กระจุกที่กลางราศี)",
                ],
            },
        ],
    },
    {
        "version": "2026.05.31-a",
        "date": "2026-05-31",
        "title": "ตรียางค์ (Drekkana) + ธาตุของราศี",
        "highlights": [
            "36 ช่องตรียางค์ + ดาวเจ้าครอง (เลขอารบิก 1-7)",
            "ตรียางค์พิษ 3 ชนิด: 🐍 พิษนาค / 🦅 พิษครุฑ / 🐕 พิษสุนัข",
            "ธาตุของราศี (ไฟ/ดิน/ลม/น้ำ) — สัญลักษณ์ที่ขอบใน",
            "Hover/tap ดู ตรียางค์ + พิษ + ความหมาย",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "โมดูล `thai_astro/triyangka.py` — คำนวณ Drekkana 36 ช่อง",
                    "ตรียางค์พิษ พร้อมระดับ หนัก/เบาตาม offset 3.20-6.39°",
                    "ธาตุของราศีพร้อม element marker บน SVG",
                    "Toggle checkbox มุมขวาบนของผัง — จำสถานะใน localStorage",
                    "Poison shadow + icon บนดาวกำเนิด/ลัคนาที่ตกพิษ",
                    "ตารางดาวกำเนิด: เพิ่ม chips ธาตุ + ตรียางค์ + พิษ + row border",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "ลัคนา hover bounce — เพิ่ม transform-origin: center",
                ],
            },
        ],
    },
    {
        "version": "2026.05.30",
        "date": "2026-05-30",
        "title": "ขยายคำทำนายโหรทายหนูให้ลึก — 3 ชั้นการตีความ",
        "highlights": [
            "Verdict (คำตอบสั้น) ด้านบน + Category lens",
            "25 categories คำถาม + score-based matching",
            "Layer 1+2+3: bhava + lord-in-bhava + planet×bhava + combo",
            "Gibberish guard + warning banner เมื่อตีคำถามไม่ออก",
            "Accordion suggestion 9 กลุ่ม — คำถามเป็นประโยคจริง",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "Question→bhava mapping 25 categories",
                    "12 ภพ น้ำเสียง prashna (`bhava_meanings_prashna.py`)",
                    "Planet × Bhava table — 84 entries (7 ดาว × 12 ภพ)",
                    "Lord-in-Bhava — port 144 entries จาก natal",
                    "Planet combo — 35 คู่ดาวพิเศษ filter ตาม category",
                    "Verdict synthesis จากทุกชั้น (good/warning/neutral)",
                    "On-topic check — ซ่อน text ที่ off-topic",
                    "Length limit 200 + 5 gibberish heuristics",
                    "Suggestion accordion 9 กลุ่ม คำถามเป็นประโยคเต็ม",
                    "Warning banner (กล่องเหลือง) เมื่อตีคำถามไม่ออก",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "Keyword 'ยา'/'หาย' สั้นเกินไป — false positive",
                    "ปุ่ม 'ทำนาย' alignment กับ input",
                ],
            },
        ],
    },
    {
        "version": "2026.05.29",
        "date": "2026-05-29",
        "title": "โหรทายหนู (Hora Thai Nu) — ดวงยามอัฐุกาล",
        "highlights": [
            "วิชาตั้งดวงจากเวลา ไม่ใช้วันเดือนปีเกิด",
            "Chain walking + ping-pong derive counts",
            "11 ดาว + ลัคนา + ภพ 12 + ดาวเกษตร",
            "ถาม-ทำนาย AJAX + 6 category renderers",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "โมดูล `thai_astro/horathaynu/` — สูตรตั้งดวงตำราอ.กานดา",
                    "14 ชุดสูตรประจำวัน (7 วัน × กลางวัน/กลางคืน)",
                    "ผังจักรราศี SVG + เลขดาวเกษตร + วงนอกเวลา 12 cell",
                    "Significator system (15+ keyword categories)",
                    "AJAX endpoint /horathaynu/ask",
                ],
            },
        ],
    },
    {
        "version": "2026.05.28",
        "date": "2026-05-28",
        "title": "Session 2: Taksa overlay + lunar + Uranus + arc-second",
        "highlights": [
            "ทักษา 8 ดาว 8 ทิศ + มหาทักษาดาษา 96 ปี",
            "ทักษาจร (Transit Taksa) + overlay × natal",
            "บทพูดของโหร (Oracle Reading) สังเคราะห์ครบทุก source",
            "ดาวมฤตยู (ดาวที่ 10) + arc-second จริงสำหรับลัคนา",
            "ปฏิทินจันทรคติไทย (ขึ้น/แรม + เดือน + ปีนักษัตร)",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "Taksa system — `thai_astro/taksa.py`",
                    "Dignities + yogas — `thai_astro/dignities.py`",
                    "Lunar calendar — `thai_astro/lunar.py`",
                    "Oracle narrative — สังเคราะห์เป็นบทพูดเดียว",
                    "ดาวมฤตยู (Uranus) — เป็นดาวที่ 10",
                    "View tabs: ดูดวง / ศึกษาโหราศาสตร์",
                ],
            },
        ],
    },
    {
        "version": "2026.05.27",
        "date": "2026-05-27",
        "title": "Initial release — ผูกดวงสุริยยาตร์ครบสูตร",
        "highlights": [
            "ปฏิทินจ.ศ. + เถลิงศก + หรคุณ + DesireFactory",
            "สมผุสดาว 9 ดวง + ลัคนา (อันโตนาที 12 ราศี)",
            "ผังจักรราศี SVG + ภพ 12 + เจ้าเรือนครองภพ",
            "คำทำนายดาวจรกระทบดาวเดิม (กุม/เล็ง)",
            "77 จังหวัด locality offset",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "Port สูตรจาก Devtino.Astrology (C#)",
                    "Web app FastAPI + Jinja2",
                    "Deploy พร้อม Railway",
                ],
            },
        ],
    },
]


def get_latest_version() -> str:
    return CHANGELOG[0]["version"] if CHANGELOG else ""
