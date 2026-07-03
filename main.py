from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
from handlers.start import start, main_menu
from handlers.diary import diary_start, diary_message, DIARY_TEXT
from handlers.natal import (
    natal_menu, birth_date, birth_time, birth_place,
    BIRTH_DATE, BIRTH_TIME, BIRTH_PLACE,
    natal_forecast_day, natal_forecast_year, natal_general
)
from handlers.tarot import tarot_menu, tarot_daily, tarot_three, tarot_relationship


def main():
    import os
    token_val = os.getenv("BOT_TOKEN")
    print(f"DEBUG BOT_TOKEN: '{token_val}' (len={len(token_val) if token_val else 0})")
    if not token_val:
        print("ERROR: BOT_TOKEN is empty or not set!")
        return
    app = Application.builder().token(BOT_TOKEN).build()

    diary_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^📝 Дневник состояния$'), diary_start)],
        states={
            DIARY_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, diary_message)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    natal_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^🔮 Натальная карта$'), natal_menu)],
        states={
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_date)],
            BIRTH_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_time)],
            BIRTH_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_place)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Regex(r'^📋 Главное меню$'), main_menu))

    app.add_handler(diary_conv)
    app.add_handler(natal_conv)

    app.add_handler(MessageHandler(filters.Regex(r'^🃏 Таро$'), tarot_menu))

    app.add_handler(MessageHandler(filters.Regex(r'^🔮 Прогноз на день$'), natal_forecast_day))
    app.add_handler(MessageHandler(filters.Regex(r'^📅 Прогноз на год$'), natal_forecast_year))
    app.add_handler(MessageHandler(filters.Regex(r'^📖 Общий разбор$'), natal_general))

    app.add_handler(MessageHandler(filters.Regex(r'^🎴 Предсказание на день$'), tarot_daily))
    app.add_handler(MessageHandler(filters.Regex(r'^🃏 Расклад на трех картах$'), tarot_three))
    app.add_handler(MessageHandler(filters.Regex(r'^💞 Расклад на отношения$'), tarot_relationship))

    print('Bot started! Press Ctrl+C to stop.')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    from telegram import Update
    main()
