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
