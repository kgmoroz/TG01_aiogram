import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

CITY = "Минск"


def get_weather():
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q": CITY}

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return f"Погода в {CITY}: {temp}°C, {condition}."
    else:
        return "Не удалось получить данные о погоде."


@dp.message(Command('weather'))
async def weather(message: Message):
    weather_info = get_weather()
    await message.answer(weather_info)


@dp.message(Command('photo'))
async def photo(message: Message):
    photo_list = [
        "https://avatars.mds.yandex.net/i?id=02a0d438915e4409b6779abb9faf64f6cfcca7e5-5380211-images-thumbs&n=13",
        "https://avatars.mds.yandex.net/i?id=1b8e0e70d61637c540f4f74748bba9fe24c7c2a2-5241344-images-thumbs&n=13",
        "https://avatars.mds.yandex.net/i?id=1cf04a6f38f0be15415a0c35010d27a3eb59c5c5-7942200-images-thumbs&n=13",
        "https://avatars.mds.yandex.net/i?id=62bf3ee67824623f81892ce9486ff3bcea1d3ca8-8981167-images-thumbs&n=13"
    ]
    rand_photo = random.choice(photo_list)
    await message.answer_photo(photo=rand_photo, caption="Случайное фото")


@dp.message(F.photo)
async def react_to_photo(message: Message):
    reactions = ["Очень хорошо", "Хорошо", "Нормально", "Плохо", "Очень плохо"]
    await message.answer(random.choice(reactions))


@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer(
        "Искусственный интеллект (ИИ) — это технология, позволяющая компьютерам выполнять задачи, требующие человеческого интеллекта, "
        "такие как понимание языка, распознавание образов, принятие решений и обучение на основе данных. Он применяется в различных "
        "областях, включая медицину, финансы и транспорт, с целью автоматизации и повышения эффективности процессов."
    )


@dp.message(Command('help'))
async def help(message: Message):
    await message.answer(
        "Этот бот умеет выполнять следующие команды:\n"
        "/start - запустить бота\n"
        "/help - помощь\n"
        "/photo - отправить случайное фото\n"
        "/weather - показать прогноз погоды"
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
