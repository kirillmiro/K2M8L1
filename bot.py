import re
import telebot
from telebot.types import Message, CallbackQuery
from datetime import datetime
from config import TOKEN, DATABASE
from logic import DB_Manager
from keyboards import main_menu, dayplan_menu, notes_menu


db = DB_Manager(DATABASE)
db.create_tables()

bot = telebot.TeleBot(TOKEN)


# ---------- START ----------
@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    db.ensure_user(message.from_user.id)
    text = ("""
✨ Привет! Я — бот-трекер привычек 🧠
Я помогу тебе организовать день, вести заметки и отслеживать привычки.

Выбери действие ниже:
""")
    bot.send_message(message.chat.id, text, reply_markup=main_menu())


# ---------- DAY_PLAN ----------
def parse_plan_text(text: str):
    items = [i.strip() for i in text.split(",") if i.strip()]
    result = []
    for item in items:
        if "-" not in item:
            raise ValueError(f"⚠️ Неправильный ввод данных! Элемент '{item}' не содержит '-'")
        parts = item.split("-", 1)
        task = parts[0].strip()
        time = parts[1].strip()
        if not task:
            raise ValueError(f"⚠️ Неправильный ввод данных! Пустая задача в элементе '{item}'")
        if not time:
            raise ValueError(f"⚠️ Неправильный ввод данных! Пустое время в элементе '{item}'")
        result.append((task, time))
    return result


def Day_plan_save(message: Message):
    user_id = message.from_user.id
    text = message.text or ""
    plan_date = datetime.now().strftime("%d.%m.%Y")  # текущая дата

    try:
        pairs = parse_plan_text(text)
    except ValueError as e:
        bot.send_message(message.chat.id, f"⚠️ Неправильный ввод данных! {e}\nПопробуй ещё раз.", reply_markup=None)
        return

    db.ensure_user(user_id)
    for task, time in pairs:
        db.save_user_day_plan(task, time, user_id, plan_date)

    bot.send_message(message.chat.id, f"План на {plan_date} сохранён ✅", reply_markup=dayplan_menu())


# ---------- NOTES ----------
def Note_save(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    if not text:
        bot.send_message(message.chat.id, "⚠️ Неправильный ввод данных! Нельзя сохранить пустую заметку. Попробуй ещё раз.")
        return

    db.ensure_user(user_id)
    note_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    db.save_user_note(text, note_date, user_id)

    bot.send_message(message.chat.id, "✅ Заметка сохранена!", reply_markup=notes_menu())

def note_delete_step(message: Message):
    user_id = message.from_user.id
    try:
        note_id = int(message.text.strip())
        db.delete_user_note(user_id, note_id)
        bot.send_message(message.chat.id, "Заметка удалена ✅", reply_markup=notes_menu())
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Неправильный ввод данных! Введите номер заметки.")
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Ошибка при удалении заметки.")

# ---------- CALLBACK HANDLER ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    data = call.data
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    db.ensure_user(user_id)

    # --- Главное меню ---
    if data == "menu_day":
        bot.send_message(chat_id, "Меню — План на день", reply_markup=dayplan_menu())
    elif data == "menu_notes":
        bot.send_message(chat_id, "Меню — Заметки", reply_markup=notes_menu())
    elif data == "menu_help":
        bot.send_message(chat_id, "Если нужна помощь — опиши проблему, и на почту kirill.miro2000@gmail.com.")
    elif data == "back_main":
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())

    # --- Планы дня ---
    elif data == "day_add":
        bot.send_message(chat_id, "Напиши свой план дня через запятую.\nПример: Проснуться - 6:00, Умыться - 6:10")
        bot.register_next_step_handler(call.message, Day_plan_save)

    elif data == "day_show":
        plans = db.get_user_day_plan(user_id)
        if not plans:
            bot.send_message(chat_id, "План пуст.")
        else:
            txt = "Твои планы:\n"
            for _id, task, time in plans:
                txt += f"• {task} — {time}\n"
            bot.send_message(chat_id, txt)

    elif data == "day_clear":
        db.clear_user_day_plan(user_id)
        bot.send_message(chat_id, "План очищен.")
    
    elif data.startswith("show_plan_"):
        date = data.replace("show_plan_", "")
        plans = db.get_user_day_plan_by_date(user_id, date)
        if not plans:
            bot.send_message(chat_id, f"План на {date} пуст.")
        else:
            txt = f"План дня на {date}:\n"
            for _id, task, time in plans:
                txt += f"• {task} — {time}\n"
            bot.send_message(chat_id, txt)

    # --- Заметки ---
    elif data == "note_add":
        bot.send_message(chat_id, "Напиши текст заметки:")
        bot.register_next_step_handler(call.message, Note_save)

    elif data == "note_show":
        notes = db.get_user_notes(user_id)
        if not notes:
            bot.send_message(chat_id, "У тебя пока нет заметок.")
        else:
            txt = "Твои заметки:\n"
            for _id, note_text, note_date in notes:
                txt += f"• {note_text}!\n Время добавления: {note_date}\n\n"
            bot.send_message(chat_id, txt)

    elif data == "note_delete":
        notes = db.get_user_notes(user_id)
        if not notes:
            bot.send_message(chat_id, "У тебя нет заметок для удаления.")
            return
        # Формируем список заметок с номерами
        txt = "Выбери номер заметки для удаления:\n"
        for note in notes:
            txt += f"{note[0]}: {note[1]} — {note[2]}\n"
        bot.send_message(chat_id, txt)
        bot.register_next_step_handler(call.message, note_delete_step)


# ---------- START BOT ----------
if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()