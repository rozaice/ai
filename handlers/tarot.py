from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.ai_service import interpret_tarot
from services.tarot_service import draw_cards

TAROT_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['🎴 Предсказание на день'],
        ['🃏 Расклад на трех картах на ситуацию'],
        ['💞 Расклад на отношения'],
        ['💰 Расклад на финансы'],
        ['💼 Расклад на карьеру'],
        ['📋 Главное меню']
    ],
    resize_keyboard=True
)


async def tarot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🃏 *Таро* — выбери тип расклада:\n\n'
        '🎴 *На день* — одна карта-совет\n'
        '🃏 *3 карты на ситуацию* — прошлое / настоящее / будущее\n'
        '💞 *Отношения* — что важно знать о твоих отношениях\n'
        '💰 *Финансы* — денежный поток и возможности\n'
        '💼 *Карьера* — профессиональный путь и перспективы',
        parse_mode='Markdown',
        reply_markup=TAROT_KEYBOARD
    )


async def tarot_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = draw_cards(1)
    msg = await update.message.reply_text('🎴 Тяну карту...')

    try:
        result = await interpret_tarot(cards, 'daily')
        card_str = _format_cards(cards)
        await msg.edit_text(
            f'🎴 *Предсказание на день*\n\n{card_str}\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери другой расклад:', reply_markup=TAROT_KEYBOARD)


async def tarot_three(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = draw_cards(3)
    positions = ['📜 *Прошлое*', '🔍 *Настоящее*', '🔮 *Будущее*']
    msg = await update.message.reply_text('🃏 Раскладываю карты...')

    try:
        result = await interpret_tarot(cards, 'three')
        cards_str = '\n'.join(
            f'{pos}\n  {c["name"]} {"(перевёрнута)" if c["reversed"] else ""} — {c["meaning"]}'
            for pos, c in zip(positions, cards)
        )
        await msg.edit_text(
            f'🃏 *Расклад на трёх картах*\n\n{cards_str}\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери другой расклад:', reply_markup=TAROT_KEYBOARD)


async def tarot_relationship(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = draw_cards(3)
    positions = ['💔 *Партнёр*', '💞 *Отношения*', '💡 *Совет*']
    msg = await update.message.reply_text('💞 Раскладываю на отношения...')

    try:
        result = await interpret_tarot(cards, 'relationship')
        cards_str = '\n'.join(
            f'{pos}\n  {c["name"]} {"(перевёрнута)" if c["reversed"] else ""} — {c["meaning"]}'
            for pos, c in zip(positions, cards)
        )
        await msg.edit_text(
            f'💞 *Расклад на отношения*\n\n{cards_str}\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери другой расклад:', reply_markup=TAROT_KEYBOARD)


async def tarot_finance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = draw_cards(3)
    positions = ['💰 *Текущее положение*', '📈 *Возможности*', '💡 *Совет*']
    msg = await update.message.reply_text('💰 Раскладываю на финансы...')

    try:
        result = await interpret_tarot(cards, 'finance')
        cards_str = '\n'.join(
            f'{pos}\n  {c["name"]} {"(перевёрнута)" if c["reversed"] else ""} — {c["meaning"]}'
            for pos, c in zip(positions, cards)
        )
        await msg.edit_text(
            f'💰 *Расклад на финансы*\n\n{cards_str}\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери другой расклад:', reply_markup=TAROT_KEYBOARD)


async def tarot_career(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = draw_cards(3)
    positions = ['💼 *Текущая ситуация*', '🚀 *Перспективы*', '🧭 *Совет*']
    msg = await update.message.reply_text('💼 Раскладываю на карьеру...')

    try:
        result = await interpret_tarot(cards, 'career')
        cards_str = '\n'.join(
            f'{pos}\n  {c["name"]} {"(перевёрнута)" if c["reversed"] else ""} — {c["meaning"]}'
            for pos, c in zip(positions, cards)
        )
        await msg.edit_text(
            f'💼 *Расклад на карьеру*\n\n{cards_str}\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери другой расклад:', reply_markup=TAROT_KEYBOARD)


def _format_cards(cards: list) -> str:
    parts = []
    for c in cards:
        rev = ' (перевёрнута)' if c['reversed'] else ''
        parts.append(f'🃏 *{c["name"]}*{rev}\n  {c["meaning"]}')
    return '\n'.join(parts)
