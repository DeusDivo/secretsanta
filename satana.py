import telebot
import random
import logging

# Вставьте токен вашего бота
BOT_TOKEN = ''
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для участников (id пользователя: имя)
participants = {}

# Настройка логирования
logging.basicConfig(
    filename='santa_game.log',  # Имя файла для логов
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщений
)

# Функция проверки, является ли пользователь администратором группы
def is_admin(chat_id, user_id):
    try:
        chat_admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in chat_admins)
    except Exception as e:
        logging.error(f"Ошибка проверки администратора: {e}")
        return False

# Команда для начала работы бота (доступна только админам)
@bot.message_handler(commands=['santastart'])
def santastart(message):
    if is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "Привет! Я бот для игры в Тайного Санту! "
                              "Напишите /join, чтобы участвовать. Когда все участники добавлены, напишите /go.")
        bot.reply_to(message, "Перед игрой убедитесь, что вы отправили мне @gogogoraszyn_bot команду /start в личные сообщения, иначе я не смогу сообщить вам ваш результат!")
    else:
        bot.reply_to(message, "Эта команда доступна только администраторам группы.")

# Команда для добавления участника
@bot.message_handler(commands=['join'])
def join(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if user_id not in participants:
        participants[user_id] = user_name
        bot.reply_to(message, f"{user_name}, вы добавлены в игру!")
        logging.info(f"Участник добавлен: {user_name} (ID: {user_id})")
    else:
        bot.reply_to(message, f"{user_name}, вы уже участвуете!")
# Команда для запуска игры (доступна только админам)
@bot.message_handler(commands=['go'])
def go(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "Эта команда доступна только администраторам группы.")
        return

    if len(participants) < 2:
        bot.reply_to(message, "Недостаточно участников для игры. Нужно минимум 2 человека.")
        logging.warning("Попытка запуска игры при недостаточном количестве участников.")
        return

    # Генерация пар
    givers = list(participants.keys())
    receivers = list(participants.keys())
    random.shuffle(receivers)

    # Убедимся, что никто не получает себя
    while any(giver == receiver for giver, receiver in zip(givers, receivers)):
        random.shuffle(receivers)

    # Рассылка пар
    for giver, receiver in zip(givers, receivers):
        giver_name = participants[giver]
        receiver_name = participants[receiver]

        try:
            bot.send_message(giver, f"Привет, {giver_name}! ты Тайный Санта для: {receiver_name} 🎁")
            logging.info(f"{giver_name} (ID: {giver}) -> {receiver_name} (ID: {receiver})")
        except telebot.apihelper.ApiTelegramException as e:
            if "403" in str(e):
                bot.send_message(message.chat.id, f"{giver_name}, я не смог отправить вам личное сообщение. Напишите мне команду /start и запустите игру заново.")
                logging.warning(f"Не удалось отправить сообщение {giver_name} (ID: {giver}): {e}")
            else:
                bot.send_message(message.chat.id, f"Ошибка при отправке сообщения {giver_name}.")
                logging.error(f"Ошибка при отправке сообщения {giver_name} (ID: {giver}): {e}")

    # Очистка списка участников
    participants.clear()
    bot.reply_to(message, "Игра завершена! 🎉 Все получили свои пары в личных сообщениях. Напоминаю что сумма на подарок состовляет 50 злот Удачи и хороших подарков!🎁")
    logging.info("Игра завершена. Участники очищены.")

# Запуск бота
bot.polling()
