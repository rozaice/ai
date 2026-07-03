from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.ai_service import interpret_astrology, astrology_followup
from handlers.start import MAIN_KEYBOARD

SIGN_INPUT, SIGN_CHOICE, FORECAST_TYPE, FOLLOW_UP = range(10, 14)

SIGN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['♈ Овен', '♉ Телец', '♊ Близнецы'],
        ['♋ Рак', '♌ Лев', '♍ Дева'],
        ['♎ Весы', '♏ Скорпион', '♐ Стрелец'],
        ['♑ Козерог', '♒ Водолей', '♓ Рыбы'],
        ['❌ Отмена']
    ],
    resize_keyboard=True
)

TYPE_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['📅 Прогноз на день'],
        ['📆 Прогноз на месяц'],
        ['📊 Прогноз на год'],
        ['❌ Отмена']
    ],
    resize_keyboard=True
)

AFTER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['❓ Уточнить/задать вопрос'],
        ['📅 Прогноз на день', '📆 Прогноз на месяц'],
        ['📊 Прогноз на год', '❌ Отмена']
    ],
    resize_keyboard=True
)

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отмена']],
    resize_keyboard=True
)

ZODIAC_MAP = {
    '♈ овен': 'Овен', '♉ телец': 'Телец', '♊ близнецы': 'Близнецы',
    '♋ рак': 'Рак', '♌ лев': 'Лев', '♍ дева': 'Дева',
    '♎ весы': 'Весы', '♏ скорпион': 'Скорпион', '♐ стрелец': 'Стрелец',
    '♑ козерог': 'Козерог', '♒ водолей': 'Водолей', '♓ рыбы': 'Рыбы',
}


def _parse_sign(text: str) -> str | None:
    key = text.strip().lower()
    if key in ZODIAC_MAP:
        return ZODIAC_MAP[key]
    for emoji, name in ZODIAC_MAP.items():
        if name.lower() in key:
            return name
    return None


async def astrology_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('chart_data'):
        await update.message.reply_text(
            '🔮 У тебя есть рассчитанная натальная карта. '
            'Использую её для персонального прогноза.\n\n'
            'Выбери период:',
            reply_markup=TYPE_KEYBOARD
        )
        return FORECAST_TYPE

    await update.message.reply_text(
        '🔮 *Астрология*\n\n'
        'Выбери свой знак зодиака или введи название:',
        parse_mode='Markdown',
        reply_markup=SIGN_KEYBOARD
    )
    return SIGN_CHOICE


async def sign_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('❌ Отмена', '📋 Главное меню'):
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    sign = _parse_sign(text)
    if not sign:
        await update.message.reply_text(
            'Не узнаю знак. Выбери из клавиатуры или напиши название:',
            reply_markup=SIGN_KEYBOARD
        )
        return SIGN_CHOICE

    context.user_data['zodiac_sign'] = sign
    await update.message.reply_text(
        f'♈ *{sign}* — отличный выбор!\n\n'
        'Какой прогноз тебя интересует?',
        parse_mode='Markdown',
        reply_markup=TYPE_KEYBOARD
    )
    return FORECAST_TYPE


async def forecast_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('❌ Отмена', '📋 Главное меню'):
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    type_map = {
        '📅 Прогноз на день': 'day',
        '📆 Прогноз на месяц': 'month',
        '📊 Прогноз на год': 'year',
    }
    ftype = type_map.get(text)
    if not ftype:
        await update.message.reply_text(
            'Выбери период из клавиатуры:',
            reply_markup=TYPE_KEYBOARD
        )
        return FORECAST_TYPE

    context.user_data['astro_type'] = ftype
    msg = await update.message.reply_text('🔮 Составляю прогноз...')

    try:
        sign = context.user_data.get('zodiac_sign', '')
        chart = context.user_data.get('chart_data')
        result = await interpret_astrology(sign, ftype, chart)
        context.user_data['astro_history'] = [
            {"role": "assistant", "content": result}
        ]
        await msg.edit_text(result, parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return FOLLOW_UP


async def follow_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('❌ Отмена', '📋 Главное меню'):
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if text == '❓ Уточнить/задать вопрос':
        await update.message.reply_text(
            'Напиши свой вопрос по прогнозу:',
            reply_markup=CANCEL_KEYBOARD
        )
        return FOLLOW_UP

    type_map = {
        '📅 Прогноз на день': 'day',
        '📆 Прогноз на месяц': 'month',
        '📊 Прогноз на год': 'year',
    }
    if text in type_map:
        context.user_data['astro_type'] = type_map[text]
        msg = await update.message.reply_text('🔮 Составляю прогноз...')
        try:
            sign = context.user_data.get('zodiac_sign', '')
            chart = context.user_data.get('chart_data')
            result = await interpret_astrology(sign, type_map[text], chart)
            context.user_data['astro_history'] = [
                {"role": "assistant", "content": result}
            ]
            await msg.edit_text(result, parse_mode='Markdown')
        except Exception as e:
            await msg.edit_text(f'❌ Ошибка: {e}')
        await update.message.reply_text(
            'Что дальше?', reply_markup=AFTER_KEYBOARD)
        return FOLLOW_UP

    msg = await update.message.reply_text('🔮 Думаю над ответом...')
    try:
        history = context.user_data.get('astro_history', [])
        answer, new_history = await astrology_followup(history, text)
        context.user_data['astro_history'] = new_history
        await msg.edit_text(answer, parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return FOLLOW_UP
