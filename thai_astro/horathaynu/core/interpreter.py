"""ประกอบ chart + relations + templates → ข้อความคำพยากรณ์"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from thai_astro.horathaynu.core.caster import Chart
from thai_astro.horathaynu.core.relations import RelationChain, chain_for
from thai_astro.horathaynu.core.time_to_yam import yam_range
from thai_astro.horathaynu.data import templates as T
from thai_astro.horathaynu.data.houses import (
    QUESTION_TO_HOUSE,
    house_name,
    house_themes,
)
from thai_astro.horathaynu.data.planet_meanings import planet_name


@dataclass
class Prediction:
    focus: str
    rule: str
    text: str


def _themes_str(themes: list[str]) -> str:
    return "/".join(themes)


def _focus_for_planet_in_house(chart: Chart, house: int) -> str:
    """เลือก planet ที่อยู่ใน house เป็น focus
    (ถ้าไม่มีดาวในห้องนั้น → fallback ไปเจ้าเรือนของห้องนั้น)
    """
    occupants = chart.planets_in_house(house)
    if occupants:
        # priority: lagna > sun > moon > อื่นๆ ตาม PLANET_KEYS
        for preferred in ("lagna", "sun", "moon"):
            if preferred in occupants:
                return preferred
        return occupants[0]
    # fallback: ใช้ดาวเกษตรของราศีในห้องนั้น (ถ้ามีใน chart)
    from thai_astro.horathaynu.core.caster import house_to_sign
    from thai_astro.horathaynu.data.lordship import lord_of
    sign = house_to_sign(house, chart.ascendant_sign)
    lord = lord_of(sign)
    if lord in chart.placements:
        return lord
    return "lagna"


def _render_chain(chain: RelationChain) -> list[Prediction]:
    results: list[Prediction] = []

    step1 = chain.step1
    results.append(Prediction(
        focus=chain.focus,
        rule="house_relation_1",
        text=T.LORD_IN_HOUSE.format(
            focus_name=planet_name(chain.focus),
            focus_house_name=house_name(chain.focus_house),
            lord_name=planet_name(step1.lord),
            lord_house=step1.lord_house,
            lord_house_name=house_name(step1.lord_house),
            lord_house_themes=_themes_str(house_themes(step1.lord_house)),
        ),
    ))

    if chain.step2 is not None:
        step2 = chain.step2
        results.append(Prediction(
            focus=chain.focus,
            rule="house_relation_2",
            text=T.CHAIN_SECOND.format(
                lord_name=planet_name(step1.lord),
                second_lord_name=planet_name(step2.lord),
                second_house=step2.lord_house,
                second_house_name=house_name(step2.lord_house),
                second_house_themes=_themes_str(house_themes(step2.lord_house)),
            ),
        ))

    return results


def interpret(chart: Chart, question: str | None = None,
              focus_override: str | None = None) -> dict:
    """ประกอบผลพยากรณ์จาก chart

    Args:
        chart: ผลจาก caster.cast()
        question: คำถาม/keyword (เช่น "love", "money") → mapping เป็น focus_house
        focus_override: บังคับ focus เป็น planet_key ที่ต้องการ
    """
    # เลือก focus
    if focus_override is not None:
        focus = focus_override
    elif question and question.lower() in QUESTION_TO_HOUSE:
        focus_house = QUESTION_TO_HOUSE[question.lower()]
        focus = _focus_for_planet_in_house(chart, focus_house)
    else:
        focus = "lagna"

    chain = chain_for(chart, focus)
    predictions = _render_chain(chain)

    start, end = yam_range(chart.yam_index)
    opening = T.OPENING.format(
        day_name=T.WEEKDAY_NAMES_TH[chart.day],
        yam_index=chart.yam_index,
        yam_time_range=f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}",
    )

    return {
        "input": {
            "day": chart.day,
            "yam_index": chart.yam_index,
            "question": question,
        },
        "chart": {
            "ascendant_sign": chart.ascendant_sign,
            "placements": {
                k: {"sign": p.sign, "house": p.house}
                for k, p in chart.placements.items()
            },
        },
        "focus": focus,
        "opening": opening,
        "predictions": [asdict(p) for p in predictions],
        "closing": T.CLOSING,
    }
