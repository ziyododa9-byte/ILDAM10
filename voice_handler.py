import os
import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from utils.claude_client import ask_claude

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # Ovoz faylini yuklab olish
        voice_file = await context.bot.get_file(update.message.voice.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name

        await voice_file.download_to_drive(tmp_path)

        # Whisper orqali matnga aylantirish
        with open(tmp_path, "rb") as audio:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language=None,  # Avtomatik til aniqlash
            )

        os.unlink(tmp_path)
        recognized_text = transcript.text

        if not recognized_text.strip():
            await update.message.reply_text(
                "Ovozni aniqlay olmadim. Qayta urinib ko'ring.\n"
                "Не удалось распознать голос. Попробуйте ещё раз."
            )
            return

        # Foydalanuvchiga qaysi matn tanilanganini ko'rsatish
        await update.message.reply_text(f'Tingladim: "{recognized_text}"')

        # Claude ga yuborish
        answer = ask_claude(user_id, recognized_text)
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(
            "Ovozni qayta ishlashda xatolik.\n"
            "Ошибка при обработке голоса."
        )
        print(f"Voice handler error: {e}")
