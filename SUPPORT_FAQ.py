import json
import telebot
from telebot import types
from keyboard import support_faq_start_keyboard, faq_keyboard, instruction_keyboard, sup_check

API_TOKEN = "5193892343:AAFbVr6RY0a3MwzgEgBOTKHotR6wK4DkxDQ"
S_F_bot = telebot.TeleBot(API_TOKEN)


def save_data(data, file_name="S_F_users_bd.json"):
    with open(file_name, "w+", encoding="UTF-8") as f:
        json.dump(data, f, indent=4)


def load_data(file_name="S_F_users_bd.json"):
    with open(file_name, "r+", encoding="UTF-8") as f:
        data = json.load(f)
    return data


S_F_users_bd = load_data()


def new_user(user_id):
    global S_F_users_bd
    S_F_users_bd[user_id] = {
        "name": "",
        "is_question": False,
        "banned": False,
        "user_id": 0,
        "flag": 1,
        "mes_id": 0
    }






@S_F_bot.message_handler(commands=["start"])
def start(message):
    global S_F_users_bd
    if str(message.from_user.id) in S_F_users_bd:
        if not (S_F_users_bd[str(message.from_user.id)]["banned"]) and \
                S_F_users_bd[str(message.from_user.id)]["name"] != "":
            S_F_bot.send_message(chat_id=str(message.from_user.id),
                                 text="✍️Напишите Ваш вопрос(проблему) одним сообщением:\n❗️Вы можете отправлять "
                                      "только один вопрос на рассмотрение одномоментно!\n\nДля отправки следующего "
                                      "вопроса, Вам необходимо дождаться ответа оператора на ранее заданный вопрос "
                                      "или отметить ранее заданный вопрос как решенный.\nСтарайтесь сформулировать "
                                      "вопрос так, чтобы он был понятен не только Вам, задавайте вопрос одним "
                                      "сообщением, формулируйте вопрос наиболее полно, дополните ваш вопрос файлами, "
                                      "скринами и пр., если это необходимо для понимания сути Вашего вопроса.",
                                 reply_markup=support_faq_start_keyboard)
        elif not S_F_users_bd[str(message.from_user.id)]["banned"] and \
                S_F_users_bd[str(message.from_user.id)]["name"] == "":
            S_F_users_bd[str(message.from_user.id)]["flag"] = 1
            S_F_bot.send_message(chat_id=str(message.from_user.id),
                                 text="❗️❗️❗️ Напишите Ваше имя:\n          ❌Как в документах❌")
        else:
            ###Ответ забаненному пользователю
            pass
    else:
        new_user(str(message.from_user.id))
        S_F_bot.send_message(chat_id=str(message.from_user.id), text="❗️❗️❗️ Напишите Ваше имя:\n❌Как в документах❌")
        save_data(S_F_users_bd)


@S_F_bot.message_handler(content_types=["text"])
def reg(message):
    global S_F_users_bd
    if str(message.from_user.id) in S_F_users_bd:
        if not S_F_users_bd[str(message.from_user.id)]["banned"]:
            if S_F_users_bd[str(message.from_user.id)]["flag"] == 1:
                S_F_users_bd[str(message.from_user.id)]["name"] = str(message.text)
                S_F_users_bd[str(message.from_user.id)]["flag"] = 0
                S_F_bot.send_message(chat_id=str(message.from_user.id), text="✍️Напишите Ваш вопрос(проблему) "
                                                                             "одним сообщением:\n❗️Вы можете "
                                                                             "отправлять только один вопрос на "
                                                                             "рассмотрение одномоментно!\n\nДля "
                                                                             "отправки следующего вопроса, "
                                                                             "Вам необходимо дождаться ответа "
                                                                             "оператора на ранее заданный вопрос "
                                                                             "или отметить ранее заданный вопрос "
                                                                             "как решенный.\nСтарайтесь "
                                                                             "сформулировать вопрос так, "
                                                                             "чтобы он был понятен не только Вам, "
                                                                             "задавайте вопрос одним сообщением, "
                                                                             "формулируйте вопрос наиболее полно, "
                                                                             "дополните ваш вопрос файлами, "
                                                                             "скринами и пр., если это необходимо "
                                                                             "для понимания сути Вашего "
                                                                             "вопроса.",
                                     reply_markup=support_faq_start_keyboard)

            elif S_F_users_bd[str(message.from_user.id)]["flag"] == 2:
                S_F_bot.delete_message(chat_id=message.from_user.id,
                                       message_id=S_F_users_bd[str(message.from_user.id)]['mes_id'])
                S_F_bot.delete_message(chat_id=message.from_user.id,
                                       message_id=message.id)
                S_F_bot.send_message(chat_id=S_F_users_bd[str(message.from_user.id)]["user_id"],
                                     text=f"Пришел ответ от поддержки:\n{message.text}\n\n"
                                          f"Вы можете задать ещё один вопрос",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text='Хорошо!',
                                                                    callback_data="good")))
                S_F_users_bd[str(message.from_user.id)]["is_question"] = False
                S_F_users_bd[S_F_users_bd[str(message.from_user.id)]["user_id"]]["is_question"] = False
                S_F_bot.send_message(chat_id=message.from_user.id,
                                     text='Ответ был отправлен пользователю',
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text='Хорошо!',
                                                                    callback_data="good")))

            elif S_F_users_bd[str(message.from_user.id)]["flag"] != 1:
                if message.text == "Инструкции":
                    S_F_bot.send_message(chat_id=str(message.from_user.id), text="Инструкции",
                                         reply_markup=instruction_keyboard)
                elif message.text == "FAQ":
                    S_F_bot.send_message(chat_id=str(message.from_user.id), text="FAQ", reply_markup=faq_keyboard)
                else:
                    if not S_F_users_bd[str(message.from_user.id)]["is_question"]:

                        if len(message.text) < 10:
                            S_F_bot.send_message(chat_id=message.from_user.id,
                                                 text="ℹ️Старайтесь сформулировать вопрос так, чтобы он был понятен "
                                                      "не только Вам, задавайте вопрос одним сообщением, формулируйте вопрос "
                                                      "наиболее полно, дополните ваш вопрос файлами, скринами и пр., если это "
                                                      "необходимо для понимания сути Вашего вопроса.\n"
                                                      "❌Текст сообщения не может быть короче 10 символов!")
                        else:
                            S_F_users_bd[str(message.from_user.id)]["is_question"] = True
                            S_F_bot.send_message(chat_id=message.chat.id,
                                                 text="💌 Ваше сообщение передано специалисту!\n\n"
                                                      "Пожалуйста, ожидайте ответа!",
                                                 reply_to_message_id=message.message_id,
                                                 allow_sending_without_reply=True,
                                                 reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                                     types.InlineKeyboardButton(text="✅Вопрос решен ",
                                                                                callback_data="question_solved")))
                            S_F_bot.send_message(chat_id=686171972,
                                                 text=f"user_id: {message.from_user.id}\n"
                                                      f"username: {message.from_user.username}\n"
                                                      f"{message.text}",
                                                 reply_markup=sup_check)


                    else:
                        S_F_bot.send_message(chat_id=str(message.from_user.id),
                                             text="⛔️ Вы можете отправлять только один вопрос на рассмотрение!\nЕсли "
                                                  "Вы желаете переформулировать или дополнить отправленный вопрос или "
                                                  "задать новый вопрос, отметьте ранее заданный вопрос как "
                                                  "решенный.\nСтарайтесь сформулировать вопрос так, чтобы он был "
                                                  "понятен не только Вам, задавайте вопрос одним сообщением, "
                                                  "формулируйте вопрос наиболее полно, дополните ваш вопрос файлами, "
                                                  "скринами и пр., если это необходимо для понимания сути Вашего "
                                                  "вопроса.")

        else:
            ###Ответ забаненному пользователю
            pass
    save_data(S_F_users_bd)


@S_F_bot.callback_query_handler(func=lambda call: True)
def hand(call):
    global S_F_users_bd
    if call.data == "question_solved":
        S_F_users_bd[str(call.from_user.id)]["is_question"] = False
        S_F_bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                  text=call.message.json["text"])
        S_F_bot.send_message(chat_id=user_id, text="Ваш вопрос закрыт!")

    elif call.data == "sup_check":
        S_F_bot.delete_message(chat_id=user_id,
                               message_id=call.message.id)
        user_id = call.message.text.split(' ')[1].split('\n')[0]
        S_F_users_bd[str(call.from_user.id)]["user_id"] = user_id
        r = S_F_bot.send_message(chat_id=user_id,
                                 text='Напишите ответ: ')
        S_F_users_bd[str(call.from_user.id)]["mes_id"] = r.id
        S_F_users_bd[str(call.from_user.id)]["flag"] = 2

    elif call.data == "sup_ban":
        user_id = call.message.text.split(' ')[1].split('\n')[0]
        S_F_users_bd[str(call.from_user.id)]["user_id"] = user_id
        S_F_bot.send_message(chat_id=user_id,
                             text='Напишите причину: ')

    elif call.data == "good":
        S_F_bot.delete_message(chat_id=user_id,
                               message_id=call.message.id)


if __name__ == "__main__":
    S_F_bot.polling(True)
