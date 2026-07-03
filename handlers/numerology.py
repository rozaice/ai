import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.numerology import calculate_all, pythagorean_square, destiny_matrix
from services.ai_service import interpret_numerology, interpret_numerology_compat
from handlers.start import MAIN_KEYBOARD

SUB_SECTION, NUM_DATE, NUM_DATE2 = range(20, 23)

SUBS_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['🔢 Матрица судьбы'],
        ['🔲 Квадрат Пифагора'],
        ['🕉️ Чакроанализ'],
        ['💞 Совместимость'],
        ['❌ Отмена']
    ],
    resize_keyboard=True
)

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отмена']],
    resize_keyboard=True
)

DATE_RE = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')


async def numerology_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🔢 *Нумерология*\n\nВыбери раздел:',
        parse_mode='Markdown',
        reply_markup=SUBS_KEYBOARD
    )
    return SUB_SECTION


async def sub_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('❌ Отмена', '📋 Главное меню'):
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    mapping = {
        '🔢 Матрица судьбы': 'matrix',
        '🔲 Квадрат Пифагора': 'pythagor',
        '🕉️ Чакроанализ': 'chakra',
        '💞 Совместимость': 'compat',
    }
    section = mapping.get(text)
    if not section:
        await update.message.reply_text(
            'Выбери раздел из клавиатуры:', reply_markup=SUBS_KEYBOARD)
        return SUB_SECTION

    context.user_data['num_section'] = section

    has_birth = bool(context.user_data.get('user_birth_date'))

    if section == 'compat':
        if has_birth:
            await update.message.reply_text(
                'Введи *дату рождения* второго человека в формате *ДД.ММ.ГГГГ*:',
                parse_mode='Markdown',
                reply_markup=CANCEL_KEYBOARD
            )
            return NUM_DATE2
        await update.message.reply_text(
            'Введи *дату рождения* первого человека в формате *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown',
            reply_markup=CANCEL_KEYBOARD
        )
        return NUM_DATE

    if has_birth:
        await update.message.reply_text(
            'У тебя уже есть дата рождения. Использовать её?\n\n'
            'Введи *ДД.ММ.ГГГГ* для новой даты или нажми *Да, моя*:',
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(
                [['✅ Да, моя дата'], ['❌ Отмена']],
                resize_keyboard=True
            )
        )
        return NUM_DATE

    await update.message.reply_text(
        'Введи дату рождения в формате *ДД.ММ.ГГГГ*:',
        parse_mode='Markdown',
        reply_markup=CANCEL_KEYBOARD
    )
    return NUM_DATE


async def numerology_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('❌ Отмена', '📋 Главное меню'):
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if text == '✅ Да, моя дата':
        date = context.user_data.get('user_birth_date')
        if date:
            return await _show_result(update, context, date)
        await update.message.reply_text(
            'Дата не найдена. Введи *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown',
            reply_markup=CANCEL_KEYBOARD
        )
        return NUM_DATE

    if not DATE_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи дату как *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown'
        )
        return NUM_DATE

    return await _show_result(update, context, text)


async def numerology_date2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('❌ Отмена', '📋 Главное меню'):
        await update.message.reply_text('Отменено.', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not DATE_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи дату как *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown'
        )
        return NUM_DATE2

    date1 = context.user_data.get('user_birth_date')
    if not date1:
        msg = await update.message.reply_text('⏳ Сначала нужна дата первого человека...')
        await update.message.reply_text(
            'Введи *дату рождения* первого человека:',
            parse_mode='Markdown',
            reply_markup=CANCEL_KEYBOARD
        )
        return NUM_DATE

    msg = await update.message.reply_text('🔢 Рассчитываю совместимость...')
    try:
        result = await interpret_numerology_compat(date1, text)
        await msg.edit_text(
            f'💞 *Нумерологическая совместимость*\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Выбери раздел:', reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END


async def _show_result(update: Update, context: ContextTypes.DEFAULT_TYPE, date: str):
    section = context.user_data.get('num_section')
    msg = await update.message.reply_text('🔢 Рассчитываю...')

    try:
        if section == 'pythagor':
            result = pythagorean_square(date)
            await msg.edit_text(
                f'*Квадрат Пифагора*\n\n{result}',
                parse_mode='Markdown'
            )
        elif section == 'matrix':
            nums = destiny_matrix(date)
            ai = await interpret_numerology(date, 'matrix', nums)
            await msg.edit_text(
                f'*Матрица Судьбы*\n\n{ai}',
                parse_mode='Markdown'
            )
        elif section == 'chakra':
            ai = await interpret_numerology(date, 'chakra')
            await msg.edit_text(
                f'*Чакроанализ*\n\n{ai}',
                parse_mode='Markdown'
            )
        else:
            nums = calculate_all(date)
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
