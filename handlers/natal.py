import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.ai_service import interpret_natal, interpret_compatibility
from services.astrology import calculate_chart
from handlers.start import MAIN_KEYBOARD

BIRTH_DATE, BIRTH_TIME, BIRTH_PLACE = range(1, 4)
COMPAT_DATE, COMPAT_TIME, COMPAT_PLACE = range(4, 7)

NATAL_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['🔮 Прогноз на день', '📅 Прогноз на год'],
        ['📖 Общий разбор', '💞 Совместимость'],
        ['📋 Главное меню']
    ],
    resize_keyboard=True
)

CHOICE_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['👤 Моя карта'],
        ['👥 Карта другого человека'],
        ['📋 Главное меню']
    ],
    resize_keyboard=True
)

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отмена']],
    resize_keyboard=True
)

DATE_RE = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
TIME_RE = re.compile(r'^\d{2}:\d{2}$')


def _get_natal_keyboard():
    return NATAL_KEYBOARD


async def natal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('chart_data'):
        await update.message.reply_text(
            '🔮 У тебя уже есть рассчитанная карта.\n'
            'Хочешь посмотреть её или рассчитать для другого человека?',
            reply_markup=CHOICE_KEYBOARD
        )
        return BIRTH_DATE
    await update.message.reply_text(
        '🔮 Для расчёта натальной карты мне нужны твои данные.\n\n'
        'Введи дату рождения в формате *ДД.ММ.ГГГГ* (например, 15.06.1995):',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return BIRTH_DATE


async def birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if context.user_data.get('chart_data'):
        if text == '👤 Моя карта':
            await update.message.reply_text(
                '✅ Использую твою карту. Выбери прогноз:',
                reply_markup=NATAL_KEYBOARD
            )
            return ConversationHandler.END
        elif text == '👥 Карта другого человека':
            context.user_data.pop('chart_data', None)
            context.user_data.pop('diary_history', None)
            await update.message.reply_text(
                'Введи дату рождения этого человека в формате *ДД.ММ.ГГГГ*:',
                parse_mode='Markdown',
                reply_markup=CANCEL_KEYBOARD
            )
            return BIRTH_DATE

    if text == '📋 Главное меню':
        await update.message.reply_text(
            'Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not DATE_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи дату как *ДД.ММ.ГГГГ* (например, 15.06.1995):',
            parse_mode='Markdown'
        )
        return BIRTH_DATE

    context.user_data['birth_date'] = text

    await update.message.reply_text(
        'Отлично! Теперь введи время рождения в формате *ЧЧ:ММ* (например, 14:30).\n'
        'Если время неизвестно — введи *12:00*.',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return BIRTH_TIME


async def birth_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if text == '📋 Главное меню':
        await update.message.reply_text(
            'Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not TIME_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи время как *ЧЧ:ММ* (например, 14:30):',
            parse_mode='Markdown'
        )
        return BIRTH_TIME

    context.user_data['birth_time'] = text

    await update.message.reply_text(
        'Последний шаг! Введи *город рождения* (например, Москва).\n'
        'Я определю координаты для точного расчёта.',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return BIRTH_PLACE


async def birth_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if text == '📋 Главное меню':
        await update.message.reply_text(
            'Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    msg = await update.message.reply_text('🔭 Рассчитываю натальную карту...')

    date = context.user_data.get('birth_date')
    time = context.user_data.get('birth_time')

    lat, lon = _get_coords(text)

    try:
        chart = calculate_chart(date, time, lat, lon)
        context.user_data['chart_data'] = chart

        simple = (
            f'✅ *Натальная карта рассчитана!*\n\n'
            f'🌍 *Город:* {text}\n'
        )
        if 'ascendant' in chart:
            simple += f'♈ *ASC:* {chart["ascendant"]}\n'
        if 'planets' in chart:
            simple += f'☀️ *Солнце:* {chart["planets"].get("Солнце", {}).get("sign", "—")} '
            simple += f'{chart["planets"].get("Солнце", {}).get("degree", "")}°\n'
            simple += f'🌙 *Луна:* {chart["planets"].get("Луна", {}).get("sign", "—")} '
            simple += f'{chart["planets"].get("Луна", {}).get("degree", "")}°\n'

        await msg.edit_text(simple, parse_mode='Markdown')

    except Exception as e:
        await msg.edit_text(f'❌ Ошибка расчёта: {e}')
        context.user_data['chart_data'] = None

    await update.message.reply_text(
        'Выбери, что хочешь узнать:',
        reply_markup=NATAL_KEYBOARD
    )
    return ConversationHandler.END


async def natal_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('chart_data'):
        await update.message.reply_text(
            'Сначала рассчитай свою натальную карту через 🔮 Натальная карта.',
            reply_markup=NATAL_KEYBOARD
        )
        return ConversationHandler.END

    await update.message.reply_text(
        '💞 *Совместимость*\n\n'
        'Введи *дату рождения* второго человека в формате *ДД.ММ.ГГГГ*:',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return COMPAT_DATE


async def compat_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text('Отменено.', reply_markup=NATAL_KEYBOARD)
        return ConversationHandler.END

    if text == '📋 Главное меню':
        await update.message.reply_text(
            'Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not DATE_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи дату как *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown'
        )
        return COMPAT_DATE

    context.user_data['compat_date'] = text

    await update.message.reply_text(
        'Теперь введи *время рождения* в формате *ЧЧ:ММ* (или 12:00, если неизвестно):',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return COMPAT_TIME


async def compat_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text('Отменено.', reply_markup=NATAL_KEYBOARD)
        return ConversationHandler.END

    if text == '📋 Главное меню':
        await update.message.reply_text(
            'Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not TIME_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи время как *ЧЧ:ММ*:',
            parse_mode='Markdown'
        )
        return COMPAT_TIME

    context.user_data['compat_time'] = text

    await update.message.reply_text(
        'Введи *город рождения* второго человека:',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return COMPAT_PLACE


async def compat_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text('Отменено.', reply_markup=NATAL_KEYBOARD)
        return ConversationHandler.END

    if text == '📋 Главное меню':
        await update.message.reply_text(
            'Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    msg = await update.message.reply_text('💞 Рассчитываю совместимость...')

    date = context.user_data.get('compat_date')
    time = context.user_data.get('compat_time')
    lat, lon = _get_coords(text)

    try:
        chart2 = calculate_chart(date, time, lat, lon)
        chart1 = context.user_data.get('chart_data')

        result = await interpret_compatibility(chart1, chart2)
        await msg.edit_text(
            f'💞 *Совместимость*\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери, что хочешь узнать:',
        reply_markup=NATAL_KEYBOARD
    )
    return ConversationHandler.END


async def _handle_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE, forecast_type: str):
    chart = context.user_data.get('chart_data')
    if not chart:
        await update.message.reply_text(
            'Сначала рассчитай натальную карту через 🔮 Натальная карта.',
            reply_markup=NATAL_KEYBOARD
        )
        return

    forecast_labels = {
        'day': '🔮 Прогноз на день',
        'year': '📅 Прогноз на год',
        'general': '📖 Общий разбор'
    }

    msg = await update.message.reply_text(
        f'{forecast_labels.get(forecast_type, "🔮")} Генерирую...')

    try:
        result = await interpret_natal(chart, forecast_type)
        await msg.edit_text(
            f'{forecast_labels.get(forecast_type, "🔮")}\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(
            f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Можешь выбрать другой прогноз:', reply_markup=NATAL_KEYBOARD)


async def natal_forecast_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_forecast(update, context, 'day')


async def natal_forecast_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_forecast(update, context, 'year')


async def natal_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_forecast(update, context, 'general')


def _get_coords(city: str) -> tuple:
    city = city.strip().lower()
    coords = {
        'москва': (55.7558, 37.6173),
        'санкт-петербург': (59.9343, 30.3351),
        'новосибирск': (55.0084, 82.9357),
        'екатеринбург': (56.8389, 60.6057),
        'казань': (55.7961, 49.1064),
        'нижний новгород': (56.3269, 44.0062),
        'челябинск': (55.1644, 61.4368),
        'самара': (53.1959, 50.1002),
        'омск': (54.9924, 73.3686),
        'ростов-на-дону': (47.2357, 39.7015),
        'уфа': (54.7388, 55.9721),
        'красноярск': (56.0184, 92.8672),
        'пермь': (58.0105, 56.2502),
        'воронеж': (51.6720, 39.1843),
        'волгоград': (48.7080, 44.5133),
        'минск': (53.8930, 27.5555),
        'киев': (50.4504, 30.5245),
        'алматы': (43.2220, 76.8512),
        'астана': (51.1605, 71.4704),
        'ташкент': (41.2995, 69.2401),
    }
    if city in coords:
        return coords[city]

    if any(word in city for word in ['москв', 'moscow']):
        return (55.7558, 37.6173)
    if any(word in city for word in ['питер', 'петерб', 'spb', 'saint']):
        return (59.9343, 30.3351)

    return (55.7558, 37.6173)
