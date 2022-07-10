from telebot import types

pay_keyboard = types.InlineKeyboardMarkup(row_width=1)
qiwi = types.InlineKeyboardButton(text="QIW📲I", callback_data="QIWI")
other_pay = types.InlineKeyboardButton(text="ДРУГОЕ", callback_data="other_pay")
pay_keyboard.add(qiwi, other_pay)

back_pay = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад🔙", callback_data="back_pay"))

country_keyboard = types.InlineKeyboardMarkup(row_width=2)
rus = types.InlineKeyboardButton(text="РОССИЯ", callback_data="РОССИЯ")
bel = types.InlineKeyboardButton(text="БЕЛАРУСЬ", callback_data="БЕЛАРУСЬ")
uak = types.InlineKeyboardButton(text="УКРАИНА", callback_data="УКРАИНА")
kaz = types.InlineKeyboardButton(text="КАЗАХСТАН", callback_data="КАЗАХСТАН")
azer = types.InlineKeyboardButton(text="АЗЕРБАЙДЖАН", callback_data="АЗЕРБАЙДЖАН")
arm = types.InlineKeyboardButton(text="АРМЕНИЯ", callback_data="АРМЕНИЯ")
kir = types.InlineKeyboardButton(text="КИРГЫЗСТАН", callback_data="КИРГЫЗСТАН")
latvia = types.InlineKeyboardButton(text="ЛАТВИЯ", callback_data="ЛАТВИЯ")
litva = types.InlineKeyboardButton(text="ЛИТВА", callback_data="ЛИТВА")
mol = types.InlineKeyboardButton(text="МОЛДОВА", callback_data="МОЛДОВА")
usa = types.InlineKeyboardButton(text="США", callback_data="США")
uzb = types.InlineKeyboardButton(text="УЗБЕКИСТАН", callback_data="УЗБЕКИСТАН")
country_keyboard.add(rus, bel, uak, kaz, azer, arm, kir, latvia, litva, mol, usa, uzb)
country_keyboard.add(types.InlineKeyboardButton(text="ПРОДОЛЖИТЬ", callback_data="save"))

document_keyboard = types.InlineKeyboardMarkup(row_width=1)
pasport = types.InlineKeyboardButton(text="ПАСПОРТ ГРАЖДАНИНА",callback_data="ВНУТРЕННИЙ ПАСПОРТ ГРАЖДАНИНА")
extract_bank = types.InlineKeyboardButton(text="ВЫПИСКА ИЗ БАНКА", callback_data="ВЫПИСКА ИЗ БАНКА")
other_document = types.InlineKeyboardButton(text="ДРУГИЕ ДОКУМЕНТЫ", callback_data="ДРУГИЕ ДОКУМЕНТЫ")
overseas_pasport = types.InlineKeyboardButton(text="ЗАГРАНИЧНЫЙ ПАСПОРТ", callback_data="ЗАГРАНИЧНЫЙ ПАСПОРТ")
driver_license = types.InlineKeyboardButton(text="ВОДИТЕЛЬСКИЕ ПРАВА", callback_data="УДОСТОВЕРЕНИЕ ВОДИТЕЛЯ")
document_keyboard.add(pasport, extract_bank, other_document, overseas_pasport, driver_license,
                      types.InlineKeyboardButton(text="ПРОДОЛЖИТЬ", callback_data="save1"))

subcribe_keyboard = types.InlineKeyboardMarkup(row_width=1)
first_chat = types.InlineKeyboardButton(text='♻️ Актуальные верификации', url="https://t.me/bistroinfo")
second_chat = types.InlineKeyboardButton(text='📚 Правила ', url="https://t.me/+Q5kiUhfDdMg1ZDVk")
ready = types.InlineKeyboardButton(text='🟢 Начать работу!', callback_data="ready")
subcribe_keyboard.add(first_chat, second_chat, ready)

manager_keyboard = types.InlineKeyboardMarkup(row_width=1)
check_acc = types.InlineKeyboardButton(text="Взять заявку на рассмотрение", callback_data='check_acc')
manager_keyboard.add(check_acc)

manager_keyboard_2 = types.InlineKeyboardMarkup(row_width=1)
accepted = types.InlineKeyboardButton(text="Принять заявку", callback_data='accepted')
deny = types.InlineKeyboardButton(text="Отклонить заявку", callback_data='deny')
manager_keyboard_2.add(accepted, deny)

withdraw_keyboard = types.InlineKeyboardMarkup(row_width=1)
check_withdraw = types.InlineKeyboardButton(text="Взять заявку на рассмотрение", callback_data='check_withdraw')
withdraw_keyboard.add(check_withdraw)

withdraw_keyboard_2 = types.InlineKeyboardMarkup(row_width=1)
complete_withdraw = types.InlineKeyboardButton(text="Принять заявку", callback_data='complete_withdraw')
deny_withdraw = types.InlineKeyboardButton(text="Отклонить заявку", callback_data='deny_withdraw')
withdraw_keyboard_2.add(check_withdraw, deny_withdraw)

start_keyboard = types.ReplyKeyboardMarkup(row_width=3).add(types.KeyboardButton("✅ Загрузить аккаунт")).add(
    types.KeyboardButton('Задания')).add(
    types.KeyboardButton("♻️ Загруженные аккаунты"),
    types.KeyboardButton("📕 Как пользоваться ботом?"),
    types.KeyboardButton("📊 Статистика"),
    types.KeyboardButton("📣 Партнерская программа"),
    types.KeyboardButton("📚 Support & FAQ"),
    types.KeyboardButton("👤 Профиль"),
    types.KeyboardButton("💤 Перезагрузка"))

start_admin_keyboard = types.ReplyKeyboardMarkup(row_width=2).add(types.KeyboardButton("✅ Загрузить аккаунт"),
                                                                  types.KeyboardButton("♻️ Загруженные аккаунты")).add(
    types.KeyboardButton('🏵 Задания')).add(
    types.KeyboardButton("📕 Как пользоваться ботом?"),
    types.KeyboardButton("📊 Статистика")).add(
    types.KeyboardButton("📣 Партнерская программа"),
    types.KeyboardButton("👤 Профиль"),
    types.KeyboardButton("💤 Перезагрузка"),
    types.KeyboardButton("Админ панель"))

sup_program_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Вывести", callback_data="withdraw")).add(
    types.InlineKeyboardButton(text="Привлечены тобой", callback_data="referrals"))

profile_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Изменить анкету", callback_data="edit_user_data")).add(
    types.InlineKeyboardButton(text="Изменить реквизиты", callback_data="edit_payment_account")).add(
    types.InlineKeyboardButton(text="Изменить ФИО", callback_data="edit_complete_name")).add(
    types.InlineKeyboardButton(text="Вывести", callback_data="withdraw"))

keyboard_loading_accs = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Отмена 🛑", callback_data="Отмена 🛑")).add(
    types.InlineKeyboardButton(text="Главное меню 🏡", callback_data="Главное меню 🏡"))

keyboard_with_accs = types.InlineKeyboardMarkup(row_width=2).add(
    types.InlineKeyboardButton(text="Как пользоваться ботом?", callback_data="using_bot"))

support_faq_start_keyboard = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton("FAQ"),
                                                                        types.KeyboardButton("Инструкции"))

faq_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Какие аккаунты подходя для загрузки в БОТ?",
                               url="https://telegra.ph/Kakie-akkaunty-podhodyat-dlya-zagruzki-v-bot-03-22")).add(
    types.InlineKeyboardButton(text="Как загрузить готовый аккаунт в БОТ?",
                               url="https://telegra.ph/Kak-zagruzit-gotovyj-akkaunt-v-bot-03-22")).add(
    types.InlineKeyboardButton(text="Как происходит проверка аккаунтов?",
                               url="https://telegra.ph/Kak-proishodit-proverka-akkauntov-03-22")).add(
    types.InlineKeyboardButton(text="Куда происходит оплата?",
                               url="https://telegra.ph/Kuda-proishodit-oplata-03-22"))

instruction_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Paxful",
                               url="https://telegra.ph/Verifikaciya-Paxful-03-21")).add(
    types.InlineKeyboardButton(text="Bitzlato",
                               url="https://telegra.ph/Verifikaciya-Bitzlato-03-21")).add(
    types.InlineKeyboardButton(text="Crypto",
                               url="https://telegra.ph/Verifikaciya-crypto-03-21")).add(
    types.InlineKeyboardButton(text="Huobi",
                               url="https://telegra.ph/Verifikaciya-Huobi-03-22")).add(
    types.InlineKeyboardButton(text="Bunq",
                               url="https://telegra.ph/Verifikaciya-Binance-03-22-2")).add(
    types.InlineKeyboardButton(text="Currency",
                               url="https://telegra.ph/Verifikaciya-Currency-03-20")).add(
    types.InlineKeyboardButton(text="Paxum",
                               url="https://telegra.ph/Verifikaciya-Wirex-03-19")).add(
    types.InlineKeyboardButton(text="Coinmama",
                               url="https://telegra.ph/Verifikaciya-Coinmama-03-19")).add(
    types.InlineKeyboardButton(text="Quppy",
                               url="https://telegra.ph/Verifikaciya-Quppy-03-19")).add(
    types.InlineKeyboardButton(text="Aximetria",
                               url="https://telegra.ph/Verifikaciya-Aximetria-03-19")).add(
    types.InlineKeyboardButton(text="Регистрация почты tutanota.com",
                               url="https://telegra.ph/Registraciya-pochty-tutanotacom-03-18")).add(
    types.InlineKeyboardButton(text="Получение выписки из банка",
                               url="https://telegra.ph/Poluchenie-vypiski-iz-banka-03-16"))

admin_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="👥 Пользователи", callback_data="user")).add(
    types.InlineKeyboardButton(text="✅ Правка акки для загрузки", callback_data="edit_account")).add(
    types.InlineKeyboardButton(text="♻️ Правка актуальные верификации", callback_data="actual")).add(
    types.InlineKeyboardButton(text="📚 Правка правила (добавление)", callback_data="important")).add(
    types.InlineKeyboardButton(text="🏷 Правка акции (добавление)", callback_data="chanel_sale")).add(
    types.InlineKeyboardButton(text="⚙️ Инструкции", callback_data="edit_button_instr")).add(
    types.InlineKeyboardButton(text="🕰 Вечный пост", callback_data="infinity_post")).add(
    types.InlineKeyboardButton(text="📤 Постинг | Рассылка", callback_data="posting_mailing")).add(
    types.InlineKeyboardButton(text="💸 Способы выплат (правка)", callback_data="payments")).add(
    types.InlineKeyboardButton(text="🏵 Задания (правка)", callback_data="tasks_admin")).add(
    types.InlineKeyboardButton(text="Добавить/удалить админа/модератора", callback_data="action_admin_moder"))


user_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="индивид. процент", callback_data="indiv_procent")).add(
    types.InlineKeyboardButton(text="блок/разблок пользователя", callback_data="edit_status_user")).add(
    types.InlineKeyboardButton(text="статистика", callback_data="statistics")).add(
    types.InlineKeyboardButton(text="начисление баланса", callback_data="calc_balance")).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

###
instr_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Изменить url кнопки", callback_data="edit_url")).add(
    types.InlineKeyboardButton(text="Добавить кнопку", callback_data="append_url")).add(
    types.InlineKeyboardButton(text="Удалить кнопку", callback_data="remove_url")).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

account_admin_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Добавить аккаунт", callback_data="append_acc")).add(
    types.InlineKeyboardButton(text="Удалить аккаунт", callback_data="remove_acc")).add(
    types.InlineKeyboardButton(text="Изменить стоимость", callback_data="change_cost")).add(
    types.InlineKeyboardButton(text='назад', callback_data="back_main_admin"))
###
block_unblock = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text='заблокировать',
                               callback_data="block"),
    types.InlineKeyboardButton(text='разблокировать',
                               callback_data="unblock"),
    types.InlineKeyboardButton(text='назад', callback_data="back_user_keyboard"))

sup_check = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Ответить на вопрос",
                               callback_data="sup_check"),
    types.InlineKeyboardButton(text="Забанить пользователя",
                               callback_data="sup_ban"))

actions_with_infinity_post = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Редактировать главное сообщение", callback_data="edit_main_mes")).add(
    types.InlineKeyboardButton(text="Редактировать периодичность", callback_data="edit_period_of_main_mes")).add(
    types.InlineKeyboardButton(text="назад", callback_data='back_main_admin'))

actions_in_actual_verify = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Редактировать главное сообщение", callback_data="edit_main_mes")).add(
    types.InlineKeyboardButton(text="Добавить сообщение", callback_data="new_message_in_actual")).add(
    types.InlineKeyboardButton(text="назад", callback_data='back_main_admin'))
editing_main_mes_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Подтвердить", callback_data="accept_to_edit_main_mes")).add(
    types.InlineKeyboardButton(text="Отменить", callback_data="deny_editing_main_mes"))

editing_period_of_main_mes_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Подтвердить", callback_data="accept_to_edit_period_of_main_mes")).add(
    types.InlineKeyboardButton(text="Отменить", callback_data="deny_editing_period_ofmain_mes"))

new_message_for_actual_verify = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Подтвердить", callback_data="accept_new_actual_verify_mes")).add(
    types.InlineKeyboardButton(text="Отменить", callback_data="deny_new_actual_verify_mes")).add(
    types.InlineKeyboardButton(text="Добавить кнопку-ссылку", callback_data="add_button"))

editing_mes_in_important_rules = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Подтвердить", callback_data="accept_editing_mes_in_important_rules")).add(
    types.InlineKeyboardButton(text="Отменить", callback_data="deny_editing_mes_in_important_rules")).add(
    types.InlineKeyboardButton(text="Добавить кнопку-ссылку", callback_data="add_button_important_rules"))

statistics_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="одного пользователя", callback_data="one_user")).add(
    types.InlineKeyboardButton(text="общая статистика", callback_data="full_statistics")).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_user_keyboard"))

action_insrt = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="yes_action")).add(
    types.InlineKeyboardButton(text="отменить", callback_data="no_action"))

filling_user_payment_acc_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="ПОДТВЕРДИТЬ", callback_data="next_step_in_reg")).add(
    types.InlineKeyboardButton(text="ИЗМЕНИТЬ", callback_data="edit_payment_acc_step_back"))

actual_verify = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

back_main_admin = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

actual_verify_composing_new_mes = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_to_composing_mes_actual_verify"))

important_rules_composing_new_mes = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_to_composing_mes_important_rules"))

back_to_infinity_post_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="НАЗАД", callback_data="infinity_post"))

posting_mailing = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Постинг", callback_data="posting"),
    types.InlineKeyboardButton(text="Постинг с закрепом", callback_data="posting_pin"),
    types.InlineKeyboardButton(text="Рассылка", callback_data="mailing"),
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

seting_payments_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="ДОБАВИТЬ", callback_data="new_payment")).add(
    types.InlineKeyboardButton(text="ИЗМЕНИТЬ", callback_data="edit_payment")).add(
    types.InlineKeyboardButton(text="УДАЛИТЬ", callback_data="del_payment")).add(
    types.InlineKeyboardButton(text="Назад", callback_data='back_main_admin'))

####клавиатура для заданий
###сторона админа
choice_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="добавить задание", callback_data="add_task")).add(
    types.InlineKeyboardButton(text="удалить задание", callback_data="del_task")).add(
    types.InlineKeyboardButton(text="прошедшие задания", callback_data="past_task")).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

##клавиатуры для добавления задания
#возвращает к выбору действия
back_choice_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="tasks_admin"))

#подтвердить или изменить введенную инструкцию
inst_task_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="confirm_inst_task")).add(
    types.InlineKeyboardButton(text="изменить", callback_data="add_task"))

back_instr_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="изменить", callback_data="add_task"))

#Подтвердить/изменить стоимость задания
cost_task_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="confirm_cost_task")).add(
    types.InlineKeyboardButton(text="изменить", callback_data="confirm_inst_task"))


#выбор фильтров для задания
filter_task_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="настроить время", callback_data="tune_time")).add(
    types.InlineKeyboardButton(text="настроить кол-во мест", callback_data="tune_seats")).add(
    types.InlineKeyboardButton(text="пропустить", callback_data="skip_filter"))

##фильтр по времени
#возврат к выбору фильтра для задания
back_choice_filters = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="confirm_inst_task"))

#подтверждение или изменение введеного фильтра по времени
act_filter_time = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="confirm_filter_time")).add(
    types.InlineKeyboardButton(text="изменить", callback_data="tune_time"))

#возможность выбрать ещё один фильтр или пропустить
end_filter_time = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="настроить кол-во мест", callback_data="tune_seats")).add(
    types.InlineKeyboardButton(text="пропустить", callback_data="skip_filter"))

##фильтр по кол-ву мест
#для возврата к выбору действия использовать клавиатуру "back_choice_task"

#подтверждение или изменение введеного фильтра по кол-ву мест
act_filter_seats = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="confirm_filter_seats")).add(
    types.InlineKeyboardButton(text="изменить", callback_data="tune_seats"))

#возможность выбрать ещё один фильтр или пропустить
end_filter_seats = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="настроить по времени", callback_data="tune_time")).add(
    types.InlineKeyboardButton(text="пропустить", callback_data="skip_filter"))

end_add_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="опубликовать", callback_data="publish_task")).add(
    types.InlineKeyboardButton(text="отменить", callback_data="add_task"))
##клавиатуры для удаления задания
act_del_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="удалить", callback_data="delete_task")).add(
    types.InlineKeyboardButton(text="назад", callback_data="del_task"))

action_del_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="да", callback_data="delete_task_finally")).add(
    types.InlineKeyboardButton(text="нет", callback_data="del_task"))

##клавиатуры для прошедших заданий
act_past_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="опубликовать", callback_data="publish_past_task")).add(
    types.InlineKeyboardButton(text="назад", callback_data="past_task"))

fire_filter_task = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="сделать задание горящим", callback_data="setting_fire_filter")).add(
    types.InlineKeyboardButton(text="пропустить", callback_data="publish_task"))

## клавиатура для возвращения в раздел "Правки акки для загрузки"
back_to_edit_account_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Назад", callback_data="back_edit_account"))

change_action_admin_moder_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="добавить админа", callback_data="app_admin"),
    types.InlineKeyboardButton(text="добавить модератора", callback_data="app_moder"),
    types.InlineKeyboardButton(text="удалить", callback_data="del_admin_moder"),
    types.InlineKeyboardButton(text="назад", callback_data="back_main_admin"))

end_app_admin_moder_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="complete_admin_moder"),
    types.InlineKeyboardButton(text="изменить", callback_data="change_admin_moder"),
    types.InlineKeyboardButton(text="назад", callback_data="action_admin_moder"))


keyboards_for_admins = {
    'main': "haha",#types.InlineKeyboardMarkup(1),
    'moder': "hoho",#types.InlineKeyboardMarkup(2),
    'manager': "hihi"#types.InlineKeyboardMarkup(3)
}