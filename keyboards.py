from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Тестовая кнопка 1')],
    [KeyboardButton(text='Тестовая кнопка 2'), KeyboardButton(text='Тестовая кнопка 3')]
], resize_keyboard=True)

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Каталог', callback_data='catalog')],
    [InlineKeyboardButton(text='Новости', callback_data='news')],
    [InlineKeyboardButton(text='Профиль', callback_data='person')]
])

test = ["кнопка 1", "кнопка 2", "кнопка 3", "кнопка 4"]

async def test_keyboard():
    builder = InlineKeyboardBuilder()
    for i in test:
        builder.add(InlineKeyboardButton(text=i, url='https://example.com'))
    return builder.adjust(2).as_markup()
