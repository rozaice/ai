from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.ai_service import analyze_diary, generic_followup
from handlers.start import MAIN_KEYBOARD

DIARY_TEXT, DIARY_AFTER = range(2)

BACK_KEYBOARD = ReplyKeyboardMarkup(
    [['🔙 Назад']],
    resize_keyboard=True
)

AFTER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['❓ Уточнить/задать вопрос'],
        ['🔙 Назад']
    ],
    resize_keyboard=True
)


async def diary_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = context.user_data.get('diary_history')
    msg = '📝 Напиши о своём состоянии, мыслях и чувствах.\n'
    if history:
        msg += 'Я помню твои прошлые записи — учту их в анализе.'
    else:
        msg += 'Я проанализирую текст и дам обратную связь.'
    await update.message.reply_text(msg, reply_markup=BACK_KEYBOARD)
    return DIARY_TEXT


async def diary_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text in ('🔙 Назад', '📋 Главное меню'):
        await update.message.reply_text(
            'Возвращайся, когда захочешь поделиться.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    msg = await update.message.reply_text('🧠 Анализирую твой текст...')

    try:
        history = context.user_data.get('diary_history')
        analysis, new_history = await analyze_diary(text, history)
        context.user_data['diary_history'] = new_history
        await msg.edit_text(f'{analysis}', parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка при анализе. Попробуй ещё раз.\n{e}')

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return DIARY_AFTER


async def diary_after(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('🔙 Назад', '📋 Главное меню'):
        await update.message.reply_text(
            'Возвращайся, когда захочешь поделиться.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if text == '❓ Уточнить/задать вопрос':
        await update.message.reply_text(
            'Напиши свой вопрос по анализу:', reply_markup=BACK_KEYBOARD)
        return DIARY_AFTER

    msg = await update.message.reply_text('🧠 Думаю над ответом...')
    try:
        history = context.user_data.get('diary_history', [])
        answer, new_history = await generic_followup(
            history, text,
            "Ты — чуткий собеседник. Ответь на уточняющий вопрос "
            "по предыдущему анализу дневника. Кратко, по делу, на русском."
        )
        context.user_data['diary_history'] = new_history
        await msg.edit_text(answer, parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return DIARY_AFTER
