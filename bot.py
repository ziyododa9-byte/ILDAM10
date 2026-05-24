import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters
)
from handlers.text_handler import handle_text
from handlers.voice_handler import handle_voice
from handlers.photo_handler import handle_photo
from handlers.document_handler import handle_document

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "Salom"
    await update.message.reply_text(
        f"Salom, {name}! Men sizning AI yordamchingizman.\n\n"
        f"Привет, {name}! Я ваш AI ассистент.\n\n"
        f"Menga yozishingiz, ovoz yuborishingiz, rasm yoki PDF fayl yuborishingiz mumkin."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Nima qila olaman:\n"
        "• Matn — istalgan savolga javob beraman\n"
        "• Ovoz — ovoz xabaringizni tinglab javob beraman\n"
        "• Rasm — rasmni tahlil qilaman\n"
        "• PDF/hujjat — faylni o'qib javob beraman\n\n"
        "Что я умею:\n"
        "• Текст — отвечу на любой вопрос\n"
        "• Голос — пойму голосовое сообщение\n"
        "• Фото — проанализирую изображение\n"
        "• PDF/документ — прочитаю и отвечу"
    )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
