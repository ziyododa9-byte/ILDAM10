import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Har bir foydalanuvchining suhbat tarixi xotirada saqlanadi
# {user_id: [{"role": "user"/"assistant", "content": ...}]}
conversation_history: dict[int, list] = {}

SYSTEM_PROMPT = """Siz professional biznes yordamchisisiz. 
Foydalanuvchi qaysi tilda yozsa yoki gaplashsa, o'sha tilda javob bering.
O'zbek yoki rus tilida muloqot qiling.
Qisqa, aniq va foydali javoblar bering.
Agar foydalanuvchi rasm, hujjat yoki ovoz yuborsa, uni diqqat bilan tahlil qiling.
Har doim xushmuomala va professional bo'ling."""


def get_history(user_id: int) -> list:
    return conversation_history.get(user_id, [])


def add_to_history(user_id: int, role: str, content):
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": role, "content": content})
    # Oxirgi 20 ta xabarni saqlash (xotira cheklovidan oshmasligi uchun)
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]


def clear_history(user_id: int):
    conversation_history[user_id] = []


def ask_claude(user_id: int, content) -> str:
    """
    Claude ga so'rov yuborish.
    content — matn (str) yoki multimodal list bo'lishi mumkin.
    """
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
    return answer
