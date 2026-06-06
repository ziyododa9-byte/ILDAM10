import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes

user_state = {}
user_leads = {}

SHEETS_URL = os.environ.get("SHEETS_WEBHOOK_URL", "")
SHEETS_TOKEN = os.environ.get("SHEETS_TOKEN", "")

def save_to_sheets(ism, telefon, manba="Telegram", savol=""):
    try:
        resp = requests.post(SHEETS_URL, json={
            "token": SHEETS_TOKEN,
            "ism": ism,
            "telefon": telefon,
            "manba": manba,
            "savol": savol,
        }, timeout=10)
        result = resp.json()
        print("Sheets natija:", result)
        return result.get("status") == "ok"
    except Exception as e:
        print("Sheets xatosi:", e)
        return False

async def handle_text_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if user_state.get(uid) == "wait_name":
        user_leads[uid] = {
            "ism": text,
            "savol": user_leads.get(uid, {}).get("savol", "")
        }
        user_state[uid] = "wait_phone"
        await update.message.reply_text(
            f"Rahmat, {text}! 📱\nEndi telefon raqamingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return True
    return False

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    contact = update.message.contact
    telefon = contact.phone_number
    ism = user_leads.get(uid, {}).get("ism", contact.first_name or "Noma'lum")
    savol = user_leads.get(uid, {}).get("savol", "")

    save_to_sheets(ism, telefon, manba="Telegram", savol=savol)

    user_state.pop(uid, None)
    user_leads.pop(uid, None)

    await update.message.reply_text(
        f"✅ Rahmat, {ism}!\nJamoamiz tez orada bog'lanadi.",
        reply_markup=ReplyKeyboardRemove()
    )

def start_lead(uid, savol=""):
    user_leads[uid] = {"savol": savol}
    user_state[uid] = "wait_name"
