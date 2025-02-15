import telebot
import requests
import sqlite3

bot = telebot.TeleBot('7959072655:AAEdgr5Qz1DrvMIUSO76n8jixqTFcs01qAQ')

user_data = {}
schedule_data = {}

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    student_id TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS schedule (
    user_id INTEGER,
    day TEXT,
    time TEXT,
    subject TEXT,
    PRIMARY KEY (user_id, day, time),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

conn.commit()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Введи свое имя и ID через пробел (Пример: Мансур 2010)")


@bot.message_handler(commands=['info'])
def get_info(message):
    user_id = message.chat.id
    # Получаем данные из базы данных
    cursor.execute("SELECT name, student_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        name, student_id = result
        bot.send_message(message.chat.id, f"Твои данные:\nИмя: {name}\nID: {student_id}")
    else:
        bot.send_message(message.chat.id, "Ты еще не зарегистрировал свои данные. Введи имя и ID через пробел.")


@bot.message_handler(commands=['add_schedule'])
def add_schedule(message):
    try:
        # Парсим данные из команды
        _, day, time, subject = message.text.split(' ', 3)
        user_id = message.chat.id

        # Проверяем, есть ли уже занятие для этого пользователя в этот день и время
        cursor.execute("SELECT * FROM schedule WHERE user_id = ? AND day = ? AND time = ?",
                       (user_id, day, time))
        existing_schedule = cursor.fetchone()

        if existing_schedule:
            bot.send_message(message.chat.id, f"Занятие в {time} в день {day} уже существует.")
        else:
            # Добавляем расписание в базу данных, если его нет
            cursor.execute("INSERT INTO schedule (user_id, day, time, subject) VALUES (?, ?, ?, ?)",
                           (user_id, day, time, subject))
            conn.commit()
            bot.send_message(message.chat.id, f"Занятие добавлено: {subject} в {time} в день {day}.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Используй: /add_schedule [день] [время] [предмет]")


@bot.message_handler(commands=['my_schedule'])
def my_schedule(message):
    user_id = message.chat.id
    # Получаем расписание пользователя
    cursor.execute("SELECT day, time, subject FROM schedule WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()

    if results:
        schedule_msg = "Твое расписание:\n"
        for day, time, subject in results:
            schedule_msg += f"{day} - {time}: {subject}\n"
        bot.send_message(message.chat.id, schedule_msg)
    else:
        bot.send_message(message.chat.id, "У тебя нет расписания. Добавь его с помощью /add_schedule.")


@bot.message_handler(commands=['delete_schedule'])
def delete_schedule(message):
    try:
        # Парсим данные из команды
        _, day, time = message.text.split(' ', 2)
        user_id = message.chat.id
        # Удаляем занятие из базы данных
        cursor.execute("DELETE FROM schedule WHERE user_id = ? AND day = ? AND time = ?",
                       (user_id, day, time))
        conn.commit()
        bot.send_message(message.chat.id, f"Занятие в {time} в день {day} удалено.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Используй: /delete_schedule [день] [время]")


@bot.message_handler(commands=['random_fact'])
def random_fact(message):
    try:
        url = "https://ru.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url)
        data = response.json()
        title = data["title"]
        extract = data["extract"]
        page_url = f"https://ru.wikipedia.org/wiki/{title.replace(' ', '_')}"

        fact_message = f"🧠 **Случайный факт:**\n\n📌 *{title}*\n{extract}\n\n🔗 Подробнее: [Википедия]({page_url})"
        bot.send_message(message.chat.id, fact_message, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        bot.send_message(message.chat.id, "⚠ Ошибка при получении факта. Попробуй еще раз позже.")


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
                     "Я помогу тебе с учебными данными. Используй команды:\n/start - Начать\n/info - Получить свои данные\n/add_schedule [день] [время] [предмет] - Добавить расписание\n/my_schedule - Посмотреть расписание\n/delete_schedule [день] [время] - Удалить занятие\n/random_fact - Получить случайный факт\n/help - Список команд")


@bot.message_handler(func=lambda message: True)
def save_user_data(message):
    try:
        name, student_id = message.text.split()
        user_id = message.chat.id
        # Сохраняем данные в базу данных
        cursor.execute("INSERT OR REPLACE INTO users (user_id, name, student_id) VALUES (?, ?, ?)",
                       (user_id, name, student_id))
        conn.commit()
        bot.send_message(message.chat.id, "Данные успешно сохранены!")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Введите имя и ID через пробел.")


print("Бот запущен...")
bot.polling(none_stop=True)