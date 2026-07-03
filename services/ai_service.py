from openai import AsyncOpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL


def _get_client():
    return AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


SYSTEM_PROMPTS = {
    "diary": (
        "Ты — эмпатичный психолог и коуч. Проанализируй дневниковую запись пользователя. "
        "Выдели ключевые эмоции, подсознательные паттерны и скрытые ресурсы. "
        "Дай поддерживающий отклик и задай 1 вопрос для рефлексии. "
        "На русском, 4-5 предложений."
    ),
    "natal_general": (
        "Ты — профессиональный астролог с 20-летним опытом. "
        "На основе данных натальной карты дай общий разбор личности: "
        "положение Солнца (сознание), Луны (эмоции), ASC (самовыражение), "
        "ключевые аспекты и их влияние на характер. Напиши на русском, 6-8 предложений."
    ),
    "natal_day": (
        "Ты — профессиональный астролог. Сделай прогноз на день на основе "
        "натальной карты. Учти текущее положение транзитных планет. "
        "Напиши, какие сферы жизни будут активны сегодня, что стоит предпринять, "
        "а чего избегать. На русском, 4-5 предложений."
    ),
    "natal_year": (
        "Ты — профессиональный астролог. Составь годовой прогноз на основе "
        "натальной карты. Опиши ключевые тенденции года: карьера, отношения, "
        "финансы, личностный рост. Укажи благоприятные и сложные периоды. "
        "На русском, 6-8 предложений."
    ),
    "tarot_daily": (
        "Ты — опытный таролог. Проинтерпретируй выпавшую карту Таро как "
        "предсказание на день. Опиши энергию дня, совет и предостережение. "
        "На русском, 4-5 предложений."
    ),
    "tarot_three": (
        "Ты — опытный таролог. У тебя расклад из 3 карт на ситуацию "
        "(прошлое → настоящее → будущее). Проинтерпретируй каждую карту "
        "и свяжи их в целостную историю. Дай совет. На русском, 6-8 предложений."
    ),
    "tarot_relationship": (
        "Ты — опытный таролог, специалист по отношениям. "
        "У тебя расклад на отношения из карт, описывающих "
        "партнёра, отношения и совет. Проинтерпретируй каждую карту "
        "и дай рекомендацию. На русском, 6-8 предложений."
    ),
}


async def analyze_diary(text: str) -> str:
    client = _get_client()
    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS["diary"]},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content


async def interpret_natal(chart_data: dict, forecast_type: str) -> str:
    client = _get_client()
    prompt_key = f"natal_{forecast_type}"
    chart_summary = _summarize_chart(chart_data)

    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[prompt_key]},
            {"role": "user", "content": f"Данные натальной карты: {chart_summary}"}
        ]
    )
    return response.choices[0].message.content


async def interpret_tarot(cards: list, spread_type: str) -> str:
    client = _get_client()
    prompt_key = f"tarot_{spread_type}"
    cards_desc = "\n".join(
        f"{i+1}. {c['name']} ({'перевёрнута' if c['reversed'] else 'прямое положение'}) — {c['meaning']}"
        for i, c in enumerate(cards)
    )

    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[prompt_key]},
            {"role": "user", "content": f"Выпавшие карты:\n{cards_desc}"}
        ]
    )
    return response.choices[0].message.content


def _summarize_chart(chart: dict) -> str:
    lines = [
        f"ASC: {chart.get('ascendant', '—')}",
        "Планеты в знаках:"
    ]
    for planet, data in chart.get("planets", {}).items():
        lines.append(f"  {planet}: {data['sign']} {data['degree']}°")
    if chart.get("aspects"):
        lines.append("Аспекты:")
        for asp in chart["aspects"]:
            lines.append(f"  {asp}")
    return "\n".join(lines)
