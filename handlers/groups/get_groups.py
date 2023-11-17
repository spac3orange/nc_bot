from aiogram.types import CallbackQuery
from aiogram import Router, F
from database import db
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'groups_info', KnownUser())
async def get_all_groups(callback: CallbackQuery):
    uid = callback.from_user.id
    groups = await db.db_get_all_telegram_channels(uid)
    group_ids = await db.db_get_all_telegram_ids(uid)
    data = []
    for g, i in zip(groups, group_ids):
        data.append(g)
        data.append('<b>ID:</b> ' + str(i)[4:])

    if data:
        await callback.message.answer('\n'.join(data), parse_mode='HTML')
    else:
        await callback.message.answer('Каналы не найдены.')

