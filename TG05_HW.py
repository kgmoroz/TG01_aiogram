import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import ClientSession
from deep_translator import GoogleTranslator
import os
from dotenv import load_dotenv

# Загрузка токена
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Глобальная переменная для HTTP-сессии
session: ClientSession = None

# ==== Функция перевода через GoogleTranslator ====
def translate_to_russian(text: str) -> str:
    try:
        return GoogleTranslator(source="auto", target="ru").translate(text)
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        return "Ошибка при переводе."


# ==== /start ====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Вот что я умею:\n"
        "💡 /quote — Цитата (на русском)\n"
        "😂 /joke — Шутка (на русском)\n"
        "🐱 /cat — Фото котика\n"
        "🐶 /dog — Фото собачки\n"
        "🔢 /number [число] — Факт о числе (на русском)"
    )


# ==== /quote ====
@dp.message(Command("quote"))
async def get_quote(message: types.Message):
    url = "https://zenquotes.io/api/random"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            quote = f"{data[0]['q']}\n\n— {data[0]['a']}"
            translated = translate_to_russian(quote)
            await message.answer(f"💬 {translated}")
        else:
            await message.answer("❌ Не удалось получить цитату.")


# ==== /joke ====
@dp.message(Command("joke"))
async def get_joke(message: types.Message):
    url = "https://official-joke-api.appspot.com/random_joke"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            joke = f"{data['setup']}\n\n{data['punchline']}"
            translated = translate_to_russian(joke)
            await message.answer(f"😂 {translated}")
        else:
            await message.answer("❌ Не удалось получить шутку.")


# ==== /cat ====
@dp.message(Command("cat"))
async def get_cat(message: types.Message):
    url = "https://api.thecatapi.com/v1/images/search"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            await message.answer_photo(photo=data[0]['url'], caption="Вот котик 🐱")
        else:
            await message.answer("❌ Не удалось получить котика.")


# ==== /dog ====
@dp.message(Command("dog"))
async def get_dog(message: types.Message):
    url = "https://dog.ceo/api/breeds/image/random"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            await message.answer_photo(photo=data['message'], caption="Вот собачка 🐶")
        else:
            await message.answer("❌ Не удалось получить собачку.")


# ==== /number (факт о числе + перевод) ====
@dp.message(Command("number"))
async def get_number_fact(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Пожалуйста, укажи число. Пример: /number 42")
        return

    number = args[1]
    url = f"http://numbersapi.com/{number}"
    async with session.get(url) as response:
        if response.status == 200:
            fact = await response.text()
            translated = translate_to_russian(fact)
            await message.answer(f"🔢 {translated}")
        else:
            await message.answer("❌ Не удалось получить факт о числе.")


# ==== Startup & Shutdown для сессии ====
@dp.startup()
async def on_startup():
    global session
    session = ClientSession()
    logging.info("HTTP-сессия создана!")


@dp.shutdown()
async def on_shutdown():
    await session.close()
    logging.info("HTTP-сессия закрыта!")


# ==== Запуск ====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
