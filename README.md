# AI Telegram Bot — Claude + Whisper

## Loyiha tuzilmasi
```
tgbot/
├── bot.py                  # Asosiy fayl
├── requirements.txt        # Kutubxonalar
├── railway.toml            # Railway sozlamasi
├── utils/
│   └── claude_client.py   # Claude + suhbat tarixi
└── handlers/
    ├── text_handler.py    # Matn xabarlar
    ├── voice_handler.py   # Ovoz xabarlar (Whisper STT)
    ├── photo_handler.py   # Rasm tahlili
    └── document_handler.py # PDF / matn fayllari
```

## Kerakli API kalitlar

| Kalit | Qayerdan olish |
|-------|---------------|
| `TELEGRAM_TOKEN` | @BotFather → /newbot |
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `OPENAI_API_KEY` | platform.openai.com (Whisper uchun) |

## Railway da deploy qilish

1. GitHub ga yuklang:
   ```bash
   git init
   git add .
   git commit -m "first commit"
   git branch -M main
   git remote add origin https://github.com/SIZNING/repo.git
   git push -u origin main
   ```

2. railway.app ga kiring → "New Project" → "Deploy from GitHub"

3. "Variables" bo'limiga kiriting:
   ```
   TELEGRAM_TOKEN=your_token_here
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

4. Deploy tugmasini bosing — tayyor!

## Botning imkoniyatlari

- **Matn** — istalgan savolga o'zbek va rus tilida javob
- **Ovoz** — Whisper orqali tanib, Claude javob beradi
- **Rasm** — Claude Vision orqali tahlil
- **PDF / TXT** — hujjatni o'qib javob beradi
- **Suhbat tarixi** — oxirgi 20 ta xabarni eslab qoladi

## Narx hisob-kitobi (taxminiy)

| Xizmat | Narx |
|--------|------|
| Claude Sonnet | ~$0.003 / xabar |
| Whisper STT | ~$0.006 / daqiqa |
| Railway hosting | $5 / oy |
