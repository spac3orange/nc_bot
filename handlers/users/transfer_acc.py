from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import db, accs_action
from filters.is_admin import IsAdmin
from keyboards import kb_admin
from states.states import TranferAcc

router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'transfer_acc')
async def transfer_acc(callback: CallbackQuery, state: FSMContext):
    users = await db.db_get_users()
    operation = 'transfer_acc'
    users_list = []
    for uid, uname, mon, notif in users:
        users_list.append(uname)
    print(users)
    await callback.message.answer('Выберите пользователя для передачи аккаунтов:',
                                  reply_markup=kb_admin.generate_users_promote(users_list, operation))

@router.callback_query(F.data.startswith('users_transfer_acc_'))
async def choose_accs_to_transfer(callback: CallbackQuery, state: FSMContext):
    user_name = callback.data.split('_')[-1]
    user_id = await db.get_user_id_by_username(user_name)
    user_info = await db.get_user_info(user_id)
    user_status = user_info.get('sub_type', None)
    accounts = len(await accs_action.db_get_all_tg_accounts())
    await state.update_data(user_name=user_name, user_id=user_id)
    await callback.message.answer(f'Выбран пользователь <b>{user_name}</b>\n'
                                  f'Уровень подписки: <b>{user_status}</b>\n\n'
                                  f'Введите количество аккаунтов для передачи:\n'
                                  f'Всего аккаунтов доступно: {accounts}', parse_mode='HTML')
    await state.set_state(TranferAcc.input_acc)

@router.message(TranferAcc.input_acc)
async def accs_transfered(message: Message, state: FSMContext):
    state_data = await state.get_data()
    acc_count = int(message.text)
    await accs_action.move_accounts(state_data['user_id'], acc_count)
    await message.answer(f'<b>{acc_count}</b> аккаунтов успешно передано пользователю'
                         f' <b>{state_data["user_name"]}</b>.',
                         reply_markup=kb_admin.users_settings_btns(), parse_mode='HTML')
    await state.clear()



