import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)


# Создание базы данных
def init_db():
    with sqlite3.connect("school_data.db") as conn:
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            grade TEXT
        )
        ''')
        conn.commit()


init_db()


# Определяем состояния
class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(StudentForm.name)


@dp.message(StudentForm.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name.isalpha():
        await message.answer("Имя должно содержать только буквы. Попробуйте снова.")
        return
    await state.update_data(name=name)
    await message.answer("Сколько тебе лет?")
    await state.set_state(StudentForm.age)


@dp.message(StudentForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите возраст числом.")
        return

    age = int(message.text)
    if age < 5 or age > 120:
        await message.answer("Введите реальный возраст (от 5 до 120 лет).")
        return

    await state.update_data(age=age)
    await message.answer("В каком классе ты учишься?")
    await state.set_state(StudentForm.grade)


async def save_student_to_db(student_data):
    try:
        with sqlite3.connect("school_data.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
                (student_data["name"], student_data["age"], student_data["grade"])
            )
            conn.commit()
            logging.info(f"Добавлен ученик: {student_data}")
    except sqlite3.DatabaseError as e:
        logging.error(f"Ошибка при сохранении в БД: {e}")


@dp.message(StudentForm.grade)
async def process_grade(message: Message, state: FSMContext):
    grade = message.text.strip()
    if len(grade) > 10:
        await message.answer("Название класса слишком длинное. Попробуйте снова.")
        return

    await state.update_data(grade=grade)
    student_data = await state.get_data()
    await save_student_to_db(student_data)

    await message.answer("Данные сохранены! Спасибо!")
    await state.clear()


async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
