import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
import aiohttp
import logging
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ],
)


class Form(StatesGroup):
    name = State()
    age = State()
    city = State()


def init_db():
    with sqlite3.connect("user_data.db") as conn:
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL
        )
        ''')
        conn.commit()


init_db()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(f"Привет! Как тебя зовут?")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Сколько тебе лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число, например: 25")
        return

    age_value = int(message.text)
    if not (1 <= age_value <= 120):  # Проверяем диапазон возраста
        await message.answer("Введите реальный возраст (от 1 до 120 лет).")
        return

    await state.update_data(age=age_value)
    await message.answer(f"В каком городе живёшь?")
    await state.set_state(Form.city)


async def save_user_to_db(user_data, message: Message):
    try:
        with sqlite3.connect("user_data.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, age, city) VALUES (?, ?, ?)",
                (user_data["name"], user_data["age"], user_data["city"]),
            )
            conn.commit()
    except sqlite3.DatabaseError as e:  # Ловим ошибки БД
        logging.error(f"Ошибка сохранения в БД: {e}")
        await message.answer("⚠ Ошибка при сохранении данных. Попробуйте позже.")


@dp.message(Form.city)
async def city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    user_data = await state.get_data()

    await save_user_to_db(user_data, message)  # Сохранение в БД

    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }
    params = {
        "q": user_data['city'],
        "lang": "ru"  # Запрос описания погоды на русском
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()

                if response.status != 200 or "error" in data:
                    logging.error(f"Ошибка API: статус {response.status}, ответ: {data}")
                    await message.answer("❌ Город не найден или сервис временно недоступен.")
                    return

                country = data.get("location", {}).get("country", "❓ Неизвестно")
                city = data.get("location", {}).get("name", "❓ Неизвестно")
                temp = data.get("current", {}).get("temp_c", "❓ N/A")
                feels_like = data.get("current", {}).get("feelslike_c", "❓ N/A")
                condition = data.get("current", {}).get("condition", {}).get("text", "❓ Неизвестно")
                humidity = data.get("current", {}).get("humidity", "❓ N/A")
                wind_speed = data.get("current", {}).get("wind_kph", "❓ N/A")
                gust_speed = data.get("current", {}).get("gust_kph", "❓ N/A")

                weather_message = (
                    f"🌍 <b>Страна:</b> {country}\n"
                    f"🏙 <b>Город:</b> {city}\n"
                    f"🌡 <b>Температура:</b> {temp}°C\n"
                    f"🤔 <b>Ощущается как:</b> {feels_like}°C\n"
                    f"⛅ <b>Погода:</b> {condition}\n"
                    f"💧 <b>Влажность:</b> {humidity}%\n"
                    f"💨 <b>Ветер:</b> {wind_speed} км/ч\n"
                    f"🌬 <b>Порывы ветра:</b> {gust_speed} км/ч"
                )

                await message.answer(weather_message, parse_mode="HTML")
                await state.clear()  # Очищаем состояние только если всё прошло успешно

        except aiohttp.ClientError as e:  # Обрабатываем сетевые ошибки
            logging.error(f"Сетевая ошибка при запросе к API: {e}")
            await message.answer("⚠ Ошибка сети. Проверьте соединение и попробуйте снова.")

        except Exception as e:  # Другие ошибки (например, JSONDecodeError)
            logging.error(f"Ошибка при обработке данных API: {e}")
            await message.answer("⚠ Ошибка при обработке данных о погоде.")


async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка во время работы бота: {e}", exc_info=True)  # Добавляем полный stack trace


if __name__ == "__main__":
    asyncio.run(main())
