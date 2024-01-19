from aiogram import Router, F
from aiogram.types import CallbackQuery

from data.logger import logger
from filters.known_user import KnownUser
from keyboards import kb_admin

router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'get_history', KnownUser())
async def get_history(callback: CallbackQuery):
    uid = callback.from_user.id
    history_path = f'history/history_{uid}.txt'
    try:
        with open(history_path, encoding='utf-8') as file:
            history = file.read()
            history = history.split('|')
            print(len(history))
            history = history[-10:] if len(history) >= 10 else history
        if history:
            for i in history:
                if len(i) > 1 and i != '\n' and i != ' ' and i != '':
                    detailed = i.split('\n')
                    print(detailed)
                    channel_name = detailed[2].split(':')[-1].strip()
                    acc = detailed[1].split(':')[-1].strip()
                    comment_id = detailed[4].split(':')[-1].strip()
                    print([channel_name, acc, comment_id])
                    await callback.message.answer(i, parse_mode='HTML', reply_markup=kb_admin.delete_comment(channel_name, acc, comment_id),
                                                  disable_web_page_preview=True)
        else:
            await callback.message.answer('История не найдена.')
    except Exception as e:
        logger.error(e)
        await callback.message.answer('История не найдена.')


@router.callback_query(F.data.startswith('delete_comment_'))
async def process_comm_del(callback: CallbackQuery):
    print(callback.data)
    channel_name, acc, comment_id = callback.data.split()[1:]
