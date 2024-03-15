from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from states.states import EditPromts
from database import db
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'groups_promts')
async def promt_choose_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    uid = callback.from_user.id
    groups = await db.db_get_all_telegram_channels(uid)
    await callback.message.answer('Выберите канал: ', reply_markup=kb_admin.generate_group_keyboard_tp(groups,
                                                                                                       'promts'))


@router.callback_query(F.data.startswith('promts'))
async def group_promts(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    group = callback.data.split('[[')[-1]
    await state.update_data(group_name=group)
    promt = await db.db_get_promts_for_group(group) or 'Нет'
    await callback.message.answer(f'<b>Выбрана группа:</b> {group}\n\n'
                                  f'<b>Текущий установленный промт</b>: \n{promt}',
                                  reply_markup=kb_admin.promt_settings(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'group_edit_promt', KnownUser())
async def set_promt(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.answer()
    await state.update_data(message_id=callback.message.message_id)
    data = await state.get_data()
    await callback.message.answer(f'Пожалуйста введите новый промт для группы: {data["group_name"]}',
                                  reply_markup=kb_admin.groups_back())
    await state.set_state(EditPromts.edit_promt)


@router.message(EditPromts.edit_promt)
async def promt_updated(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.db_add_promts_for_group(data["group_name"], message.text)
    await message.answer('Промт успешно установлен.')
    await message.answer('Настройки телеграм каналов: ', reply_markup=kb_admin.pro_settings_btns())
    await state.clear()


