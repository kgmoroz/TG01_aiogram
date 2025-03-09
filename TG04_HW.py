import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from keyboards import main_keyboard, inline_links_keyboard, dynamic_keyboard, expanded_keyboard

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Выберите действие:", reply_markup=main_keyboard)

# Обработчик кнопок "Привет" и "Пока"
@dp.message(F.text == "Привет")
async def hello_response(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")

@dp.message(F.text == "Пока")
async def goodbye_response(message: Message):
    await message.answer(f"До свидания, {message.from_user.first_name}!")

# Обработчик команды /links - отправляет инлайн-клавиатуру с ссылками
@dp.message(Command("links"))
async def links_command(message: Message):
    await message.answer("Выберите ссылку:", reply_markup=inline_links_keyboard)

# Обработчик команды /dynamic - отправляет кнопку "Показать больше"
@dp.message(Command("dynamic"))
async def dynamic_command(message: Message):
    await message.answer("Нажмите кнопку ниже:", reply_markup=dynamic_keyboard())

# Обработчик нажатия на кнопку "Показать больше", заменяет её на две новые кнопки
@dp.callback_query(F.data == "show_more")
async def show_more_options(callback: CallbackQuery):
    await callback.message.edit_text("Выберите опцию:", reply_markup=expanded_keyboard())

# Обработчик нажатия на кнопки "Опция 1" и "Опция 2", отправляет сообщение с выбранной опцией
@dp.callback_query(F.data.in_({"option_1", "option_2"}))
async def option_selected(callback: CallbackQuery):
    option_text = "Опция 1" if callback.data == "option_1" else "Опция 2"
    await callback.message.answer(f"Вы выбрали: {option_text}")
    await callback.answer()

# Функция запуска бота
async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

# Запуск бота при выполнении скрипта
if __name__ == "__main__":
    asyncio.run(main())
