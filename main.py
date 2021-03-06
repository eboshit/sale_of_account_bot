import json
import telebot
from telebot import types
import re
import datetime
import pickle
from multiprocessing import *
import schedule
import time
from datetime import timedelta
from flask import Flask, request
import ssl
from keyboard import *
from classes import *
from config import *

bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()
bot.delete_webhook()

app = Flask(__name__)
task1 = Task()
pay_keyboard_list = load_data(file_name="payment_methods.json")
pay_keyboard = list_to_keyboard(pay_keyboard_list)
pay_keyboard_for_admin = list_to_keyboard(pay_keyboard_list, "_change").add(
    types.InlineKeyboardButton(text="Назад", callback_data="payments"))


@app.route(f'/{API_TOKEN}', methods=["POST", "GET"])
def handle():
    json_string = request.get_data().decode('utf-8')
    save_data(json_string, 'json_string.json')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "ok", 200


@app.route(f'/', methods=["POST", "GET"])
def h():
    return "HELLO"


###установка дефолтных значений админу
def default_admin_value(admin: Admin) -> None:
    admin.telegraph_name = ''
    admin.telegraph_url = ''
    admin.telegraph_action = 0
    admin.flag = 4
    admin.telegraph_name = ''
    admin.telegraph_url = ''
    admin.telegraph_action = 0

    admin.edit_acc_name = ""
    admin.edit_acc_first_mes = ""
    admin.edit_acc_second_mes = ""
    admin.edit_acc_third_mes = ""
    admin.edit_acc_price = 0

    admin.post_mail_text = ""
    admin.post_mail_text_button = ""
    admin.post_mail_url = ""
    admin.post_mail_action = 0
    admin.post_mail_disable_notification = True

    admin.channel_sale_text = ""
    admin.channel_sale_button = []
    admin.channel_sale_count = -1

    admin.procent_name = []
    admin.procent_lvl_1 = 0
    admin.procent_lvl_2 = 0
    admin.edit_period = 0
    admin.edit_main_mes = ""


###Проверка на подписку на каналы
def checking_for_subscription(user_id: int) -> bool:  # Оставить
    try:
        m = bot.get_chat_member(chat_id='-1001695261290', user_id=user_id)
        r = bot.get_chat_member(chat_id='-1001558866443', user_id=user_id)
        if m.status != 'left' and r.status != 'left':
            return True
        else:
            return False
    except:
        return False


###изменение клавиатуры настройки(телеграф) для админа # V
def edit_button_instr(admin: int, name: str, url: str, action: int,
                      message_id: int | None) -> None:  # 0-изменить url кнопки; 1-добавить кнопку # 2-удалить кнопку

    try:
        with open("file.pkl", "rb") as fp:
            a = pickle.load(fp)
        instruction_keyboard = pickle.loads(a["instruction_keyboard"])
        if action == 0:
            for i in range(len(instruction_keyboard.keyboard)):
                if instruction_keyboard.keyboard[i][0].text == name:
                    instruction_keyboard.keyboard[i][0].text = name
                    instruction_keyboard.keyboard[i][0].url = url
                    break
            else:
                bot.edit_message_text(chat_id=admin,
                                      message_id=message_id,
                                      text='Такая кнопка не нашлась\nПопробуйте ещё раз',
                                      reply_markup=instr_keyboard)

        elif action == 1:
            instruction_keyboard.keyboard.append([types.InlineKeyboardButton(text=name, url=url)])
        elif action == 2:
            for i in range(len(instruction_keyboard.keyboard)):
                if instruction_keyboard.keyboard[i][0].text == name:
                    del instruction_keyboard.keyboard[i]
                    break
            else:
                bot.send_message(chat_id=admin,
                                 text='Такая кнопка не нашлась\nПопробуйте ещё раз',
                                 reply_markup=instr_keyboard)
        serialized = pickle.dumps(instruction_keyboard)
        data = {'instruction_keyboard': serialized}
        with open("file.pkl", "wb+") as fp:
            pickle.dump(data, fp)
        instruction_keyboard.keyboard.append([types.InlineKeyboardButton(text="Вернуться к выбору действия",
                                                                         callback_data='edit_button_instr')])
        instruction_keyboard.keyboard.append([types.InlineKeyboardButton(text="Вернуться в меню функций админа",
                                                                         callback_data='back_main_admin')])
        bot.send_message(chat_id=admin,
                         text="Клавиатура теперь выглядит так:",
                         reply_markup=instruction_keyboard)
    except:
        bot.send_message(chat_id=admin,
                         text="Произошла ошибка\n Возможно ошибка в url, которое Вы написали",
                         reply_markup=admin_keyboard)


###отправка и удаление главного сообщения в "Актуальные верификации"
def sending_and_deleting_main_message():  # V Оставить
    set_main_message = load_data("main_mes.json")
    try:
        bot.delete_message(chat_id=actual_verify_channel, message_id=set_main_message["message_id"])
    except:
        pass
    r = bot.send_message(chat_id=actual_verify_channel, text=f"{set_main_message['text']}")
    set_main_message["message_id"] = r.id
    save_data(set_main_message, "main_mes.json")


###отправка сообщения по времени
class P_schedule():  # Class для работы с schedule
    def start_schedule(self):
        set_main_message = load_data("main_mes.json")
        schedule.every(set_main_message["period"]).minutes.do(sending_and_deleting_main_message)

        while True:  # Запуск цикла
            schedule.run_pending()
            time.sleep(1)


class periodic_main_mes:
    p0 = Process(target=P_schedule.start_schedule, args=())

    def start_process(self):
        self.p0 = Process(target=P_schedule.start_schedule, args=())
        self.p0.start()

    def stop_process(self):
        self.p0.terminate()


# /start
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user = users.get_elem(user_id)
    if message.from_user.username:
        ###Если пользователя нет в БД
        if not user:
            ###Если пользователь перешёл по реферральной ссылке
            if "start" in message.text and len(str(message.text).split(' ')) == 2 \
                    and str(message.text).split(' ')[-1] in users.data and \
                    str(message.text).split(' ')[-1] != str(user_id):
                ref_boss_1 = int(str(message.text).split(' ')[-1])
                ref_boss_2 = users.get_elem(user_id).referral_bosses[0]
                users.add_elem(user_id, ref_boss=ref_boss_1, ref_boss_2=ref_boss_2)
            ###Иначе
            else:
                users.add_elem(user_id)
            user = users.get_elem(user_id)
            r = bot.send_message(chat_id=message.from_user.id,
                                 text=text_ancet,
                                 parse_mode='Markdown')
            user.bot_messageId = r.id
            time = datetime.datetime.today().strftime("%Y.%m.%d в %H:%M")
            user.registration_date = time
        ###Если пользователь забанен
        elif not user.status:
            bot.send_message(chat_id=user_id,
                             text="❌❌❌\nВаш профиль, в нашем сервисе, ЗАБЛОКИРОВАН!\n⛔️⛔️⛔️\n-------------\n<strong>O "
                                  "причине блокировки "
                                  "читайте комментарий.\nКомментарий: Напишите в бот поддержки @VerifSupportBot для "
                                  "проверки личности.</strong>\n "
                                  "-------------\n⚠️ Если Вы желаете обжаловать решение о блокировке, пишите в бот "
                                  "поддержки, дайте развёрнутое "
                                  " объяснение ситуации и напишите почему Вы считаете, что Вас нужно разблокировать.",
                             parse_mode="HTML")
        ###Если пользователь полностью зарегистрирован
        elif user.full_registered:
            if checking_for_subscription(message.from_user.id):
                user.flag = 0
                ###Если пользователь на изменении ФИО
                if user.changing_complete_name:
                    user.complete_name = []
                    user.flag = 25
                    r = bot.send_message(chat_id=user_id,
                                         text="Изменение ФИО\n🖌 Введите Вашу фамилию на английском ниже ⬇️\n"
                                              "Например: Taylor / Sergeevsky")
                ###Если пользователь на изменении анкеты(страна+документы)
                elif user.changing_country_type_document:
                    user.flag = 25
                    user.document_types = []
                    r = bot.send_message(chat_id=user_id,
                                         text="Выберите страну ваших документов:",
                                         reply_markup=country_keyboard)
                ###Если пользователь на изменении способа выплат
                elif user.changing_payment:
                    user.flag = 3
                    r = bot.send_message(chat_id=user_id,
                                         text="Выберите способ выплат:\n*Будьте внимательны, "
                                              "замена реквизитов делается только вручную!",
                                         reply_markup=pay_keyboard)
                ###Если админ
                elif user_id in admins.data:
                    admin = admins.get_elem(user_id)
                    user.flag = 0
                    admin.flag = 4
                    r = bot.send_message(chat_id=user_id,
                                         text=f"{start_text}",
                                         reply_markup=start_admin_keyboard,
                                         parse_mode='Markdown')
                ###Если простой пользователь
                else:
                    r = bot.send_message(chat_id=user_id,
                                         text=f"{start_text}",
                                         reply_markup=start_keyboard,
                                         parse_mode='Markdown')
                user.bot_messageId = r.id
            else:
                bot.send_message(chat_id=message.from_user.id,
                                 text="🙌 Вы в одном шаге от начала работы\nПодпишитесь:\n♻️ Актуальные верификации "
                                      "- узнай о работе и оплате\n📚 Правила и условия работы с ботом\nИ нажмите кнопку "
                                      "🟢 Начать работу!",
                                 reply_markup=subcribe_keyboard)
        ###Если не прошёл полную регистрацию, но есть в БД
        else:
            user.flag = 25
            user.status = True
            user.complete_name = []
            user.payment_method = ""
            user.payment_account = ""
            user.countries = []
            user.document_types = []
            user.balance = 0
            user.earnings = 0
            user.date_edit_payment = ""
            r = bot.send_message(chat_id=message.from_user.id,
                                 text=text_ancet,
                                 parse_mode='Markdown')
            user.bot_messageId = r.id
        save_object(users, "users.pkl")
    ###Проверка username пользователя
    else:
        bot.send_message(chat_id=user_id,
                         text="ОШИБКА!\nУкажите"
                              " @username в Вашем профиле Telegram, чтобы продолжить работу с ботом!")


@bot.message_handler(content_types=["text"])  # , func=lambda message: users.get_elem(message.from_user.id).flag == 4 )
def reg(message):
    user_id = message.from_user.id
    user = users.get_elem(user_id)
    if message.from_user.username:
        if user:
            if user.status:
                if message.text == "💤 Перезагрузка":
                    if user_id in admins.data:
                        r = bot.send_message(chat_id=user_id,
                                             text=f"{start_text}",
                                             reply_markup=start_admin_keyboard,
                                             parse_mode='Markdown')
                    else:
                        r = bot.send_message(chat_id=user_id,
                                             text=f"{start_text}",
                                             reply_markup=start_keyboard,
                                             parse_mode='Markdown')
                    user.bot_messageId = r.id
                ###сохранение фамилии
                elif len(user.complete_name) == 0:
                    if user.flag != 27:
                        if re.match("^[ABCDEFGHIJKLMNOPQRSTUVWXYZ]", message.text.upper()):
                            if " " in message.text:
                                bot.send_message(chat_id=user_id,
                                                 text="Неправильно введено. Пишите без пробелов")
                            else:
                                resp_keyboard = types.InlineKeyboardMarkup().add(
                                    types.InlineKeyboardButton(text="ПОДТВЕРДИТЬ",
                                                               callback_data="next_step_in_reg")).add(
                                    types.InlineKeyboardButton(text="ИЗМЕНИТЬ",
                                                               callback_data="edit_complete_name_element"))
                                if not user.full_registered:
                                    resp_keyboard.add(
                                        types.InlineKeyboardButton(text="ОТМЕНА", callback_data="cancel_fio"))
                                user.flag = 27
                                user.complete_name.append(message.text)
                                bot.delete_message(chat_id=user_id,
                                                   message_id=user.bot_messageId)
                                bot.delete_message(chat_id=user_id,
                                                   message_id=message.message_id)
                                bot.send_message(chat_id=user_id,
                                                 text=f"Вы ввели {message.text}",
                                                 reply_markup=resp_keyboard)

                        else:
                            bot.send_message(chat_id=user_id,
                                             text="Ошибка: для начала заполните профиль латинскими буквами! "
                                                  "Если бот не работает нажмите /start для перезапуска")
                    else:
                        bot.delete_message(chat_id=user_id, message_id=message.id)

                ###сохранение имени
                elif len(user.complete_name) == 1:
                    if user.flag != 27:
                        if re.match("^[ABCDEFGHIJKLMNOPQRSTUVWXYZ]", message.text.upper()):
                            if " " in message.text:
                                bot.send_message(chat_id=user_id,
                                                 text="Неправильно введено. Пишите без пробелов")
                            else:
                                resp_keyboard = types.InlineKeyboardMarkup().add(
                                    types.InlineKeyboardButton(text="ПОДТВЕРДИТЬ",
                                                               callback_data="next_step_in_reg")).add(
                                    types.InlineKeyboardButton(text="ИЗМЕНИТЬ",
                                                               callback_data="edit_complete_name_element"))
                                if not user.full_registered:
                                    resp_keyboard.add(
                                        types.InlineKeyboardButton(text="ОТМЕНА", callback_data="cancel_fio"))
                                user.flag = 27
                                user.complete_name.append(message.text)
                                bot.delete_message(chat_id=user_id,
                                                   message_id=user.bot_messageId)
                                bot.delete_message(chat_id=user_id,
                                                   message_id=message.message_id)
                                bot.send_message(chat_id=user_id,
                                                 text=f'Вы ввели {user.complete_name[0]} {message.text}',
                                                 reply_markup=resp_keyboard)
                        else:
                            bot.send_message(chat_id=user_id,
                                             text="Ошибка: для начала заполните профиль латинскими буквами! "
                                                  "Если бот не работает нажмите /start для перезапуска")
                    else:
                        bot.delete_message(chat_id=user_id, message_id=message.id)

                ###сохранение отчества
                elif len(user.complete_name) == 2:
                    if user.flag != 27:
                        if re.match("^[ABCDEFGHIJKLMNOPQRSTUVWXYZ]", message.text.upper()):
                            if " " in message.text:
                                bot.send_message(chat_id=user_id,
                                                 text="Неправильно введено. Пишите без пробелов")
                            else:
                                resp_keyboard = types.InlineKeyboardMarkup().add(
                                    types.InlineKeyboardButton(text="ПОДТВЕРДИТЬ",
                                                               callback_data="next_step_in_reg")).add(
                                    types.InlineKeyboardButton(text="ИЗМЕНИТЬ",
                                                               callback_data="edit_complete_name_element"))
                                if not user.full_registered:
                                    resp_keyboard.add(
                                        types.InlineKeyboardButton(text="ОТМЕНА", callback_data="cancel_fio"))
                                user.flag = 27
                                user.complete_name.append(message.text)
                                bot.delete_message(chat_id=user_id,
                                                   message_id=user.bot_messageId)
                                bot.delete_message(chat_id=user_id, message_id=message.message_id)
                                bot.send_message(chat_id=user_id,
                                                 text=f'Вы ввели {user.complete_name[0]} {user.complete_name[1]} '
                                                      f'{message.text}',
                                                 reply_markup=resp_keyboard)

                        else:
                            bot.send_message(chat_id=user_id,
                                             text="Ошибка: для начала заполните профиль латинскими буквами! "
                                                  "Если бот не работает нажмите /start для перезапуска")
                    else:
                        bot.delete_message(chat_id=user_id, message_id=message.id)

                ###сохранение реквизитов выплаты
                ###сохранение реквизитов выплаты
                elif user.flag == 2 or user.flag == 3:
                    if user.flag != 28 and user.flag != 29:
                        # if message.text.isdigit():
                        bot.delete_message(chat_id=user_id,
                                           message_id=user.bot_messageId)
                        user.payment_account = message.text
                        bot.send_message(chat_id=user_id,
                                         text=f"Вы ввели: {message.text}",
                                         reply_markup=filling_user_payment_acc_keyboard)

                        if user.flag != 3:
                            user.flag = 28
                        else:
                            user.flag = 29

                        # else:
                        # bot.send_message(chat_id=message.from_user.id,
                        #                 text="Неверно введено!\nВведите как указано в примере")
                    else:
                        bot.delete_message(chat_id=user_id, message_id=message.id)

                elif message.text == '📕 Как пользоваться ботом?':
                    if user_id in admins.data:
                        bot.send_message(chat_id=user_id,
                                         text="1. Заполняете свой профиль.\n2. Делаете актуальные аккаунты, "
                                              "по условиями на канале.\n3. Загружаете аккаунт бот, получаете выплату!\n"
                                              "`Так-же действует партнерская программа!`",
                                         reply_markup=start_admin_keyboard,
                                         parse_mode="Markdown")
                    else:
                        bot.send_message(chat_id=user_id,
                                         text="1. Заполняете свой профиль.\n2. Делаете актуальные аккаунты, "
                                              "по условиями на канале.\n3. Загружаете аккаунт бот, получаете выплату!\n"
                                              "`Так-же действует партнерская программа!`",
                                         reply_markup=start_keyboard,
                                         parse_mode="Markdown")

                elif message.text == '✅ Загрузить аккаунт':

                    bot.send_message(chat_id=user_id,
                                     text="✅ Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале, в будни"
                                          " с 11:00 до 19:00 МСК.\nВыберите сервис:",
                                     reply_markup=services_accounts.keyboard_init(user))

                elif message.text == '♻️ Загруженные аккаунты':
                    if len(user.accounts_check) != 0:
                        bot.send_message(chat_id=user_id,
                                         text=f"📍 Ваши загруженные аккаунты:\n"
                                              f"Здесь вы можете изменить/удалить данные аккаунтов "
                                              f"отправленных Вами на проверку!",
                                         reply_markup=user.keyboard_with_accs())
                    else:
                        bot.send_message(chat_id=user_id,
                                         text=f"Ваши загруженные аккаунты\nЗдесь вы можете изменить/удалить "
                                              f"данные аккаунтов отправленных Вами на проверку!")

                elif message.text == '📊 Статистика':
                    count_no_verified = user.count_no_verified_accs
                    count_verified_paid = user.count_verified_paid_accs
                    count_verified_rejected = user.count_verified_rejected_accs
                    if user_id in admins.data:
                        bot.send_message(chat_id=user_id,
                                         text=f"Ваша статистика:\nКоличество не проверенных: {count_no_verified}\n"
                                              f"Количество проверенных и оплаченных: {count_verified_paid}\n"
                                              f"Количество проверенных и отклоненных: {count_verified_rejected}",
                                         reply_markup=start_admin_keyboard)
                    else:
                        bot.send_message(chat_id=user_id,
                                         text=f"Ваша статистика:\nКоличество не проверенных: {count_no_verified}\n"
                                              f"Количество проверенных и оплаченных: {count_verified_paid}\n"
                                              f"Количество проверенных и отклоненных: {count_verified_rejected}",
                                         reply_markup=start_keyboard)

                elif message.text == '👤 Профиль':
                    user_name = message.from_user.username
                    if message.from_user.first_name is None:
                        first_name = ''
                    else:
                        first_name = str(message.from_user.first_name) + ' '
                    if message.from_user.last_name is None:
                        last_name = ''
                    else:
                        last_name = str(message.from_user.last_name)
                    registration_date = user.registration_date

                    if user.payment_method == "QIWI":
                        requisites = user.payment_account + " (Qiwi 📲)"
                    else:
                        requisites = user.payment_account
                    country_docs = user.get_str_countries_and_document_types()
                    full_name = user.complete_name[0] + " " + user.complete_name[1] + " " + user.complete_name[2]
                    user_balance = user.balance
                    r = bot.send_message(chat_id=user_id,
                                         text=f"`{first_name + last_name}`, это Ваш профиль!\n"
                                              f"🆔 Ваш id: `{user_id}`\n"
                                              f"👤 Ваш логин: `@{user_name}`\n"
                                              f"📝 ФИО указанные в анкете: `{full_name}`\n"
                                              f"✅ Дата регистрации: *{registration_date}*\n"
                                              f"🌍 Страна: *{country_docs['countries']}*\n"
                                              f"📂 Документы: *{country_docs['document_types']}*\n"
                                              f"💳 Реквизиты выплат: `{requisites}`\n"
                                              f"💰Ваш баланс: *{user_balance} руб*",
                                         reply_markup=profile_keyboard,
                                         parse_mode="Markdown")
                    user.bot_messageId = r.id

                elif message.text == '📣 Партнерская программа':
                    personal_link = user.referral_link
                    status = user.referral_status
                    invited_users = user.invited_users()
                    personal_balance = user.balance
                    reward_lvl_1 = user.reward_lvl_1
                    reward_lvl_2 = user.reward_lvl_2
                    bot.send_message(chat_id=message.from_user.id,
                                     text=f"Партнерская программа:\n\n"
                                          f"Вы можете приглашать новых пользователей и "
                                          f"получать вознаграждения за оплаченные"
                                          f" аккаунты ваших рефералов\nУсловия участия в партнерской программе читайте"
                                          f" [ЗДЕСЬ]({rules_link})\n\n🔗 "
                                          f"Ваша ссылка для приглашения людей:\n`{personal_link}`\n"
                                          f"🔰 Ваш статус: *{status}*\n💵"
                                          f"Вознаграждение по уровням в статусе *{status}*:\n"
                                          f"Уровень 1 - {reward_lvl_1}%\n"
                                          f"Уровень 2 - {reward_lvl_2}%\n\n"
                                          f"Вы пригласили (по уровням):\n"
                                          f"👤Уровень 1 - {invited_users['lvl1']}\n"
                                          f"👤Уровень 2 - {invited_users['lvl2']} \n\n"
                                          f"Ваш баланс - {personal_balance} руб",
                                     reply_markup=sup_program_keyboard,
                                     parse_mode='MarkDown')

                elif message.text == '📚 Support & FAQ':
                    if user_id in admins.data:

                        bot.send_message(chat_id=user_id,
                                         text=f"👩 Контакты:\n\n"
                                              f"По всем вопросам обращайтесь в [БОТА ПОДДЕРЖКИ]({support_bot_link}) 🤖\n"
                                              f"Правила и ссылка на канал З[ДЕСЬ]({sup_rules_link}) 👉📃",
                                         reply_markup=start_admin_keyboard,
                                         parse_mode='Markdown')
                    else:
                        bot.send_message(chat_id=user_id,
                                         text=f"👩 Контакты:\n\n"
                                              f"По всем вопросам обращайтесь в [БОТА ПОДДЕРЖКИ]({support_bot_link}) 🤖\n"
                                              f"Правила и ссылка на канал З[ДЕСЬ]({sup_rules_link}) 👉📃",
                                         reply_markup=start_keyboard,
                                         parse_mode='Markdown')

                elif message.text == "Задания":
                    bot.send_message(chat_id=user_id,
                                     text='Список заданий',
                                     reply_markup=all_tasks.get_choice_tasks_keyboard())

                ###ввод почты
                elif user.flag == 20:
                    if "@gmail.com" in message.text and len(message.text) > 10:
                        user.cur_acc["Email"] = str(message.text)
                        if services_accounts.get_elem(user.cur_acc["key"]).third_mes != "":
                            user.flag = 22
                            bot.send_message(chat_id=user_id,
                                             text=f"ℹ️ Напишите название сервиса:\n"
                                                  f"пишите без http и www, пишите так domen.com",
                                             reply_markup=keyboard_loading_accs)
                        else:
                            user.flag = 21
                            bot.send_message(chat_id=user_id,
                                             text=f"🔑 Введите пароль, в поле ввода и отправьте в бот:\n"
                                                  f"(пароль должен быть одинаковый на почте и сервисах)")
                    else:
                        bot.send_message(chat_id=user_id,
                                         text="ОШИБКА: Не верный Email!",
                                         reply_markup=keyboard_loading_accs)
                ###ввод пароля
                elif user.flag == 21:
                    user.flag = 23
                    user.cur_acc["password"] = str(message.text)
                    if services_accounts.get_elem(user.cur_acc["key"]).third_mes != "":
                        bot.send_message(chat_id=user_id,
                                         text=f"{services_accounts.data[user.cur_acc['key']].third_mes}",
                                         reply_markup=keyboard_loading_accs, disable_web_page_preview=True)
                    else:
                        bot.send_message(chat_id=user_id,
                                         text=f"{services_accounts.data[user.cur_acc['key']].second_mes}",
                                         reply_markup=keyboard_loading_accs, disable_web_page_preview=True)
                ###ввод домена
                elif user.flag == 22:
                    user.cur_acc["service_name"] = str(message.text)
                    user.flag = 21
                    bot.send_message(chat_id=user_id,
                                     text="🔑 Введите пароль, в поле ввода и отправьте в бот:\n"
                                          "(пароль должен быть одинаковый на почте и сервисах)",
                                     reply_markup=keyboard_loading_accs)
                ###ввод остальных данных
                elif user.flag == 23:
                    user.cur_acc["info"] = str(message.text)
                    if "service_name" in user.cur_acc:
                        ser_name = user.cur_acc["service_name"]
                    else:
                        ser_name = user.cur_acc["key"]
                    bot.send_message(chat_id=user_id,
                                     text=f"Вы подтверждаете внесение данных?\n"
                                          f"Сервис: {ser_name}\n"
                                          f"Email: {user.cur_acc['Email']}\n"
                                          f"{user.cur_acc['info']}",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text="Отмена 🛑", callback_data="Отмена"),
                                         types.InlineKeyboardButton(text="Подтвердить",
                                                                    callback_data="Подтвердить")).add(
                                         types.InlineKeyboardButton(text="Главное меню 🏡",
                                                                    callback_data="Главное меню 🏡")))
                ###изменение данных отправленных на проверку
                elif user.flag == 24:
                    user.accounts_check[user.chosen_acc[0]]["info"] = str(message.text)
                    if user_id in admins.data:
                        bot.send_message(chat_id=user_id,
                                         text="Данные сохранены", reply_markup=start_admin_keyboard)
                    else:
                        bot.send_message(chat_id=user_id,
                                         text="Данные сохранены", reply_markup=start_keyboard)
                    bot.send_message(chat_id=user_id,
                                     text=f"Ваши загруженные аккаунты\n"
                                          f"Здесь вы можете изменить/удалить данные аккаунтов"
                                          f" отправленных Вами на проверку!",
                                     reply_markup=user.keyboard_with_accs())

                elif user.flag == 38:
                    user.tasks["answer"] = message.text
                    bot.send_message(chat_id=user_id,
                                     text=f"Ваш ответ: {message.text}",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text='Подтвердить',
                                                                    callback_data="send_task_manager"),
                                         types.InlineKeyboardButton(text="изменить",
                                                                    callback_data="change_task_user")
                                     ))
                    user.flag = 0

                ###блок админа
                elif user_id in admins.data:
                    if message.text == 'Админ панель':
                        bot.send_message(chat_id=user_id,
                                         text='Вы попали в админ панель!\n'
                                              'Доступные функции:',
                                         reply_markup=keyboards_for_admins[admins.get_elem(user_id).admin_lvl])

                else:
                    if user_id in users.data:
                        if user_id in admins.data:
                            bot.send_message(chat_id=user_id,
                                             text="Я хоть и искусственный интеллект, но только начинающий своё "
                                                  "обучение, пока я не знаю ответ на ваш вопрос, но я обязательно "
                                                  "исправлюсь!\nСообщения которые вы отправляете боту, вне алгоритма "
                                                  "отправки заявки, не получает администрация сервиса, на такие "
                                                  "сообщения здесь отвечает только бот, если у вас есть вопросы, "
                                                  "задавайте их пожалуйста в бота поддержки ",
                                             reply_markup=start_admin_keyboard)
                        else:
                            bot.send_message(chat_id=user_id,
                                             text="Я хоть и искусственный интеллект, но только начинающий своё "
                                                  "обучение, пока я не знаю ответ на ваш вопрос, но я обязательно "
                                                  "исправлюсь!\nСообщения которые вы отправляете боту, вне алгоритма "
                                                  "отправки заявки, не получает администрация сервиса, на такие "
                                                  "сообщения здесь отвечает только бот, если у вас есть вопросы, "
                                                  "задавайте их пожалуйста в бота поддержки ",
                                             reply_markup=start_keyboard)
                save_object(users, "users.pkl")
            else:
                bot.send_message(chat_id=user_id,
                                 text="❌❌❌\nВаш профиль, в нашем сервисе, ЗАБЛОКИРОВАН!\n"
                                      "⛔️⛔️⛔️\n-------------\n<strong>O причине блокировки "
                                      "читайте комментарий.\nКомментарий: Напишите в бот поддержки @VerifSupportBot "
                                      "для проверки личности.</strong>\n-------------\n⚠️ Если Вы желаете обжаловать "
                                      "решение о блокировке, пишите в бот поддержки, дайте развёрнутое объяснение"
                                      " ситуации и напишите почему Вы считаете, что Вас нужно разблокировать.",
                                 parse_mode="HTML")
        else:
            bot.send_message(chat_id=user_id,
                             text="Напишите /start")
    ###Проверка username пользователя
    else:
        bot.send_message(chat_id=user_id,
                         text="ОШИБКА!\nУкажите"
                              " @username в Вашем профиле Telegram, чтобы продолжить работу с ботом!")


###условие другое: проверка на флаг
@bot.callback_query_handler(func=lambda call: True)
def hand(call):
    global message_1, all_tasks
    user_id = call.from_user.id
    user = users.get_elem(user_id)
    if user_id in users.data:
        if call.from_user.username:
            if users.get_user_status(user_id):
                if call.from_user.username not in list_username:
                    list_username[call.from_user.username] = str(user_id)
                    save_data(list_username, "username.json")
                ###измениние клавиатуры для органичения доступа
                if call.data == "-":
                    '''bot.forward_message(chat_id=user_id,
                                        from_chat_id=user_id,
                                        message_id=call.message.id)'''
                    bot.answer_callback_query(callback_query_id=call.id, text="Действие больше недоступно",
                                              show_alert=True)
                elif user.flag not in [25, 27, 43, 46, 47, 48] and call.message.json["chat"]['id'] != -1001516204936:
                    bot.edit_message_text(message_id=call.message.id,
                                          chat_id=user_id,
                                          text=call.message.text,
                                          reply_markup=editing_call_keyboard(
                                              call.message.json["reply_markup"]["inline_keyboard"]))

                if call.data == "back_pay":
                    user.payment_method = ""
                    bot.edit_message_text(message_id=call.message.id,
                                          chat_id=user_id,
                                          text="Выберите способ выплат:\n*Будьте внимательны, замена "
                                               "реквизитов делается только вручную!",
                                          reply_markup=pay_keyboard)

                elif str(call.data) in pay_keyboard_list:
                    if user.payment_method == '' or user.flag in [2, 3]:
                        r = bot.send_message(chat_id=user_id,
                                             text=f'{pay_keyboard_list[str(call.data)]}',
                                             reply_markup=back_pay)

                        user.bot_messageId = r.id
                        user.payment_method = call.data
                        if user.flag != 3:
                            user.flag = 2
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text='Это действие уже недоступно',
                                                  show_alert=True)

                ###Выбор стран
                elif call.data in country:
                    if f"{call.data}" in user.countries:
                        ind = user.countries.index(f"{call.data}")
                        del user.countries[ind]
                        bot.answer_callback_query(callback_query_id=call.id, text="Выбор снят!",
                                                  show_alert=False)
                    else:
                        user.countries.append(f"{call.data}")
                        bot.answer_callback_query(callback_query_id=call.id, text="Выбрано!",
                                                  show_alert=False)
                    if len(user.countries) == 0:

                        bot.edit_message_text(message_id=call.message.id,
                                              chat_id=user_id,
                                              text=f'Выберите страну ваших документов:',
                                              reply_markup=country_keyboard)
                    else:
                        print(user.__dict__)
                        txt = ''
                        for i in user.countries:
                            txt += i + "\n"

                        r = bot.edit_message_text(message_id=call.message.id,
                                                  chat_id=user_id,
                                                  text=f'Вы выбрали:\n{txt}',
                                                  reply_markup=country_keyboard)

                        user.bot_messageId = r.id

                ###Сохранение выбора стран
                elif call.data == 'save':
                    if len(user.countries) == 0:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Вы не выбрали ни одной страны! "
                                                       "Выберите страну ваших документов:",
                                                  show_alert=True)
                    else:
                        bot.delete_message(chat_id=user_id,
                                           message_id=user.bot_messageId)
                        bot.send_message(chat_id=user_id,
                                         text="Выберите документы, которые у вас есть:",
                                         reply_markup=document_keyboard)

                ###Выбор типа документов
                elif call.data in types_documents:
                    if f"{call.data}" in user.document_types:
                        ind = user.document_types.index(f"{call.data}")
                        del user.document_types[ind]
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Выбор снят!",
                                                  show_alert=False)
                    else:
                        user.document_types.append(f"{call.data}")
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Выбрано!",
                                                  show_alert=False)
                    if len(user.document_types) == 0:
                        bot.edit_message_text(message_id=call.message.id,
                                              chat_id=user_id,
                                              text="Выберите документы, которые у вас есть:",
                                              reply_markup=document_keyboard)
                    else:
                        txt = ''
                        for i in user.document_types:
                            txt += i + "\n"
                        r = bot.edit_message_text(message_id=call.message.id,
                                                  chat_id=user_id,
                                                  text=f'Вы выбрали:\n{txt}',
                                                  reply_markup=document_keyboard)
                        user.bot_messageId = r.id

                elif call.data == "save1":
                    if len(user.document_types) == 0:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Вы не выбрали ни один тип документов! Выберите тип документов",
                                                  show_alert=True)
                    else:
                        bot.send_message(chat_id=user_id,
                                         text="🙌 Вы в одном шаге от начала работы\nПодпишитесь:\n "
                                              "♻️ Актуальные верификации - узнай о работе и оплате\n"
                                              "📚 Правила и условия работы с ботом\n"
                                              "И нажмите кнопку 🟢 Начать работу!",
                                         reply_markup=subcribe_keyboard)

                ###конец этапа регистрации
                elif call.data == "ready":
                    try:
                        m = bot.get_chat_member(chat_id='-1001695261290', user_id=user_id)
                        r = bot.get_chat_member(chat_id='-1001558866443', user_id=user_id)
                        if m.status != 'left' and r.status != 'left':
                            if user_id in admins:
                                r = bot.send_message(chat_id=str(user_id), text=start_text,
                                                     reply_markup=start_admin_keyboard,
                                                     parse_mode='Markdown')
                            else:
                                r = bot.send_message(chat_id=str(user_id), text=start_text,
                                                     reply_markup=start_keyboard,
                                                     parse_mode='Markdown')
                            user.full_registered = True
                            user.bot_messageId = r.id
                            user.flag = 0
                            user.changing_country_type_document = False
                            # user.flag = 1

                        else:
                            bot.answer_callback_query(callback_query_id=call.id,
                                                      text="Нужно быть подписанным на обе группы!",
                                                      show_alert=True)
                    except:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Нужно быть подписанным на обе группы!",
                                                  show_alert=True)

                ###создание заявки вывода средств
                elif call.data == "withdraw":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="Заявка на вывод отправлена менеджером",
                                              show_alert=True)

                    bot.send_message(chat_id=-1001516204936,
                                     text=f"user_id: {user_id} \nusername: {call.from_user.username}\n"
                                          f"Вывод средств на сумму: {user.balance}",
                                     reply_markup=withdraw_keyboard)

                elif call.data == "cancel_fio":
                    user.flag = 25
                    user.complete_name = []
                    r = bot.send_message(chat_id=user_id,
                                         text=text_ancet,
                                         parse_mode='Markdown')
                    user.bot_messageId = r.id

                ###измение анкеты пользователя
                elif call.data == "edit_user_data":
                    user.type_document = []
                    user.countries = []
                    user.changing_country_type_document = True
                    user.flag = 25
                    bot.edit_message_text(message_id=call.message.id,
                                          chat_id=user_id,
                                          text="Выберите страну ваших документов:",
                                          reply_markup=country_keyboard)

                ###рефераллы пользователя
                elif call.data == "referrals":
                    if len(user.referrals_lvl_1) != 0 or len(user.referrals_lvl_2) != 0:
                        bot.send_message(chat_id=user_id, text="Вами привлечены (по уровням):")
                        if len(user.referrals_lvl_1) != 0:
                            users_names_lvl_1 = user.referrals_by_lvl_to_str(1)
                        else:
                            users_names_lvl_1 = "Уровень 1:\nПривлечённых пользователей первого уроня нет("
                        if len(user.referrals_lvl_2) != 0:
                            users_names_lvl_2 = user.referrals_by_lvl_to_str(2)
                        else:
                            users_names_lvl_2 = "Уровень 2:\nПривлечённых пользователей второго уроня нет("
                        bot.send_message(chat_id=user_id, text=users_names_lvl_1)
                        bot.send_message(chat_id=user_id, text=users_names_lvl_2)
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="У Вас нет ни одного привлечённого реферала",
                                                  show_alert=True)
                ###слайдер
                elif call.data == ">":
                    user.current_but = user.current_but + 9
                    bot.edit_message_text(message_id=call.message.id, chat_id=user_id,
                                          text="✅ Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале,"
                                               " в будни с 11:00 до 19:00 МСК.\nВыберите сервис:",
                                          reply_markup=services_accounts.keyboard_init(user))
                ###слайдер
                elif call.data == "<":
                    user.current_but = user.current_but - 9
                    bot.edit_message_text(message_id=call.message.id, chat_id=user_id,
                                          text="✅ Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале,"
                                               " в будни с 11:00 до 19:00 МСК.\nВыберите сервис:",
                                          reply_markup=services_accounts.keyboard_init(user))
                ###слайдер
                elif call.data == "!>":
                    user.current_acc_but = user.current_acc_but + 9
                    bot.edit_message_text(message_id=call.message.id, chat_id=user_id,
                                          text=f"✅ Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале, "
                                               f"в будни с 11:00 до 19:00 МСК.\nВыберите сервис:",
                                          reply_markup=keyboard_with_accs(str(call.from_user.id)))
                ###слайдер
                elif call.data == "!<":
                    user.current_acc_but = user.current_acc_but - 9
                    bot.edit_message_text(message_id=call.message.id, chat_id=user_id,
                                          text=f"✅ Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале, "
                                               f"в будни с 11:00 до 19:00 МСК.\nВыберите сервис:",
                                          reply_markup=keyboard_with_accs(str(call.from_user.id)))

                ###выбор аккаунта
                elif call.data in services_accounts.data:
                    user.cur_acc["key"] = call.data
                    bot.send_message(chat_id=user_id,
                                     text=f"Сервис: {call.data}\n{services_accounts.data[str(call.data)].first_mes}",
                                     reply_markup=types.InlineKeyboardMarkup().add(
                                         types.InlineKeyboardButton(text="Начать", callback_data="Начать")).add(
                                         types.InlineKeyboardButton(text="Назад 🔙", callback_data="Назад 🔙")))

                elif call.data == "Начать":
                    user.flag = 20
                    bot.send_message(chat_id=user_id,
                                     text=f"📧 Введите Email, на который регистрировался сервис, "
                                          f"в поле ввода и отправьте в бот:",
                                     reply_markup=keyboard_loading_accs)

                elif call.data == "Назад 🔙":
                    bot.send_message(chat_id=user_id,
                                     text="✅ Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале, в будни"
                                          " с 11:00 до 19:00 МСК.\nВыберите сервис:",
                                     reply_markup=services_accounts.keyboard_init(user))

                elif call.data == "Отмена":
                    user.flag = 0
                    bot.send_message(chat_id=user_id, text="Действие отменено.")
                    bot.send_message(chat_id=user_id,
                                     text=start_text,
                                     parse_mode='Markdown')

                elif call.data == "Отмена 🛑":
                    user.flag = 0
                    user.cur_acc = {"key": user.cur_acc["key"]}
                    bot.send_message(chat_id=user_id,
                                     text=f"Сервис: {user.cur_acc['key']}\n"
                                          f"{services_accounts.data[user.cur_acc['key']].first_mes}",
                                     reply_markup=types.InlineKeyboardMarkup().add(
                                         types.InlineKeyboardButton(text="Начать", callback_data="Начать")).add(
                                         types.InlineKeyboardButton(text="Назад 🔙", callback_data="Назад 🔙")))

                elif call.data == "Главное меню 🏡":
                    user.flag = 0
                    bot.send_message(chat_id=user_id,
                                     text=start_text,
                                     parse_mode='Markdown')

                ###отправка аккаунта менеджерам
                elif call.data == "Подтвердить":
                    user.accounts_check[str(call.message.id)] = user.cur_acc
                    if "service_name" in user.cur_acc:
                        service = user.cur_acc["service_name"]
                    else:
                        service = user.cur_acc["key"]
                    user.count_no_verified_accs += 1
                    bot.send_message(chat_id=user_id,
                                     text=f"Данные аккаунта {service} отправлены!\n"
                                          f"Проверка АКТУАЛЬНЫХ сервисов из ЗАКРЕПЛЕНОГО сообщения на канале,\n"
                                          f"в будни с 11:00 до 19:00 МСК.\nВ выходные и праздники мы отдыхаем!")
                    app_number = str(call.message.id)
                    email = user.accounts_check[str(call.message.id)]["Email"]
                    password = user.accounts_check[str(call.message.id)]["password"]
                    other_info = user.accounts_check[str(call.message.id)]["info"]
                    if user.balance < user.earnings:
                        txt = f"id пользователя: {user_id}\n" \
                              f"номер заявки: {app_number}\n" \
                              f"у пользователя были осуществлены выводы средств\n" \
                              f"domen: {service}\n" \
                              f"email: {email}\n" \
                              f"пароль: {password}\n" \
                              f"остальная информация: \n{other_info}"
                    else:
                        txt = f"id пользователя: {user_id}\n" \
                              f"номер заявки: {app_number}\n" \
                              f"у пользователя не были осуществлены выводы средств\n" \
                              f"domen: {service}\n" \
                              f"email: {email}\n" \
                              f"пароль: {password}\n" \
                              f"остальная информация: \n{other_info}"
                    bot.send_message(chat_id=-1001516204936,
                                     text=txt,
                                     reply_markup=manager_keyboard)

                elif call.data == "Назад ⬆️":
                    user.flag = 0
                    bot.send_message(chat_id=user_id,
                                     text=f"Ваши загруженные аккаунты\n"
                                          f"Здесь вы можете изменить/удалить данные аккаунтов отправленных "
                                          f"Вами на проверку!",
                                     reply_markup=keyboard_with_accs(str(user_id)))

                elif call.data == "Изменить 🖊":
                    user.flag = 24
                    service_account = services_accounts.get_elem(user.chosen_acc[0])

                    if service_account.third_mes == "":
                        resp = service_account.second_mes
                    else:
                        resp = service_account.third_mes
                    bot.send_message(chat_id=user_id,
                                     text=f"Напишите новые данные заявки "
                                          f"№{user.chosen_acc[0]} "
                                          f"для сервиса {user.chosen_acc[1]}:\n\n"
                                          f"{resp}",
                                     reply_markup=types.InlineKeyboardMarkup().add(
                                         types.InlineKeyboardButton(text="Назад ⬆️", callback_data="Назад ⬆️")),
                                     disable_web_page_preview=True)

                elif call.data == "Удалить 🗑":
                    bot.send_message(chat_id=user_id,
                                     text=f"Вы уверены что хотите удалить заявку №"
                                          f"{user.chosen_acc[0]}?\n"
                                          f"Сервис: {user.chosen_acc[1]}\n"
                                          f"Email: {user.accounts_check[user.chosen_acc[0]]['Email']}",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text="Отмена 🛑", callback_data="Назад ⬆️"),
                                         types.InlineKeyboardButton(text="Подтвердить ✅",
                                                                    callback_data="Удалить аккаунт")))

                elif call.data == "Удалить аккаунт":
                    del user.accounts_check[user.chosen_acc[0]]
                    if call.from_user_id in admins:
                        bot.send_message(chat_id=user_id,
                                         text=start_text,
                                         parse_mode='Markdown',
                                         reply_markup=start_admin_keyboard)
                        bot.answer_callback_query(callback_query_id=call.id, text="Данные успешно удалены.",
                                                  show_alert=True)
                    else:
                        bot.send_message(chat_id=user_id,
                                         text=start_text,
                                         parse_mode='Markdown',
                                         reply_markup=start_keyboard)
                        bot.answer_callback_query(callback_query_id=call.id, text="Данные успешно удалены.",
                                                  show_alert=True)

                elif "№" in call.data:
                    service = str(call.data).replace(f"{str(call.data).split(' ')[0]}", '').replace(' ', '')
                    user.chosen_acc = [str(call.data).split(' ')[0].replace('№', ''), service]
                    bot.send_message(chat_id=user_id,
                                     text=f"Выбрана заявка {str(call.data).split(' ')[0]}\nНазвание сервиса: {service}",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text="Изменить 🖊", callback_data="Изменить 🖊"),
                                         types.InlineKeyboardButton(text="Удалить 🗑", callback_data="Удалить 🗑")).add(
                                         types.InlineKeyboardButton(text="Назад ⬆️", callback_data="Назад ⬆️")))

                elif call.data == 'edit_payment_account':
                    if user.date_edit_payment == "":
                        user.changing_payment = True
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Менять реквизиты выплат можно только раз в 6 месяцев",
                                                  show_alert=True)
                        bot.send_message(chat_id=user_id,
                                         text="Выберите способ выплат:\n*Будьте внимательны, замена реквизитов "
                                              "делается только вручную!",
                                         reply_markup=pay_keyboard)
                        user.flag = 3
                    else:
                        time_ = datetime.datetime.today().strftime("%Y.%m").split('.')
                        time_1 = user.date_edit_payment.split('.')
                        year, year_1 = int(time_[0]), int(time_1[0])
                        month, month_1 = int(time_[1]), int(time_1[1])
                        if year <= year_1 and ((month - month_1 >= 6) or (month_1 - month >= 6)):
                            user.changing_payment = True
                            bot.answer_callback_query(callback_query_id=call.id,
                                                      text="Менять реквизиты выплат можно только раз в 6 месяцев",
                                                      show_alert=True)
                            bot.send_message(chat_id=user_id,
                                             text="Выберите способ выплат:\n*Будьте внимательны, "
                                                  "замена реквизитов делается только вручную!",
                                             reply_markup=pay_keyboard)
                            user.flag = 3
                        else:
                            bot.answer_callback_query(callback_query_id=call.id,
                                                      text="К сожалению 6 месяцев ещё не прошло!",
                                                      show_alert=False)

                elif call.data == "edit_complete_name":
                    user.previous_complete_name = user.complete_name
                    user.complete_name = []
                    user.changing_complete_name = True
                    user.flag = 25
                    r = bot.send_message(chat_id=user_id,
                                         text="Изменение ФИО\n🖌 Введите Вашу фамилию на английском ниже ⬇️"
                                              "\nНапример: Taylor / Sergeevsky")
                    user.bot_messageId = r.id

                elif call.data == "edit_complete_name_element":
                    user.flag = 25
                    if len(user.complete_name) == 1:
                        user.complete_name = []
                        r = bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                                  text="🖌 Введите Вашу фамилию на английском ниже ⬇️\n"
                                                       "Например: Taylor / Sergeevsky")
                        user.bot_messageId = r.id

                    elif len(user.complete_name) == 2:
                        del user.complete_name[-1]
                        r = bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                                  text="🖌 Введите Ваше имя на английском ниже ⬇️\n"
                                                       "Например, Mark / Ivan")
                        user.bot_messageId = r.id

                    elif len(user.complete_name) == 3:
                        del user.complete_name[-1]
                        r = bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                                  text="🖌 Введите Ваше отчество на английском ⬇️"
                                                       "\nНапример: отсутствует в англ языке / Sergeevich")
                        user.bot_messageId = r.id

                elif call.data == 'edit_payment_acc_step_back':
                    if user.flag == 28:
                        user.flag = 2
                    else:
                        user.flag = 3
                    bot.send_message(chat_id=user_id,
                                     text="Выберите способ выплат:\n*Будьте внимательны, замена "
                                          "реквизитов делается только вручную!",
                                     reply_markup=pay_keyboard)

                elif call.data == "next_step_in_reg":
                    print(user.flag)
                    ''''''
                    if user.flag == 28:
                        user.flag = 25
                        bot.send_message(chat_id=user_id,
                                         text="Выберите страну ваших документов:",
                                         reply_markup=country_keyboard)

                    elif user.flag == 29:
                        time = datetime.datetime.today().strftime("%Y.%m")
                        user.changing_payment = False
                        user.date_edit_payment = time
                        user.flag = 0
                        if user_id in admins:
                            r = bot.send_message(chat_id=str(call.from_user.id), text=start_text,
                                                 reply_markup=start_admin_keyboard)
                        else:
                            r = bot.send_message(chat_id=str(call.from_user.id), text=start_text,
                                                 reply_markup=start_keyboard)
                        user.bot_messageId = r.id
                        users.count_requisites += 1

                    elif len(user.complete_name) == 1:
                        user.flag = 25
                        r = bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                                  text="🖌 Введите Ваше имя на английском ниже ⬇️\n"
                                                       "Например, Mark / Ivan")
                        user.bot_messageId = r.id

                    elif len(user.complete_name) == 2:
                        user.flag = 25
                        r = bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                                  text="🖌 Введите Ваше отчество на английском ⬇️"
                                                       "\nНапример: отсутствует в англ языке / Sergeevich")
                        user.bot_messageId = r.id

                    elif len(user.complete_name) == 3:
                        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id,
                                                      reply_markup=None)
                        if user.payment_method == "":
                            user.flag = 25
                            bot.send_message(chat_id=user_id,
                                             text="💰Выберите способ получения вашего вознаграждения:\n"
                                                  "*Будьте внимательны, замена реквизитов делается только вручную!",
                                             reply_markup=pay_keyboard)
                        else:
                            user.changing_complete_name = False
                            user.flag = 0
                            user_name = call.from_user.username
                            user_id = str(call.from_user.id)
                            if call.from_user.first_name is None:
                                first_name = ''
                            else:
                                first_name = str(call.from_user.first_name) + ' '
                            if call.from_user.last_name is None:
                                last_name = ''
                            else:
                                last_name = str(call.from_user.last_name)
                            registration_date = user.registration_date

                            if user.payment_method == "QIWI":
                                requisites = user.payment_account + " (Qiwi 📲)"
                            else:
                                requisites = user.payment_account

                            country_docs = user.get_str_countries_and_document_types()
                            full_name = user.complete_name[0] + " " + user.complete_name[1] + " " + user.complete_name[
                                2]
                            user_balance = user.balance
                            bot.send_message(chat_id=user_id,
                                             text=f"`{first_name + last_name}`, это Ваш профиль!\n"
                                                  f"🆔 Ваш id: `{user_id}`\n"
                                                  f"👤 Ваш логин: `@{user_name}`\n"
                                                  f"📝 ФИО указанные в анкете: `{full_name}`\n"
                                                  f"✅ Дата регистрации: *{registration_date}*\n"
                                                  f"🌍 Страна: *{country_docs['countries']}*\n"
                                                  f"📂 Документы: *{country_docs['document_types']}*\n"
                                                  f"💳 Реквизиты выплат: `{requisites}`\n"
                                                  f"💰Ваш баланс: *{user_balance} руб*",
                                             reply_markup=profile_keyboard,
                                             parse_mode="Markdown")
                elif call.data == "fire_task_user":
                    user.flag = 46
                    user.count_tasks_keyboard = 0
                    keyboard = all_tasks.get_fire_tasks_keyboard()

                    if len(keyboard.keyboard) != 0:
                        bot.delete_message(chat_id=call.from_user.id,
                                           message_id=call.message.id)
                        bot.send_message(chat_id=call.from_user.id,
                                         text="Вот список заданий",
                                         reply_markup=all_tasks.slider_keyboard(keyboard, 0))
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="К сожалению заданий нет")

                elif call.data == "all_task_user":
                    user.flag = 43
                    user.count_tasks_keyboard = 0
                    keyboard = all_tasks.get_actual_tasks_keyboard()

                    if len(keyboard.keyboard) != 0:
                        bot.delete_message(chat_id=call.from_user.id,
                                           message_id=call.message.id)
                        bot.send_message(chat_id=call.from_user.id,
                                         text="Вот список заданий",
                                         reply_markup=all_tasks.slider_keyboard(keyboard, 0))
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="К сожалению заданий нет")

                elif call.data == "task_time_user":
                    user.flag = 47
                    user.count_tasks_keyboard = 0
                    keyboard = all_tasks.get_time_tasks_keyboard()
                    if len(keyboard.keyboard) != 0:
                        bot.delete_message(chat_id=call.from_user.id,
                                           message_id=call.message.id)
                        bot.send_message(chat_id=call.from_user.id,
                                         text="Вот список заданий",
                                         reply_markup=all_tasks.slider_keyboard(keyboard, 0))
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="К сожалению заданий нет")

                elif call.data == "task_seats_user":
                    user.flag = 48
                    user.count_tasks_keyboard = 0
                    keyboard = all_tasks.get_seats_tasks_keyboard()
                    if len(keyboard.keyboard) != 0:
                        bot.delete_message(chat_id=call.from_user.id,
                                           message_id=call.message.id)
                        bot.send_message(chat_id=call.from_user.id,
                                         text="Вот список заданий",
                                         reply_markup=all_tasks.slider_keyboard(keyboard, 0))
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="К сожалению заданий нет")

                elif call.data == "back_in_choice_task_user":
                    bot.send_message(chat_id=call.from_user.id,
                                     text='Выберите:',
                                     reply_markup=all_tasks.get_choice_tasks_keyboard())

                elif call.data == "change_task_user":
                    user.flag = 38
                    bot.send_message(chat_id=call.from_user.id,
                                     text=f"Введите ответ",
                                     reply_markup=types.InlineKeyboardMarkup().add(
                                         types.InlineKeyboardButton(text="назад",
                                                                    callback_data="back_in_choice_task_user")))

                elif call.data == "send_task_manager":
                    # user_id, instruction, filter
                    now = datetime.datetime.today()
                    task = all_tasks.get_actual_tasks()[
                        user.task_id]  # users_bd[str(call.from_user.id)]['tasks']['id_task']]
                    check1 = task.get_send_seats() is None
                    check2 = task.get_end_time_task() is None
                    check3 = None
                    check4 = None

                    if not check1:
                        check3 = task.get_send_seats() != task.get_seats()
                    if not check2:
                        check4 = task.get_end_time_task() > datetime.datetime(year=int(now.strftime("%Y")),
                                                                              month=int(now.strftime("%m")),
                                                                              day=int(now.strftime("%d")),
                                                                              hour=int(now.strftime("%H")),
                                                                              minute=int(now.strftime("%M")))

                    if check3 is not None and not check3:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Уже было отправлено необходимое кол-во ответов. Но ещё не все "
                                                       "обработаны. Заходите чуть позже, места могут повиться",
                                                  show_alert=True)

                    if check4 is not None and not check4:
                        all_tasks -= user.task_id  # users_bd[str(call.from_user.id)]['tasks']['id_task']
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text='Время на отправку ответа истекло',
                                                  show_alert=True)
                    # print(check1, '\n', check2, '\n', check3, '\n', check4)

                    if (check1 and check2 and check3 is None and check4 is None) or (
                            check1 and not check2 and check3 is None and check4 is None) or (
                            not check1 and not check2 and check3 and check4 is None) or (
                            not check1 and not check2 and check3 is None and check4) or (
                            not check1 and not check2 and check3 and check4):

                        if not check1:
                            task.change_send_seats()
                        mes = f"id пользователя: {call.from_user.id}\n" \
                              f"Инструкция задания:\n{task.get_str_task()}\n" \
                              f"Ответ пользователя: {user.task_answer}"
                        bot.edit_message_text(chat_id=call.from_user.id,
                                              message_id=call.message.id,
                                              text='Список заданий',
                                              reply_markup=all_tasks.get_choice_tasks_keyboard())

                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Ваш ответ отправлен")

                        bot.send_message(chat_id=-1001516204936,
                                         text=mes,
                                         reply_markup=types.InlineKeyboardMarkup().add(
                                             types.InlineKeyboardButton(text="взять заявку на рассмотрение",
                                                                        callback_data="check_test_manager")))

                elif call.data.isdigit():
                    if int(call.data) in all_tasks.get_actual_tasks() or int(call.data) in all_tasks.get_past_tasks():
                        user.task_to_some_act = int(call.data)
                        if user.flag == 42:
                            bot.send_message(chat_id=call.from_user.id,
                                             text=f"Задание:\n"
                                                  f"{all_tasks.get_actual_tasks()[int(call.data)].get_str_task()}",
                                             reply_markup=act_del_task)
                        elif user.flag == 45:
                            bot.send_message(chat_id=call.from_user.id,
                                             text=f"Задание:\n"
                                                  f"{all_tasks.get_past_tasks()[int(call.data)].get_str_task()}",
                                             reply_markup=act_past_task)

                        elif user.flag in [43, 46, 47, 48]:
                            task = all_tasks.get_actual_tasks()[int(call.data)].get_str_task()
                            user.flag = 38
                            user.task_id = int(call.data)
                            bot.send_message(chat_id=call.from_user.id,
                                             text=f"{task}",
                                             reply_markup=types.InlineKeyboardMarkup().add(
                                                 types.InlineKeyboardButton(text="назад",
                                                                            callback_data="back_in_choice_task_user")))

                save_object(users, 'users.pkl')

            else:
                bot.send_message(chat_id=user_id, text="❌❌❌\nВаш профиль, в нашем сервисе, "
                                                       "ЗАБЛОКИРОВАН!\n⛔️⛔️⛔️\nO причине блокировки читайте "
                                                       "комментарий. \n-------------\nКомментарий: Напишите в "
                                                       "бот поддержки @VerifSupportBot для проверки "
                                                       "личности.\n-------------\nЕсли Вы желаете обжаловать "
                                                       "решение о блокировке, пишите в бот поддержки, "
                                                       "дайте развёрнутое объяснение ситуации и напишите почему "
                                                       "Вы считаете, что Вас нужно разблокировать.\nБот "
                                                       "поддержки ❗️❗️❗️ @VerifSupportBot")

        ###Проверка username пользователя
        else:
            bot.send_message(chat_id=user_id,
                             text="ОШИБКА!\nУкажите"
                                  " @username в Вашем профиле Telegram, чтобы продолжить работу с ботом!")


###условие другое: проверка на флаг
@bot.callback_query_handler(func=lambda call: True)
def man(call):
    global all_tasks
    user_id = call.from_user.id
    manager = managers.get_elem(user_id)
    if user_id not in managers.data:
        managers.add_elem(user_id)
        manager = managers.get_elem(user_id)
    ###работа менеджера с заданиями
    if call.data == "check_test_manager":
        mes = call.message.text.replace('\n', ' ').split(' ')
        manager.accounts_to_check.append([mes[2], call.message.id, int(mes[6].strip("№"))])
        bot.send_message(chat_id=mes[2],
                         text=f"♻ Ваше ответ на задание {mes[6]} проверяется\n")
        bot.edit_message_text(chat_id=-1001516204936,
                              message_id=call.message.id,
                              text=f"Эта заявка рассматривается @{call.from_user.username}\n{call.message.text}",
                              reply_markup=types.InlineKeyboardMarkup().add(
                                  types.InlineKeyboardButton(text="подтвердить",
                                                             callback_data="confirm_task_manager"),
                                  types.InlineKeyboardButton(text="отклонить",
                                                             callback_data="deny_task_manager")
                              ))

    elif call.data == "confirm_task_manager":
        flag = False
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.accounts_to_check:
                if int(mes_id[1]) == int(call.message.message_id) and int(id) == int(user_id):
                    flag = True
                    bot.delete_message(chat_id=-1001516204936,
                                       message_id=call.message.message_id)
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text='ПОДТВЕРЖЕНО',
                                              show_alert=True)
                    bot.send_message(chat_id=mes_id[0],
                                     text=f"Ваш ответ на задание №{mes_id[2]} был принят")
                    user = users.get_elem(mes_id[0])
                    user.earnings += all_tasks.get_actual_tasks()[mes_id[2]].get_cost()
                    user.balance += all_tasks.get_actual_tasks()[mes_id[2]].get_cost()
                    all_tasks.get_actual_tasks()[mes_id[2]].change_confirm_seats()
                    if int(all_tasks.get_actual_tasks()[mes_id[2]].get_confirm_seats()) == int(
                            all_tasks.get_actual_tasks()[mes_id[2]].get_seats()):
                        all_tasks -= mes_id[2]
                    ind = manager.accounts_to_check.index(mes_id)
                    del manager.accounts_to_check[ind]
        if not flag:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Эту заявку рассматривает другой менеджер",
                                      show_alert=True)

    elif call.data == "deny_task_manager":
        flag = False
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.accounts_to_check:
                if int(mes_id[1]) == int(call.message.message_id) and int(id) == int(user_id):
                    flag = True
                    ind = manager.accounts_to_check.index(mes_id)
                    del manager.accounts_to_check[ind]
                    bot.delete_message(chat_id=-1001516204936,
                                       message_id=call.message.message_id)
                    bot.answer_callback_query(callback_query_id=call.id, text='ОТКЛОНЕНО',
                                              show_alert=True)
                    bot.send_message(chat_id=mes_id[0],
                                     text=f"❗️ Ваш ответ на задание №{mes_id[2]} был отклонен")
                    all_tasks.get_actual_tasks()[mes_id[2]].change_send_seats()
        if not flag:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Эту заявку рассматривает другой менеджер",
                                      show_alert=True)

    ###взятие менеджером заявку на рассмотрение
    elif call.data == "check_acc":

        mes = call.message.text.replace('\n', ' ').split(' ')
        manager.accounts_to_check.append([mes[2], mes[5], call.message.id])
        bot.send_message(chat_id=mes[2],
                         text=f"♻ Ваша заявка №{mes[5]} проверяется!\n"
                              f"Сервис: {mes[7]}\n"
                              f"Почта: {mes[9]}\n"
                              f"Во время проверки:\n1️⃣ Выйдите из аккаунта сервиса и почты!\n2️⃣ "
                              f"Не выполняйте никаких дополнительных действий по авторизации!\n❗️"
                              f"Любые действия только по просьбе проверяющего")

        bot.edit_message_text(chat_id=-1001516204936,
                              message_id=call.message.id,
                              text=f"Эта заявка рассматривается @{call.from_user.username}\n{call.message.text}",
                              reply_markup=manager_keyboard_2)

    ###подтверждение менеджером
    elif call.data == 'accepted':
        flag = False
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.accounts_to_check:
                if int(mes_id[2]) == int(call.message.message_id) and int(id) == int(user_id):
                    flag = True
                    bot.delete_message(chat_id=-1001516204936,
                                       message_id=call.message.message_id)
                    bot.answer_callback_query(callback_query_id=call.id, text='ПОДТВЕРЖЕНО',
                                              show_alert=True)
                    user = users.get_elem(mes_id[0])
                    user.count_verified_paid_accs += 1
                    user.count_no_verified_accs -= 1
                    ###сумма пополнения нужно подтягивать из админки
                    amount = 100
                    user.balance += amount
                    user.earnings += amount
                    bot.send_message(chat_id=mes_id[0],
                                     text=f"✅ Ваша заявка №{mes_id[1]} была подтвержена")
                    if (10000 >= user.earnings > 30000) and (user.referral_status != 'individual'):
                        user.referral_status = "Партнер"
                        user.reward_lvl_1 = 10
                        user.reward_lvl_2 = 3
                    elif (user.earnings >= 30000) and (user.referral_status != 'individual'):
                        user.referral_status = "Мастер"
                        user.reward_lvl_1 = 15
                        user.reward_lvl_2 = 5
                    users.referral_profit(mes_id[0], amount)
                    del user.accounts_check[mes_id[1]]
                    ind = manager.accounts_to_check.index(mes_id)
                    del manager.accounts_to_check[ind]

        if not flag:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Эту заявку рассматривает другой менеджер",
                                      show_alert=True)

    ###отклонение менеджером
    elif call.data == 'deny':
        flag = False
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.accounts_to_check:
                if int(mes_id[2]) == int(call.message.message_id) and int(id) == int(user_id):
                    flag = True
                    user = users.get_elem(mes_id[0])
                    user.count_verified_rejected_accs += 1
                    user.count_no_verified_accs -= 1
                    del user.accounts_check[mes_id[1]]
                    ind = manager.accounts_to_check.index(mes_id)
                    del manager.accounts_to_check[ind]
                    bot.delete_message(chat_id=-1001516204936,
                                       message_id=call.message.message_id)
                    bot.answer_callback_query(callback_query_id=call.id, text='ОТКЛОНЕНО',
                                              show_alert=True)
                    bot.send_message(chat_id=mes_id[0],
                                     text=f"❗️ Ваша заявка №{mes_id[1]} была отклонена")

        if not flag:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Эту заявку рассматривает другой менеджер",
                                      show_alert=True)

    ###взятие менеджером заявки на вывод средств
    elif call.data == "check_withdraw":
        mes = call.message.text.replace('\n', ' ').split(' ')
        user_id = mes[1]
        manager.withdraw.append([user_id])
        bot.edit_message_text(chat_id=-1001516204936,
                              message_id=call.message.id,
                              text=f"Эта заявка рассматривается @{call.from_user.username}\n{call.message.text}",
                              reply_markup=withdraw_keyboard_2)

    ###подтверждение заявки на вывод средств
    elif call.data == "complete_withdraw":
        flag = False
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.withdraw:
                if int(mes_id[0]) == int(call.message.message_id) and int(id) == int(user_id):
                    flag = True
                    user = users.get_elem(mes_id[0])
                    user.balance = 0
                    bot.delete_message(chat_id=-1001516204936,
                                       message_id=call.message.message_id)
                    bot.send_message(chat_id=mes_id[0],
                                     text=f"✅ Ваша заявка на вывод средств была подтвержена")

                    ind = manager.withdraw.index(mes_id)
                    del manager.withdraw[ind]

        if not flag:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Эту заявку рассматривает другой менеджер",
                                      show_alert=True)

    ###отклонение заявки на вывод средств
    elif call.data == "deny_withdraw":
        flag = False
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.withdraw:
                if int(mes_id[0]) == int(call.message.message_id) and int(id) == int(user_id):
                    flag = True
                    bot.delete_message(chat_id=-1001516204936,
                                       message_id=call.message.message_id)
                    bot.send_message(chat_id=mes_id[0],
                                     text=f"❗️ Ваша заявка на вывод средств была отклонена")
                    ind = manager.withdraw.index(mes_id)
                    del manager.withdraw[ind]

        if not flag:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Эту заявку рассматривает другой менеджер",
                                      show_alert=True)

    ###блокировка пользователя
    elif call.data == "block_user":
        for id in managers.data:
            manager = managers.get_elem(id)
            for mes_id in manager.accounts_to_check:
                if int(mes_id[0]) == int(call.message.message_id) and int(id) == int(user_id):
                    bot.send_message(chat_id=mes_id[1], text="❌❌❌\nВаш профиль, в нашем сервисе, "
                                                             "ЗАБЛОКИРОВАН!\n⛔️⛔️⛔️\nO причине блокировки читайте "
                                                             "комментарий. \n-------------\nКомментарий: Напишите "
                                                             "в бот поддержки @VerifSupportBot для проверки "
                                                             "личности.\n-------------\nЕсли Вы желаете "
                                                             "обжаловать решение о блокировке, пишите в бот "
                                                             "поддержки, дайте развёрнутое объяснение ситуации и "
                                                             "напишите почему Вы считаете, что Вас нужно "
                                                             "разблокировать.\nБот поддержки ❗️❗️❗️ "
                                                             "@VerifSupportBot")
                    user = users.get_elem(mes_id[1])
                    user.status = False
    save_object(managers, "managers.pkl")


###условие другое: проверка на флаг
@bot.message_handler(func=lambda message: message.from_user.id in admins)
def message_admin(message):
    global task1, pay_keyboard_for_admin
    user_id = message.from_user.id
    admin = admins.get_elem(user_id)
    ###настройка кнопок инструкции(телеграф)
    if admin.flag in [5, 6]:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        if admin.telegraph_name == "":
            admin.telegraph_name = message.text
            if admin.flag == 6:
                txt = f'Название сервиса: {admin.telegraph_name}\n' \
                      f'Действие: {admin.telegraph_action}\n(0-добавление, ' \
                      f'1 - изменение, 2 - удаление)'
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text=txt,
                                      reply_markup=action_insrt)

            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text='Данные сохранены!\nВведите url',
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                          types.InlineKeyboardButton(text="назад", callback_data='append_url')))

        else:
            admin.telegraph_url = message.text
            txt = f'Название сервиса: {admin.telegraph_name}\n' \
                  f'Ссылка: {admin.telegraph_url}\n' \
                  f'Действие: {admin.telegraph_action}\n(0 - изменение, ' \
                  f'1 - добавление, 2 - удаление)'
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=txt,
                                  reply_markup=action_insrt)

    ###сохранение информации для добавления аккаунта/удаление аккаунта
    elif admin.flag in [9, 10, 11]:
        ###добавление аккаунта
        bot.delete_message(chat_id=user_id, message_id=message.id)
        if admin.edit_acc_name == "" and admin.flag == 9:
            ####bot.delete_message(chat_id=user_id,message_id=message.id)
            admin.edit_acc_name = message.text
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text="Теперь введите первое сообщение",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="отменить все действия",
                                                                 callback_data='back_main_admin')))

        elif admin.edit_acc_name != "" and admin.edit_acc_first_mes == "" and admin.flag == 9:
            admin.edit_acc_first_mes = message.text
            ####bot.delete_message(chat_id=user_id,message_id=message.id)
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text="Теперь введите второе сообщение",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="отменить все действия",
                                                                 callback_data='back_main_admin')))

        elif admin.edit_acc_name != "" and admin.edit_acc_first_mes != "" and admin.edit_acc_second_mes == "" \
                and admin.flag == 9:
            ####bot.delete_message(chat_id=user_id,message_id=message.id)
            admin.edit_acc_second_mes = message.text
            yes_no_acc = types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton(text="Да", callback_data="yes_acc")).add(
                types.InlineKeyboardButton(text="Нет", callback_data="ready_acc"))

            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text="Необходимо третье сообщение?",
                                  reply_markup=yes_no_acc)
        ###удаление аккаунта
        elif admin.flag == 10:

            if message.text in services_accounts.data:
                del services_accounts.data[message.text]
                admin.flag = 4
                services_accounts.data = dict(sorted(services_accounts.data.items(), key=lambda item: item[0]))
                save_object(services_accounts, "services_accounts.pkl")
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="Нажмите кнопку готово",
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                          types.InlineKeyboardButton(text="Готово",
                                                                     callback_data='back_main_admin')))
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=user_id,
                                      text='Такой сервис не нашелся\nПопробуйте ещё раз',
                                      reply_markup=account_admin_keyboard)

        ###редактирование цены
        elif admin.flag == 11:
            ####bot.delete_message(chat_id=user_id,message_id=message.id)
            if admin.edit_acc_name == "":
                if message.text in services_accounts.data:
                    admin.edit_acc_name = message.text
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=admin.message_id,
                                          text="Теперь введите цену",
                                          reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                              types.InlineKeyboardButton(text="Вернуться в меню выбора функций",
                                                                         callback_data='back_main_admin')))
                else:
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=admin.message_id,
                                          text='Такой сервис не нашелся\nПопробуйте ещё раз',
                                          reply_markup=account_admin_keyboard)

            elif admin.edit_acc_price == 0:
                if message.text.isdigit():
                    service_account = services_accounts.get_elem(admin.edit_acc_name)
                    service_account.price = int(message.text)
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=admin.message_id,
                                          text="Нажмите кнопку готово",
                                          reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                              types.InlineKeyboardButton(text="Готово", callback_data='ready_acc')
                                          ))
                    admin.edit_acc_name = ""
                    services_accounts.data = dict(sorted(services_accounts.data.items(), key=lambda item: item[0]))
                    save_object(services_accounts, "services_accounts.pkl")
                else:
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=admin.message_id,
                                          text="Введите целое число")

        else:
            ####bot.delete_message(chat_id=user_id,message_id=message.id)
            admin.edit_acc_third_mes = message.text
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text="Нажмите кнопку готово",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="Готово", callback_data='ready_acc')))

    ###блокировка/разблокировка пользователя
    elif admin.flag in [13, 14]:
        bot.delete_message(chat_id=user_id, message_id=message.id)
        list_username = load_data("username.json")
        ls_username = message.text.split(' ')
        no_user = list()
        for username in ls_username:
            if username.isdigit():
                try:
                    if admin.flag == 13:
                        users.get_elem(int(username)).status = False
                    else:
                        users.get_elem(int(username)).status = True
                except:
                    no_user.append(username)
            else:
                if username in list_username:
                    try:
                        if admin.flag == 13:
                            users.get_elem(int(list_username[username])).status = False
                        else:
                            users.get_elem(int(list_username[username])).status = True
                    except:
                        no_user.append(username)

                else:
                    admin.flag = 4
                    no_user.append(username)

        if len(no_user) == 0:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text='Пользователи заблокированы/разблокированы!\nЕщё что-то?',
                                  reply_markup=admin_keyboard)
        else:
            txt = ""
            for i in no_user:
                txt += "@" + i + "\n"
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f"Не получилось заблокировать следующих пользователей:\n{txt}",
                                  reply_markup=admin_keyboard)

    ###общий блок начисления индивидуального процента
    elif admin.flag == 16:
        list_username = load_data("username.json")
        bot.delete_message(chat_id=user_id, message_id=message.id)
        ###сохранение id пользователей
        if len(admin.procent_name) == 0:
            admin.procent_name = message.text.split(' ')
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text='Теперь через пробел напишите процентную ставку '
                                       'по 1-му лвл, а затем по 2-му лвл ',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data='indiv_procent')))

        ###начисление процента пользователям
        elif len(admin.procent_name) != 0:
            no_username = ""
            if ' ' in message.text:
                lvl_1, lvl_2 = message.text.split(' ')[0], message.text.split(' ')[1]
                if lvl_1.isdigit() and lvl_1.isdigit():
                    for id in admin.procent_name:
                        if id.isdigit():
                            try:
                                user = users.get_elem(int(id))
                                user.referral_status = "individual"
                                user.reward_lvl_1 = int(lvl_1)
                                user.reward_lvl_2 = int(lvl_2)
                            except:
                                no_username += "@" + id + "\n"
                        else:
                            try:
                                user = users.get_elem(int(list_username[id]))
                                user.referral_status = "individual"
                                user.reward_lvl_1 = int(lvl_1)
                                user.reward_lvl_2 = int(lvl_2)
                            except:
                                no_username += "@" + id + "\n"
                    else:
                        if len(no_username) != 0:
                            bot.edit_message_text(chat_id=user_id,
                                                  message_id=admin.message_id,
                                                  text=f"Не получилось начислить индивидуальный "
                                                       f"процент:\n{no_username}",
                                                  reply_markup=admin_keyboard)
                        else:
                            bot.edit_message_text(chat_id=user_id,
                                                  message_id=admin.message_id,
                                                  text=f"Индивидуальные проценты начислены",
                                                  reply_markup=admin_keyboard)
                        admin.procent_name = []
                        admin.procent_lvl_1 = 0
                        admin.procent_lvl_2 = 0
                        admin.flag = 0
                else:
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=admin.message_id,
                                          text="Напишите через пробел 2 целых числа")
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="Напишите через пробел 2 целых числа")

    ###отправка данных по конкретному пользователю
    elif admin.flag == 19:
        data = load_data("username.json")
        bot.delete_message(chat_id=user_id, message_id=message.id)
        try:
            username = ''
            for i in data:
                if data[i] == message.text:
                    username = i
            if message.text.isdigit():
                user_id = str(message.text)
            else:
                user_id = data[username]
            user = users.get_elem(int(user_id))
            registration_date = user.registration_date
            if user.payment_method == "QIWI":
                requisites = user.payment_account + " (Qiwi 📲)"
            else:
                requisites = user.payment_account
            countries_docs = user.get_str_countries_and_document_types()
            full_name = user.complete_name[0] + user.complete_name[1] + user.complete_name[2]
            user_balance = user.balance

            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f"Вот профиль пользователя\n"
                                       f"id: {user_id}\n"
                                       f"логин: @{username}\n"
                                       f"дата регистрации: {registration_date}\n"
                                       f"реквизиты выплат: {requisites}  \n"
                                       f"страна:\n{countries_docs['countries']}\n"
                                       f"документы:\n{countries_docs['document_types']}\n"
                                       f"ФИО указанные в анкете:\n{full_name}\n"
                                       f"баланс: {user_balance} руб.",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="Вернуться в меню админа",
                                                                 callback_data='back_main_admin')),
                                  parse_mode="Markdown")

        except:
            txt = ""
            for i in data:
                txt += i + ' - ' + data[i] + '\n'
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f"Такого пользователя нет, попробуйте ещё раз\n{txt}")

    ###блок изменения баланс пользователя
    elif admin.flag == 26:
        data = load_data("username.json")
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        if len(admin.calc_balance) == 0:
            admin.calc_balance = message.text.split(' ')
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text="Теперь введите сумму пополнения, если хотите баланс понизить, "
                                       "то просто напишите отрицательное число",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="calc_balance")))
        else:
            if message.text.isdigit():
                no_user = ""
                amount = int(message.text)
                for id in admin.calc_balance:
                    if id.isdigit():
                        if id in users:
                            user = users.get_elem(int(id))
                            user.balance += amount
                            user.earnings += amount
                        else:
                            no_user += id + '\n'
                    else:
                        if id in data:
                            user = users.get_elem(int(data[id]))
                            user.balance += amount
                            user.earnings += amount
                        else:
                            no_user += "@" + id + '\n'
                else:
                    if len(no_user) != 0:
                        bot.edit_message_text(chat_id=user_id,
                                              message_id=admin.message_id,
                                              text=f"Не получилось изменить баланс:\n{no_user}",
                                              reply_markup=admin_keyboard)
                    else:
                        bot.edit_message_text(chat_id=user_id,
                                              message_id=admin.message_id,
                                              text=f"Баланс изменен",
                                              reply_markup=admin_keyboard)
                    admin.calc_balance = []

            elif "-" in message.text and message.text[1:].isdigit():
                no_user = ""
                amount = int(message.text[1:])
                for id in admin.calc_balance:
                    if id.isdigit():
                        if id in users:
                            user = users.get_elem(int(id))
                            user.balance -= amount
                            user.earnings -= amount
                        else:
                            no_user += id + '\n'
                    else:
                        if id in data:
                            user = users.get_elem(int(data[id]))
                            user.balance -= amount
                            user.earnings -= amount
                        else:
                            no_user += "@" + id + '\n'
                else:
                    if len(no_user) != 0:
                        bot.edit_message_text(chat_id=user_id,
                                              message_id=admin.message_id,
                                              text=f"Не получилось изменить баланс:\n{no_user}",
                                              reply_markup=admin_keyboard)
                    else:
                        bot.edit_message_text(chat_id=user_id,
                                              message_id=admin.message_id,
                                              text=f"Баланс изменен",
                                              reply_markup=admin_keyboard)
                    admin.calc_balance = []
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="Введите целое число")

    elif admin.flag == 30:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        if admin.post_mail_text == "":
            admin.post_mail_text = message.text
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f'Вы ввели:\n{message.text}',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="продолжить", callback_data="continue_post_mail"),
                                      types.InlineKeyboardButton(text="изменить", callback_data="change_post_mail")))

        elif admin.post_mail_text != "" and admin.post_mail_text_button == "":
            admin.post_mail_text_button = message.text
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f'Вы ввели:\n{message.text}',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="продолжить",
                                                                 callback_data="continue_but_post_mail"),
                                      types.InlineKeyboardButton(text="изменить", callback_data="yes_post")))

        elif admin.post_mail_text != "" and admin.post_mail_text_button != "":
            admin.post_mail_url = message.text
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f'Вы ввели:\n{message.text}',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="продолжить", callback_data="no_post"),
                                      types.InlineKeyboardButton(text="изменить",
                                                                 callback_data="continue_but_post_mail")))
            """if admin.post_mail_action in [5,6,7]:
                bot.edit_message_text(chat_id=user_id,
                                    message_id=admin.message_id,
                                    text=f'Пост выглядит так:\n{admin.post_mail_text}\n'
                                        f'Уведомить всех участников?',
                                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                                 types.InlineKeyboardButton(text="Да", callback_data="yes_disable_notification"),
                                                 types.InlineKeyboardButton(text="Нет", callback_data="ready_post")))
            else:
                bot.edit_message_text(chat_id=user_id,
                                    message_id=admin.message_id,
                                    text=f'Пост выглядит так:\n{admin.post_mail_text}',
                                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                                 types.InlineKeyboardButton(text=admin.post_mail_text_button, url=admin.post_mail_url),
                                                 types.InlineKeyboardButton(text="Подтверить", callback_data="ready_post"),
                                                 types.InlineKeyboardButton(text="Изменить", callback_data="no_ready_post")))
            admin.flag = 4"""

    elif admin.flag == 35:
        bot.delete_message(chat_id=admin,
                           message_id=message.id)
        admin.channel_sale_text = message.text
        bot.edit_message_text(chat_id=admin,
                              message_id=admin.message_id,
                              text=f"Вы ввели:\n{message.text}",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="Подтвердить",
                                                             callback_data="confirm_chanel_sale"),
                                  types.InlineKeyboardButton(text="Изменить",
                                                             callback_data="chanel_sale")
                              ))
        admin.flag = 4

    elif admin.flag == 37:
        bot.delete_message(chat_id=admin,
                           message_id=message.id)
        admin.channel_sale_count += 1
        admin.channel_sale_button.append([message.text])
        bot.edit_message_text(chat_id=admin,
                              message_id=admin.message_id,
                              text=f'Вы ввели:\n{message.text}\nПодтвердить?',
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="Подтвердить",
                                                             callback_data="add_url_chanel_sale"),
                                  types.InlineKeyboardButton(text="Изменить",
                                                             callback_data="change_but_sale")
                              ))
        admin.flag = 4

    elif admin.flag == 36:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        try:
            admin.channel_sale_button[admin.channel_sale_count].append(message.text)
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for i in admin.channel_sale_button:
                keyboard.add(types.InlineKeyboardButton(text=i[0], url=i[1]))
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f"Вы ввели: {message.text}",
                                  reply_markup=keyboard.add(
                                      types.InlineKeyboardButton(text="Подтвердить",
                                                                 callback_data="confirm_chanel_sale"),
                                      types.InlineKeyboardButton(text="Изменить", callback_data="change_url_sale"), ))
            admin.flag = 4
        except:
            del admin.channel_sale_button[admin.channel_sale_count][1]
            bot.edit_message_text(chat_id=user_id,
                                  message_id=admin.message_id,
                                  text=f"Кнопку с таким url  невозможно создать. Попробуйте ввести ещё раз")

    ###изменение главного сообщения
    elif admin.flag == 7:
        admin.edit_main_mes = str(message.text)
        bot.send_message(chat_id=message.from_user.id,
                         reply_to_message_id=message.message_id,
                         text="Вы точно хотите изменить главное сообщение?",
                         reply_markup=editing_main_mes_keyboard)

    ###изменение периодичности отправки главного сообщения
    elif admin.flag == 8:
        if str(message.text).isdigit():
            admin.edit_period = int(message.text)
            bot.send_message(chat_id=message.from_user.id,
                             reply_to_message_id=message.message_id,
                             text="Вы точно хотите изменить периодичность отправки главного сообщения?",
                             reply_markup=editing_period_of_main_mes_keyboard)
        else:
            bot.send_message(chat_id=user_id,
                             text="Введите периодичность в часах")

    ###добавление клавиатуры для отправки сообщения в "Актуальные верификации"
    elif admin.flag == 12:
        admin.new_actual_verify_mes = {"text": str(message.text), "keyboard": None}
        bot.send_message(chat_id=message.from_user.id,
                         reply_to_message_id=message.message_id,
                         text="Выберете клавиатуру, если она нужна. "
                              "Подтвердите создание нового сообщения или отмените",
                         reply_markup=new_message_for_actual_verify)
    ###добавление клавиатуры для отправки сообщения в "Важные правила"
    elif admin.flag == 17:

        admin.new_important_rules_mes = {"text": str(message.text), "keyboard": None}
        bot.send_message(chat_id=message.from_user.id,
                         reply_to_message_id=message.message_id,
                         text="Выберете клавиатуру, если она нужна. "
                              "Подтвердите создание нового сообщения или отмените",
                         reply_markup=editing_mes_in_important_rules)
    ###прием ссылки
    elif admin.flag == 15:
        if "https://" in message.text or "http://" in message.text:
            a = str(message.text).split("\n")
            if len(a) == 2:
                if a[1] != "https://" and a[1] != "http://":

                    admin.new_actual_verify_mes["keyboard"] = [a[0], a[1]]
                    bot.send_message(chat_id=message.from_user.id,
                                     reply_to_message_id=message.message_id,
                                     text="Красава",
                                     reply_markup=new_message_for_actual_verify)
                else:
                    bot.send_message(chat_id=message.from_user.id,
                                     reply_to_message_id=message.message_id,
                                     text="Ошибка. Пример:\nТЕКСТ КНОПКИ\nhttp(s)://...",
                                     reply_markup=new_message_for_actual_verify)
            else:
                bot.send_message(chat_id=message.from_user.id,
                                 reply_to_message_id=message.message_id,
                                 text="Ошибка. Пример:\nТЕКСТ КНОПКИ\nhttp(s)://...",
                                 reply_markup=new_message_for_actual_verify)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             reply_to_message_id=message.message_id,
                             text="Ошибка. Пример:\nТЕКСТ КНОПКИ\nhttp(s)://...",
                             reply_markup=new_message_for_actual_verify)
    ###прием ссылки
    elif admin.flag == 18:
        if "https://" in message.text or "http://" in message.text:
            a = str(message.text).split("\n")
            if len(a) == 2:
                if a[1] != "https://" and a[1] != "http://":
                    admin.new_important_rules_mes["keyboard"] = [a[0], a[1]]
                    bot.send_message(chat_id=message.from_user.id,
                                     reply_to_message_id=message.message_id,
                                     text="Красава",
                                     reply_markup=editing_mes_in_important_rules)
                else:
                    bot.send_message(chat_id=message.from_user.id,
                                     reply_to_message_id=message.message_id,
                                     text="Ошибка. Пример:\nТЕКСТ КНОПКИ\nhttp(s)://...",
                                     reply_markup=editing_mes_in_important_rules)
            else:
                bot.send_message(chat_id=message.from_user.id,
                                 reply_to_message_id=message.message_id,
                                 text="Ошибка. Пример:\nТЕКСТ КНОПКИ\nhttp(s)://...",
                                 reply_markup=editing_mes_in_important_rules)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             reply_to_message_id=message.message_id,
                             text="Ошибка. Пример:\nТЕКСТ КНОПКИ\nhttp(s)://...",
                             reply_markup=editing_mes_in_important_rules)
    elif admin.flag == 31:
        admin.flag = 32
        admin.payment_method_settings_name = message.text
        bot.send_message(chat_id=message.from_user.id,
                         text=f"Вы ввели:\n{message.text}\n\nВведите инструкции для этого способа оплаты",
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="Назад", callback_data="new_payment")))

    elif admin.flag == 32:
        admin.flag = 4
        admin.payment_method_settings_instruction = message.text
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Для {admin.payment_method_settings_name} введена инструкция:\n{message.text}',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="СОХРАНИТЬ", callback_data="save_new_payment_but")).add(
                             types.InlineKeyboardButton(text="ОТМЕНА", callback_data="payments")).add(
                             types.InlineKeyboardButton(text="НАЗАД", callback_data="back_to_input_instruction")))
    elif admin.flag == 33:
        ##save_new_data_for_pay_method edit_payment_method_instruction edit_payment_method_name
        admin.payment_method_settings_new_name = message.text
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Для {admin.payment_method_settings_name} введено новое название: {message.text}',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="СОХРАНИТЬ",
                                                        callback_data="save_new_data_for_pay_method")).add(
                             types.InlineKeyboardButton(text="НАЗАД", callback_data="edit_payment_method_name")))
    elif admin.flag == 34:
        admin.flag = 4
        ##save_new_data_for_pay_method edit_payment_method_instruction edit_payment_method_name
        admin.payment_method_settings_new_instruction = message.text
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Для {admin.payment_method_settings_name} введена новая инструкция:\n{message.text}',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="СОХРАНИТЬ",
                                                        callback_data="save_new_data_for_pay_method")).add(
                             types.InlineKeyboardButton(text="НАЗАД", callback_data="edit_payment_method_instruction")))

    ###ввод инструкции
    elif admin.flag == 39:
        admin.flag = 4
        task1.set_instruction(message.text)
        bot.send_message(chat_id=message.from_user.id, text=f"Вы ввели:\n{message.text}",
                         reply_markup=inst_task_keyboard)

    ###ввод фильтра по времени
    elif admin.flag in [40, 41, 44]:
        if message.text.isdigit():
            if admin.flag == 40:
                task1.set_time(int(message.text))
                bot.send_message(chat_id=message.from_user.id, text=f"Вы ввели: {message.text}",
                                 reply_markup=act_filter_time)
            elif admin.flag == 41:
                task1.set_seats(int(message.text))
                bot.send_message(chat_id=message.from_user.id, text=f"Вы ввели: {message.text}",
                                 reply_markup=act_filter_seats)
            else:
                task1.set_cost(int(message.text))
                bot.send_message(chat_id=message.from_user.id, text=f"Вы ввели: {message.text}",
                                 reply_markup=cost_task_keyboard)
                admin.flag = 4
        else:
            bot.send_message(chat_id=message.from_user.id, text="Введите целое число")


#
##условие другое: проверка на флаг
@bot.callback_query_handler(func=lambda call: call.from_user.id in admins)
def callback_admin(call):
    global task1, pay_keyboard_for_admin, pay_keyboard, all_tasks
    user_id = call.from_iser.id
    admin = admins.get_elem(user_id)
    if call.data == "user":
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Выберите:",
                                  reply_markup=user_keyboard)
        admin.message_id = r.id

    elif call.data == "statistics":
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Выберите:",
                              reply_markup=statistics_keyboard)

    ###статистика для 1 пользователя
    elif call.data == "one_user":
        list_username = load_data("username.json")
        txt = ""
        for i in list_username:
            txt += f"{i} - {list_username[i]}\n"
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Отправьте id или username пользователя, "
                                       f"чью статистику хотели бы посмотреть\n"
                                       f"Вот полный список(username - user_id)\n{txt}",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад",
                                                                 callback_data="statistics")),
                                  parse_mode="Markdown")
        admin.message_id = r.id
        admin.flag = 19

    ###общая статистика
    elif call.data == "full_statistics":
        data = users.full_statistic()
        txt = f"Количество пользователей: {data['count_user']}\n" \
              f"Количество не проверенных аккаунтов: {data['count_no_verified']}\n" \
              f"Количество подтвержденных аккаунтов: {data['count_verified_paid']}\n" \
              f"Количество отклоненных аккаунтов: {data['count_verified_rejected']}\n" \
              f"Баланс пользователей за все время: {data['all_balance']}\n" \
              f"Весь баланс, который сейчас не выведен: {data['balance']}\n" \
              f"Баланс, который вывели: {data['paid']}\n" \
              f"Количество смен реквизитов: {data['count_requisites']}"

        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text=txt,
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="назад",
                                                             callback_data="statistics")))

    ###выбор того, что делать с кнопками из  инструкции(или же вернуться к выбору)
    elif call.data == 'edit_button_instr':
        bot.delete_message(chat_id=user_id,
                           message_id=call.message.id)
        admin.flag = 4

        bot.send_message(chat_id=user_id,
                         text='Выберите что вы именно хотите:',
                         reply_markup=instr_keyboard)

    ###изменение/добавление url кнопки в инструкции
    elif call.data == 'edit_url' or call.data == 'append_url':
        bot.delete_message(chat_id=user_id,
                           message_id=call.message.id)
        admin.telegraph_name = ""
        admin.telegraph_url = ""
        admin.flag = 5
        if call.data == "edit_url":
            admin.telegraph_action = 0
        else:
            admin.telegraph_action = 1
        with open("file.pkl", "rb") as fp:
            a = pickle.load(fp)
        instruction_keyboard = pickle.loads(a["instruction_keyboard"])
        txt = ''
        for i in instruction_keyboard.keyboard:
            txt += i[0].text + '\n'
        txt = ''
        for i in instruction_keyboard.keyboard:
            txt += i[0].text + '\n'
        if call.data == 'edit_url':
            r = bot.send_message(chat_id=user_id,
                                 text=f'Сначала введите название сервиса, которого хотите изменить, '
                                      f'а после url кнопки\nНа данный момент существующие кнопки:\n{txt}',
                                 reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                     types.InlineKeyboardButton(text='назад',
                                                                callback_data="edit_button_instr")
                                 ))
        else:
            r = bot.send_message(chat_id=user_id,
                                 text=f'Сначала введите название сервиса, который хотите добавить, '
                                      f'а после url кнопки\nНа данный момент существующие кнопки:\n{txt}',
                                 reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                     types.InlineKeyboardButton(text='назад',
                                                                callback_data="edit_button_instr")
                                 ))
        admin.message_id = r.id

    ###удаление кнопки из инструкции
    elif call.data == 'remove_url':
        admin.name = ""
        admin.url = ""
        admin.action = 2
        bot.delete_message(chat_id=user_id,
                           message_id=call.message.id)
        admin.flag = 6
        with open("file.pkl", "rb") as fp:
            a = pickle.load(fp)
        instruction_keyboard = pickle.loads(a["instruction_keyboard"])
        txt = ''
        for i in instruction_keyboard.keyboard:
            txt += i[0].text + '\n'
        txt = ''
        for i in instruction_keyboard.keyboard:
            txt += i[0].text + '\n'

        r = bot.send_message(chat_id=user_id,
                             text=f'Введите название сервиса, который хотите удалить\n'
                                  f'На данный момент существующие кнопки:\n{txt}',
                             reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                 types.InlineKeyboardButton(text='назад',
                                                            callback_data="edit_button_instr")
                             ))

        admin.message_id = r.id

    elif call.data == "yes_action":
        bot.delete_message(chat_id=user_id,
                           message_id=call.message.id)
        edit_button_instr(admin=user_id,
                          name=admin.telegraph_name,
                          url=admin.telegraph_url,
                          action=admin.telegraph_action,
                          message_id=None)
        admin.telegraph_name = ""
        admin.telegraph_url = ""
        admin.telegraph_action = 0
        admin.flag = 4

    elif call.data == "no_action":
        admin.telegraph_name = ""
        admin.telegraph_url = ""
        admin.telegraph_action = 0
        admin.flag = 4
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text=f"{start_text}",
                              reply_markup=start_admin_keyboard,
                              parse_mode='Markdown')

    ###возможность выбрать добавление/удаление аккаунтов для загрузки и редактирование цен
    elif call.data == "edit_account":
        bot.delete_message(chat_id=user_id,
                           message_id=call.message.id)
        bot.send_message(chat_id=user_id,
                         text="Выберите нужное действие:",
                         reply_markup=account_admin_keyboard)

    ###добавление аккаунта
    elif call.data == "append_acc":

        mes = ""
        for i in services_accounts.data:
            mes += i + "\n"
        admin.flag = 9
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Сначала введите название сервиса(с большой буквы)\n"
                                       f"Доступные сервисы на данный момент\n{mes}",
                                  reply_markup=back_to_edit_account_keyboard)

        admin.message_id = r.id

    ###удаление аккаунта
    elif call.data == "remove_acc":

        mes = ""
        for i in services_accounts.data:
            mes += i + "\n"
        admin.flag = 10
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Введите название сервиса(с большой буквы)"
                                       f"Доступные сервисы на данный момент\n{mes}",
                                  reply_markup=back_to_edit_account_keyboard)
        admin.message_id = r.id

    ###изменение цены аккаунту
    elif call.data == "change_cost":
        mes = ""
        for i in services_accounts.data:
            mes += i + "\n"
        admin.flag = 11
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Введите название сервиса(с большой буквы)"
                                       f"Доступные сервисы на данный момент\n{mes}",
                                  reply_markup=back_to_edit_account_keyboard)
        admin.message_id = r.id

    ###переход на добавление третьего сообщения для добавления аккаунта
    elif call.data == 'yes_acc':
        bot.edit_message_text(chat_id=user_id,
                              message_id=admin.message_id,
                              text="Введите третье сообщение")

    elif call.data == "back_edit_account":
        admin.flag = 4
        bot.send_message(chat_id=user_id,
                         text="Выберите нужное действие:",
                         reply_markup=account_admin_keyboard)

    ###конец добавления аккаунта
    elif call.data == 'ready_acc':
        if admin.flag == 9:
            service_account = Service_Account()
            service_account.first_mes = admin.edit_acc_first_mes
            service_account.second_mes = admin.edit_acc_second_mes
            service_account.third_mes = admin.edit_acc_third_mes
            service_account.price = 0
            services_accounts.data[admin.edit_acc_name] = service_account
            admin.edit_acc_name = ""
            admin.edit_acc_first_mes = ""
            admin.edit_acc_second_mes = ""
            admin.edit_acc_third_mes = ""
            admin.price = 0
            services_accounts.data = dict(sorted(services_accounts.data.items(), key=lambda item: item[0]))
            save_object(services_accounts, "services_accounts.pkl")
        acc_keyboard = services_accounts.keyboard_init(user_id)
        bot.edit_message_text(chat_id=user_id,
                              message_id=admin.message_id,
                              text="Аккаунты выглядят теперь так",
                              reply_markup=acc_keyboard)
        admin.flag = 4

    ###выбор между блок/разблок
    elif call.data == "edit_status_user":
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Выберите:",
                                  reply_markup=block_unblock)
        admin.message_id = r.id

    ###блокировка пользователя
    elif call.data == "block":
        admin.flag = 13
        list_username = load_data("username.json")
        txt = ""
        for i in list_username:
            txt += i + ' - ' + list_username[i] + '\n'
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Отправьте id пользователя, которого хотите заблокировать."
                                       f"Вот полный список(username - user_id)\n{txt}",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад",
                                                                 callback_data="edit_status_user")))
        admin.message_id = r.id

    ###разблокировка пользователя
    elif call.data == "unblock":
        admin.flag = 14
        list_username = load_data("username.json")
        txt = ""
        for i in list_username:
            txt += i + ' - ' + list_username[i] + '\n'
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Отправьте id пользователя, которого хотите разблокировать."
                                       f"Вот полный список(username - user_id)\n{txt}",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад",
                                                                 callback_data="edit_status_user")))
        admin.message_id = r.id

    ###начисление инд процента
    elif call.data == "indiv_procent":
        admin.flag = 16
        list_username = load_data("username.json")
        admin.procent_name = []
        txt = ""
        for i in list_username:
            txt += '`' + i + '`' + ' - ' + '`' + list_username[i] + '`' + '\n'
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Напишите кому именно(id пользователя) вы хотите поставить "
                                       f"индивидуальный процент\n{txt}",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад",
                                                                 callback_data='user')
                                  ),
                                  parse_mode="Markdown")
        admin.message_id = r.id

    ###начисление баланс
    elif call.data == "calc_balance":
        admin.flag = 26
        admin.calc_balance = []
        list_username = load_data("username.json")
        txt = ""
        for i in list_username:
            txt += '`' + i + '`' + ' - ' + '`' + list_username[i] + '`' + '\n'
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f"Напишите кому именно вы хотите изменить баланс \n{txt}",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад",
                                                                 callback_data='user')),
                                  parse_mode="Markdown")
        admin.message_id = r.id

    ###переход в постинг&рассылка
    elif call.data == "posting_mailing":
        admin.post_mail_text = ""
        admin.post_mail_text_button = ""
        admin.post_mail_url = ""
        admin.post_mail_action = 0
        admin.post_mail_disable_notification = True
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Выберите:",
                                  reply_markup=posting_mailing)
        admin.message_id = r.id

    ###выбор постинга
    elif call.data == "posting":
        admin.post_mail_text = ""
        admin.post_mail_text_button = ""
        admin.post_mail_url = ""
        admin.post_mail_action = 0
        admin.post_mail_disable_notification = True
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Выберите:",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="В чат", callback_data="post_chat"),
                                  types.InlineKeyboardButton(text="В канал", callback_data="post_chanel"),
                                  types.InlineKeyboardButton(text="В оба",
                                                             callback_data="post_chat_chanel"),
                                  types.InlineKeyboardButton(text="назад", callback_data="posting_mailing")
                              ))

    ###постинк с закрепом
    elif call.data == "posting_pin":
        admin.post_mail_text = ""
        admin.post_mail_text_button = ""
        admin.post_mail_url = ""
        admin.post_mail_action = 0
        admin.post_mail_disable_notification = True
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Выберите:",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="В чат", callback_data="post_chat_pin"),
                                  types.InlineKeyboardButton(text="В канал",
                                                             callback_data="post_chanel_pin"),
                                  types.InlineKeyboardButton(text="В оба",
                                                             callback_data="post_chat_chanel_pin"),
                                  types.InlineKeyboardButton(text="назад", callback_data="posting_mailing")
                              ))

    ##рассылка
    elif call.data == "mailing":
        admin.post_mail_text = ""
        admin.post_mail_text_button = ""
        admin.post_mail_url = ""
        admin.post_mail_action = 0
        admin.post_mail_disable_notification = True
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Введите текст",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="назад", callback_data="posting_mailing")
                              ))
        admin.flag = 30

        admin.posting_mailing_action = 4

    ###выбор куда отправлять
    elif call.data == "post_chat" or call.data == "post_chanel" or call.data == "post_chat_chanel" \
            or call.data == "post_chat_pin" or call.data == "post_chanel_pin" or call.data == "post_chat_chanel_pin":
        admin.flag = 30

        if call.data == "post_chat":
            admin.post_mail_action = 1
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите текст",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting")
                                  ))

        elif call.data == "post_chanel":
            admin.post_mail_action = 2
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите текст",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting")
                                  ))

        elif call.data == "post_chat_chanel":
            admin.post_mail_action = 3
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите текст",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting")
                                  ))

        elif call.data == "post_chat_pin":
            admin.post_mail_action = 5
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите текст",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting_pin")
                                  ))

        elif call.data == "post_chanel_pin":
            admin.post_mail_action = 6
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите текст",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting_pin")
                                  ))

        elif call.data == "post_chat_chanel_pin":
            admin.posting_mailing_action = 7
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите текст",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting_pin")
                                  ))

    elif call.data == "change_post_mail":
        admin.post_mail_text = ""
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Введите текст",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="назад", callback_data="posting_pin")
                              ))

    elif call.data == "continue_post_mail":
        bot.edit_message_text(chat_id=user_id,
                              message_id=admin.message_id,
                              text="Нужна клавиатура?",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="Да", callback_data="yes_post"),
                                  types.InlineKeyboardButton(text="Нет", callback_data="no_post")
                              ))

    ###добавление кнопки в пост
    elif call.data == "yes_post":
        admin.post_mail_text_button = ""
        if admin.post_mail_action == 1 or \
                admin.post_mail_action == 2 or \
                admin.post_mail_action == 3:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите название кнопки",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting")
                                  ))
        elif admin.post_mail_action == 4:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите название кнопки",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="mailing")
                                  ))
        else:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите название кнопки",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад", callback_data="posting_pin")
                                  ))

    elif call.data == "continue_but_post_mail":
        admin.post_mail_url = ""
        bot.edit_message_text(chat_id=user_id,
                              message_id=admin.message_id,
                              text="Введите url")

    ###подтверждение поста
    elif call.data == "no_post":
        if admin.post_mail_action == 5 or \
                admin.post_mail_action == 6 or \
                admin.post_mail_action == 7:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f'Уведомить всех участников?',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="Да",
                                                                 callback_data="yes_disable_notification"),
                                      types.InlineKeyboardButton(text="Нет", callback_data="ready_post")
                                  ))
        else:
            if len(admin.post_mail_text_button) == 0:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=call.message.id,
                                      text=f'Пост выглядит так:\n{admin.post_mail_text}',
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                          types.InlineKeyboardButton(text="Подтвердить",
                                                                     callback_data="ready_post"),
                                          types.InlineKeyboardButton(text="Отменить",
                                                                     callback_data="posting_mailing")
                                      ))
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=call.message.id,
                                      text=f'Пост выглядит так:\n{admin.post_mail_text}',
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                          types.InlineKeyboardButton(
                                              text=admin.post_mail_text_button,
                                              url=admin.post_mail_url),
                                          types.InlineKeyboardButton(text="Подтвердить",
                                                                     callback_data="ready_post"),
                                          types.InlineKeyboardButton(text="Отменить",
                                                                     callback_data="posting_mailing")
                                      ))

    ###включение уведомления
    elif call.data == "yes_disable_notification":
        admin.post_mail_disable_notification = False
        if len(admin.post_mail_text_button) == 0:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f'Пост выглядит так:\n{admin.post_mail_text}',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="Подтвердить",
                                                                 callback_data="ready_post"),
                                      types.InlineKeyboardButton(text="Отменить",
                                                                 callback_data="posting_mailing")
                                  ))
        else:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f'Пост выглядит так:\n{admin.post_mail_text}',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(
                                          text=admin.post_mail_text_button,
                                          callback_data=admin.post_mail_url),
                                      types.InlineKeyboardButton(text="Подтвердить",
                                                                 callback_data="ready_post"),
                                      types.InlineKeyboardButton(text="Отменить",
                                                                 callback_data="posting_mailing")
                                  ))

    ###отправка поста
    elif call.data == "ready_post":
        ###В чат
        if admin.post_mail_action == 1 or admin.post_mail_action == 5:
            if len(admin.post_mail_text_button) == 0:
                r = bot.send_message(chat_id=-1001747603263,
                                     text=admin.post_mail_text)
            else:
                r = bot.send_message(chat_id=-1001747603263,
                                     text=admin.post_mail_text,
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(
                                             text=admin.post_mail_text_button,
                                             url=admin.post_mail_url)))

            if admin.post_mail_action == 6:
                bot.pin_chat_message(chat_id=-1001747603263,
                                     message_id=r.id,
                                     disable_notification=admin.post_mail_disable_notification)

        elif admin.post_mail_action == 2 or \
                admin.post_mail_action == 6:
            if len(admin.post_mail_text_button) == 0:
                r = bot.send_message(chat_id=-1001695261290,
                                     text=admin.post_mail_text)
            else:
                r = bot.send_message(chat_id=-1001695261290,
                                     text=admin.post_mail_text,
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(
                                             text=admin.post_mail_text_button,
                                             url=admin.post_mail_url)))
            if admin.post_mail_action == 6:
                bot.pin_chat_message(chat_id=-1001695261290,
                                     message_id=r.id,
                                     disable_notification=admin.post_mail_disable_notification)

        elif admin.post_mail_action == 3 or \
                admin.post_mail_action == 7:
            if admin.post_mail_action == 0:
                r = bot.send_message(chat_id=-1001695261290,
                                     text=admin.post_mail_text)
                m = bot.send_message(chat_id=-1001747603263,
                                     text=admin.post_mail_text)
            else:
                r = bot.send_message(chat_id=-1001695261290,
                                     text=admin.post_mail_text,
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(
                                             text=admin.post_mail_text_button,
                                             url=admin.post_mail_url)))
                m = bot.send_message(chat_id=-1001747603263,
                                     text=admin.post_mail_text,
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(
                                             text=admin.post_mail_text_button,
                                             url=admin.post_mail_url)))
            if admin.post_mail_action == 7:
                bot.pin_chat_message(chat_id=-1001695261290,
                                     message_id=r.id,
                                     disable_notification=admin.post_mail_disable_notification)

                bot.pin_chat_message(chat_id=-1001747603263,
                                     message_id=m.id,
                                     disable_notification=admin.post_mail_disable_notification)

        elif admin.post_mail_action == 4:
            if len(admin.post_mail_text_button) == 0:
                for i in users.data:
                    if i not in admins:
                        bot.send_message(chat_id=i,
                                         text=admin.post_mail_text)

            else:
                for i in users.data:
                    if i not in admins:
                        bot.send_message(chat_id=i,
                                         text=admin.post_mail_text,
                                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                             types.InlineKeyboardButton(
                                                 text=admin.post_mail_text_button,
                                                 url=admin.post_mail_url)))

        admin.post_mail_text_button = ""
        admin.post_mail_action = 0
        admin.post_mail_disable_notification = True
        admin.post_mail_url = ""
        admin.post_mail_text = ""

        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text=f"{start_text}",
                              reply_markup=admin_keyboard,
                              parse_mode='Markdown')

        admin.flag = 4

    elif call.data == "chanel_sale":
        admin.channel_sale_text = ""
        admin.channel_sale_button = []
        admin.channel_sale_count = -1
        r = bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text="Введите пост",
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="назад",
                                                                 callback_data="back_main_admin")
                                  ))
        admin.message_id = r.id
        admin.flag = 35

    elif call.data == "confirm_chanel_sale":
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Нужно добавить кнопку?",
                              reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                  types.InlineKeyboardButton(text="добавить кнопку",
                                                             callback_data="add_chanel_sale"),
                                  types.InlineKeyboardButton(text="не добавлять кнопку",
                                                             callback_data="ready_post_sale")
                              ))

    elif call.data == "add_chanel_sale":
        admin.flag = 37
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Введите название кнопки")

    elif call.data == "change_but_sale":
        admin.flag = 37
        del admin.channel_sale_button[admin.channel_sale_count]
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Введите название кнопки")
        admin.channel_sale_count -= 1

    elif call.data == "add_url_chanel_sale":
        admin.flag = 36
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Введите url")

    elif call.data == "change_url_sale":
        del admin.channel_sale_button[admin.channel_sale_count][1]
        admin.flag = 36
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Введите url")

    elif call.data == "ready_post_sale":
        if len(admin.channel_sale_button) == 0:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f'{admin.channel_sale_text}\nОтправить?',
                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                      types.InlineKeyboardButton(text="отправить",
                                                                 callback_data="send_chanel_sale"),
                                      types.InlineKeyboardButton(text="изменить",
                                                                 callback_data="chanel_sale")
                                  ))
        else:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for i in admin.channel_sale_button:
                keyboard.add(types.InlineKeyboardButton(text=i[0], url=i[1]))
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.id,
                                  text=f'{admin.channel_sale_text}\nОтправить?',
                                  reply_markup=keyboard.add(
                                      types.InlineKeyboardButton(text="отправить",
                                                                 callback_data="send_chanel_sale"),
                                      types.InlineKeyboardButton(text="отменить",
                                                                 callback_data="back_main_admin")
                                  ))

    elif call.data == "send_chanel_sale":
        if len(admin.channel_sale_button) == 0:
            bot.send_message(chat_id=-1001747603263,
                             text=admin.channel_sale_text)
        else:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for i in admin.channel_sale_button:
                keyboard.add(types.InlineKeyboardButton(text=i[0], url=i[1]))
            bot.send_message(chat_id=-1001747603263,
                             text=admin.channel_sale_text,
                             reply_markup=keyboard)

        admin.channel_sale_text = ""
        admin.channel_sale_button = []
        admin.channel_sale_count = -1
        admin.flag = 4

    elif call.data == "infinity_post":
        bot.send_message(chat_id=user_id,
                         text=f"🔳 Вечный пост - сообщение, которое дублируется каждый день путем удаления "
                              f"и повторного постинга в канале, позволяя тем самым быть всегда наверху "
                              f"сообщений чатов и каналов у пользователя\n"
                              f"🔘Кнопка 'Редактировать главное сообщение' - "
                              f"изменить сообщение вечного постинга\n"
                              f"🔘 Кнопка 'Редактировать периодичность' - "
                              f"задать периодичность, в которую сообщение будет удаляться "
                              f"и заново всплывать у пользователя",
                         reply_markup=actions_with_infinity_post)

    elif call.data == "edit_main_mes":
        admin.flag = 7
        bot.send_message(chat_id=user_id,
                         text="Введите новое главное сообщение",
                         reply_markup=actual_verify)

    elif call.data == "edit_period_of_main_mes":
        admin.flag = 8
        bot.send_message(chat_id=user_id,
                         text="Ввведите периодичность отпраки главного сообщения",
                         reply_markup=back_to_infinity_post_keyboard)

    elif call.data == "add_button":
        admin.flag = 15
        bot.send_message(chat_id=user_id,
                         text="Введите текст и ссылку кнопки. Пример:\nАктульные верификации\nhttps://...",
                         reply_markup=actual_verify_composing_new_mes)

    elif call.data == "back_to_composing_mes_actual_verify":
        bot.send_message(chat_id=user_id,
                         text="Выберете клавиатуру, если она нужна. Подтвердите создание нового сообщения или отмените",
                         reply_markup=new_message_for_actual_verify)

    elif call.data == "accept_new_actual_verify_mes":
        admin.flag = 4
        if admin.new_actual_verify_mes["text"] == "" and admin.new_actual_verify_mes["keyboard"] == []:
            bot.send_message(chat_id=actual_verify_channel,
                             text=admin.new_actual_verify_mes["text"])

            bot.send_message(chat_id=user_id,
                             text="Сообщение изменено",
                             reply_markup=admin_keyboard)
            sending_and_deleting_main_message()
        else:
            try:
                bot.send_message(chat_id=actual_verify_channel,
                                 text=admin.new_actual_verify_mes["text"],
                                 reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                     types.InlineKeyboardButton(
                                         text=admin.new_actual_verify_mes["keyboard"][0],
                                         url=admin.new_actual_verify_mes["keyboard"][
                                             1])))  # admin.new_actual_verify_mes_keyboard)
                bot.send_message(chat_id=user_id,
                                 text="Сообщение изменено",
                                 reply_markup=admin_keyboard)
                sending_and_deleting_main_message()
            except:
                bot.send_message(chat_id=user_id,
                                 text="Неверно указана ссылка. Попробуйте создать сообщение заново",
                                 reply_markup=admin_keyboard)

    elif call.data == "deny_new_actual_verify_mes":
        admin.flag = 4
        bot.send_message(chat_id=user_id,
                         text="Добавление нового сообщения в Актуальные верификации отменено",
                         reply_markup=admin_keyboard)

    elif call.data == "accept_to_edit_main_mes":
        admin.flag = 4
        set_main_message["text"] = admin.edit_main_mes
        save_data(set_main_message, "main_mes.json")
        sending_and_deleting_main_message()
        bot.send_message(chat_id=user_id,
                         text="Сообщение изменено",
                         reply_markup=admin_keyboard)

    elif call.data == "back_to_actual_verify":
        bot.send_message(chat_id=user_id,
                         text="Вот что Вы можете сделать в актуальных верификациях",
                         reply_markup=actions_with_infinity_post)

    elif call.data == "deny_editing_main_mes":
        admin.flag = 4
        bot.send_message(chat_id=user_id,
                         text="Изменение отменено",
                         reply_markup=admin_keyboard)

    elif call.data == "accept_to_edit_period_of_main_mes":
        admin.flag = 4
        set_main_message["period"] = admin.edit_period
        message_1.stop_process()
        message_1.start_process()
        save_data(set_main_message, "main_mes.json")
        bot.send_message(chat_id=user_id,
                         text="Периодичность изменена",
                         reply_markup=admin_keyboard)

    elif call.data == "actual":
        bot.send_message(chat_id=user_id,
                         text="Вот что Вы можете сделать в актуальных верификациях",
                         reply_markup=actions_in_actual_verify)

    elif call.data == "new_message_in_actual":
        admin.flag = 12
        bot.send_message(chat_id=user_id,
                         text="Введите новое сообщение",
                         reply_markup=actual_verify)

    elif call.data == "deny_editing_period_ofmain_mes":
        admin.flag = 4
        bot.send_message(chat_id=user_id,
                         text="Изменение периодичности отменено",
                         reply_markup=admin_keyboard)

    elif call.data == "important":
        admin.flag = 17
        bot.send_message(chat_id=user_id,
                         text='Изменение сообщения в канале "Важные правила". Напишите новое сообщение',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="Назад", callback_data='back_main_admin')))

    elif call.data == "back_to_composing_mes_important_rules":
        bot.send_message(chat_id=user_id,
                         text="Выберете клавиатуру, если она нужна. "
                              "Подтвердите создание нового сообщения или отмените",
                         reply_markup=new_message_for_actual_verify)

    elif call.data == "add_button_important_rules":
        admin.flag = 18
        bot.send_message(chat_id=user_id,
                         text="Введите текст и ссылку кнопки. Пример:\nАктульные верификации\nhttps://...",
                         reply_markup=important_rules_composing_new_mes)

    elif call.data == "accept_editing_mes_in_important_rules":
        admin.flag = 4
        if admin.new_important_rules_mes["keyboard"] is None:
            try:
                bot.delete_message(chat_id=important_rules,
                                   message_id=load_data("main_mes_in_important_rules.json")["message_id"])
            except:
                pass
            r = bot.send_message(chat_id=important_rules,
                                 text=admin.new_important_rules_mes["text"])
            save_data({"message_id": r.id}, "main_mes_in_important_rules.json")
            bot.send_message(chat_id=user_id,
                             text="Сообщение изменено",
                             reply_markup=admin_keyboard)
        else:
            try:
                try:
                    bot.delete_message(chat_id=important_rules,
                                       message_id=load_data("main_mes_in_important_rules.json")[
                                           "message_id"])
                except:
                    pass
                r = bot.send_message(chat_id=important_rules,
                                     text=admin.new_important_rules_mes["text"],
                                     reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text=admin.new_important_rules_mes["keyboard"][0],
                                                                    url=admin.new_important_rules_mes["keyboard"][
                                                                        1])))  # admin.new_actual_verify_mes_keyboard)
                save_data({"message_id": r.id}, "main_mes_in_important_rules.json")
                bot.send_message(chat_id=user_id,
                                 text="Сообщение изменено",
                                 reply_markup=admin_keyboard)
            except:
                bot.send_message(chat_id=user_id,
                                 text="Неверно указана ссылка. Попробуйте создать сообщение заново",
                                 reply_markup=admin_keyboard)

    elif call.data == "deny_editing_mes_in_important_rules":
        admin.flag = 4
        bot.send_message(chat_id=user_id,
                         text="Добавление нового сообщения в Важные правила отменено",
                         reply_markup=admin_keyboard)

    elif call.data == "payments":
        ###очистка полей с информацией о способе оплаты
        admin.flag = 4
        admin.payment_method_settings_name = ""
        admin.payment_method_settings_instruction = ""
        bot.send_message(chat_id=user_id,
                         text="Предлагаемые действия",
                         reply_markup=seting_payments_keyboard)

    elif call.data == "new_payment":
        admin.flag = 31
        bot.send_message(chat_id=user_id,
                         text="Введите название способа оплаты (текст кнопки)",
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="Назад", callback_data="payments")))

    elif call.data == "back_to_input_instruction":
        admin.flag = 32
        admin.payment_method_settings_instruction = ""
        bot.send_message(chat_id=user_id,
                         text=f'Вы ввели:\n{admin.payment_method_settings_name}\n\n'
                              f'Введите инструкции для этого способа оплаты',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="Назад", callback_data="new_payment")))

    elif call.data == "save_new_payment_but":
        # Сохранение кнопки в клавиатуру + сохранение клавиатуры в отдельный файл
        pay_keyboard_list[admin.payment_method_settings_name] = \
            admin.payment_method_settings_instruction
        pay_keyboard = list_to_keyboard(pay_keyboard_list)
        pay_keyboard_for_admin = list_to_keyboard(pay_keyboard_list, "_change").add(
            types.InlineKeyboardButton(text="Назад", callback_data="payments"))
        save_data(pay_keyboard_list, "payment_methods.json")
        admin.payment_method_settings_name = ""
        admin.payment_method_settings_instruction = ""
        bot.send_message(chat_id=user_id,
                         text="Предлагаемые действия",
                         reply_markup=seting_payments_keyboard)

    elif call.data == "edit_payment":
        admin.flag = 4
        admin.payment_method_settings_name = ""
        admin.payment_method_settings_instruction = ""
        bot.send_message(chat_id=user_id,
                         text="Предлагаемые действия",
                         reply_markup=pay_keyboard_for_admin)

    elif "_change" in call.data or call.data == "back_to_chose_action_for_method":
        if "_change" in call.data:
            admin.payment_method_settings_name = str(call.data).split("_")[
                0]
        if admin.payment_method_settings_action != "":
            bot.send_message(chat_id=user_id,
                             text=f'{admin.payment_method_settings_name}',
                             reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                 types.InlineKeyboardButton(text="Удалить",
                                                            callback_data="delete_pay_method")).add(
                                 types.InlineKeyboardButton(text="Отмена", callback_data="del_payment")))
        else:
            bot.send_message(chat_id=user_id,
                             text=f'{admin.payment_method_settings_name}',
                             reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                 types.InlineKeyboardButton(text="Изменить название",
                                                            callback_data="edit_payment_method_name")).add(
                                 types.InlineKeyboardButton(text="Изменить инструкцию",
                                                            callback_data="edit_payment_method_instruction")).add(
                                 types.InlineKeyboardButton(text="Назад", callback_data="edit_payment")))

    elif call.data == "edit_payment_method_name":
        admin.flag = 33
        bot.send_message(chat_id=user_id,
                         text=f'Вы выбрали:\n{admin.payment_method_settings_name}\n\n'
                              f'Напишите новое название для способа оплаты',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="Назад",
                                                        callback_data="back_to_chose_action_for_method")))

    elif call.data == "edit_payment_method_instruction":
        admin.flag = 34
        bot.send_message(chat_id=user_id,
                         text=f'Вы выбрали:\n{admin.payment_method_settings_name}\n\n'
                              f'Напишите новую инструкцию для способа оплаты',
                         reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                             types.InlineKeyboardButton(text="Назад",
                                                        callback_data="back_to_chose_action_for_method")))

    elif call.data == "save_new_data_for_pay_method":
        if admin.payment_method_settings_new_name != "":
            pay_keyboard_list[admin.payment_method_settings_new_name] = \
                pay_keyboard_list[admin.payment_method_settings_name]
            del pay_keyboard_list[admin.payment_method_settings_name]
        elif admin.payment_method_settings_new_instruction:
            pay_keyboard_list[admin.payment_method_settings_name] = admin.payment_method_settings_name
        pay_keyboard = list_to_keyboard(pay_keyboard_list)
        pay_keyboard_for_admin = list_to_keyboard(pay_keyboard_list, "_change").add(
            types.InlineKeyboardButton(text="Назад", callback_data="payments"))
        save_data(pay_keyboard_list, "payment_methods.json")
        admin.payment_method_settings_name = ""
        admin.payment_method_settings_instruction = ""
        admin.payment_method_settings_new_name = ""
        admin.payment_method_settings_new_instruction = ""
        admin.flag = 4
        bot.send_message(chat_id=user_id,
                         text="Изменение сохранено. Что-то ещё?",
                         reply_markup=pay_keyboard_for_admin)

    elif call.data == "del_payment":
        admin.flag = 4
        admin.payment_method_settings_action = "del"
        bot.send_message(chat_id=user_id,
                         text="Предлагаемые действия",
                         reply_markup=pay_keyboard_for_admin)

    elif call.data == "delete_pay_method":
        del pay_keyboard_list[admin.payment_method_settings_name]
        pay_keyboard = list_to_keyboard(pay_keyboard_list)
        pay_keyboard_for_admin = list_to_keyboard(pay_keyboard_list, "_change").add(
            types.InlineKeyboardButton(text="Назад", callback_data="payments"))
        save_data(pay_keyboard_list, "payment_methods.json")
        admin.flag = 4
        admin.payment_method_settings_name = ""
        admin.payment_method_settings_instruction = ""
        admin.payment_method_settings_new_name = ""
        admin.payment_method_settings_new_instruction = ""
        bot.send_message(chat_id=user_id,
                         text=f'Кнопка {admin.payment_method_settings_name} удалена',
                         reply_markup=seting_payments_keyboard)
    ################################################

    #######
    ###переход к удалению конкретного задания
    elif call.data == "delete_task":
        bot.send_message(chat_id=call.from_user.id, text="Вы точно хотите удалить это задание?",
                         reply_markup=action_del_task)

    ###подтверждение удаления задания
    elif call.data == "delete_task_finally":
        all_tasks -= admin.task_to_some_act
        bot.answer_callback_query(callback_query_id=call.id,
                                  text="Задание удалено",
                                  show_alert=True)
        bot.send_message(chat_id=call.from_user.id, text="Выберете действие",
                         reply_markup=choice_task)

    ###переход к публикации прошедшего задания
    elif call.data == "past_task":
        if len(all_tasks.get_past_tasks()) == 0:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Нет заданий",
                                      show_alert=True)
            bot.send_message(chat_id=call.from_user.id, text="Выберете действие",
                             reply_markup=choice_task)
        else:
            admin.flag = 45
            admin.count_tasks_keyboard = 0
            bot.send_message(chat_id=call.from_user.id,
                             text="Все задания",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_past_tasks_keyboard(), 0))

    ###отправляет к выбору действия с заданиями
    elif call.data == "tasks_admin":
        bot.send_message(chat_id=call.from_user.id,
                         text="Выберете действие",
                         reply_markup=choice_task)

    ###подтверждение введеной инструкции
    elif call.data == "confirm_inst_task":
        admin.flag = 44
        bot.send_message(chat_id=call.from_user.id, text="Введите стоимость задания",
                         reply_markup=back_instr_task)

    ###подтверждение введенной стоимости задания
    elif call.data == "confirm_cost_task":
        bot.send_message(chat_id=call.from_user.id,
                         text="Выберете один из фильров или пропустите этот этап",
                         reply_markup=filter_task_keyboard)

    ###добавление нового задания
    elif call.data == "add_task":
        admin.flag = 39
        task1 = Task()
        task1.set_id(int(call.message.id))
        bot.send_message(chat_id=call.from_user.id, text="Введите инструкцию",
                         reply_markup=back_choice_task)

    ###начало ветви ввода фильтра по времени
    elif call.data == "tune_time":
        admin.flag = 40
        bot.send_message(chat_id=call.from_user.id, text="Введите время в часах",
                         reply_markup=back_choice_filters)

    ###подтверждение введеного фильтра по времени
    elif call.data == "confirm_filter_time":
        if task1.get_seats() is None:
            bot.send_message(chat_id=call.from_user.id, text=f"Задание:\n{task1.get_str_task()}",
                             reply_markup=end_filter_time)
        else:
            bot.send_message(chat_id=call.from_user.id,
                             text=f"Задание:\n{task1.get_str_task()}",
                             reply_markup=types.InlineKeyboardMarkup(row_width=1).
                             add(types.InlineKeyboardButton(text="готово",
                                                            callback_data="skip_filter")))

    ###начало ветви ввода фильтра по кол-ву мест
    elif call.data == "tune_seats":
        admin.flag = 41
        bot.send_message(chat_id=call.from_user.id, text="Введите кол-во мест",
                         reply_markup=back_choice_filters)

    ###подтверждение введенного фильтра по код-ву мест
    elif call.data == "confirm_filter_seats":
        if task1.get_time() is None:
            bot.send_message(chat_id=call.from_user.id, text=f"Задание:\n{task1.get_str_task()}",
                             reply_markup=end_filter_seats)
        else:
            bot.send_message(chat_id=call.from_user.id,
                             text=f"Задание:\n{task1.get_str_task()}",
                             reply_markup=fire_filter_task)

    ###начало ветви удаления задачи
    elif call.data == "del_task":
        if len(all_tasks.get_actual_tasks()) == 0:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Нет заданий",
                                      show_alert=True)
            bot.send_message(chat_id=call.from_user.id, text="Выберете действие",
                             reply_markup=choice_task)
        else:
            admin.flag = 42
            admin.count_tasks_keyboard = 0
            bot.send_message(chat_id=call.from_user.id,
                             text="Все задания",
                             reply_markup=all_tasks.slider_keyboard(
                                 all_tasks.get_actual_tasks_keyboard(), 0))

    elif call.data == "?back":
        if admin.flag in [42, 45]:
            admin.flag = 4
            bot.send_message(chat_id=call.from_user.id, text="Выберете действие",
                             reply_markup=choice_task)
        elif admin.flag in [43, 46, 47, 48]:
            bot.send_message(chat_id=call.from_user.id, text="Выберете действие",
                             reply_markup=all_tasks.get_choice_tasks_keyboard())

    elif call.data == "?>":
        admin.count_tasks_keyboard += 1
        if admin.flag == 42:
            bot.send_message(chat_id=call.from_user.id,
                             text="Все задания",
                             reply_markup=all_tasks.slider_keyboard(
                                 all_tasks.get_actual_tasks_keyboard(),
                                 admin.count_tasks_keyboard))
        elif admin.flag == 43:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_actual_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))
        elif admin.flag == 46:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_fire_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))
        elif admin.flag == 47:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_time_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))
        elif admin.flag == 48:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_seats_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))

    elif call.data == "?<":
        admin.count_tasks_keyboard -= 1
        if admin.flag == 42:
            bot.send_message(chat_id=call.from_user.id,
                             text="Все задания",
                             reply_markup=all_tasks.slider_keyboard(
                                 all_tasks.get_actual_tasks_keyboard(),
                                 admin.count_tasks_keyboard))
        elif admin.flag == 43:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_actual_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))
        elif admin.flag == 46:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_fire_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))
        elif admin.flag == 47:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_time_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))
        elif admin.flag == 48:
            bot.send_message(chat_id=call.from_user.id,
                             text="Вот список заданий",
                             reply_markup=all_tasks.slider_keyboard(all_tasks.get_seats_tasks_keyboard(),
                                                                    admin.count_tasks_keyboard))

    ###публикация прошедшего задания
    elif call.data == "publish_task":
        all_tasks += task1
        bot.answer_callback_query(callback_query_id=call.id,
                                  text="Задание добавлено!",
                                  show_alert=True)
        bot.send_message(chat_id=call.from_user.id,
                         text="Выберите",
                         reply_markup=choice_task)
        save_object(all_tasks)

    elif call.data == "publish_past_task":
        all_tasks.move_from_past_tasks_to_actual(int(admin.task_to_some_act))
        bot.answer_callback_query(callback_query_id=call.id,
                                  text="Задание опубликовано",
                                  show_alert=True)
        bot.send_message(chat_id=call.from_user.id, text="Выберете действие",
                         reply_markup=choice_task)

    ###пропуск фильтра и публикация задания
    elif call.data == "skip_filter":
        bot.send_message(chat_id=call.from_user.id,
                         text=f"Задание:\n{task1.get_str_task()}",
                         reply_markup=fire_filter_task)

    elif call.data == "setting_fire_filter":
        task1.set_fire(True)
        bot.send_message(chat_id=call.from_user.id,
                         text=f"Задание:\n{task1.get_str_task()}",
                         reply_markup=end_add_task)

    ##########################

    ###возвращение к админ панели
    elif call.data == "back_main_admin":
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.id,
                              text="Вы попали в админ панель!\n"
                                   "Доступные функции:",
                              reply_markup=admin_keyboard)
        default_admin_value(admin)


if __name__ == "__main__":
    print("START")
    #bot.infinity_polling()
    WEBHOOK_LISTEN = "0.0.0.0"
    WEBHOOK_PORT = 80
    SERWER = "62.113.107.20"
    WEBHOOK_SSL_CERT = 'webhook_cert.pem'
    WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    bot.set_webhook(url=f"https://{SERWER}:{WEBHOOK_PORT}/{API_TOKEN}",
                    certificate=open(WEBHOOK_SSL_CERT, "r"))
    print(bot.get_webhook_info())
    app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV), debug=False)
    
