from aiogram.types import CallbackQuery
from aiogram import Router, F
from database import db
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'groups_info', KnownUser())
async def get_all_user_channel_info(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    channels = await db.db_get_all_telegram_channels(uid)
    channels_ids = await db.db_get_all_telegram_ids(uid)
    group_links = await db.db_get_all_telegram_groups(uid)
    data = []
    for g, i, d in zip(channels, channels_ids, group_links):
        data.append(g)
        data.append('<b>ID:</b> ' + str(i)[4:])
        data.append(f'<b>Группа</b>: {d}')
        if data:
            await callback.message.answer('\n'.join(data), parse_mode='HTML')
            data = []
        else:
            await callback.message.answer('Каналы не найдены')



