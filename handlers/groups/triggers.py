from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from states.states import Triggers
from database import db
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'groups_triggers', KnownUser())
async def trigger_choose_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    uid = callback.from_user.id
    groups = await db.db_get_all_telegram_channels(uid)
    await callback.message.answer('Выберите канал: ', reply_markup=kb_admin.generate_group_keyboard_tp(groups,
                                                                                                     'triggers'))


@router.callback_query(F.data.startswith('triggers'))
async def group_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    group = callback.data.split('[[')[-1]
    await state.update_data(group_name=group)
    triggers = await db.db_get_triggers_for_group(group) or 'Нет'

    await callback.message.answer(f'Выбрана группа: {group}\n\n'
                                  f'Установленные триггеры: \n\n{triggers}',
                                  reply_markup=kb_admin.triggers_settings())


@router.callback_query(F.data == 'group_add_triggers')
async def add_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    await callback.message.answer('Введите добавляемые триггеры через запятую:')
    await state.set_state(Triggers.add_trigger)


@router.message(Triggers.add_trigger)
async def triggers_added(message: Message, state: FSMContext):
    data = await state.get_data()
    triggers = message.text.lower().split(',')
    triggers = [x.strip() for x in triggers]
    await db.db_add_trigger_for_group(data["group_name"], triggers)
    await message.answer('Триггеры успешно обновлены.', reply_markup=kb_admin.pro_settings_btns())
    await state.clear()


@router.callback_query(F.data == 'group_del_triggers')
async def del_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    await callback.message.answer('Введите удаляемые триггеры через запятую:')
    await state.set_state(Triggers.del_trigger)


@router.message(Triggers.del_trigger)
async def triggers_deleted(message: Message, state: FSMContext):
    data = await state.get_data()
    triggers = message.text.lower().split(',')
    triggers = [x.strip() for x in triggers]
    await db.db_remove_triggers_for_group(data["group_name"], triggers)
    await message.answer('Триггеры успешно обновлены.', reply_markup=kb_admin.pro_settings_btns())
    await state.clear()