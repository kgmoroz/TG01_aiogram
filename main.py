import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
import os
import logging
from gtts import gTTS
from dotenv import load_dotenv
from aiogram.client.session.aiohttp import AiohttpSession
from deep_translator import GoogleTranslator

load_dotenv()

TOKEN = os.getenv("TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Создаем папку img, если она не существует
os.makedirs("img", exist_ok=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем асинхронный бот и диспетчер
session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
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

@dp.message(Command('video'))
async def video(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_video")
    video = FSInputFile("video.mp4")
    await bot.send_video(message.chat.id, video=video)

@dp.message(Command('audio'))
async def audio(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_audio")
    audio = FSInputFile("audio.mp3")
    await bot.send_audio(message.chat.id, audio=audio)

@dp.message(Command('voice'))
async def voice(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_voice")
    voice = FSInputFile("voice.ogg")
    await bot.send_voice(message.chat.id, voice=voice)

@dp.message(Command('doc'))
async def doc(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_document")
    doc = FSInputFile("doc.pdf")
    await bot.send_document(message.chat.id, document=doc)

@dp.message(Command('training'))
async def training(message: Message):
    training_list = [
        """Кардио-сессия (15 минут):
   - Прыжки на месте: 1 минута
   - Приседания с собственным весом: 1 минута
   - Высокие колени: 1 минута
   - Отдых: 30 секунд
   - Повторите цикл 3 раза""",
        """Тренировка на укрепление мышц (15 минут):
   - Отжимания: 10 повторений
   - Планка: 30 секунд
   - Выпады вперед: по 10 повторений на каждую ногу
   - Отдых: 1 минута
   - Повторите цикл 3 раза""",
        """Йога и растяжка (15 минут):
   - Кошка-корова (для спины): 1 минута
   - Поза собаки мордой вниз: 1 минута
   - Наклон вперед сидя: 1 минута
   - Поза бабочки (для бедер): 1 минута
   - Повторите цикл 2-3 раза, сосредотачиваясь на дыхании и расслаблении"""
    ]
    rand_training = random.choice(training_list)
    await message.answer(f"Это ваша тренировка:\n{rand_training}")

    gtts = gTTS(text=rand_training, lang="ru")
    gtts.save("training.ogg")
    voice = FSInputFile("training.ogg")
    await message.answer_voice(voice=voice)
    os.remove("training.ogg")

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


# Обработчик фото
@dp.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    photo = message.photo[-1] # Берем изображение с наибольшим разрешением
    file_info = await bot.get_file(photo.file_id)
    file_name = f"img/{photo.file_id}.jpg" # Формируем путь сохранения
    await bot.download_file(file_info.file_path, file_name) # Скачиваем и сохраняем файл
    await message.reply(f"Фото сохранено как {file_name}") # Отправляем подтверждение пользователю
"""
@dp.message(F.photo)
async def react_to_photo(message: Message):
    reactions = ["Очень хорошо", "Хорошо", "Нормально", "Плохо", "Очень плохо"]
    await message.answer(random.choice(reactions))
    await bot.download(message.photo[-1], destination=f"tmp/{message.photo[-1].file_id}.jpg")
"""

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
        "/weather - показать прогноз погоды\n"
        "/doc - отправить документ\n"
        "/audio - отправить аудио\n"
        "/video - отправить видео\n"
        "/voice - отправить голосовое сообщение\n"
        "/training - отправить тренировку\n\n"
        "Любое сообщение пользователя будет автоматически переведено на английский язык.\n"
        "Любое фото пользователя будет автоматически сохранено.\n\n"
        "Приятного пользования!"
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот!")


# Обработчик текстовых сообщений
@dp.message(F.text)
async def translate_text(message: Message):
    user_text = message.text # Получаем текст от пользователя
    try:
        translated_text = GoogleTranslator(source="auto", target="en").translate(user_text) # Переводим текст на английский
        await message.reply(f"**Перевод на английский:**\n{translated_text}") # Отправляем переведенный текст пользователю
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        await message.reply("Произошла ошибка при переводе.")

@dp.message()
async def echo(message: Message):
    if message.text.lower() == "тест":
        await message.answer("Тест OK")
    else:
        await message.answer(message.text)
        await message.send_copy(chat_id=message.chat.id)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
