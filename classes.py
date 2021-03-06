from telebot import types
from keyboard import keyboards_for_admins
import datetime
import json
import pickle


###сохранение файла в json
def save_data(data, file_name="users_bd.json") -> None:
    with open(file_name, "w+", encoding="UTF-8") as f:
        json.dump(data, f, indent=4)


###загрузка файла из .json
def load_data(file_name="users_bd.json") -> dict:
    with open(file_name, "r+", encoding="UTF-8") as f:
        data = json.load(f)
    return data


def list_to_keyboard(array: dict,
                     target='') -> types.InlineKeyboardMarkup:
    # target: 0 - клавиатура для пользователей; 
    # 1 - клавиатура для админа.
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for method in array:
        keyboard.add(types.InlineKeyboardButton(text=method, callback_data=method + target))
    return keyboard


def editing_call_keyboard(call_message_reply_markup) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in call_message_reply_markup:
        if len(i) == 2:
            keyboard.add(types.InlineKeyboardButton(text=i[0]['text'], callback_data="-"),
                         types.InlineKeyboardButton(text=i[1]['text'], callback_data="-"))
        else:
            keyboard.add(types.InlineKeyboardButton(text=i[0]['text'], callback_data="-"))
    return keyboard


###Класс аккаунта/сервиса
class Service_Account:
    def __init__(self) -> None:
        self.first_mes = ""
        self.second_mes = ""
        self.third_mes = ""
        self.price = 0


###Класс админа
class Admin:
    def __init__(self, admin_lvl: str) -> None:
        self.flag = 4
        self.admin_lvl = admin_lvl  # "moder" | "main" | "manager"
        self.telegraph_name = ''  # telegraph
        self.telegraph_url = ''
        self.telegraph_action = 0
        self.edit_acc_name = ""  # edit_acc
        self.edit_acc_first_mes = ""
        self.edit_acc_second_mes = ""
        self.edit_acc_third_mes = ""
        self.edit_acc_price = 0
        self.post_mail_text = ""  # posting_mailing
        self.post_mail_text_button = ""
        self.post_mail_url = ""
        self.post_mail_action = 0
        self.post_mail_disable_notification = True
        self.channel_sale_text = ""  # channel_sale
        self.channel_sale_button = []
        self.channel_sale_count = -1
        self.procent_name = []  # procent
        self.procent_lvl_1 = 0
        self.procent_lvl_2 = 0
        self.calc_balance = []
        self.message_id = 0  # admin_id
        self.edit_period = 0
        self.edit_main_mes = ""
        self.main_mes = "Главное сообщение"
        self.payment_method_settings = {}
        self.payment_method_settings_name = ""
        self.payment_method_settings_instruction = ""
        self.payment_method_settings_new_name = ""
        self.payment_method_settings_action = ""
        self.payment_method_settings_new_instruction = ""
        self.accounts_to_check = []
        self.new_actual_verify_mes = {"text": '', "keyboard": []}
        self.new_important_rules_mes = {}

        self.task_id = 0
        self.task_answer = ''

    def get_keyboard(self) -> types.InlineKeyboardMarkup:
        return keyboards_for_admins[self.admin_lvl]


###Класс юзера
class User:
    def __init__(self, ref_boss=False, ref_boss_2=False):
        # info
        self.status = True  # Не забанен

        ###
        self.full_registered = False  # Полностью зарегистрирован
        self.changing_complete_name = False  # На изменении ФИО
        self.changing_country_type_document = False  # На изменении списка документов
        self.changing_payment = False  # На изменении реквизитов для выплат
        self.flag = 25  # Флаг/логическая ступень
        self.bot_messageId = 0  # id сообщения от бота

        # info
        self.complete_name = []  # ФИО
        self.payment_method = ""  # Способ выплат
        self.payment_account = ""  # Счёт/номер/реквизиты для выплат
        self.countries = []  # Страны
        self.document_types = []  # Документы
        self.balance = 0  # Текущий баланс
        self.earnings = 0  # all_balance #Весь доход
        self.registration_date = None  # Дата регистрации
        self.date_edit_payment = None  # Дата изменения реквизитов
        self.previous_complete_name = ""

        # referral
        self.referral_link = None  # Реферальная ссылка!
        self.referral_bosses = [ref_boss, ref_boss_2]  # Реферал-боссы
        self.referral_status = "Пользователь"  # Реферальный статус
        self.reward_lvl_1 = 5  # Вознаграждение в процентах за реферала первого уровня
        self.reward_lvl_2 = 1  # Вознаграждение в процентах за реферала второго уровня
        self.referrals_lvl_1 = []  # Рефералы первого уровня id
        self.referrals_lvl_2 = []  # Рефералы второго уровня id

        # accs
        ###Статистика
        self.count_no_verified_accs = 0  # Кол-во неверифицированных аккаунтов
        self.count_verified_paid_accs = 0  # Кол-во верифицированных и оплаченных аккаунтов
        self.count_verified_rejected_accs = 0  # Кол-во верифицированных и отклоненных аккаунтов
        ###~Статистика
        self.accounts_check = {}  # Проверенные аккаунты
        self.count_tasks_keyboard = 0  # Индекс просматриваемой кнопки!
        self.cur_acc = {"key": "", "service_name": ""}  # Текущий аккаунт!
        self.chosen_acc = []  # Выбранный сервис!
        self.current_but = 0  # Текущая кнопка!
        self.current_acc_but = 0  # Текущая кнопка аккаунта!
        # tasks
        self.tasks = {"id_task": 0, "answer": ""}  # Задания!

    # Получение словаря из списка стран и типов документов
    def get_str_countries_and_document_types(self) -> dict:
        countries = ''
        for i in self.countries:
            countries += i.capitalize() + " , "
        countries = countries[0:-2]
        document_types = ''
        for i in self.document_types:
            document_types += i.capitalize() + " , "
        document_types = document_types[0:-2]
        return {"countries": countries, "document_types": document_types}

    def keyboard_with_accs(self) -> types.InlineKeyboardMarkup:
        list_with_accs_buts = self.accounts_check
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        i = self.current_acc_but
        b = len(list_with_accs_buts) - 1
        k = 0
        for m in list_with_accs_buts:
            if i <= k < i + 9:
                if "service_name" in list_with_accs_buts[m]:
                    key = list_with_accs_buts[m]["service_name"]
                else:
                    key = list_with_accs_buts[m]["key"]
                button = types.InlineKeyboardButton(text=f"№{m} {key}", callback_data=f"№{m} {key}")
                keyboard.add(button)
            k += 1
        if i > 8 and b - i >= 9:
            keyboard.add(types.InlineKeyboardButton(text="Назад ⏪", callback_data="!<"),
                         types.InlineKeyboardButton(text="Далее ⏩", callback_data="!>"))
        elif i > 8:
            keyboard.add(types.InlineKeyboardButton(text="Назад ⏪", callback_data="!<"))
        elif b - i >= 9:
            keyboard.add(types.InlineKeyboardButton(text="Далее ⏩", callback_data="!>"))
        return keyboard

    def referrals_by_lvl_to_str(self, lvl: int) -> str:
        response = ''
        if lvl == 1:
            response = 'Уровень 1:\n'
            for i in self.referrals_lvl_1:
                response = response + i + '\n'
        if lvl == 2:
            response = 'Уровень 2:\n'
            for i in self.referrals_lvl_2:
                response = response + i + '\n'
        response = response[0:-1]
        return response

    ###подсчет рфераллов по уровню
    def invited_users(self) -> dict:
        return {"lvl1": str(len(self.referrals_lvl_1)), "lvl2": str(len(self.referrals_lvl_2))}


class Manager:
    def __init__(self) -> None:
        self.accounts_to_check = []
        self.withdraw = []


###Класс нереляционной бд
class nsql_database:
    def __init__(self) -> None:
        self.data = {}

    # Получение значения по ключу
    def get_elem(self, key: int | str) -> User | Admin | Manager | Service_Account | bool:
        if key in self.data:
            return self.data[key]
        else:
            return False


class Admins(nsql_database):
    def __init__(self) -> None:
        super().__init__()

    def __contains__(self, other) -> bool:
        if other in self.data:
            return True
        else:
            return False

    # Добавление админа
    def add_elem(self, id: int, admin_lvl: str) -> bool:
        if admin_lvl in ["main", "moder"]:
            self.data[id] = Admin(admin_lvl)
            return True
        else:
            return False

    def del_elem(self, id: int) -> bool:
        if id in self.data:
            del self.data[id]
            return True
        else:
            return False

    # Получение уровня админа
    def get_admin_lvl(self, id: int) -> str:
        return self.data[id].admin_lvl


class Users(nsql_database):
    def __init__(self) -> None:
        super().__init__()
        self.count_requisites = 0  # Кол-во изменений реквизитов
        self.count_fio = 0  # Кол-во изменений ФИО
        self.count_no_verified = 0
        self.count_verified_paid = 0
        self.count_verified_rejected = 0
        self.all_balance = 0
        self.balance = 0
        self.paid = 0

    def __contains__(self, other) -> bool:
        if other in self.data:
            return True
        else:
            return False

    # Добавление пользователя
    def add_elem(self, id: int, ref_boss: int | bool = False, ref_boss_2: int | bool = False) -> None:
        self.data[id] = User(ref_boss=ref_boss, ref_boss_2=ref_boss_2)

        if ref_boss and ref_boss_2:
            self.get_elem(ref_boss).referrals_lvl_1.append(id)
            self.get_elem(ref_boss_2).referrals_lvl_2.append(id)
        elif ref_boss and not ref_boss_2:
            self.get_elem(ref_boss).referrals_lvl_1.append(id)

    # Получение статуса(забанен ли пользователь?)
    def get_user_status(self, id: int) -> bool:
        return self.data[id].status

    def full_statistic(self) -> dict:
        return {
            "count_user": len(self.data),
            "count_no_verified": self.count_no_verified,
            "count_verified_paid": self.count_verified_paid,
            "count_verified_rejected": self.count_verified_rejected,
            "all_balance": self.all_balance,
            "balance": self.balance,
            "paid": self.paid,
            "count_requisites": self.count_requisites
        }

    ###начисление за рефераллов
    def referral_profit(self, user_id: int, amount: int) -> None:
        referral_lvl_1_id = self.get_elem(user_id).referral_bosses[0]
        referral_lvl_2_id = self.get_elem(user_id).referral_bosses[1]
        if referral_lvl_1_id and referral_lvl_2_id:
            self.get_elem(referral_lvl_1_id).balance += amount * self.get_elem(referral_lvl_1_id).reward_lvl_1 / 100
            self.get_elem(referral_lvl_1_id).earnings += amount * self.get_elem(referral_lvl_1_id).reward_lvl_1 / 100
            self.get_elem(referral_lvl_2_id).balance += amount * self.get_elem(referral_lvl_2_id).reward_lvl_2 / 100
            self.get_elem(referral_lvl_2_id).earnings += amount * self.get_elem(referral_lvl_2_id).reward_lvl_2 / 100
        elif referral_lvl_1_id and not referral_lvl_2_id:
            self.get_elem(referral_lvl_1_id).balance += amount * self.get_elem(referral_lvl_1_id).reward_lvl_1 / 100
            self.get_elem(referral_lvl_1_id).earnings += amount * self.get_elem(referral_lvl_1_id).reward_lvl_1 / 100


# Класс задания
class Task:
    __id = None
    __instruction = None
    __time = None
    __seats = None
    __fire_filter = None
    __send_seats = None
    __confirm_seats = None
    __end_time_task = None
    __cost = None

    def set_id(self, id):
        self.__id = id

    def set_instruction(self, instruction):
        self.__instruction = instruction

    def set_time(self, time):
        self.__end_time_task = datetime.datetime.today() + datetime.timedelta(hours=time)
        self.__time = time

    def change_confirm_seats(self):
        if self.__confirm_seats is None:
            self.__confirm_seats = 1
        else:
            self.__confirm_seats += 1
        self.__send_seats -= 1

    def change_send_seats(self):
        if self.__send_seats is None:
            self.__send_seats = 1
        else:
            self.__send_seats += 1

    def set_seats(self, seats):
        self.__seats = int(seats)
        self.__send_seats = 0
        self.__confirm_seats = 0

    def set_fire(self, fire_filter):
        self.__fire_filter = fire_filter

    def set_cost(self, cost):
        self.__cost = int(cost)

    def get_id(self):
        return self.__id

    def get_instruction(self):
        return self.__instruction

    def get_time(self):
        return self.__time

    def get_end_time_task(self):
        return self.__end_time_task

    def get_seats(self):
        return self.__seats

    def get_fire(self):
        return self.__fire_filter

    def get_send_seats(self):
        return self.__send_seats

    def get_confirm_seats(self):
        return self.__confirm_seats

    def get_cost(self):
        return self.__cost

    def get_str_task(self):
        task = f"Задание №{self.get_id()}\nИнструкция:\n{self.__instruction}\n"
        if self.__time is not None:
            task += f"Время закрытия задания: {self.__end_time_task}\n"
        if self.__seats is not None:
            task += f"Ограничение по местам: {self.__seats}\n"
        if self.__fire_filter is not None and self.__fire_filter is not False:
            task += f"Горящее: Да"
        else:
            task += f"Горящее: Нет"
        return task


# Класс заданий
class Tasks:
    def __init__(self):
        self.__past_tasks = {}  # Прошедшие задания
        self.__actual_tasks = {}  # Все/актуальные задания
        self.__actual_tasks_keyboard = types.InlineKeyboardMarkup(
            row_width=1)  # Клавиатура со всеми/актуальными заданиями
        self.__time_tasks_keyboard = types.InlineKeyboardMarkup(row_width=1)  # Клавиатура с заданиями на время
        self.__seats_tasks_keyboard = types.InlineKeyboardMarkup(row_width=1)  # Клавиатура с заданиями на кол-во мест
        self.__fire_tasks_keyboard = types.InlineKeyboardMarkup(row_width=1)  # Клавиатура с горящими заданиями
        self.__past_tasks_keyboard = types.InlineKeyboardMarkup(row_width=1)  # Клавиатура с прошедшими заданиями

    def set_actual_tasks(self, value):
        self.__actual_tasks = value

    def set_actual_tasks_keyboard(self, value):
        self.__actual_tasks_keyboard = value

    def set_time_tasks_keyboard(self, value):
        self.__time_tasks_keyboard = value

    def set_seats_tasks_keyboard(self, value):
        self.__seats_tasks_keyboard = value

    def set_fire_tasks_keyboard(self, value):
        self.__fire_tasks_keyboard = value

    def set_past_tasks(self, value):
        self.__past_tasks_keyboard = value

    # Функция добавления нового задания / для + и +=
    def __add_task(self, task):
        self.__actual_tasks[task.get_id()] = task
        self.__actual_tasks_keyboard.add(
            types.InlineKeyboardButton(text=f"Задание {task.get_id()}", callback_data=task.get_id()))
        if task.get_seats() is not None:
            self.__seats_tasks_keyboard.add(
                types.InlineKeyboardButton(text=f"Задание {task.get_id()}", callback_data=task.get_id()))
        if task.get_time() is not None:
            self.__time_tasks_keyboard.add(
                types.InlineKeyboardButton(text=f"Задание {task.get_id()}", callback_data=task.get_id()))
        if task.get_fire():
            self.__fire_tasks_keyboard.add(
                types.InlineKeyboardButton(text=f"Задание {task.get_id()}", callback_data=task.get_id()))

        return self

    # Оператор +=
    def __iadd__(self, task):
        return self.__add_task(task)

    # Оператор +
    def __add__(self, task):
        return self.__add_task(task)

    # Функция изменения клавиатуры (удаляется один элемент)
    @staticmethod
    def __del_button(dict_keyboard, task_id):
        new_keyboard = types.InlineKeyboardMarkup()
        for row in dict_keyboard["inline_keyboard"]:
            if row[0]["callback_data"] != task_id:
                new_keyboard.add(
                    types.InlineKeyboardButton(text=row[0]["text"], callback_data=row[0]["callback_data"]))
        return new_keyboard

    # Функция удаления задания / для - и -=
    def __remove_task(self, task_id):
        self.__past_tasks[task_id] = self.__actual_tasks[task_id]
        self.__past_tasks_keyboard.add(
            types.InlineKeyboardButton(text=f"Задание {task_id}", callback_data=task_id))
        del self.__actual_tasks[task_id]
        self.__actual_tasks_keyboard = self.__del_button(self.__actual_tasks_keyboard.to_dict(), task_id)
        if self.__past_tasks[task_id].get_time() is not None:
            self.__time_tasks_keyboard = self.__del_button(self.__time_tasks_keyboard.to_dict(), task_id)
        if self.__past_tasks[task_id].get_seats() is not None:
            self.__seats_tasks_keyboard = self.__del_button(self.__seats_tasks_keyboard.to_dict(), task_id)
        if self.__past_tasks[task_id].get_fire() is not None:
            self.__fire_tasks_keyboard = self.__del_button(self.__fire_tasks_keyboard.to_dict(), task_id)
        return self

    # Оператор -
    def __sub__(self, task_id):
        return self.__remove_task(task_id)

    # Оператор -=
    def __isub__(self, task_id):
        return self.__remove_task(task_id)

    # Удаление элемента из прошедших заданий (публикация прошедших заданий)
    def move_from_past_tasks_to_actual(self, task_id):
        self.__actual_tasks[task_id] = self.__past_tasks[task_id]
        self.__actual_tasks_keyboard.add(
            types.InlineKeyboardButton(text=f"Задание {task_id}", callback_data=task_id))
        del self.__past_tasks[task_id]
        self.__past_tasks_keyboard = self.__del_button(self.__past_tasks_keyboard.to_dict(), task_id)

    def slider_keyboard(self, keyboard, count):
        m = len(keyboard.keyboard)
        # print(m)
        keyboard_page = types.InlineKeyboardMarkup()
        keyboard_page.keyboard = keyboard.keyboard[count * 8:min(8 + count * 8, m)]
        if m > 8:
            if count == 0:
                keyboard_page.add(types.InlineKeyboardButton(text=">", callback_data="?>"))
            elif count == (m - 1) // 8:
                keyboard_page.add(types.InlineKeyboardButton(text="<", callback_data="?<"))
            else:
                keyboard_page.add(types.InlineKeyboardButton(text="<", callback_data="?<"),
                                  types.InlineKeyboardButton(text=">", callback_data="?>"))
        keyboard_page.add(types.InlineKeyboardButton(text="Назад", callback_data="?back"))
        return keyboard_page

    def get_actuals(self):
        return self.__actual_tasks

    def get_actual_tasks_keyboard(self):
        return self.__actual_tasks_keyboard

    def get_time_tasks_keyboard(self):
        return self.__time_tasks_keyboard

    def get_seats_tasks_keyboard(self):
        return self.__seats_tasks_keyboard

    def get_fire_tasks_keyboard(self):
        return self.__fire_tasks_keyboard

    def get_actual_tasks(self):
        return self.__actual_tasks

    def get_past_tasks(self):
        return self.__past_tasks

    def get_choice_tasks_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        if len(self.__actual_tasks_keyboard.keyboard) != 0:
            keyboard.add(types.InlineKeyboardButton(text="📝 Все задания", callback_data="all_task_user"))
            if len(self.__fire_tasks_keyboard.keyboard) != 0:
                keyboard.add(types.InlineKeyboardButton(text="🔥 Горящие задания", callback_data="fire_task_user"))
            if len(self.__seats_tasks_keyboard.keyboard) != 0:
                keyboard.add(
                    types.InlineKeyboardButton(text="0️⃣1️⃣ Лимитированные задания", callback_data="task_seats_user"))
            if len(self.__time_tasks_keyboard.keyboard) != 0:
                keyboard.add(types.InlineKeyboardButton(text="🕰 Временные задания", callback_data="task_time_user"))
            return keyboard
        else:
            return None

    def get_past_tasks_keyboard(self):
        return self.__past_tasks_keyboard


###Класс Аккаунтов/сервисов
class Services_Accounts(nsql_database):
    def __init__(self) -> None:
        super().__init__()

    def keyboard_init(self, user: User) -> types.InlineKeyboardMarkup:
        list_with_accs_buts = self.data
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        i = user.current_but
        b = len(list_with_accs_buts) - 1
        k = 0
        for m in list_with_accs_buts:
            if i <= k < i + 9:
                button = types.InlineKeyboardButton(text=m, callback_data=m)
                keyboard.add(button)
            k += 1
        if i > 8 and b - i >= 9:
            keyboard.add(types.InlineKeyboardButton(text="Назад ⏪", callback_data="<"),
                         types.InlineKeyboardButton(text="Далее ⏩", callback_data=">"))
        elif i > 8:
            keyboard.add(types.InlineKeyboardButton(text="Назад ⏪", callback_data="<"))
        elif b - i >= 9:
            keyboard.add(types.InlineKeyboardButton(text="Далее ⏩", callback_data=">"))
        return keyboard


class Managers(nsql_database):
    def __init__(self) -> None:
        super().__init__()

    def add_elem(self, id: int, ) -> None:
        self.data[id] = Manager()


def save_object(data, file_name="tasks.pkl") -> None:
    with open(file_name, "wb+") as fp:
        pickle.dump(data, fp)


def load_object(file_name="tasks.pkl") -> Admins | Users | Tasks | Services_Accounts | nsql_database:
    with open(file_name, "rb+") as fp:
        data = pickle.load(fp)
    return data
