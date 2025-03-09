from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Главное меню
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Привет')],
        [KeyboardButton(text='Пока')]
    ],
    resize_keyboard=True
)

# Клавиатура с URL-ссылками
inline_links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Новости', url='https://news.example.com')],
        [InlineKeyboardButton(text='Музыка', url='https://music.example.com')],
        [InlineKeyboardButton(text='Видео', url='https://video.example.com')]
    ]
)

# Динамическая клавиатура
def dynamic_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Показать больше', callback_data='show_more'))
    return builder.as_markup()

# Расширенная клавиатура после "Показать больше"
def expanded_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Опция 1', callback_data='option_1'))
    builder.add(InlineKeyboardButton(text='Опция 2', callback_data='option_2'))
    return builder.as_markup()

test = ["кнопка 1", "кнопка 2", "кнопка 3", "кнопка 4"]

async def test_keyboard():
    builder = InlineKeyboardBuilder()
    for i in test:
        builder.add(InlineKeyboardButton(text=i, url='https://example.com'))
    return builder.adjust(2).as_markup()
