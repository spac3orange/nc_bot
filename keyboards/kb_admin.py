from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запустить', callback_data='monitoring_start')
    kb_builder.button(text='Остановить', callback_data='monitoring_stop')
    kb_builder.button(text='История', callback_data='get_history')
    kb_builder.button(text='Настройки', callback_data='settings')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def settings_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Аккаунты Tg', callback_data='tg_accs')
    kb_builder.button(text='Аккаунты Gpt', callback_data='gpt_accs')
    kb_builder.button(text='Каналы', callback_data='groups_settings')
    kb_builder.button(text='◀️Назад', callback_data='back_to_main')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def tg_accs_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='tg_accs_add')
    kb_builder.button(text='Удалить', callback_data='tg_accs_del')
    kb_builder.button(text='Монитор', callback_data='tg_accs_monitor')
    kb_builder.button(text='Информация', callback_data='tg_accs_status')
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
    kb_builder.button(text='◀️Назад', callback_data='back_to_settings')

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
    kb_builder.button(text='Триггеры', callback_data='groups_triggers')
    kb_builder.button(text='Промты', callback_data='groups_promts')
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


def generate_accs_keyboard(accs, operation):
    kb_builder = InlineKeyboardBuilder()

    for acc in accs:
        kb_builder.button(text=acc, callback_data=f'account_{operation}_{acc}')
    kb_builder.button(text='◀️Назад', callback_data='back_to_accs')


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
    kb_builder.button(text='◀️Назад', callback_data='back_to_groups')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def triggers_settings():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='group_add_triggers')
    kb_builder.button(text='Удалить', callback_data='group_del_triggers')
    kb_builder.button(text='◀️Назад', callback_data='back_to_groups')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)