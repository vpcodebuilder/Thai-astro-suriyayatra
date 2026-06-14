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
        "version": "2026.06.14-b",
        "date": "2026-06-14",
        "title": "⚡ มาตรฐานดาว 10 ตำแหน่งไทย + dignity ผสมเข้าทุกการ์ด",
        "highlights": [
            "เพิ่มตำแหน่งดาวมาตรฐานไทย 6 ตัว: มหาจักร / จุลจักร / ราชาโชค / เทวีโชค / อุจจาภิมุข / อุจจาวิลาส",
            "ลำดับกำลังใหม่: อุจจ์ > มหาจักร > จุลจักร > ราชาโชค > เทวีโชค > เกษตร > อุจจาภิมุข > อุจจาวิลาส > ประ > นิจ",
            "ดาวรายดวงในการ์ดผูกดวงแสดงครบ 10 ดวง (เดิมแสดงเฉพาะแข็ง/อ่อน)",
            "Tooltip ผังจักรราศี + ตารางดาวกำเนิด/ดาวจร แสดงตำแหน่งกำลัง + คะแนน",
            "คำพยากรณ์ในชีวิต (การเงิน/การงาน/ความรัก/ครอบครัว) มี suffix dignity ทุกตำแหน่ง",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "thai_astro/dignities.py: ตาราง MAHACHAK/JULACHAK/RAJA_YOKE/TEVI_YOKE/UJ_PHIMUKH/UJ_VILAS",
                    "ตาราง PRA_RASIS ใหม่ (ตำราไทยมาตรฐาน) แทน fallback PLANET_RELATIONS",
                    "compute_dignity ตรวจ 10 ตำแหน่งตามลำดับกำลัง",
                    "dignity-pill (in natal/transit table) — สีตามตำแหน่ง 13 แบบ",
                    "_DIGNITY_SUFFIX 13 entries (ผสมเข้าทุกคำทำนายเจ้าเรือนภพ)",
                    "Section ตำแหน่งกำลังดาว: แสดงครบ 10 ดวง พร้อม score ±N",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "บั๊ก: เกษตร/อุจจ์ ไม่แสดงในตำแหน่งกำลังดาว (filter is_strong/is_weak เข้มเกิน)",
                    "จัดเรียงการ์ดคำพยากรณ์: เกณฑ์ดวงพื้นฐาน → โยค/เกณฑ์ → ตำแหน่งกำลังดาว → ที่ยังไม่ครบ",
                    "ย้าย near-misses ไป view-student เฉพาะ (ดูดวงไม่เห็นรกตา)",
                    "เกณฑ์ดวงพื้นฐานสร้างจากโยค match จริง (ตัด template ปทุมเกณฑ์ที่ hardcoded)",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "UI tooltip ดาวบนผัง: เพิ่มแถว ⚡ กำลัง + คะแนน +N/-N",
                    "ตารางดาวกำเนิด/ดาวจร: ใส่ dignity pill ในแถว tag (ธาตุ/ตรียางค์/พิษ)",
                    "astropattern.md: เพิ่มหัวข้อ 'ตำแหน่งดาวมาตรฐานไทย' + 6 ตาราง",
                    "ปัญจมหาบุรุษ (VE-001..005): เปลี่ยนนิยาม strong = อุจจ์/เกษตรเท่านั้น (ไม่รวมตำแหน่งเสริม)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.14",
        "date": "2026-06-14",
        "title": "📜 รูปดวง / โยค / เกณฑ์ — ฐานข้อมูล 28 กฎ + จัดเรียง Oracle ใหม่",
        "highlights": [
            "ระบบใหม่ ตรวจรูปดวง/โยค/เกณฑ์ ๒๘ กฎ จากตำราอุดมเดช + ภารตะ",
            "แยกหมวด: รูปดวงไทย / กลุ่มลัคนา / องค์เกณฑ์+อุดมเกณฑ์ / ปัญจมหาบุรุษ / โยคสำคัญ / จันทรโยค / โยคเสีย",
            "เกณฑ์ดวงพื้นฐาน สรุปจากโยคที่เข้าจริง ๆ ไม่ใช่ template หลอก",
            "รายละเอียดเชิงลึก (ตำแหน่งกำลังดาว + เกณฑ์ + คำแนะนำ) ย้ายเข้าโหมดศึกษา",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "thai_astro/astro_patterns.py — 28 rule detector",
                    "TH-001..004 รูปดวงไทย: มาลัย / คันศร / จตุสดัย (ราศีจร) / ลัคนานำพล",
                    "TH-101..104 กลุ่มลัคนา: นระ/อัมพุ/กีฏะ/ปัศวะ",
                    "TH-105 องค์เกณฑ์ + TH-106 อุดมเกณฑ์ ตามตำราไทย (ยศ-ทรัพย์)",
                    "VE-001..005 ปัญจมหาบุรุษ: รูจกะ/ภัทร/หังสะ/มาลวยะ/ศศะ",
                    "VE-101..106 โยคสำคัญ: คชเกสรี/ลักษมี/อธิ/อมล/ราชา/ธน",
                    "VE-201..205 จันทรโยค: สุนภา/อนภา/ทุรธรา/วาสิ/อุภยจารี",
                    "MA-001..002 โยคเสีย: พินทุบาทว์ / บาปเคราะห์รุมลัคนา",
                    "ส่วน \"เกณฑ์ที่ยังเข้าไม่ครบ\" — แนะนำว่าขาดอะไร ดาวจรไหนจะหนุน",
                    "tests/test_astro_patterns.py — 12 tests (180/180 ผ่าน)",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "TH-003 จตุสดัย — จาก \"ภพ 1/4/7/10\" → ถูกต้องคือ \"ราศีจร เมษ/กรกฎ/ตุลย์/มกร\"",
                    "VE-101 คชเกสรี — เพิ่มเงื่อนไข พฤหัสไม่นิจ/ประ",
                    "VE-103 อธิโยค — ต้องครบทั้ง 3 ดวง (พุธ+พฤหัส+ศุกร์) ไม่ใช่ ≥2",
                    "เกณฑ์ดวงพื้นฐาน — ลบ template ปทุมเกณฑ์ที่ hardcoded; ใช้โยคที่ match จริง",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "หมวดกลุ่มลัคนา (TH-101..104) แสดงเฉพาะเมื่อเข้าทั้ง องค์+อุดมเกณฑ์ พร้อมกัน",
                    "ตำแหน่งกำลังดาว + รูปดวง/โยค/เกณฑ์ + เกณฑ์ที่ยังไม่ครบ → ย้ายเข้ากล่อง \"📊 รายละเอียดสำหรับผู้ศึกษา\" (view-student)",
                    "หน้าดูดวงปกติเห็นแค่ \"เกณฑ์ดวงพื้นฐานของคุณ\" — ไม่รก",
                    "astropattern.md → v1.1 (28 rule + อธิบายกฎแสดงผล)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.13",
        "date": "2026-06-13",
        "title": "📅 ฤกษ์ 7 วัน strip + ดิถีใหม่ ๓ แบบ + ความละเอียดเวลา + แก้ Edge bug",
        "highlights": [
            "เพิ่ม \"ฤกษ์ 7 วัน\" บนหัวหน้าหาฤกษ์ — เห็นภาพรวมเหมือนพยากรณ์อากาศ",
            "คลิกการ์ดวันแล้วคลิกกิจกรรม → ขยายเวลาฤกษ์อินไลน์พร้อม tag ครบ",
            "เพิ่มดิถี ๓ แบบ: ทักทิน (ครหา), ยมขันธ์ (ไฟไหม้), ปัญจมหาเศรษฐี (ทรัพย์)",
            "เพิ่มช่วงวันหาฤกษ์: 15/45 วัน (รวมเป็น 15/30/45/60/90)",
            "Tag \"📚 ตำราขัดกัน\" ในวันที่ตำราต่างเล่มไม่ตรงกัน",
            "แก้บั๊ก ครึ่งดาว ⯨ แสดงเป็นกล่องบน Edge — ใช้ ★ + CSS clip แทน",
            "แก้บั๊ก แถวดิถีหายในวันอังคาร/พุธ/เสาร์ ที่ไม่ตรง event ใด",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "ฤกษ์ 7 วัน strip (−2..+4): ดาวเฉลี่ย + เกรด + icon top 3 กิจกรรม",
                    "การ์ดวันแต่ละใบคลิกแล้ว expand → list กิจกรรมเหมาะ/ห้าม",
                    "Chip กิจกรรมในแต่ละวัน บอกเกรด + จำนวนเวลา → คลิกขยายฤกษ์จริงพร้อม tag",
                    "ดิถีทักทิน (ทัคธทิน) — universal_bad severity 2",
                    "ดิถียมขันธ์ — universal_bad severity 3 (ไฟไหม้)",
                    "ฤกษ์ปัญจมหาเศรษฐี — ดี business+ceremony severity 3",
                    "ปุ่มช่วงวันหาฤกษ์ 15 และ 45 วัน (เดิมมีแค่ 30/60/90)",
                    "Tag \"📚 ตำราขัดกัน\" เมื่อมีดิถีมงคล+ดิถีร้ายในวันเดียว (พฤหัส 5 / เสาร์ 9)",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "ครึ่งดาวบน Edge แสดงเป็นกล่อง — ใช้ ★ + CSS overlay clip",
                    "แถวดิถีหายในวันอังคาร/พุธ/เสาร์ที่ไม่ตรง event — fallback เป็น \"ดิถีปกติ\"",
                    "ปุ่มดูฤกษ์ละเอียดเดิมที่ไม่ตอบ → เปลี่ยนเป็น chip คลิกขยายอินไลน์",
                    "Event detail panel ค้างเมื่อสลับการ์ดวัน — reset เมื่อ onCardClick",
                ],
            },
        ],
    },
    {
        "version": "2026.06.08",
        "date": "2026-06-08",
        "title": "🌟 หาฤกษ์ — เพิ่มดิถี ๑๙ แบบ + ฤกษ์ใหญ่ ๙ + UI โดดเด่นกว่าเดิม",
        "highlights": [
            "เพิ่มดิถีตามตำราโหรไทย ๑๙ แบบ พร้อมคำอธิบายให้ความรู้",
            "ฤกษ์ใหญ่ ๙ ฤกษ์ (มหัทธโน/ราชา/เทวี/ภูมิปาโล ฯลฯ) เป็น tag กดอ่านได้",
            "เกณฑ์พิเศษ (กนกนารี/กนกกุญชร/จักขุมายา) เป็น tag กดอ่านได้",
            "ระบบอัจฉริยะ: ดิถีเฉพาะกิจกรรม (เช่น เรียงหมอน, สงฆ์ 14) จะแสดงเฉพาะกิจกรรมที่ตรงเท่านั้น",
            "เพิ่มแถบช่วงเวลาบนหัวการ์ดฤกษ์ — เห็นชัดทันทีว่าเช้า/บ่าย/กลางคืน",
            "เพิ่มแถบเตือนสีแดง ⚠️ เมื่อมีดิถีร้ายที่ตรงกิจกรรม",
            "กรองเฉพาะฤกษ์ที่ดีเยี่ยม >= 60% — ไม่แสดงฤกษ์คะแนนน้อย",
            "ปรับน้ำหนักคะแนนใหม่: ดิถีร้ายลดคะแนน ×2 ทำให้แตกต่างชัดเจน",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "ดิถีมงคล: เรียงหมอน (สำหรับแต่งงานเฉพาะ)",
                    "ดิถีร้าย: พิฆาต, ทรธึก, อายกรรมพลาย, กทิงวันแท้, กทิงวันไม่เต็ม",
                    "วันห้ามเฉพาะดิถี: สงฆ์ 14 (ห้ามบวช), นารี 11, แต่งงาน 7",
                    "วันห้ามเฉพาะวาร: ห้ามขึ้นบ้านวันเสาร์, ห้ามแต่งงานวันพุธ, ห้ามโกนจุกวันอังคาร",
                    "ฤกษ์ใหญ่ ๙ ฤกษ์ พร้อมคำอธิบายและกิจกรรมที่เหมาะ",
                    "เกณฑ์พิเศษ ๓ แบบ พร้อมคำอธิบายและกิจกรรมที่เหมาะ",
                    "Popover แสดงรายละเอียดดิถี/ฤกษ์/เกณฑ์ — กด tag เพื่ออ่าน",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "แถบช่วงเวลาบนหัวการ์ดฤกษ์ — สีตามช่วง (เช้า/สาย/บ่าย/เย็น/ค่ำ/กลางคืน)",
                    "ดิถี/ฤกษ์/เกณฑ์ เปลี่ยนจาก list ยาวเป็น tag chip ประหยัดพื้นที่",
                    "เกณฑ์การกรอง: แสดงเฉพาะฤกษ์คะแนน >= 60% (เกรด \"ดีเยี่ยม\")",
                    "ดิถีร้ายลดคะแนน ×2 (-4 หรือ -6) ทำให้ฤกษ์ที่ติดดิถีร้ายต่ำกว่าวันธรรมดาชัดเจน",
                    "Logic ถูกต้อง: \"ห้ามขึ้นบ้านใหม่วันเสาร์\" จะแสดงเฉพาะ housewarming (ไม่ใช่ ซื้อที่ดิน)",
                    "กทิงวัน: แก้กฎให้ถูกตำรา (วาร-ดิถี-เดือน ตรงกัน) + แยกระดับ \"แท้\" / \"ไม่เต็ม\"",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "เลิกใช้กาลโยค dithi/rasi/roek match ที่เป็นแค่ผลคณิตศาสตร์ (mod-N) — ใช้เฉพาะ WAN",
                    "ปุ่ม \"ตรวจสอบฤกษ์ที่ได้มา\" คืนผลลัพธ์ได้แล้ว (JS bug)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.05-d",
        "date": "2026-06-05",
        "title": "Checkbox toggles → ปุ่ม collapsible (ไม่บัง chip อีก)",
        "highlights": [
            "ปุ่ม ⚙ ชั้น เล็กกว่าเดิม ไม่บังราศีกุมภ์/พฤษภ/มีน อีกแล้ว",
            "คลิกปุ่มเพื่อกาง 5 toggles (ราศี/ธาตุ/ภพ/ตรียางค์/Orbit)",
            "Click outside / click ปุ่มอีกครั้ง → ปิด",
            "จำสถานะ open/close ใน localStorage",
            "Mobile: ปุ่มยิ่งเล็ก ซ่อน label \"ชั้น\" เหลือแค่ไอคอน ⚙",
            "เพิ่ม seed.py: auto-import 401 ปีอธิกมาส (BE 2300-2700) ทุก deploy",
        ],
        "details": [
            {
                "category": "แก้",
                "items": [
                    ".chart-cb-stack — เพิ่มชั้น collapsible: ปุ่ม ⚙ ชั้น + รายการ checkboxes ที่ซ่อน default",
                    "JS: bind click toggle + outside-click close + persist state",
                    "Mobile: hide \"ชั้น\" label, font/padding เล็กลง (≤600px)",
                ],
            },
            {
                "category": "เพิ่ม",
                "items": [
                    "seed_adhikamasa() — import data/adhikamasa_scraped.json (401 entries) อัตโนมัติ",
                    "idempotent: skip ถ้ามี row อยู่แล้ว",
                ],
            },
        ],
    },
    {
        "version": "2026.06.05-c",
        "date": "2026-06-05",
        "title": "Fix: หลาย sub-intent ให้คำตอบซ้ำกัน — เพิ่ม category-specific intros",
        "highlights": [
            "ปัญหา: career/promotion/boss_conflict ใช้ sig+bhava เดียวกัน → text ออกซ้ำ",
            "แก้: CATEGORY_INTROS — 33 categories × 3 tier (good/warn/neutral)",
            "เพิ่ม work_conflict sub-intent (priority 10) สำหรับ \"อุปสรรคงาน/ปัญหาที่ทำงาน\"",
            "Intro เปลี่ยนตาม verdict tier — ทำให้แต่ละคำถามได้คำตอบเฉพาะตัว",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "horathaynu/data/category_intros.py — get_category_intro() + 33 entries",
                    "QuestionMapping work_conflict — primary_bhava=6 (อริ), sig=mars, priority=10",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "prophecy.predict() — ผนวก cat_intro เข้า header (บรรทัด 3) เปลี่ยนตาม cat+tier",
                ],
            },
        ],
    },
    {
        "version": "2026.06.05-b",
        "date": "2026-06-05",
        "title": "โหรทายหนู ลึก 5 ชั้น — Intent + Dignity + Verdict + House relation + Sub-intents",
        "highlights": [
            "Intent parser: จับ yes_no / when / where / who / why / how / outcome",
            "Polarity: hope / worry / neutral (จาก keyword อยาก/กลัว/ห่วง)",
            "Verdict tier 5 ระดับ + โอกาส % (very_high 85 → very_low 15)",
            "Dignity ของ sig — อุจน์/เกษตร/มูล/มิตร/ประ/นิจ ผนวกเข้าทุกคำทำนาย",
            "House relation 12 ระยะ (ลาภะ✓/ตรีโกณ/ทุกข์...) ตอบ \"ภพผสมภพ\"",
            "ขยาย sub-intents: career, love, wealth, study, home → +18 categories",
            "ลัคนา/ดาวเกษตรกุมภ์ในโหรทายหนู = ราหู (sync Session 13)",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "horathaynu/core/intent.py — parse_intent + INTENT_HEADLINE_TEMPLATES",
                    "horathaynu/core/dignity_score.py — compute_sig_dignity + DIGNITY_SUFFIX",
                    "horathaynu/core/verdict.py — compute_verdict (yes/no scoring)",
                    "horathaynu/core/house_relation.py — 12 ระยะภพคำถาม→sig",
                    "ProphecyResult: เพิ่ม 13 fields ใหม่ (intent/verdict/dignity/relation)",
                    "Sub-intents: promotion, boss_conflict, freelance, love_loyalty, love_reconcile, love_new, love_thirdparty, investment, loan, bonus, repay, health_recover, health_surgery, exam_pass, scholarship, buy_house, move_home (+18)",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "horathaynu/data/lordship.py: กุมภ์ = ราหู (เดิมเสาร์ — sync RASI_LORD)",
                    "career priority ลด 7→6 เพื่อให้ sub-intents ชนะ score-based matching",
                    "love category match love_loyalty/love_reconcile/love_new prefix สำหรับ renderer",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "prophecy.predict() orchestrate 5 phases: Intent → Dignity → House relation → Verdict → Render",
                    "answer text: บรรทัดบนสุด = intent_headline + verdict label + %",
                    "JSON response /horathaynu/ask: ขยาย field 13 ตัว (verdict/intent/dignity/relation)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.05-a",
        "date": "2026-06-05",
        "title": "ดาวเกษตรกุมภ์ = ราหู + คำพยากรณ์โหรขยาย dignity",
        "highlights": [
            "RASI_LORD[กุมภ์] เปลี่ยนจากเสาร์ → ราหู (เลขเกษตร 8 ตามตำราไทย)",
            "ทุก section ของ \"คำพยากรณ์จากโหร\" แสดงดาวจรเสมอ (ไม่หายเงียบ)",
            "แยกชั้น \"ดวงเดิม\" / \"ดาวจร\" พร้อมเส้นคั่น + label วันที่ดาวจร",
            "คำทำนายแต่ละ entry ผนวก dignity: เกษตร / อุจน์ / นิจ / ประ ฯลฯ",
            "ดาวเกษตรในราศีตัวเอง → \"แสดงพลังเต็ม\"; ดาวนิจ → พลิกดีเป็นเตือน",
        ],
        "details": [
            {
                "category": "แก้",
                "items": [
                    "planets.py: RASI_LORD[10] = ราหู (สอดคล้องเลขเกษตรกุมภ์ = 8)",
                    "dignities.py: SWAKSHETRA — เสาร์={9}, ราหู={10}",
                    "oracle_narrative._build_life_area_section: รับประกัน transit ≥1 line + แยก natal/transit",
                    "ลัคนาที่ทำให้กุมภ์เป็นภพสำคัญ → chart_lord/house_lords เปลี่ยนเป็นราหู (กระทบทั่วระบบ)",
                ],
            },
            {
                "category": "เพิ่ม",
                "items": [
                    "BhavaLordPrediction: field dignity / dignity_label / dignity_strength",
                    "_DIGNITY_SUFFIX 7 ระดับ — append เข้าทุกคำทำนาย เจ้าเรือนภพ",
                    "Auto-flip tone: อุจน์/เกษตร/มูล บรรเทาเตือน; นิจ/ประ พลิกดีเป็นปะปน",
                    "oracle_narrative: transit_date_label + แสดงในการ์ดหัว + per-section",
                    "server.py: คำนวณ transit_dignities ผ่าน compute_all_dignities(transit_chart.planets)",
                    "CSS .oracle-source-label / .oracle-divider / .oracle-transit-window",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "Template life_areas — render natal block → <hr> → transit block",
                    "label ดาวจร per section มีวันที่: \"🌠 ดาวจร (5 กรกฎาคม พ.ศ. 2569 09:55 น.)\"",
                    "Cap good/warn เพิ่มจาก [:2] → [:3] (รองรับทั้งดวงเดิม+ดาวจร)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-g",
        "date": "2026-06-03",
        "title": "Polish — scrubber textbox theme + label prophecy",
        "highlights": [
            "Scrubber วันที่ดาวจร: textbox มี gold border + Sarabun font (เดิม browser default)",
            "Prophecy life areas: เปลี่ยน label \"ดวงพื้นฐาน\"→\"ดวงเดิม\", \"ช่วงนี้\"→\"ดาวจร\"",
            "→ คำเตือนที่ขึ้น \"⚠ ดวงเดิม\" ฟังเข้าใจง่ายขึ้น (เกณฑ์ติดตัว ≠ ช่วงนี้)",
        ],
        "details": [
            {
                "category": "แก้",
                "items": [
                    "oracle_narrative.py: prefix natal=\"ดวงเดิม\", transit=\"ดาวจร\"",
                    "CSS .scrubber-date-wrap input[type=text]: border+bg+font ตามธีม + :focus glow",
                    "CSS .scrubber-date-wrap .date-picker-btn: gold button hover state",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-f",
        "date": "2026-06-03",
        "title": "ดวงชะตา/ดาวจร/ทักษา UX rework",
        "highlights": [
            "ดวงชะตา (ดาวกำเนิด): แยก 2 บรรทัด — สูติกาล (ตำราไทย) / ตรงกับสากล",
            "ดาวจร header dynamic: \"ดาวจร — DD MMM พ.ศ. YYYY · HH:MM น.\"",
            "ฟอร์มดาวจร: เลือกวันเป็น พ.ศ. (DD/MM/YYYY) + ปุ่ม 📅",
            "ทักษา sync ตาม transit: เลื่อน scrubber → คำทำนายเปลี่ยน + chip บอกวันที่",
            "Edge case: ถ้า transit < birth → ปิดทักษา + แสดง \"ยังไม่เกิดในเวลานี้\"",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "result.birth_intl: weekday + date_th + time + shifted (วันเกิดสากลก่อน sunrise shift)",
                    "result.taksa_ref_label / taksa_age_label — chip บอก \"ทำนายตามวันที่ X · อายุ Y\"",
                    "result.taksa_disabled / taksa_disabled_reason — เมื่อ transit < birth",
                    "transit_meta.day/month/be_year — สำหรับฟอร์ม scrubber พ.ศ.",
                    "JS sync scrubber-date-picker-th (DD/MM/YYYY พ.ศ.) ⇄ scrubber-date-picker (ISO ค.ศ.)",
                    "CSS: .taksa-ref-chip, .taksa-disabled-banner, .transit-header-sep, .scrubber-date-wrap",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "chart_to_view รับ original_birth_intl parameter",
                    "compute_taksa รับ today= taksa_reference_date (จาก transit_chart) แทน datetime.now()",
                    "ดวงชะตา card: ลบ row \"จันทรคติ\" แยก — รวมเข้าบรรทัด \"สูติกาล\"",
                    "ดาวจร card: y h2 header แสดง dynamic date + time",
                    "_date import ย้ายขึ้น top-level เพื่อใช้ใน intl_view section",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-e",
        "date": "2026-06-03",
        "title": "Layout fix — sunrise banner อยู่ใน chart column",
        "highlights": [
            "ย้าย sunrise banner เข้าไปใน chart-section (col 2)",
            "Form ฝั่งซ้าย, banner+chart ฝั่งขวา — layout กลับมาปกติ",
        ],
        "details": [
            {
                "category": "แก้",
                "items": [
                    "เดิม banner ใช้ grid-column: 1/-1 ทำให้ chart ตกแถวล่าง",
                    "ย้าย banner HTML ไปอยู่ใน chart-section element แรก",
                    "ลบ grid-column: 1/-1 ของ .sunrise-banner-section ออก (ไม่ใช้แล้ว)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-d",
        "date": "2026-06-03",
        "title": "Thai sunrise day convention — ผูกดวงตามตำราไทย",
        "highlights": [
            "ตำราไทย: วันใหม่เริ่มที่พระอาทิตย์ขึ้น ไม่ใช่เที่ยงคืน — ระบบรองรับให้อัตโนมัติ",
            "ใส่วันและเวลาแบบเวลาสากล → ระบบปรับเป็นการนับวันแบบไทยให้",
            "2 โหมด: 'อาทิตย์ขึ้นจริง' (default ตามวัน+จังหวัด) / '06:00 ตรง' (ตำราคลาสสิก)",
            "Toggle หลังตั้งดวงเสร็จ สลับโหมดได้",
            "Today widget ใช้ Thai sunrise convention — เที่ยงคืน-06:00 จะแสดงเป็นวันก่อนหน้า",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "thai_astro/sunrise.py — NOAA-based sunrise computation per (date, จังหวัด)",
                    "LATITUDE_BY_PROVINCE — 77 จังหวัด (accuracy ±0.3°)",
                    "thai_birth_day_adjust(birth_dt, province, mode) — auto shift -1 day ถ้าก่อน sunrise",
                    "server.py POST /: รับ sunrise_mode form field + apply adjustment ก่อน Chart.calculate",
                    "Sunrise info banner หลังตั้งดวง — แสดงโหมด, sunrise ที่ใช้, วันที่ปรับแล้ว",
                    "Toggle button: สลับ real_sunrise ⇄ six_am",
                    "Info note ในฟอร์ม: อธิบายว่ากรอกเวลาสากล ระบบปรับให้",
                    "calendar.html: note ว่าใช้วันตามเวลาสากล",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "_today_widget(): ใช้ Thai sunrise convention (วันใหม่ที่ ~06:00)",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-c",
        "date": "2026-06-03",
        "title": "แก้สูตรเดือนจันทรคติ — ใช้ Devtino mas counter (เลิกใช้ floor approximation)",
        "highlights": [
            "User report: 7 ก.พ. 2556 → ระบบแสดง เดือน 3 แต่ที่ถูกคือ เดือน 2",
            "เปลี่ยนสูตรเดือนจันทรคติจาก floor(surathin/29.53) → desire.mas (Devtino) − mas_at_thaloengsok",
            "ผลข้างเคียง: แก้ off-by-1 month ใน adhikamasa year ทั้งหมด",
        ],
        "details": [
            {
                "category": "แก้",
                "items": [
                    "lunar.py: เพิ่ม _mas_at_thaloengsok() พร้อม cache ต่อ cs_year",
                    "lunar.py: compute_lunar_date() ใช้ mas_diff แทน floor(surathin/29.53)",
                    "ปีปกติ: mas_diff 0..11 → เดือน 5,6,7,...,4 (12 เดือน)",
                    "ปีอธิกมาส: mas_diff 0..12 → เดือน 5,6,7,8(ต้น),8(หลัง),9,10,...,4 (13 เดือน)",
                    "ทดสอบผ่าน: 7 ก.พ. 2556 = แรม 12 ค่ำ เดือน 2, Visakha 2569 = เดือน 7, Asalha 2569 = เดือน 8 หลัง",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-b",
        "date": "2026-06-03",
        "title": "Timeline ใหม่ — 13 cinematic scenes + ภาพประกอบเฉพาะ",
        "highlights": [
            "Timeline ปฏิทินไทยใหม่ทั้งหมด: 13 scenes (จากเดิม 11)",
            "Cinematic full-width scene layout — ภาพ background + overlay + ปีใหญ่ซ้าย",
            "เพิ่ม 2 entries ใหม่: ดาราศาสตร์อินเดียรุ่งเรือง (ค.ศ. 499) + อิทธิพลปฏิทินตะวันตก (ค.ศ. 1855)",
            "เพิ่ม SCENE 13 (บทสรุป): ปฏิทินไทยในยุคดิจิทัล (ค.ศ. 2026)",
            "ภาพประกอบใหม่ทั้ง 13 ภาพ — ฉากประวัติศาสตร์ wide cinematic",
            "เส้นเชื่อมสีทอง glow ระหว่าง scene + โทนสีเปลี่ยนตามยุค",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "13 ภาพ timeline01-13.png สำหรับ scenes ใหม่",
                    "Era types ใหม่ใน calendar_epochs: sukhothai, ayutthaya, rattanakosin, digital",
                    "Gold glowing connector ระหว่าง scenes (linear-gradient + box-shadow)",
                    "Overlay tone ต่อยุค: อินเดียโบราณ=น้ำเงินทอง, สุโขทัย=ทองแดง, อยุธยา=ทองแดงเข้ม, รัตนโกสินทร์=ทอง-แดง, digital=น้ำเงิน-ทอง",
                    "Hover effect: scene-bg scale(1.04) 0.6s ease",
                    "Header card สำหรับ Timeline title พร้อม shadow + border ทอง (กัน text กลืนหลัง)",
                ],
            },
            {
                "category": "เปลี่ยน",
                "items": [
                    "Layout เก่า 2-column alternating → cinematic full-width hero scenes",
                    "ลบ SCENE 0X label ออก (เคยมี SCENE 01 ... SCENE 13 ใต้ title)",
                    "Description ของ 11 entries เดิม — เขียนใหม่ทั้งหมดให้ละเอียดและเป็นทางการมากขึ้น",
                    "Image source: ภาพถ่ายบุคคล (Wikimedia) → ภาพประกอบ cinematic 13 ภาพ",
                    "Timeline-intro text สีอ่อน → ใส่ใน dark card กับ text สีครีม-ทอง",
                ],
            },
        ],
    },
    {
        "version": "2026.06.03-a",
        "date": "2026-06-03",
        "title": "ปฏิทินครบรูป — DB + ปีอธิกมาสจริง + ยุคพุทธกาล + วันสำคัญทางราชการ + counter",
        "highlights": [
            "ย้าย calendar data → PostgreSQL/SQLite (SQLAlchemy + Alembic)",
            "ตารางอธิกมาสจริง 401 ปี (BE 2300-2700) จาก myhora.com — แก้ off-by-1 เดือน + เดือน 8 หลัง (8/8)",
            "รองรับ ม.ศ. / ร.ศ. input + แสดง 5 ศักราชในผลลัพธ์",
            "ยุคพุทธกาล (พ.ศ. 544-1180) ผ่าน Meeus algorithm (±5-15 วัน)",
            "20 วันสำคัญทางราชการ (จักรี, รัฐธรรมนูญ, สงกรานต์ ฯลฯ)",
            "Auto-detect today widget บนหน้าแรก + national/holy day chip",
            "Usage counter: ผูกดวง / โหรทายหนู (ไม่เก็บข้อมูลดวง)",
            "Sukhothai/Ayutthaya/เสียกรุง เพิ่มใน Timeline",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "webapp/db.py + models.py + alembic/ — SQLAlchemy infrastructure, DATABASE_URL pattern",
                    "5 tables: calendar_epochs, holy_days, national_holidays, adhikamasa_years, usage_stats",
                    "scripts/scrape_adhikamasa.py — ดึงปีอธิกมาส/อธิกวารจาก myhora.com (มี title-check กัน redirect ปีที่ไม่รองรับ)",
                    "scripts/import_adhikamasa.py — upsert ลง DB (source='myhora')",
                    "thai_astro/ancient_lunar.py — Meeus new-moon algorithm + compute_ancient_lunar_date()",
                    "thai_astro/calendar.py: ce_to_ratanakosin() + convert_year_to_ce(year, era)",
                    "เลือก era (พ.ศ./ค.ศ./จ.ศ./ม.ศ./ร.ศ.) ในฟอร์มเทียบปฏิทิน",
                    "Checkbox \"เดือน 8 หลัง\" (intercalary) ในฟอร์ม lunar→solar — โผล่เมื่อเลือกเดือน 8 เท่านั้น",
                    "20 วันสำคัญทางราชการใน calendar_data: 6 categories (royal/national/tradition/memorial/holiday/international)",
                    "Today widget บนหน้าแรก: \"วันนี้ + จันทรคติ + ปีนักษัตร + holy/national chip\" คลิกไป /calendar",
                    "usage_stats counter: 3 features (suriyayatra_chart, horathaynu_chart, horathaynu_ask)",
                    "3 Timeline entries ใหม่: สุโขทัย (1238), อยุธยา (1351), เสียกรุงครั้งที่ 2 (1767)",
                    "Round-trip warning chip บนวันสำคัญ \"⚠ อาจคลาดเคลื่อน ±1 วันจากปฏิทินทางการ\"",
                    "Ancient mode tag \"⚠ ประมาณ ±5-15 วัน\" สำหรับยุคพุทธกาล",
                    "Procfile release command: alembic upgrade head + seed",
                ],
            },
            {
                "category": "แก้",
                "items": [
                    "lunar.py: is_leap_month_year() query DB ก่อน fallback formula (port จาก Devtino)",
                    "lunar.py: shift logic ปีอธิกมาส — base 5,6,7 → 6,7,8 / base 8 → 8 หลัง (intercalary flag)",
                    "lunar.py: เพิ่ม is_intercalary_month field ใน LunarDate dataclass",
                    "calendar_data: find_holy_day() ใช้กฎ adhikamasa — reverse shift ก่อน lookup",
                    "calendar_convert: lunar_to_solar() รับ is_intercalary_month + error message ฉลาดขึ้น (\"ปีอาจไม่ใช่ปีอธิกมาส\")",
                    "calendar_convert: รองรับ พ.ศ. 544-1180 (auto-route ไปยัง Meeus)",
                    "Timeline dot alignment: -4% → -100%×4/46 (% offset ของ item width ไม่ใช่ container)",
                    "Description ของ จอมพล ป. — เปลี่ยน \"ทรงนำเอา\" → \"ประกาศให้ใช้\" (ราชาศัพท์ผิด ใช้เฉพาะเชื้อพระวงศ์)",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "calendar_data.py: hardcoded lists → query functions (lazy load wrapper เผื่อ caller เก่า)",
                    "requirements.txt: + sqlalchemy>=2.0, alembic>=1.13, psycopg2-binary>=2.9",
                    ".gitignore: + local.db, .env, *.sqlite",
                ],
            },
        ],
    },
    {
        "version": "2026.06.02-a",
        "date": "2026-06-02",
        "title": "เมนูใหม่ \"เทียบปฏิทิน\" + Timeline ประวัติศาสตร์",
        "highlights": [
            "เมนูใหม่: เทียบปฏิทิน — จันทรคติ ⇄ สุริยคติ (2-way conversion)",
            "Timeline ประวัติศาสตร์ปฏิทินไทย 8 ยุค พร้อมภาพประวัติศาสตร์",
            "ภาพพระมหากษัตริย์ + จอมพล ป. (Public Domain จาก Wikimedia Commons)",
            "Theme background ตามยุค (cosmos/lotus/mandala/temple/gear)",
            "วันสำคัญทางพุทธศาสนา 6 วัน + Holy day detection",
        ],
        "details": [
            {
                "category": "เพิ่ม",
                "items": [
                    "หน้า /calendar — Tab 1: สุริยคติ→จันทรคติ + Tab 2: จันทรคติ→สุริยคติ",
                    "thai_astro/calendar_convert.py — solar_to_lunar() + lunar_to_solar() (search-based 2-year window)",
                    "webapp/calendar_data.py — 8 epochs + 6 buddhist holy days (hardcoded; Phase 2 จะย้าย DB)",
                    "Timeline 2-column alternating (odd ซ้าย, even ขวา) + เส้นกลางแนวตั้ง gradient",
                    "Dot connectors + SVG decorative patterns ตามยุค (cosmos/lotus/mandala/crown/gear)",
                    "ภาพประวัติศาสตร์ 4 ภาพ (PD): ร.1 (1782), ร.5 (1889), ร.6 (1912), จอมพล ป. (1941)",
                    "Photo frame ทอง 100×130px + caption + license credit + ornament corners",
                    "Holy day detection: แสดง 🪷 badge เมื่อตรงวันสำคัญ (วิสาขบูชา, มาฆบูชา, ลอยกระทง ฯลฯ)",
                    "วันพระ marker (ขึ้น/แรม 8, 15 ค่ำ)",
                ],
            },
            {
                "category": "ปรับ",
                "items": [
                    "Nav link เพิ่ม \"เทียบปฏิทิน\" ในทุก template (index/horathaynu/about)",
                    "Cache version → v=20260601j",
                ],
            },
        ],
    },
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
