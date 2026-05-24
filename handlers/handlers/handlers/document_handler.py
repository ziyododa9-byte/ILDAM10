import tempfile
import os
import httpx
import base64
from telegram import Update
from telegram.ext import ContextTypes
from utils.claude_client import ask_claude, add_to_history, client, SYSTEM_PROMPT, get_history

MAX_FILE_SIZE_MB = 10


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    doc = update.message.document

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    if doc.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            f"Fayl hajmi {MAX_FILE_SIZE_MB}MB dan katta.\n"
            f"Файл больше {MAX_FILE_SIZE_MB}МБ."
        )
        return

    try:
        file = await context.bot.get_file(doc.file_id)
        file_url = file.file_path
        file_bytes = httpx.get(file_url).content
        caption = update.message.caption or "Bu hujjatni o'qib, asosiy ma'lumotlarni ayt."
        mime = doc.mime_type or ""

        if "pdf" in mime:
            pdf_data = base64.standard_b64encode(file_bytes).decode("utf-8")
            content = [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": caption},
            ]

            add_to_history(user_id, "user", content)
            history = get_history(user_id)

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=history,
            )

            answer = response.content[0].text
            add_to_history(user_id, "assistant", answer)
            await update.message.reply_text(answer)

        elif mime.startswith("text/") or doc.file_name.endswith(
            (".txt", ".csv", ".md", ".py", ".js", ".json")
        ):
            text_content = file_bytes.decode("utf-8", errors="ignore")
            if len(text_content) > 8000:
                text_content = text_content[:8000] + "\n\n[...fayl qisqartirildi]"
            prompt = f"{caption}\n\nFayl mazmuni:\n```\n{text_content}\n```"
            answer = ask_claude(user_id, prompt)
            await update.message.reply_text(answer)

        else:
            await update.message.reply_text(
                "Bu fayl turini qo'llab-quvvatlamayman. PDF, TXT, CSV yuboring.\n"
                "Этот тип файла не поддерживается."
            )

    except Exception as e:
        await update.message.reply_text(
            "Hujjatni qayta ishlashda xatolik.\n"
            "Ошибка при обработке документа."
        )
        print(f"Document handler error: {e}")
