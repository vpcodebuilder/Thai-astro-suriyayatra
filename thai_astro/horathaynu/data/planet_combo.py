"""Planet combo — คู่ดาวที่อยู่ราศีเดียวกันแล้วมีนัยพิเศษ

หลักการ:
    เมื่อดาว significator มี "ดาวครองร่วม" (อยู่ราศีเดียวกัน)
    บางคู่จะให้ความหมายพิเศษที่ไม่ใช่แค่ผลรวมของดาวเดี่ยว
    เช่น ศุกร์ (รัก) + เสาร์ (ความช้า/อายุ) = "รักคนสูงวัย / รักนาน"
        ศุกร์ + ราหู = "รักผิดศีล / รักลับ / ของแปลก"

ใช้ในชั้น 3 ของการพยากรณ์ — มาเสริม planet × bhava ของ significator
เพื่อบอกว่า "ดาว A + ดาว B ในเรื่องนี้หมายถึงอะไร"

ลำดับคู่ในตารางไม่สำคัญ — lookup ใช้ frozenset
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanetCombo:
    """คู่ดาวพิเศษ."""

    planets: frozenset[str]    # 2 keys ของดาว
    label: str                 # ป้ายสั้น 1 บรรทัด
    text: str                  # คำตีความ
    tone: str                  # good / warning / neutral
    contexts: tuple[str, ...]  # category ที่คู่นี้สำคัญที่สุด (เช่น love, wealth)


def _c(a: str, b: str) -> frozenset[str]:
    return frozenset({a, b})


# ===========================================================================
# 22 คู่ดาวพิเศษ — เลือกจากคู่ที่ตำราโหรไทยกล่าวบ่อย
# ===========================================================================
_COMBOS: tuple[PlanetCombo, ...] = (

    # ---------- คู่ดาวเกี่ยวกับความรัก ----------
    PlanetCombo(
        planets=_c("venus", "saturn"),
        label="ศุกร์ + เสาร์ — รักหนัก/รักคนสูงวัย",
        text=("ศุกร์คู่กับเสาร์: ความรักหนักแน่นแต่ติดขัด คู่อายุห่างกัน "
              "หรือมีปัญหาที่ต้องอดทน เป็นรักที่ใช้เวลาบ่มเพาะ"),
        tone="warning",
        contexts=("love", "marriage", "breakup"),
    ),
    PlanetCombo(
        planets=_c("venus", "rahu"),
        label="ศุกร์ + ราหู — รักผิดศีล/รักลับ",
        text=("ศุกร์คู่กับราหู: ความรักลึกลับ ผิดประเพณี หรือคู่ที่ไม่เปิดเผย "
              "อาจมีของแปลก/ของลึกลับเข้ามาเกี่ยวข้อง ระวังความหลง"),
        tone="warning",
        contexts=("love", "marriage", "lost_item"),
    ),
    PlanetCombo(
        planets=_c("venus", "moon"),
        label="ศุกร์ + จันทร์ — รักหวานชื่น",
        text=("ศุกร์คู่กับจันทร์: ความรักเปี่ยมอารมณ์ คู่อ่อนโยน "
              "เกื้อกูลทางใจ ดวงเสน่ห์ที่ดึงดูดผู้คน"),
        tone="good",
        contexts=("love", "marriage"),
    ),
    PlanetCombo(
        planets=_c("venus", "jupiter"),
        label="ศุกร์ + พฤหัส — รักมีบุญ",
        text=("ศุกร์คู่กับพฤหัสบดี: ความรักนำพาความรุ่งเรือง คู่ที่ยกระดับให้กัน "
              "แต่งงานเป็นมงคล มีลาภและบุตรหนุน"),
        tone="good",
        contexts=("love", "marriage", "child"),
    ),
    PlanetCombo(
        planets=_c("venus", "mars"),
        label="ศุกร์ + อังคาร — รักร้อนแรง",
        text=("ศุกร์คู่กับอังคาร: ความรักหุนหัน เร่าร้อน อาจปะทะกันบ่อย "
              "เสน่ห์ทางกาย แต่ระวังทะเลาะรุนแรง"),
        tone="neutral",
        contexts=("love", "marriage", "breakup"),
    ),

    # ---------- คู่ดาวเกี่ยวกับงาน/อำนาจ ----------
    PlanetCombo(
        planets=_c("sun", "saturn"),
        label="อาทิตย์ + เสาร์ — อำนาจกับภาระ",
        text=("อาทิตย์คู่กับเสาร์: ตำแหน่งสูงแต่ภาระหนัก ผู้ใหญ่ที่เข้มงวด "
              "หรืออาจกระทบกับเจ้านายอาวุโส ระวังขัดผู้ที่อาวุโสกว่า"),
        tone="warning",
        contexts=("career", "resign", "parent"),
    ),
    PlanetCombo(
        planets=_c("sun", "mars"),
        label="อาทิตย์ + อังคาร — อำนาจที่ดุดัน",
        text=("อาทิตย์คู่กับอังคาร: เด็ดขาด กล้าได้กล้าเสีย "
              "ดีในเรื่องคดี/แข่งขัน แต่ระวังคำขัดแย้งกับเจ้านาย"),
        tone="neutral",
        contexts=("career", "lawsuit", "enemy"),
    ),
    PlanetCombo(
        planets=_c("sun", "jupiter"),
        label="อาทิตย์ + พฤหัส — เกียรติยศบุญหนุน",
        text=("อาทิตย์คู่กับพฤหัสบดี: ตำแหน่งและเกียรติยศมาด้วยบุญ "
              "ผู้ใหญ่และครูเปิดทาง ขึ้นสูงได้แน่นอน"),
        tone="good",
        contexts=("career", "job_search", "luck_windfall"),
    ),
    PlanetCombo(
        planets=_c("sun", "rahu"),
        label="อาทิตย์ + ราหู — อำนาจคลุมเครือ",
        text=("อาทิตย์คู่กับราหู: อำนาจถูกบดบัง หรือเรื่องที่ดูดี "
              "มีเงาแฝง ระวังการเสียตำแหน่งจากเรื่องลึกลับ"),
        tone="warning",
        contexts=("career", "resign"),
    ),

    # ---------- คู่ดาวเกี่ยวกับทรัพย์ ----------
    PlanetCombo(
        planets=_c("jupiter", "mercury"),
        label="พฤหัส + พุธ — ลาภจากความรู้",
        text=("พฤหัสบดีคู่กับพุธ: ลาภและรายได้จากความรู้ การพูด การค้า "
              "เหมาะกับงานที่ใช้สมองและการเจรจา"),
        tone="good",
        contexts=("wealth", "business", "study"),
    ),
    PlanetCombo(
        planets=_c("jupiter", "venus"),
        label="พฤหัส + ศุกร์ — ลาภและความสุข",
        text=("พฤหัสบดีคู่กับศุกร์: ลาภและความสุขมาด้วยกัน "
              "การเงินดี ความรักสมหวัง บุญใหญ่ทั้งสองทาง"),
        tone="good",
        contexts=("wealth", "luck_windfall", "love"),
    ),
    PlanetCombo(
        planets=_c("jupiter", "rahu"),
        label="พฤหัส + ราหู — ลาภลอย/โชคคาดไม่ถึง",
        text=("พฤหัสบดีคู่กับราหู: ลาภลอย โชคไม่คาดฝัน "
              "แต่ระวังว่าลาภนั้นอาจมีเรื่องไม่โปร่งใส"),
        tone="neutral",
        contexts=("luck_windfall", "wealth"),
    ),
    PlanetCombo(
        planets=_c("jupiter", "saturn"),
        label="พฤหัส + เสาร์ — ลาภช้าแต่ใหญ่",
        text=("พฤหัสบดีคู่กับเสาร์: ลาภมาช้าแต่มั่นคงและยาวนาน "
              "การสะสมระยะยาวจะเห็นผล ลาภหลังวัยกลางคน"),
        tone="good",
        contexts=("wealth", "property_home", "career"),
    ),

    # ---------- คู่ดาวอันตราย/ปะทะ ----------
    PlanetCombo(
        planets=_c("mars", "saturn"),
        label="อังคาร + เสาร์ — ปะทะแบบยาว",
        text=("อังคารคู่กับเสาร์: การปะทะที่ยืดเยื้อ "
              "คดียาวนาน ศัตรูเก่าแก่ ระวังอุบัติเหตุที่มาจากเรื่องค้างเก่า"),
        tone="warning",
        contexts=("lawsuit", "enemy", "health"),
    ),
    PlanetCombo(
        planets=_c("mars", "rahu"),
        label="อังคาร + ราหู — รุนแรงไม่คาดคิด",
        text=("อังคารคู่กับราหู: ความรุนแรงที่มาแบบไม่คาดคิด "
              "อุบัติเหตุ ของเก่าระเบิด ระวังการตัดสินใจรีบร้อน"),
        tone="warning",
        contexts=("lawsuit", "enemy", "health", "travel_far"),
    ),
    PlanetCombo(
        planets=_c("saturn", "rahu"),
        label="เสาร์ + ราหู — ทุกข์ลึก/เรื่องลับยาว",
        text=("เสาร์คู่กับราหู: เรื่องลึกลับที่กดทับยาวนาน "
              "หนี้เก่า ภาระจากอดีต ระวังเรื่องสุขภาพจิต"),
        tone="warning",
        contexts=("debt", "health", "enemy"),
    ),
    PlanetCombo(
        planets=_c("mars", "ketu"),
        label="อังคาร + เกตุ — ตัดขาด/พลัดพราก",
        text=("อังคารคู่กับเกตุ: การตัดขาดอย่างเด็ดขาด "
              "การแยกทาง อุบัติเหตุที่ทำให้ต้องห่าง"),
        tone="warning",
        contexts=("breakup", "resign", "lawsuit"),
    ),

    # ---------- คู่ดาวเกี่ยวกับการสื่อสาร/การเดินทาง ----------
    PlanetCombo(
        planets=_c("mercury", "moon"),
        label="พุธ + จันทร์ — สื่อสารอ่อนโยน",
        text=("พุธคู่กับจันทร์: การสื่อสารด้วยอารมณ์ดี "
              "เหมาะกับงานบริการ การพูดเข้าใจคนอื่น"),
        tone="good",
        contexts=("travel_near", "business", "sibling_friend"),
    ),
    PlanetCombo(
        planets=_c("mercury", "mars"),
        label="พุธ + อังคาร — พูดเด็ด ขาดเฉียบ",
        text=("พุธคู่กับอังคาร: คำพูดเด็ดขาดและคม "
              "ดีในการเจรจาเข้มข้น แต่ระวังพูดทำร้ายคน"),
        tone="neutral",
        contexts=("business", "lawsuit", "sibling_friend"),
    ),
    PlanetCombo(
        planets=_c("mercury", "rahu"),
        label="พุธ + ราหู — คำพูดลึกลับ/หลอกลวง",
        text=("พุธคู่กับราหู: คำพูดมีเงาแฝง การหลอกลวง "
              "เอกสารคลุมเครือ ระวังถูกหลอกหรือเซ็นโดยไม่อ่าน"),
        tone="warning",
        contexts=("business", "lawsuit", "debt"),
    ),

    # ---------- คู่ดาวเกี่ยวกับครอบครัว/บุญเก่า ----------
    PlanetCombo(
        planets=_c("moon", "jupiter"),
        label="จันทร์ + พฤหัส — มารดากับบุญ",
        text=("จันทร์คู่กับพฤหัสบดี: มารดามีบุญหนุน "
              "ความเอื้ออาทร ความช่วยเหลือจากผู้หญิงที่มีปัญญา"),
        tone="good",
        contexts=("parent", "child", "luck_windfall"),
    ),
    PlanetCombo(
        planets=_c("moon", "saturn"),
        label="จันทร์ + เสาร์ — อารมณ์หนัก",
        text=("จันทร์คู่กับเสาร์: อารมณ์หนัก หม่นหมอง "
              "มารดาหรือคนใกล้ตัวมีภาระ ระวังโรคซึมเศร้า"),
        tone="warning",
        contexts=("health", "parent", "breakup"),
    ),

    # ---------- พิเศษ — ลัคนากับดาว ----------
    PlanetCombo(
        planets=_c("lagna", "rahu"),
        label="ลัคนา + ราหู — ตัวเองอยู่ในเงา",
        text=("ลัคนาคู่กับราหู: ตัวเจ้าชะตาอยู่ในเรื่องลึกลับ "
              "ระวังการตัดสินใจที่ไม่ชัดเจน หลงไปทางที่ไม่ควร"),
        tone="warning",
        contexts=("current_event", "lost_person"),
    ),
    PlanetCombo(
        planets=_c("lagna", "jupiter"),
        label="ลัคนา + พฤหัส — ตัวเองได้บุญ",
        text=("ลัคนาคู่กับพฤหัสบดี: ตัวเจ้าชะตามีบุญหนุน "
              "เป็นที่นับถือ มีโอกาสในทุกเรื่อง"),
        tone="good",
        contexts=("current_event", "career", "luck_windfall"),
    ),

    # ---------- คู่กับ "เกตุ" — มักพบใน Horathaynu chart ----------
    PlanetCombo(
        planets=_c("venus", "ketu"),
        label="ศุกร์ + เกตุ — รักที่เกือบหลุดมือ",
        text=("ศุกร์คู่กับเกตุ: ความรักหรือของรักที่เคยใกล้แต่กำลังห่าง "
              "หรือมีอดีตคนรักเก่าเข้ามาเกี่ยวข้อง"),
        tone="neutral",
        contexts=("love", "marriage", "lost_item", "breakup"),
    ),
    PlanetCombo(
        planets=_c("sun", "ketu"),
        label="อาทิตย์ + เกตุ — อำนาจที่ถอย",
        text=("อาทิตย์คู่กับเกตุ: ตำแหน่ง/อำนาจกำลังลดลง "
              "หรือผู้ใหญ่ในชีวิตเริ่มถอนตัว"),
        tone="neutral",
        contexts=("career", "resign", "parent"),
    ),
    PlanetCombo(
        planets=_c("jupiter", "ketu"),
        label="พฤหัส + เกตุ — บุญเก่าที่ปลด",
        text=("พฤหัสบดีคู่กับเกตุ: บุญเก่ากำลังหมดไปหรือเปลี่ยนรูป "
              "เหมาะกับการปล่อยวาง การทำบุญแบบไม่หวังผล"),
        tone="neutral",
        contexts=("luck_windfall", "wealth", "study"),
    ),
    PlanetCombo(
        planets=_c("mercury", "ketu"),
        label="พุธ + เกตุ — สื่อสารคลุมเครือ",
        text=("พุธคู่กับเกตุ: คำพูดที่ไม่ชัด ความเข้าใจผิดในการสื่อสาร "
              "ระวังคนกลางที่บิดข้อความ"),
        tone="warning",
        contexts=("business", "sibling_friend", "travel_near"),
    ),

    # ---------- คู่กับ "มฤตยู" — ความเปลี่ยนแปลงฉับพลัน ----------
    PlanetCombo(
        planets=_c("venus", "uranus"),
        label="ศุกร์ + มฤตยู — รักแบบฉับพลัน",
        text=("ศุกร์คู่กับมฤตยู: ความรักหรือของรักมีการเปลี่ยนแปลงฉับพลัน "
              "ตกหลุมรักเร็ว เลิกเร็ว หรือเจอของในที่คาดไม่ถึง"),
        tone="neutral",
        contexts=("love", "marriage", "lost_item", "breakup"),
    ),
    PlanetCombo(
        planets=_c("sun", "uranus"),
        label="อาทิตย์ + มฤตยู — เปลี่ยนตำแหน่งฉับพลัน",
        text=("อาทิตย์คู่กับมฤตยู: ตำแหน่ง/ผู้ใหญ่เปลี่ยนแปลงไม่ทันตั้งตัว "
              "การโยกย้ายฉับพลัน"),
        tone="warning",
        contexts=("career", "resign"),
    ),
    PlanetCombo(
        planets=_c("mercury", "uranus"),
        label="พุธ + มฤตยู — ข่าวสารฉับพลัน",
        text=("พุธคู่กับมฤตยู: ข่าวด่วน เทคโนโลยี การเปลี่ยนแปลงทางการสื่อสาร "
              "เด็ก/เพื่อนที่ใช้เทคโนโลยี"),
        tone="neutral",
        contexts=("business", "travel_near", "study"),
    ),

    # ---------- คู่กับ "พุธ" — มักพบ ----------
    PlanetCombo(
        planets=_c("venus", "mercury"),
        label="ศุกร์ + พุธ — รักผ่านคำพูด",
        text=("ศุกร์คู่กับพุธ: ความรักเริ่มจากการสื่อสาร/เพื่อน "
              "คู่อายุน้อยกว่า เด็กฉลาด เสน่ห์ทางคำพูด"),
        tone="good",
        contexts=("love", "marriage", "study"),
    ),
    PlanetCombo(
        planets=_c("sun", "mercury"),
        label="อาทิตย์ + พุธ — ผู้ใหญ่ที่สื่อสาร",
        text=("อาทิตย์คู่กับพุธ: ผู้ใหญ่ที่พูดเก่ง ตำแหน่งทางสื่อสาร "
              "หรือเจ้านายฉลาดเฉลียว"),
        tone="good",
        contexts=("career", "job_search", "study"),
    ),
    PlanetCombo(
        planets=_c("moon", "mercury"),
        label="จันทร์ + พุธ — อารมณ์เด็ก",
        text=("จันทร์คู่กับพุธ: อารมณ์อ่อนไหวเหมือนเด็ก "
              "หรือมีเด็ก/ผู้หญิงเด็กในเรื่อง"),
        tone="neutral",
        contexts=("parent", "child", "sibling_friend"),
    ),
    PlanetCombo(
        planets=_c("mars", "mercury"),
        label="อังคาร + พุธ — พูดเฉือนเก่ง",
        text=("อังคารคู่กับพุธ: การโต้เถียงเก่ง การวิเคราะห์เฉียบ "
              "ดีในงานวิจัย/วิเคราะห์ แต่ระวังคำเฉือนคน"),
        tone="neutral",
        contexts=("lawsuit", "study", "business"),
    ),
)


# ===========================================================================
# Index for fast lookup
# ===========================================================================
_INDEX: dict[frozenset[str], PlanetCombo] = {c.planets: c for c in _COMBOS}


def get_combo(planet_a: str, planet_b: str) -> PlanetCombo | None:
    """ค้นหาคู่ดาวพิเศษ. คืน None ถ้าไม่ใช่คู่พิเศษ.

    Order ไม่สำคัญ: get_combo("venus", "saturn") == get_combo("saturn", "venus")
    """
    if planet_a == planet_b:
        return None
    return _INDEX.get(frozenset({planet_a, planet_b}))


def find_combos(planets: list[str], category: str | None = None) -> list[PlanetCombo]:
    """หา combo ทั้งหมดในกลุ่มดาวที่อยู่ร่วมกัน.

    ถ้าระบุ category → คืนเฉพาะ combo ที่ category อยู่ใน contexts
    (เพื่อให้คำทำนายเข้ากับเรื่องที่ถาม)
    """
    found: list[PlanetCombo] = []
    seen: set[frozenset[str]] = set()
    n = len(planets)
    for i in range(n):
        for j in range(i + 1, n):
            key = frozenset({planets[i], planets[j]})
            if key in seen:
                continue
            seen.add(key)
            combo = _INDEX.get(key)
            if combo is None:
                continue
            if category is not None and category not in combo.contexts:
                continue
            found.append(combo)
    return found


__all__ = ["PlanetCombo", "get_combo", "find_combos"]
