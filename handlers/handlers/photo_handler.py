import base64
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from utils.claude_client import ask_claude, add_to_history, client, SYSTEM_PROMPT, get_history


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_url = file.file_path

        image_data = base64.standard_b64encode(
            httpx.get(file_url).content
        ).decode("utf-8")

        caption = update.message.caption or "Bu rasmni tahlil qil va tushuntir."

        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data,
                },
            },
            {"type": "text", "text": caption},
        ]

        add_to_history(user_id, "user", content)
        history = get_history(user_id)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=history,
        )

        answer = response.content[0].text
        add_to_history(user_id, "assistant", answer)
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(
            "Rasmni qayta ishlashda xatolik.\n"
            "Ошибка при обработке фото."
        )
        print(f"Photo handler error: {e}")
