from aiogram import Router, html, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart
from filters.filter import PlaylistIdentifierFilter
from service.youtubeapiclientv3 import YouTubeAPIClientV3
from service.telegram_db_excel_service import send_excel_file
from service.telegram_log_input import get_log_file_as_bytesio
from models.methods import DataBase
from lexicon.lexicon import LEXICON_RU
from config.config import bot
from utils.logger import logger


handler_router = Router()  # Создание объекта Router для управления обработчиками сообщений
service = YouTubeAPIClientV3()  # Создание объекта YouTubeAPIClientV3 для работы с API YouTube
database = DataBase()  # Создание объекта базы данных для взаимодействия с данными


# Обработчик команды /start
@handler_router.message(CommandStart())  
async def cmd_start(message: Message):
    """
    Обработчик команды /start.

    Args:
        message (Message): Объект сообщения, содержащий информацию о команде.

    Returns:
        None
    """
    await message.delete()  # Удаление сообщения с командой /start
    await message.answer(
        text=LEXICON_RU['cmd_start'].format(message.from_user.username)  # Отправка ответного сообщения с приветствием
    )
    logger.info(f'Вызов команды /start пользователем: {message.from_user.full_name} | {message.from_user.id}')  # Логирование вызова команды /start


# Обработчик сообщений с командой /help
@handler_router.message(F.text == '/help')  
async def cmd_help(message: Message):
    """
    Обработчик команды /help.

    Args:
        message (Message): Объект сообщения, содержащий информацию о команде.

    Returns:
        None
    """
    await message.delete()  # Удаление сообщения с командой /help
    await message.answer(
        text=LEXICON_RU['cmd_help']  # Отправка ответного сообщения с общей справочной информацией
    )
    logger.info(f'Вызов команды /help пользователем: {message.from_user.full_name} | {message.from_user.id}')  # Логирование вызова команды /help


# Обработчик сообщений с текстом /help_playlist
@handler_router.message(F.text == '/help_playlist')
async def cmd_help_playlist(message: Message):
    """
    Обработчик команды /help_playlist.

    Args:
        message (Message): Объект сообщения, содержащий информацию о команде.

    Returns:
        None
    """
    await message.delete()  # Удаление сообщения с командой /help_playlist
    await message.answer(
        text=LEXICON_RU['cmd_help_playlist']  # Отправка ответного сообщения с помощью по плейлистам
    )
    logger.info(f'Вызов команды /help_playlist пользователем: {message.from_user.full_name} | {message.from_user.id}')  # Логирование вызова команды /help_playlist


# Обработчик сообщений, прошедших фильтр PlaylistIdentifierFilter
@handler_router.message(PlaylistIdentifierFilter())  
async def cmd_playlist(message: Message):    
    """
    Обработчик команд, содержащих идентификаторы плейлистов YouTube.

    Args:
        message (Message): Объект сообщения с информацией о команде и содержимом.

    Returns:
        None
    """
    try:
        playlist_info: dict = service.playlist.get_info(message.text)  # Получение информации о плейлисте
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')  # Логирование ошибки
        return
    
    try:
        entities = message.entities or []  # Получение сущностей сообщения (если есть)
        for item in entities:
            if item.type in playlist_info.keys():
                playlist_info[item.type] = item.extract_from(message.text)  # Извлечение информации из сущностей сообщения
        # Отправка информации о плейлисте пользователю
        await message.reply(
            f'📹 Информация о плейлисте\n'
            f'🔒 Тип ресурса: {html.quote(str(playlist_info["kind"]))}\n'
            f'🔑 Механизм кеширования: {html.quote(str(playlist_info["etag"]))}\n'
            f'🆔 Идентификатор: {html.quote(str(playlist_info["id_playlist"]))}\n'
            f'🕒 Дата и время публикации: {html.quote(str(playlist_info["publishedAt"]))}\n'
            f'👤 Идентификатор канала: {html.quote(str(playlist_info["channelId"]))}\n'
            f'🎬 Название: {html.quote(str(playlist_info["title"]))}\n'
            f'🖼️ URL Изображения: {html.quote(str(playlist_info["thumbnails_url"]))}\n'
            f'📏 Ширина изображения: {html.quote(str(playlist_info["thumbnails_width"]))}\n'
            f'📐 Высота изображения: {html.quote(str(playlist_info["thumbnails_height"]))}\n'
            f'🔏 Статус конфиденциальности: {html.quote(str(playlist_info["privacyStatus"]))}\n'
            f'👀 Количество видео: {html.quote(str(playlist_info["itemCount"]))}\n'
            f'⏱️ Продолжительность плейлиста: {html.quote(str(playlist_info["duration"]))}\n'
        )
        logger.info(f'Данные о плейлисте: {str(playlist_info["id_playlist"])} были успешно отправлены пользователю: {message.from_user.full_name} | {message.from_user.id}')  # Логирование успешной отправки информации о плейлисте
        database.save_playlist_info(playlist_info)  # Сохранение информации о плейлисте в базе данных
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')  # Логирование ошибки
        return


# Обработчик сообщений с текстом /help_export
@handler_router.message(F.text == '/help_export')  
async def cmd_help_export(message: Message):
    """
    Обработчик команды /help_export.

    Args:
        message (Message): Объект сообщения, содержащий информацию о команде.

    Returns:
        None
    """
    await message.delete()  # Удаление сообщения с командой /help_export
    await message.answer(
        text=LEXICON_RU['cmd_help_export']  # Отправка ответного сообщения с помощью по экспорту данных
    )
    logger.info(f'Вызов команды /help_export пользователем: {message.from_user.full_name} | {message.from_user.id}')  # Логирование вызова команды /help_export
    

# Обработчик сообщений, содержащих команду /export
@handler_router.message(F.text == '/export')
async def cmd_export(message: Message):
    """
    Обработчик команды /export, который отправляет пользователю файл Excel с данными из базы данных.

    Args:
        message (Message): Объект сообщения с информацией о команде и отправителе.

    Returns:
        None
    """
    excel_file = send_excel_file()  # Генерация файла Excel с данными из базы данных
    await bot.send_document(message.from_user.id, document=BufferedInputFile(excel_file.read(), 'db_data.xlsx'))  # Отправка файла пользователю
    logger.info(f'Произведена выгрузка данных /export для польователя: {message.from_user.full_name} | {message.from_user.id}')  # Логирование события выгрузки данных


# Обработчик сообщений, содержащих команду /export_log
@handler_router.message(F.text == '/export_log')   
async def cmd_export(message: Message):
    """
    Обработчик команды /export_дщп, который отправляет пользователю файл bot.log с данными о логах системы.

    Args:
        message (Message): Объект сообщения с информацией о команде и отправителе.

    Returns:
        None
    """
    log_file = get_log_file_as_bytesio()
    await bot.send_document(message.from_user.id, document=BufferedInputFile(log_file.read(), 'bot.log'))  # Отправка файла пользователю
    logger.info(f'Произведена выгрузка логов /export_log для польователя: {message.from_user.full_name} | {message.from_user.id}')  # Логирование события выгрузки данных