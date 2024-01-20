from aiogram import Router, F
from aiogram.types import CallbackQuery

from data.logger import logger
from data.config_telethon_scheme import TelethonSendMessages
from filters.known_user import KnownUser
from keyboards import kb_admin
from database import accs_action, db
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
                    group_id = detailed[4].split(':')[-1].strip().split(',')[-1].strip()
                    acc = detailed[1].split(':')[-1].strip()
                    comment_id = detailed[4].split(':')[-1].strip().split(',')[0].strip()
                    print([group_id, acc, comment_id])
                    await callback.message.answer(i, parse_mode='HTML', reply_markup=kb_admin.delete_comment(group_id, acc, comment_id),
                                                  disable_web_page_preview=True)
        else:
            await callback.message.answer('История не найдена.')
    except Exception as e:
        logger.error(e)
        await callback.message.answer('История не найдена.')


@router.callback_query(F.data.startswith('delete_comment///'))
async def process_comm_del(callback: CallbackQuery):
    print(callback.data.split('///'))
    data = callback.data.split('///')
    group_id, acc, comment_id = data[1], data[2], data[3]
    all_basic_users = await db.get_user_ids_by_sub_type('DEMO')
    uid = callback.from_user.id
    if uid in all_basic_users:
        table = 'telegram_accounts'
    else:
        table = f'accounts_{uid}'
    acc_status = await accs_action.get_in_work_status(acc, table)
    if not acc_status:
        print(f'acc {acc}')
        session = TelethonSendMessages(acc)
        await session.delete_comment(int(group_id), comment_id, uid)
    else:
        await callback.message.answer('Аккаунт в работе. Пожалуйста, попробуйте еще раз через 30 секунд.')


