# Импорт необходимых библиотек
import asyncio  # Для асинхронного запуска бота
import sqlite3  # Для работы с базой данных SQLite
import logging  # Для логирования действий бота
from aiogram import Bot, Dispatcher, F  # Основные компоненты Aiogram
from aiogram.filters import CommandStart  # Фильтр для команды /start
from aiogram.types import Message  # Тип сообщения
from aiogram.fsm.context import FSMContext  # Контекст для работы с состояниями (FSM)
from aiogram.fsm.state import State, StatesGroup  # Определение состояний (FSM)
from aiogram.fsm.storage.memory import MemoryStorage  # Хранение состояний в памяти
import os  # Для работы с переменными окружения
from dotenv import load_dotenv  # Для загрузки переменных окружения из .env файла

# Загрузка переменных окружения из файла .env
load_dotenv()
TOKEN = os.getenv("TOKEN")  # Получаем токен бота

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # Хранилище состояний в оперативной памяти (без базы)

# Настройка логирования (лог сохраняется в файл и выводится в консоль)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)


# Функция для инициализации базы данных (создание таблицы, если не существует)
def init_db():
    with sqlite3.connect("school_data.db") as conn:
        cur = conn.cursor()
        # Создание таблицы студентов
        cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            grade TEXT
        )
        ''')
        conn.commit()


# Запуск инициализации базы данных
init_db()


# Класс с определением шагов (состояний) для ввода данных о студенте
class StudentForm(StatesGroup):
    name = State()  # Состояние для ввода имени
    age = State()   # Состояние для ввода возраста
    grade = State() # Состояние для ввода класса (группы)


# Хэндлер для команды /start, начало диалога
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(StudentForm.name)  # Устанавливаем состояние "имя"


# Хэндлер обработки введённого имени
@dp.message(StudentForm.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name.isalpha():  # Проверка, что имя состоит только из букв
        await message.answer("Имя должно содержать только буквы. Попробуйте снова.")
        return
    await state.update_data(name=name)  # Сохраняем имя во временное хранилище состояний
    await message.answer("Сколько тебе лет?")
    await state.set_state(StudentForm.age)  # Переход к следующему состоянию "возраст"


# Хэндлер обработки введённого возраста
@dp.message(StudentForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():  # Проверка, что возраст введён числом
        await message.answer("Введите возраст числом.")
        return

    age = int(message.text)
    if age < 5 or age > 120:  # Проверка адекватности возраста
        await message.answer("Введите реальный возраст (от 5 до 120 лет).")
        return

    await state.update_data(age=age)  # Сохраняем возраст
    await message.answer("В каком классе ты учишься?")
    await state.set_state(StudentForm.grade)  # Переход к состоянию "класс"


# Функция для сохранения данных студента в базу данных
async def save_student_to_db(student_data):
    try:
        with sqlite3.connect("school_data.db") as conn:
            cur = conn.cursor()
            # Вставка данных в таблицу
            cur.execute(
                "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
                (student_data["name"], student_data["age"], student_data["grade"])
            )
            conn.commit()
            logging.info(f"Добавлен ученик: {student_data}")  # Лог успешного добавления
    except sqlite3.DatabaseError as e:
        logging.error(f"Ошибка при сохранении в БД: {e}")  # Лог ошибки при записи в БД


# Хэндлер обработки введённого класса
@dp.message(StudentForm.grade)
async def process_grade(message: Message, state: FSMContext):
    grade = message.text.strip()
    if len(grade) > 10:  # Ограничение на длину названия класса
        await message.answer("Название класса слишком длинное. Попробуйте снова.")
        return

    await state.update_data(grade=grade)  # Сохраняем класс
    student_data = await state.get_data()  # Получаем все сохранённые данные
    await save_student_to_db(student_data)  # Сохраняем данные в БД

    await message.answer("Данные сохранены! Спасибо!")  # Подтверждение для пользователя
    await state.clear()  # Очистка состояния (завершение диалога)


# Основная функция запуска бота
async def main():
    logging.info("Бот запущен")  # Лог старта
    await dp.start_polling(bot)  # Запуск лонг-поллинга


# Точка входа (запуск бота)
if __name__ == "__main__":
    asyncio.run(main())
