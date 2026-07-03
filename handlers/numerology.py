import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.numerology import calculate_all
from handlers.start import MAIN_KEYBOARD

NUM_DATE = 0

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отмена']],
    resize_keyboard=True
)

DATE_RE = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')


async def numerology_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🔢 *Нумерология*\n\n'
        'Введи дату рождения в формате *ДД.ММ.ГГГГ* (например, 15.06.1995):',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return NUM_DATE


async def numerology_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '❌ Отмена':
        await update.message.reply_text(
            'Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not DATE_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи дату как *ДД.ММ.ГГГГ* (например, 15.06.1995):',
            parse_mode='Markdown'
        )
        return NUM_DATE

    msg = await update.message.reply_text('🔢 Рассчитываю нумерологию...')

    try:
        nums = calculate_all(text)
        result = (
            f"*1. Жизненный Путь — {nums['life_path'][0]}*\n"
            f"{nums['life_path'][1]}\n\n"
            f"*2. Выражение — {nums['expression'][0]}*\n"
            f"{nums['expression'][1]}\n\n"
            f"*3. Душа — {nums['soul'][0]}*\n"
            f"{nums['soul'][1]}\n\n"
            f"*4. Личность — {nums['personality'][0]}*\n"
            f"{nums['personality'][1]}\n\n"
            f"*5. День Рождения — {nums['birth_day'][0]}*\n"
            f"{nums['birth_day'][1]}"
        )
        await msg.edit_text(result, parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери раздел:', reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END
