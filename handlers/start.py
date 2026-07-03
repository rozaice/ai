from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['📝 Дневник состояния'],
        ['🔮 Натальная карта'],
        ['🃏 Таро', '🔢 Нумерология']
    ],
    resize_keyboard=True,
    is_persistent=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🌟 Добро пожаловать в бота самопознания!\n\n'
        'Я помогу тебе:\n'
        '📝 Вести дневник состояния с AI-анализом\n'
        '🔮 Рассчитать и разобрать натальную карту\n'
        '🃏 Получить предсказания Таро\n'
        '🔢 Рассчитать нумерологию\n\n'
        'Выбери раздел:',
        reply_markup=MAIN_KEYBOARD
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Главное меню:',
        reply_markup=MAIN_KEYBOARD
    )
