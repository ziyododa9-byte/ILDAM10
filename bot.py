import os
import logging
import tempfile
import base64
import httpx
from anthropic import Anthropic
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

history = {}
SYSTEM = """Siz professional biznes yordamchisisiz. Faqat O'ZBEK yoki RUS tilida javob bering. Agar foydalanuvchi boshqa tilda yozsa ham, javobni O'ZBEK tilida bering. Qisqa, aniq va foydali javoblar bering."""

def get_history(uid): return history.get(uid, [])
def add_history(uid, role, content):
    if uid not in history: history[uid] = []
    history[uid].append({"role": role, "content": content})
    if len(history[uid]) > 20: history[uid] = history[uid][-20:]

def ask_claude(uid, content):
    add_history(uid, "user", content)
    r = anthropic.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1500, system=SYSTEM, messages=get_history(uid))
    answer = r.content[0].text
    add_history(uid, "assistant", answer)
    return answer

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men sizning AI yordamchingizman.\n\nYozing, ovoz yuboring, rasm yoki PDF yuboring!\n\nRasm yaratish uchun: /rasm [tavsif]")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        answer = ask_claude(update.effective_user.id, update.message.text)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("Xatolik yuz berdi.")
        print(e)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name
        await file.download_to_drive(tmp_path)
        with open(tmp_path, "rb") as audio:
            transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=audio)
        os.unlink(tmp_path)
        text = transcript.text
        if not text.strip():
            await update.message.reply_text("Ovozni aniqlay olmadim.")
            return
        await update.message.reply_text(f'Tingladim: "{text}"')
        await update.message.reply_text(ask_claude(update.effective_user.id, text))
    except Exception as e:
        await update.message.reply_text("Ovozni qayta ishlashda xatolik.")
        print(e)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        img = base64.standard_b64encode(httpx.get(file.file_path).content).decode()
        caption = update.message.caption or "Bu rasmni tahlil qil."
        uid = update.effective_user.id
        content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}}, {"type": "text", "text": caption}]
        add_history(uid, "user", content)
        r = anthropic.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1500, system=SYSTEM, messages=get_history(uid))
        answer = r.content[0].text
        add_history(uid, "assistant", answer)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("Rasmni qayta ishlashda xatolik.")
        print(e)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        doc = update.message.document
        if doc.file_size > 10 * 1024 * 1024:
            await update.message.reply_text("Fayl juda katta. 10MB dan kichik fayl yuboring.")
            return
        file = await context.bot.get_file(doc.file_id)
        data = httpx.get(file.file_path).content
        caption = update.message.caption or "Bu hujjatni o'qib, asosiy ma'lumotlarni ayt."
        uid = update.effective_user.id
        mime = doc.mime_type or ""
        if "pdf" in mime:
            content = [{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": base64.standard_b64encode(data).decode()}}, {"type": "text", "text": caption}]
            add_history(uid, "user", content)
            r = anthropic.messages.create(model="claude-haiku-4-5-20251001", max_tokens=2000, system=SYSTEM, messages=get_history(uid))
            answer = r.content[0].text
            add_history(uid, "assistant", answer)
        else:
            text = data.decode("utf-8", errors="ignore")[:8000]
            answer = ask_claude(uid, f"{caption}\n\n{text}")
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("Hujjatni qayta ishlashda xatolik.")
        print(e)

async def handle_image_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
    prompt = " ".join(context.args) if context.args else None
    if not prompt:
        await update.message.reply_text("Rasm uchun tavsif yozing:\n/rasm tog'da qor yog'ayotgan manzara")
        return
    try:
        await update.message.reply_text("Rasm tayyorlanmoqda...")
        response = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        image_data = response.data[0].b64_json
        image_bytes = base64.b64decode(image_data)
        await update.message.reply_photo(photo=image_bytes, caption=f"{prompt}")
    except Exception as e:
        await update.message.reply_text("Rasm yaratishda xatolik yuz berdi.")
        print(f"Image gen error: {e}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rasm", handle_image_gen))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
print("Bot ishga tushdi!")
app.run_polling()
