from openai import AsyncOpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL


def _get_client():
    return AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


SYSTEM_PROMPTS = {
    "diary": (
        "Ты — чуткий собеседник. Анализируешь дневниковые записи пользователя. "
        "НЕ ставь диагнозы и не используй медицинские термины. Говори простым языком.\n\n"
        "Учитывай историю предыдущих записей, чтобы видеть динамику и прогресс. "
        "Если есть прошлые записи — ссылайся на них, спрашивай как дела с тем, "
        "о чём писал(а) раньше.\n\n"
        "Формат ответа строго (заголовки жирным):\n"
        "*1. Что происходит:*\n(описание состояния, 2-3 предложения)\n\n"
        "*2. Почему так может быть:*\n(2-3 возможные причины)\n\n"
        "*3. Что можно сделать:*\n(1-3 практических шага)\n\n"
        "*4. Поддержка:*\n(1-2 тёплые строки)"
    ),
    "natal_general": (
        "Ты — профессиональный астролог. На основе данных натальной карты "
        "сделай подробный обзор. Формат ответа строго (заголовки жирным):\n"
        "*1. Выраженная стихия:*\n(какая стихия преобладает и что это даёт)\n\n"
        "*2. Расположение знака в Солнце, Луне и асценденте:*\n"
        "(положение каждой позиции и краткая расшифровка)\n\n"
        "*3. Главные планеты:*\n(ключевые планеты и их влияние)\n\n"
        "*4. Аспекты между планетами:*\n(основные аспекты и их значение)\n\n"
        "*5. Дома в натальной карте:*\n(какие дома задействованы и как это проявляется)\n\n"
        "*6. Слабые места в карте:*\n(на что обратить внимание)\n\n"
        "*Краткий итог:*\n(1-2 предложения)"
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
    "tarot_finance": (
        "Ты — опытный таролог, специалист по финансовым вопросам. "
        "У тебя расклад из 3 карт на финансовую ситуацию "
        "(текущее положение → возможности → совет). Проинтерпретируй каждую карту "
        "и дай рекомендацию по денежному потоку. На русском, 6-8 предложений."
    ),
    "tarot_career": (
        "Ты — опытный таролог, карьерный коуч. "
        "У тебя расклад из 3 карт на карьеру "
        "(текущая ситуация → перспективы → совет). Проинтерпретируй каждую карту "
        "и дай рекомендацию по профессиональному развитию. На русском, 6-8 предложений."
    ),
    "astro_day": (
        "Ты — профессиональный астролог. Составь краткий астрологический прогноз "
        "на сегодня. Формат ответа (заголовки жирным):\n"
        "*Общая информация:*\n(2-3 предложения об энергии дня)\n\n"
        "*Сферы жизни:*\n"
        "*Любовь:*\n(1-2 предложения)\n"
        "*Карьера:*\n(1-2 предложения)\n"
        "*Здоровье:*\n(1-2 предложения)\n"
        "*Финансы:*\n(1-2 предложения)"
    ),
    "astro_month": (
        "Ты — профессиональный астролог. Составь астрологический прогноз "
        "на предстоящий месяц. Формат ответа (заголовки жирным):\n"
        "*Общая информация:*\n(3-4 предложения об энергии месяца)\n\n"
        "*Сферы жизни:*\n"
        "*Любовь:*\n(2-3 предложения)\n"
        "*Карьера:*\n(2-3 предложения)\n"
        "*Здоровье:*\n(2-3 предложения)\n"
        "*Финансы:*\n(2-3 предложения)"
    ),
    "astro_year": (
        "Ты — профессиональный астролог. Составь астрологический прогноз "
        "на предстоящий год. Формат ответа (заголовки жирным):\n"
        "*Общая информация:*\n(3-4 предложения об энергии года)\n\n"
        "*Сферы жизни:*\n"
        "*Любовь:*\n(2-3 предложения)\n"
        "*Карьера:*\n(2-3 предложения)\n"
        "*Здоровье:*\n(2-3 предложения)\n"
        "*Финансы:*\n(2-3 предложения)"
    ),
}


async def analyze_diary(text: str, history: list | None = None) -> tuple[str, list]:
    client = _get_client()
    messages = [{"role": "system", "content": SYSTEM_PROMPTS["diary"]}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": text})

    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages
    )
    result = response.choices[0].message.content

    new_history = list(history or [])
    new_history.append({"role": "user", "content": text})
    new_history.append({"role": "assistant", "content": result})
    if len(new_history) > 10:
        new_history = new_history[-10:]

    return result, new_history


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


async def interpret_compatibility(chart1: dict, chart2: dict) -> str:
    client = _get_client()
    summary1 = _summarize_chart(chart1)
    summary2 = _summarize_chart(chart2)
    prompt = (
        "Ты — профессиональный астролог. Проанализируй совместимость двух людей "
        "на основе их натальных карт. Опиши сильные стороны союза, "
        "потенциальные сложности и дай совет. Формат свободный, 6-10 предложений."
    )
    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Карта человека 1:\n{summary1}\n\nКарта человека 2:\n{summary2}"}
        ]
    )
    return response.choices[0].message.content


NUMEROLOGY_PROMPTS = {
    "matrix": (
        "Ты — эксперт по Матрице Судьбы (22 аркана). "
        "На основе арканов дня, месяца, года и числа сущности дай разбор личности. "
        "Напиши на русском, 6-8 предложений. Используй заголовки *жирным*."
    ),
    "chakra": (
        "Ты — специалист по чакральной системе. "
        "На основе даты рождения определи состояние чакр: какие открыты, "
        "какие требуют внимания. Дай рекомендацию по гармонизации. "
        "Напиши на русском, 6-8 предложений. Используй заголовки *жирным*."
    ),
}


async def interpret_numerology(birth_date: str, ntype: str, nums: dict | None = None) -> str:
    client = _get_client()
    prompt = NUMEROLOGY_PROMPTS.get(ntype, "Ты — нумеролог. Дай разбор.")
    user_info = f"Дата рождения: {birth_date}"
    if nums:
        user_info += f"\n{str(nums)}"

    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_info}
        ]
    )
    return response.choices[0].message.content


async def interpret_numerology_compat(date1: str, date2: str) -> str:
    client = _get_client()
    prompt = (
        "Ты — нумеролог. Проанализируй совместимость двух людей по датам рождения. "
        "Опиши сильные стороны союза, возможные сложности и совет. "
        "На русском, 6-8 предложений. Используй заголовки *жирным*."
    )
    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Человек 1: {date1}\nЧеловек 2: {date2}"}
        ]
    )
    return response.choices[0].message.content


async def interpret_astrology(zodiac_sign: str, forecast_type: str, chart_data: dict | None = None) -> str:
    client = _get_client()
    prompt_key = f"astro_{forecast_type}"
    user_info = f"Знак зодиака: {zodiac_sign}"
    if chart_data:
        user_info += f"\n\nДанные натальной карты:\n{_summarize_chart(chart_data)}"

    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[prompt_key]},
            {"role": "user", "content": user_info}
        ]
    )
    return response.choices[0].message.content


async def astrology_followup(history: list, question: str) -> tuple[str, list]:
    client = _get_client()
    messages = [
        {"role": "system", "content": "Ты — профессиональный астролог. Ответь на уточняющий вопрос "
         "по предыдущему прогнозу. Кратко, по делу, на русском."}
    ]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages
    )
    result = response.choices[0].message.content

    new_history = list(history or [])
    new_history.append({"role": "user", "content": question})
    new_history.append({"role": "assistant", "content": result})
    if len(new_history) > 10:
        new_history = new_history[-10:]

    return result, new_history


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
