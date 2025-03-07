# -*- coding: utf-8 -*-
"""bot.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1OegX6y6iyfINt6NKhKdqy7WmtDqZ2Xwl
"""

!pip install aiogram -q

# Импортируем необходимые модули

from aiogram import Bot, Dispatcher, types  # Основные классы для работы с ботом
import logging  # Логирование для отслеживания работы бота
import asyncio  # Модуль для работы с асинхронным кодом
import nest_asyncio
import sys  # Используется для работы с системными вызовами
import json
import numpy as np

from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.types.message import ContentType

import gensim
from gensim.models import Word2Vec

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""**Код частями**"""

# Токен API бота

API_TOKEN = "token"

## Проверяем работу бота

# Настраиваем логирование, чтобы видеть информацию о работе бота в консоли
logging.basicConfig(level=logging.INFO)
# Создаем объект диспетчера, который управляет входящими сообщениями и командами
dp = Dispatcher()

# Декоратор @dp.message() указывает, что функция будет обрабатывать входящие сообщения
@dp.message()
async def echo(message: types.Message):
    """
    Асинхронная функция (корутина), которая отвечает пользователю.
    Она получает объект сообщения и отправляет ответ.

    :param message: объект сообщения от пользователя
    """
    await message.answer("Привет! Я твой бот.")  # Отправляем ответное сообщение

async def main():
    """
    Основная асинхронная функция для запуска бота.
    1. Создает объект бота с API токеном.
    2. Запускает диспетчер, который начинает обрабатывать сообщения.
    """
    bot = Bot(token=API_TOKEN)
    await dp.start_polling(bot)

# Проверяем, запущен ли скрипт напрямую (не импортирован в другой файл)
if __name__ == "__main__":
    # Запускаем основную функцию
    await main()

## Загружаем json с вопросами и ответами

!wget data.json https://raw.githubusercontent.com/vifirsanova/compling/refs/heads/main/tasks/task3/faq.json -O data.json


with open("data.json", "r") as file:
    data = json.load(file)  # data - это словарь из JSON-файла


# Извлекаем вопросы и ответы из данных
faq_questions = []
faq_answers = []
for i in data.values():
    for y in i:
        faq_questions.append(y['question'])
        faq_answers.append(y['answer'])

#print(faq_questions)
#print(faq_answers)

## Вариант с выводом двух ответов (на основе двух методов)

# Инициализируем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подготовка TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(faq_questions)

# Подготовка Word2Vec
sentences = [q.split() for q in faq_questions]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Функция для усреднения векторов слов в вопросе
def sentence_vector(sentence, model):
    words = sentence.split()
    vectors = [model.wv[word] for word in words if word in model.wv]

    if not vectors:
        return np.zeros(model.vector_size)

    return np.mean(vectors, axis=0)

# Векторизуем вопросы для Word2Vec
faq_vectors = np.array([sentence_vector(q, model) for q in faq_questions])

# Функция для выбора наиболее подходящего ответа на основе TF-IDF
def get_answer_tfidf(query):
    query_vec = vectorizer.transform([query])
    similarities_tfidf = cosine_similarity(query_vec, tfidf_matrix)
    best_match_idx_tfidf = similarities_tfidf.argmax()
    return faq_answers[best_match_idx_tfidf]

# Функция для выбора наиболее подходящего ответа на основе Word2Vec
def get_answer_word2vec(query):
    query_vector = sentence_vector(query, model).reshape(1, -1)
    similarities_w2v = cosine_similarity(query_vector, faq_vectors)
    best_match_idx_w2v = similarities_w2v.argmax()
    return faq_answers[best_match_idx_w2v]

# Обработка вопросов пользователей
@dp.message()
async def answer_question(message: types.Message):
    question = message.text
    answer_tfidf = get_answer_tfidf(question)
    answer_word2vec = get_answer_word2vec(question)
    await message.answer("Ответ на основе TF-IDF: " + answer_tfidf)
    await message.answer("Ответ на основе Word2Vec: " + answer_word2vec)


# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    await main()

## Вариант с выводом одного ответа (на основе выбора лучшего - с большей семантической близостью)

# Инициализируем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подготовка TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(faq_questions)

# Подготовка Word2Vec
sentences = [q.split() for q in faq_questions]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Функция для усреднения векторов слов в вопросе
def sentence_vector(sentence, model):
    words = sentence.split()
    vectors = [model.wv[word] for word in words if word in model.wv]

    if not vectors:
        return np.zeros(model.vector_size)

    return np.mean(vectors, axis=0)

# Векторизуем вопросы для Word2Vec
faq_vectors = np.array([sentence_vector(q, model) for q in faq_questions])

# Функция для выбора наиболее подходящего ответа на основе TF-IDF
def get_answer_tfidf(query):
    query_vec = vectorizer.transform([query])
    similarities_tfidf = cosine_similarity(query_vec, tfidf_matrix)
    best_match_idx_tfidf = similarities_tfidf.argmax()
    return faq_answers[best_match_idx_tfidf], similarities_tfidf.max()

# Функция для выбора наиболее подходящего ответа на основе Word2Vec
def get_answer_word2vec(query):
    query_vector = sentence_vector(query, model).reshape(1, -1)
    similarities_w2v = cosine_similarity(query_vector, faq_vectors)
    best_match_idx_w2v = similarities_w2v.argmax()
    return faq_answers[best_match_idx_w2v], similarities_w2v.max()

# Функция для выбора наилучшего ответа из TF-IDF и Word2Vec
def get_best_answer(query):
    answer_tfidf, similarity_tfidf = get_answer_tfidf(query)
    answer_word2vec, similarity_w2v = get_answer_word2vec(query)

    # Сравниваем схожести и выбираем лучший ответ
    if similarity_tfidf > similarity_w2v:
        return answer_tfidf
    else:
        return answer_word2vec

# Обработка вопросов пользователей
@dp.message()
async def answer_question(message: types.Message):
    question = message.text
    best_answer = get_best_answer(question)  # Выбираем лучший ответ
    await message.answer(best_answer)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    await main()

## Реализация кнопок

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаём список кнопок для клавиатуры
kb = [
    [
        KeyboardButton(text="О компании"), # Кнопка для запроса информации о компании
        KeyboardButton(text="Пожаловаться")  # Кнопка для того, чтобы пожаловаться
    ]
]

# Создаём объект клавиатуры с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=kb, # Передаём список кнопок
    resize_keyboard=True, # Уменьшаем клавиатуру под размер экрана
    input_field_placeholder="Выберите действие" # Текст-подсказка в поле ввода
    )

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот, который может ответить на ваши вопросы о работе компании. С чем вам помочь?", reply_markup=keyboard) # Отправляем сообщение с клавиатурой в команду start

# Обрабатываем нажатие кнопки "О боте"
@dp.message(lambda message: message.text == "О компании") # Фильтр для сообщений с текстом "О компании"
async def about_bot(message: types.Message):
    """
    Функция отвечает пользователю, если он нажал кнопку "О боте".
    """
    await message.answer("➡ Наша компания занимается доставкой товаров по всей стране.")

# Обрабатываем нажатие кнопки "Пожаловаться": бот принимает на вход картинку (например, скриншот) и возвращает её название и размер файла, а также текст "Ваш запрос передан специалисту"
@dp.message(lambda message: message.text == "Пожаловаться")
async def complain(message: types.Message):
    await message.answer("📎 Пожалуйста, отправьте скриншот с жалобой.")

# Обрабатываем полученные изображения
@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # Берём изображение с наибольшим разрешением
    file_info = await message.bot.get_file(photo.file_id)

    # Отправляем пользователю информацию о фото
    response = f"✅ Ваше фото получено!\n\n📌 Название файла: {file_info.file_path}\n🔎 Размер файла: ~{photo.file_size} байт\n\n📲 Ваш запрос передан специалисту."
    await message.answer(response)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

"""**КОД ЦЕЛИКОМ (вариант с отправкой одного лучшего ответа)**"""

!pip install aiogram -q

# Импортируем необходимые модули

from aiogram import Bot, Dispatcher, types  # Основные классы для работы с ботом
import logging  # Логирование для отслеживания работы бота
import asyncio  # Модуль для работы с асинхронным кодом
import nest_asyncio
import sys  # Используется для работы с системными вызовами
import json
import numpy as np

from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.types.message import ContentType

import gensim
from gensim.models import Word2Vec

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Токен API бота
API_TOKEN = "token"

# Загружаем файл
!wget data.json https://raw.githubusercontent.com/vifirsanova/compling/refs/heads/main/tasks/task3/faq.json -O data.json
with open("data.json", "r") as file:
    data = json.load(file)  # data - это словарь из JSON-файла


# Извлекаем вопросы и ответы из данных
faq_questions = []
faq_answers = []
for i in data.values():
    for y in i:
        faq_questions.append(y['question'])
        faq_answers.append(y['answer'])


# Инициализируем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подготовка TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(faq_questions)

# Подготовка Word2Vec
sentences = [q.split() for q in faq_questions]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Функция для усреднения векторов слов в вопросе
def sentence_vector(sentence, model):
    words = sentence.split()
    vectors = [model.wv[word] for word in words if word in model.wv]

    if not vectors:
        return np.zeros(model.vector_size)

    return np.mean(vectors, axis=0)

# Векторизуем вопросы для Word2Vec
faq_vectors = np.array([sentence_vector(q, model) for q in faq_questions])

# Функция для выбора наиболее подходящего ответа на основе TF-IDF
def get_answer_tfidf(query):
    query_vec = vectorizer.transform([query])
    similarities_tfidf = cosine_similarity(query_vec, tfidf_matrix)
    best_match_idx_tfidf = similarities_tfidf.argmax()
    return faq_answers[best_match_idx_tfidf], similarities_tfidf.max()

# Функция для выбора наиболее подходящего ответа на основе Word2Vec
def get_answer_word2vec(query):
    query_vector = sentence_vector(query, model).reshape(1, -1)
    similarities_w2v = cosine_similarity(query_vector, faq_vectors)
    best_match_idx_w2v = similarities_w2v.argmax()
    return faq_answers[best_match_idx_w2v], similarities_w2v.max()

# Функция для выбора наилучшего ответа из TF-IDF и Word2Vec
def get_best_answer(query):
    answer_tfidf, similarity_tfidf = get_answer_tfidf(query)
    answer_word2vec, similarity_w2v = get_answer_word2vec(query)

    # Сравниваем схожести и выбираем лучший ответ
    if similarity_tfidf > similarity_w2v:
        return answer_tfidf
    else:
        return answer_word2vec

# Создаём список кнопок для клавиатуры
kb = [
    [
        KeyboardButton(text="О компании"), # Кнопка для запроса информации о компании
        KeyboardButton(text="Пожаловаться")  # Кнопка для того, чтобы пожаловаться
    ]
]

# Создаём объект клавиатуры с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=kb, # Передаём список кнопок
    resize_keyboard=True, # Уменьшаем клавиатуру под размер экрана
    input_field_placeholder="Выберите действие" # Текст-подсказка в поле ввода
    )

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот, который может ответить на ваши вопросы о работе компании. С чем вам помочь?", reply_markup=keyboard) # Отправляем сообщение с клавиатурой в команду start

# Обрабатываем нажатие кнопки "О боте"
@dp.message(lambda message: message.text == "О компании") # Фильтр для сообщений с текстом "О компании"
async def about_bot(message: types.Message):
    """
    Функция отвечает пользователю, если он нажал кнопку "О боте".
    """
    await message.answer("➡ Наша компания занимается доставкой товаров по всей стране.")

# Обрабатываем нажатие кнопки "Пожаловаться": бот принимает на вход картинку (например, скриншот) и возвращает её название и размер файла, а также текст "Ваш запрос передан специалисту"
@dp.message(lambda message: message.text == "Пожаловаться")
async def complain(message: types.Message):
    await message.answer("📎 Пожалуйста, отправьте скриншот с жалобой.")

# Обрабатываем полученные изображения
@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # Берём изображение с наибольшим разрешением
    file_info = await message.bot.get_file(photo.file_id)

    # Отправляем пользователю информацию о фото
    response = f"✅ Ваше фото получено!\n\n📌 Название файла: {file_info.file_path}\n🔎 Размер файла: ~{photo.file_size} байт\n\n📲 Ваш запрос передан специалисту."
    await message.answer(response)

# Обработка вопросов пользователей
@dp.message()
async def answer_question(message: types.Message):
    question = message.text
    best_answer = get_best_answer(question)  # Выбираем лучший ответ
    await message.answer(best_answer)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    await main()
