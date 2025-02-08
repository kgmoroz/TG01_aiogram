import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import TOKEN

import random

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('photo'))
async def photo(message: Message):
    list = ["https://avatars.mds.yandex.net/i?id=02a0d438915e4409b6779abb9faf64f6cfcca7e5-5380211-images-thumbs&n=13",
            "https://avatars.mds.yandex.net/i?id=1b8e0e70d61637c540f4f74748bba9fe24c7c2a2-5241344-images-thumbs&n=13",
            "https://avatars.mds.yandex.net/i?id=1cf04a6f38f0be15415a0c35010d27a3eb59c5c5-7942200-images-thumbs&n=13",
            "https://avatars.mds.yandex.net/i?id=62bf3ee67824623f81892ce9486ff3bcea1d3ca8-8981167-images-thumbs&n=13"]
    rand_photo = random.choice(list)
    await message.answer_photo(photo=rand_photo, caption="Случайное фото")

@dp.message(F.photo)
async def react_to_photo(message: Message):
    list = ["Очень хорошо", "Хорошо", "Нормально", "Плохо", "Очень плохо"]
    await message.answer(random.choice(list))
@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer("Искусственный интеллект (ИИ) — это технология, позволяющая компьютерам выполнять задачи, требующие человеческого интеллекта, такие как понимание языка, распознавание образов, принятие решений и обучение на основе данных. Он применяется в различных областях, включая медицину, финансы и транспорт, с целью автоматизации и повышения эффективности процессов.")

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять следующие команды: \n/start - запустить бота \n/help - помощь")

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())