import telebot

bot = telebot.TeleBot('7959072655:AAEdgr5Qz1DrvMIUSO76n8jixqTFcs01qAQ')


user_data = {}
schedule_data = {}


facts = [
    "Python был создан Гвидо ван Россумом в 1991 году.",
    "Первый компьютерный баг был найден в 1947 году в виде настоящей моли в реле компьютера.",
    "Алгоритм PageRank, используемый Google, был назван в честь Ларри Пейджа."
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Введи свое имя и ID через пробел (Пример: Иван 12345)")

@bot.message_handler(commands=['info'])
def get_info(message):
    user_id = message.chat.id
    if user_id in user_data:
        name = user_data[user_id]["name"]
        student_id = user_data[user_id]["student_id"]
        bot.send_message(message.chat.id, f"Твои данные:\nИмя: {name}\nID: {student_id}")
    else:
        bot.send_message(message.chat.id, "Ты еще не зарегистрировал свои данные. Введи имя и ID через пробел.")

@bot.message_handler(commands=['add_schedule'])
def add_schedule(message):
    user_id = message.chat.id
    text = message.text.split(" ", 3)
    if len(text) < 3:
        bot.send_message(message.chat.id, "Использование: /add_schedule [день] [время] [предмет]")
        return
    day, time, subject = text[1], text[2], text[3]
    if user_id not in schedule_data:
        schedule_data[user_id] = []
    schedule_data[user_id].append((day, time, subject))
    bot.send_message(message.chat.id, f"Добавлено занятие: {day} {time} - {subject}")

@bot.message_handler(commands=['my_schedule'])
def my_schedule(message):
    user_id = message.chat.id
    if user_id in schedule_data and schedule_data[user_id]:
        schedule_text = "Твое расписание:\n" + "\n".join([f"{d} {t} - {s}" for d, t, s in schedule_data[user_id]])
        bot.send_message(message.chat.id, schedule_text)
    else:
        bot.send_message(message.chat.id, "Твое расписание пусто. Добавь занятия с помощью /add_schedule")

@bot.message_handler(commands=['delete_schedule'])
def delete_schedule(message):
    user_id = message.chat.id
    text = message.text.split(" ", 2)
    if len(text) < 3:
        bot.send_message(message.chat.id, "Использование: /delete_schedule [день] [время]")
        return
    day, time = text[1], text[2]
    if user_id in schedule_data:
        schedule_data[user_id] = [entry for entry in schedule_data[user_id] if not (entry[0] == day and entry[1] == time)]
        bot.send_message(message.chat.id, "Занятие удалено, если оно существовало.")
    else:
        bot.send_message(message.chat.id, "У тебя нет расписания.")

@bot.message_handler(commands=['random_fact'])
def random_fact(message):
    from random import choice
    bot.send_message(message.chat.id, choice(facts))

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Я помогу тебе с учебными данными. Используй команды:\n/start - Начать\n/info - Получить свои данные\n/add_schedule [день] [время] [предмет] - Добавить расписание\n/my_schedule - Посмотреть расписание\n/delete_schedule [день] [время] - Удалить занятие\n/random_fact - Получить случайный факт\n/help - Список команд")

@bot.message_handler(func=lambda message: True)
def save_user_data(message):
    user_id = message.chat.id
    text = message.text.split(" ", 1)
    if len(text) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, введи имя и ID через пробел.")
        return
    name, student_id = text
    user_data[user_id] = {"name": name, "student_id": student_id}
    bot.send_message(message.chat.id, f"Данные сохранены!\nИмя: {name}\nID: {student_id}")

print("Бот запущен...")
bot.polling(none_stop=True)
