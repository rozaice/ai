from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.ai_service import analyze_diary
from handlers.start import MAIN_KEYBOARD

DIARY_TEXT = 0

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отмена']],
    resize_keyboard=True
)


async def diary_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📝 Напиши о своём состоянии, мыслях и чувствах.\n'
        'Я проанализирую текст и дам обратную связь.',
        reply_markup=CANCEL_KEYBOARD
    )
    return DIARY_TEXT


async def diary_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '❌ Отмена':
        await update.message.reply_text(
            'Возвращайся, когда захочешь поделиться.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    msg = await update.message.reply_text('🧠 Анализирую твой текст...')

    try:
        analysis = await analyze_diary(text)
        await msg.edit_text(
            f'📝 *Результат анализа:*\n\n{analysis}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(
            f'❌ Ошибка при анализе. Попробуй ещё раз.\n{e}')

    await update.message.reply_text(
        'Можешь написать ещё или вернуться в меню.',
        reply_markup=MAIN_KEYBOARD
    )
    return ConversationHandler.END
