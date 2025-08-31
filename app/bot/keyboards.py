from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def suggestion_keyboard(msg_id: int, n: int):
    rows = []
    for i in range(n):
        rows.append([InlineKeyboardButton(
            text=f"제안 {i+1} 등록",
            callback_data=f"suggest_add:{msg_id}:{i}"
        )])
    return InlineKeyboardMarkup(rows)
