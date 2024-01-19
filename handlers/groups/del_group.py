from aiogram.types import CallbackQuery
from data.logger import logger
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from database import db
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)

@router.callback_query(F.data == 'groups_del', KnownUser())
async def del_input_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    uid = callback.from_user.id
    groups = await db.db_get_all_telegram_channels(uid)
    await callback.message.answer('Выберите канал: ', reply_markup=kb_admin.generate_group_keyboard(groups, 'delete'))


@router.callback_query(F.data.startswith('delete[['))
async def group_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    group = callback.data.split('[[')[-1]
    await db.db_remove_telegram_group(group)
    await callback.message.answer('Канал удален из базы данных.')
    await callback.message.answer('Настройки телеграм каналов:', reply_markup=kb_admin.group_settings_btns())
    logger.info(f'group {group} was deleted from database')
    

# @router.message(DelGroup.input_group)
# async def group_deleted(message: Message, state: FSMContext):
#     group = message.text
#     if await group_in_table(group):
#         await db_remove_telegram_group(group)
#         await message.answer('Группы удалена из базы данных.')
#         await message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
#         logger.info(f'group {group} was deleted from database')
#     else:
#         await message.answer('Группа не найдена в базе данных.')
#         await message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
#         logger.error('group not found')
#     await state.clear()