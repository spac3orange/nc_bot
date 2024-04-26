from pprint import pprint

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import db, payment_action, accs_shop_action, accs_action
from keyboards import kb_admin
from states.states import BuyAccs
from data.config_telethon_scheme import TelethonSendMessages

router = Router()
router.message.filter(
)


@router.message(Command('post_stories'))
async def p_post_stories(message: Message):
    uid = message.from_user.id
    accs = await accs_action.get_user_accounts(uid)
    for acc in accs:
        sess = TelethonSendMessages(acc)
        await sess.send_story()
        print('completed')
        break
