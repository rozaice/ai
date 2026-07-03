import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.numerology import calculate_all, pythagorean_square, destiny_matrix
from services.ai_service import (
    interpret_numerology, interpret_numerology_compat,
    interpret_pythagorean_square, generic_followup
)
from handlers.start import MAIN_KEYBOARD

SUB_SECTION, NUM_DATE, NUM_DATE2, NUM_NAME2, NUM_AFTER = range(20, 25)

SUBS_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['🔢 Матрица судьбы'],
        ['🔲 Квадрат Пифагора'],
        ['🕉️ Чакроанализ'],
        ['💞 Совместимость'],
        ['🔙 Назад']
    ],
    resize_keyboard=True
)

BACK_KEYBOARD = ReplyKeyboardMarkup(
    [['🔙 Назад']],
    resize_keyboard=True
)

AFTER_KEYBOARD = ReplyKeyboardMarkup(
    [['🔙 Назад']],
    resize_keyboard=True
)

PYTHAGOR_KEYBOARD = ReplyKeyboardMarkup(
    [
        ['🔍 Расшифровать'],
        ['🔙 Назад']
    ],
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
    if text in ('🔙 Назад', '📋 Главное меню'):
        await update.message.reply_text('Главное меню:', reply_markup=MAIN_KEYBOARD)
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
                '💞 *Совместимость*\n\n'
                'Как зовут второго человека?',
                parse_mode='Markdown',
                reply_markup=BACK_KEYBOARD
            )
            return NUM_NAME2
        await update.message.reply_text(
            '💞 *Совместимость*\n\n'
            'Введи *дату рождения* первого человека в формате *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown',
            reply_markup=BACK_KEYBOARD
        )
        return NUM_DATE

    if has_birth:
        await update.message.reply_text(
            'У тебя уже есть дата рождения. Использовать её?\n\n'
            'Введи *ДД.ММ.ГГГГ* для новой даты или нажми *Да, моя*:',
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(
                [['✅ Да, моя дата'], ['🔙 Назад']],
                resize_keyboard=True
            )
        )
        return NUM_DATE

    await update.message.reply_text(
        'Введи дату рождения в формате *ДД.ММ.ГГГГ*:',
        parse_mode='Markdown',
        reply_markup=BACK_KEYBOARD
    )
    return NUM_DATE


async def numerology_name2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('🔙 Назад', '📋 Главное меню'):
        await update.message.reply_text('Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    context.user_data['compat_name2'] = text.strip()

    await update.message.reply_text(
        f'Введи *дату рождения* *{text.strip()}* в формате *ДД.ММ.ГГГГ*:',
        parse_mode='Markdown',
        reply_markup=BACK_KEYBOARD
    )
    return NUM_DATE2


async def numerology_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('🔙 Назад', '📋 Главное меню'):
        await update.message.reply_text('Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if text == '✅ Да, моя дата':
        date = context.user_data.get('user_birth_date')
        if date:
            return await _show_result(update, context, date)
        await update.message.reply_text(
            'Дата не найдена. Введи *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown',
            reply_markup=BACK_KEYBOARD
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
    if text == '🔙 Назад':
        await update.message.reply_text(
            '💞 *Совместимость*\n\n'
            'Как зовут второго человека?',
            parse_mode='Markdown',
            reply_markup=BACK_KEYBOARD
        )
        return NUM_NAME2
    if text in ('📋 Главное меню',):
        await update.message.reply_text('Главное меню:', reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    if not DATE_RE.match(text):
        await update.message.reply_text(
            'Неверный формат. Введи дату как *ДД.ММ.ГГГГ*:',
            parse_mode='Markdown'
        )
        return NUM_DATE2

    date1 = context.user_data.get('user_birth_date')
    if not date1:
        await update.message.reply_text(
            '⏳ Сначала нужна дата первого человека...\n'
            'Введи *дату рождения* первого человека:',
            parse_mode='Markdown',
            reply_markup=BACK_KEYBOARD
        )
        return NUM_DATE

    msg = await update.message.reply_text('🔢 Рассчитываю совместимость...')
    try:
        name2 = context.user_data.get('compat_name2', 'Человек 2')
        result = await interpret_numerology_compat(date1, text, name1='Я', name2=name2)
        context.user_data['num_history'] = [{"role": "assistant", "content": result}]
        await msg.edit_text(
            f'💞 *Нумерологическая совместимость*\n\n{result}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return NUM_AFTER


async def numerology_after(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ('🔙 Назад', '📋 Главное меню'):
        await update.message.reply_text(
            '🔢 *Нумерология*\n\nВыбери раздел:',
            parse_mode='Markdown',
            reply_markup=SUBS_KEYBOARD
        )
        return SUB_SECTION

    if text == '🔍 Расшифровать':
        date = context.user_data.get('num_date')
        square = context.user_data.get('pythagor_result', '')
        msg = await update.message.reply_text('🔍 Расшифровываю квадрат Пифагора...')
        try:
            interpretation = await interpret_pythagorean_square(date, square)
            await msg.edit_text(
                f'*🔍 Расшифровка Квадрата Пифагора*\n\n{interpretation}',
                parse_mode='Markdown'
            )
        except Exception as e:
            await msg.edit_text(f'❌ Ошибка: {e}')
        await update.message.reply_text(
            'Что дальше?', reply_markup=PYTHAGOR_KEYBOARD)
        return NUM_AFTER

    if text == '❓ Уточнить/задать вопрос':
        await update.message.reply_text(
            'Напиши свой вопрос:', reply_markup=BACK_KEYBOARD)
        return NUM_AFTER

    msg = await update.message.reply_text('🔢 Думаю над ответом...')
    try:
        history = context.user_data.get('num_history', [])
        answer, new_history = await generic_followup(
            history, text,
            "Ты — нумеролог. Ответь на уточняющий вопрос по предыдущему разбору. "
            "Кратко, по делу, на русском."
        )
        context.user_data['num_history'] = new_history
        await msg.edit_text(answer, parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f'❌ Ошибка: {e}')

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return NUM_AFTER


async def _show_result(update: Update, context: ContextTypes.DEFAULT_TYPE, date: str):
    section = context.user_data.get('num_section')
    msg = await update.message.reply_text('🔢 Рассчитываю...')

    try:
        if section == 'pythagor':
            result = pythagorean_square(date)
            context.user_data['num_date'] = date
            context.user_data['pythagor_result'] = result
            await msg.edit_text(
                f'*Квадрат Пифагора*\n\n{result}',
                parse_mode='Markdown'
            )
            await update.message.reply_text(
                'Что дальше?', reply_markup=PYTHAGOR_KEYBOARD)
            return NUM_AFTER

        elif section == 'matrix':
            nums = destiny_matrix(date)
            ai = await interpret_numerology(date, 'matrix', nums)
            context.user_data['num_history'] = [{"role": "assistant", "content": ai}]
            await msg.edit_text(
                f'*Матрица Судьбы*\n\n{ai}',
                parse_mode='Markdown'
            )

        elif section == 'chakra':
            ai = await interpret_numerology(date, 'chakra')
            context.user_data['num_history'] = [{"role": "assistant", "content": ai}]
            await msg.edit_text(
                f'*Чакроанализ*\n\n{ai}',
                parse_mode='Markdown'
            )

        elif section == 'compat':
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
            'Выбери раздел:', reply_markup=SUBS_KEYBOARD)
        return SUB_SECTION

    await update.message.reply_text(
        'Что дальше?', reply_markup=AFTER_KEYBOARD)
    return NUM_AFTER
