from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запустить', callback_data='monitoring_start_users')
    kb_builder.button(text='Остановить', callback_data='monitoring_stop_users')
    kb_builder.button(text='Настройки', callback_data='settings')
    kb_builder.button(text='Личный Кабинет', callback_data='lk')
    kb_builder.button(text='История', callback_data='get_history')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def start_btns_admin():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запустить', callback_data='monitoring_start_users')
    kb_builder.button(text='Остановить', callback_data='monitoring_stop_users')
    kb_builder.button(text='Настройки', callback_data='settings')
    kb_builder.button(text='Личный Кабинет', callback_data='lk')
    kb_builder.button(text='История', callback_data='get_history')
    kb_builder.button(text='Админ Панель', callback_data='admin_panel')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def admin_panel():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Ключи ChatGPT', callback_data='gpt_accs')
    kb_builder.button(text='Аккаунты Tg', callback_data='tg_accs')
    kb_builder.button(text='Пользователи', callback_data='users_settings')
    kb_builder.button(text='Магазин', callback_data='admin_shop')
    kb_builder.button(text='Мониторинг', callback_data='monitor_settings')
    kb_builder.button(text='Статистика', callback_data='admin_stats')
    kb_builder.button(text='◀️Назад', callback_data='back_to_main')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def monitoring_settings():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запустить', callback_data='monitoring_start')
    kb_builder.button(text='Остановить', callback_data='monitoring_stop')
    kb_builder.button(text='◀️Назад', callback_data='admin_panel')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def settings_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Каналы', callback_data='groups_settings')
    kb_builder.button(text='Telegram аккаунты', callback_data='user_tg_accs_settings')
    kb_builder.button(text='Pro Настойки', callback_data='pro_settings')
    kb_builder.button(text='Уведомления', callback_data='notifications_settings')
    kb_builder.button(text='◀️Назад', callback_data='back_to_main')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def pro_settings_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Триггеры', callback_data='groups_triggers')
    kb_builder.button(text='Промты', callback_data='groups_promts')
    kb_builder.button(text='◀️Назад', callback_data='back_to_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def lk_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Продлить подписку', callback_data='subscribe')
    kb_builder.button(text='Пополнить баланс', callback_data='add_balance')
    kb_builder.button(text='◀️Назад', callback_data='back_to_main')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def users_settings_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='users_add')
    kb_builder.button(text='Удалить', callback_data='users_del')
    kb_builder.button(text='Изменить статус', callback_data='promote_user')
    kb_builder.button(text='Передать аккаунты', callback_data='transfer_acc')
    kb_builder.button(text='◀️Назад', callback_data='admin_panel')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def users_names_btns(users):
    kb_builder = InlineKeyboardBuilder()

    for user_name in users:
        kb_builder.button(text=user_name, callback_data=f'users_del_{user_name}')
    kb_builder.button(text='◀️Назад', callback_data='back_to_users_settings')

    kb_builder.adjust(1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)



def tg_accs_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='tg_accs_add')
    kb_builder.button(text='Удалить', callback_data='tg_accs_del')
    kb_builder.button(text='Монитор', callback_data='tg_accs_monitor')
    kb_builder.button(text='Информация', callback_data='tg_accs_status')
    kb_builder.button(text='◀️Назад', callback_data='admin_panel')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def users_tg_accs_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Выбрать аккаунт', callback_data='choose_acc_user')
    kb_builder.button(text='Мои аккаунты', callback_data='users_accs_get_info')
    kb_builder.button(text='◀️Назад', callback_data='back_to_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)



def tg_back():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='◀️Назад', callback_data='back_to_accs')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def groups_back():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='◀️Назад', callback_data='back_to_groups')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)



def gpt_accs_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='gpt_accs_add')
    kb_builder.button(text='Удалить', callback_data='gpt_accs_del')
    kb_builder.button(text='Статус ключей', callback_data='gpt_accs_info')
    kb_builder.button(text='◀️Назад', callback_data='admin_panel')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def gpt_back():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='◀️Назад', callback_data='back_to_gpt')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def approve():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Понял', callback_data='approve')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def group_settings_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='groups_add')
    kb_builder.button(text='Удалить', callback_data='groups_del')
    kb_builder.button(text='Список каналов', callback_data='groups_info')
    kb_builder.button(text='◀️Назад', callback_data='back_to_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def generate_group_keyboard(groups, operation):
    kb_builder = InlineKeyboardBuilder()

    for group in groups:
        kb_builder.button(text=group, callback_data=f'{operation}[[{group}')
    kb_builder.button(text='◀️Назад', callback_data='back_to_groups')


    kb_builder.adjust(len(groups) // 2 + 1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)

def generate_group_keyboard_tp(groups, operation):
    kb_builder = InlineKeyboardBuilder()

    for group in groups:
        kb_builder.button(text=group, callback_data=f'{operation}[[{group}')
    kb_builder.button(text='◀️Назад', callback_data='pro_settings')


    kb_builder.adjust(len(groups) // 2 + 1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)


def generate_accs_keyboard(accs, operation):
    kb_builder = InlineKeyboardBuilder()

    for acc in accs:
        kb_builder.button(text=acc, callback_data=f'account_{operation}_{acc}')

    kb_builder.button(text='◀️Назад', callback_data='back_to_accs')
    kb_builder.adjust(len(accs) // 2 + 1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)


def generate_accs_keyboard_users(accs, operation):
    kb_builder = InlineKeyboardBuilder()

    for acc in accs:
        kb_builder.button(text=acc, callback_data=f'account_{operation}_{acc}')

    kb_builder.button(text='◀️Назад', callback_data='back_to_users_accs')
    kb_builder.adjust(len(accs) // 2 + 1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)


def generate_gpt_accs_keyboard(accs):
    kb_builder = InlineKeyboardBuilder()

    for acc in accs:
        kb_builder.button(text=acc, callback_data=f'gpt_del_{acc}')
    kb_builder.button(text='◀️Назад', callback_data='back_to_gpt')

    kb_builder.adjust(1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)



def promt_settings():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Изменить', callback_data='group_edit_promt')
    kb_builder.button(text='◀️Назад', callback_data='pro_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def triggers_settings():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='group_add_triggers')
    kb_builder.button(text='Удалить', callback_data='group_del_triggers')
    kb_builder.button(text='◀️Назад', callback_data='pro_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def notifications_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Включить', callback_data='notif_enable')
    kb_builder.button(text='Выключить', callback_data='notif_disable')
    kb_builder.button(text='◀️Назад', callback_data='back_to_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def generate_users_promote(users, operation):
    kb_builder = InlineKeyboardBuilder()

    for user_name in users:
        kb_builder.button(text=user_name, callback_data=f'users_{operation}__{user_name}')
    kb_builder.button(text='◀️Назад', callback_data='users_settings')

    kb_builder.adjust(1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)

def edit_acc_info(account):
    kb_builder = InlineKeyboardBuilder()
    print('acc_edit_name_' + account)
    kb_builder.button(text='Имя', callback_data=f'acc_edit_name_{account}')
    kb_builder.button(text='Фамилия', callback_data=f'acc_edit_surname_{account}')
    kb_builder.button(text='Username', callback_data=f'acc_edit_username_{account}')
    kb_builder.button(text='Bio', callback_data=f'acc_edit_bio_{account}')
    kb_builder.button(text='Аватар', callback_data=f'acc_edit_avatar_{account}')
    kb_builder.button(text='◀️Назад', callback_data=f'user_tg_accs_settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def process_license():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Продолжить👍', callback_data='start_accept_license')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)