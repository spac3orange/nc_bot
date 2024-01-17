from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import default_prompts_action
from filters.is_admin import IsAdmin
from keyboards import kb_admin
from states import states

router = Router()
router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'change_default_prompt')
async def process_default_promt(callback: CallbackQuery):
    default_promt = await default_prompts_action.get_all_default_prompts() or 'Нет'

    if default_promt == 'Нет':
        await callback.message.answer('<b>Список текущих промтов по умолчанию:</b> Нет', parse_mode='HTML')
        await callback.message.answer('Выберите действие: ', reply_markup=kb_admin.default_prompts())
    else:
        await callback.message.answer('<b>Список текущих промтов по умолчанию:</b> ', parse_mode='HTML')
        for i, v in enumerate(default_promt, 1):
            await callback.message.answer(f'\n{i}. {v}')
        await callback.message.answer('Выберите действие: ', reply_markup=kb_admin.default_prompts())


@router.callback_query(F.data == 'def_prompt_add')
async def process_add_def_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новый промт: ')
    await state.set_state(states.ChangeDefPromt.add_promt)
@router.message(states.ChangeDefPromt.add_promt)
async def def_promt_added(message: Message, state: FSMContext):
    await message.answer('Промт добавлен в список промтов по умолчанию.')
    promt_text = message.text
    await default_prompts_action.add_default_prompt(promt_text)
    await state.clear()

    default_promt = await default_prompts_action.get_all_default_prompts() or 'Нет'
    if default_promt == 'Нет':
        await message.answer('<b>Список текущих промтов по умолчанию:</b> Нет', parse_mode='HTML')
        await message.answer('Выберите действие: ', reply_markup=kb_admin.default_prompts())
    else:
        await message.answer('<b>Список текущих промтов по умолчанию:</b> ', parse_mode='HTML')
        for i, v in enumerate(default_promt, 1):
            await message.answer(f'\n{i}. {v}')
        await message.answer('Выберите действие: ', reply_markup=kb_admin.default_prompts())


@router.callback_query(F.data == 'def_prompt_del')
async def process_del_def_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.ChangeDefPromt.del_promt)
    await callback.message.answer('Введите номер промта для удаления: ')

@router.message(states.ChangeDefPromt.del_promt)
async def process_del_def_prompt(message: Message, state: FSMContext):
    promt = message.text
    if promt.isdigit():
        await default_prompts_action.delete_default_prompt(int(promt))
        await message.answer('Промт успешно удален из списка промтов по умолчанию.')

        default_promt = await default_prompts_action.get_all_default_prompts() or 'Нет'
        if default_promt == 'Нет':
            await message.answer('<b>Список текущих промтов по умолчанию:</b> Нет', parse_mode='HTML')
            await message.answer('Выберите действие: ', reply_markup=kb_admin.default_prompts())
        else:
            await message.answer('<b>Список текущих промтов по умолчанию:</b> ', parse_mode='HTML')
            for i, v in enumerate(default_promt, 1):
                await message.answer(f'\n{i}. {v}')
            await message.answer('Выберите действие: ', reply_markup=kb_admin.default_prompts())
    else:
        await message.answer('Ошибка! Введите номер промта для удаления, например: 1'
                             '\n\nОтменить /cancel')
