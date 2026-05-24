from telegram import Update
from telegram.ext import ContextTypes
from utils.claude_client import ask_claude


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        answer = ask_claude(user_id, user_text)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(
            "Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.\n"
            "Произошла ошибка. Пожалуйста, попробуйте ещё раз."
        )
        print(f"Text handler error: {e}")
