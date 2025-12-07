from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DATABASE
from logic import DB_Manager
db = DB_Manager(DATABASE)
db.create_tables()


def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📅 План на день", callback_data="menu_day"),
        InlineKeyboardButton("📝 Заметки", callback_data="menu_notes")
    )
    kb.add(InlineKeyboardButton("ℹ️ Помощь", callback_data="menu_help"))
    return kb

def dayplan_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Добавить план", callback_data="day_add"),
        InlineKeyboardButton("📋 Показать", callback_data="day_show")
    )
    kb.add(
        InlineKeyboardButton("🗑 Очистить", callback_data="day_clear"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    return kb

def notes_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Добавить заметку", callback_data="note_add"),
        InlineKeyboardButton("📚 Показать заметки", callback_data="note_show")
    )
    kb.add(
        InlineKeyboardButton("🗑 Удалить заметку", callback_data="note_delete"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    return kb

# def plan_dates_buttons(user_id):
#     plans = db.get_user_day_plan_dates(user_id)  # вернём уникальные даты
#     kb = InlineKeyboardMarkup()
#     for date in plans:
#         kb.add(InlineKeyboardButton(f"План дня на {date}", callback_data=f"show_plan_{date}"))
#     kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
#     return kb