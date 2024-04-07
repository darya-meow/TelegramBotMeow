import sqlite3
from utils.logger import logger
from config.config import load_config_database
from typing import Dict, Any
from utils.logger import logger


class DataBase:
    def __init__(self) -> None:
        config = load_config_database()
        self.__path_database = config.database.path_database
        
        try:
            self.__create_table_playlist()
            logger.info(f'Таблица плейлист успешно инициализирована')
        except sqlite3.Error as e:
            logger.error(f'Произошла ошибка при инициализации таблицы плейлист: {e}')


    def save_playlist_info(self, playlist_info: Dict[str, Any]) -> None:
        try:
            with sqlite3.connect(self.__path_database) as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM playlist_info WHERE id_playlist = ?', (playlist_info['id_playlist'],))
                existing_data = cursor.fetchone()
                
                if existing_data:
                    self.__update_table_playlist(cursor, playlist_info, existing_data)
                else:
                    self.__insert_table_playlist(cursor, playlist_info)
                    
        except sqlite3.Error as e:
            logger.error(f'Произошла ошибка при сохранении данных плейлиста: {e}')
    
    def __create_table_playlist(self) -> None:
        try:
            with sqlite3.connect(self.__path_database) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS playlist_info ( 
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        kind TEXT,
                        etag TEXT,
                        id_playlist TEXT UNIQUE,
                        publishedAt TEXT,
                        channelId TEXT,
                        title TEXT,
                        thumbnails_url TEXT,
                        thumbnails_width INTEGER,
                        thumbnails_height INTEGER,
                        channelTitle TEXT,
                        privacyStatus TEXT,
                        itemCount INTEGER,
                        duration TEXT
                    )
                """)
        except sqlite3.Error as e:
            logger.error(f'Произошла ошибка при создании таблицы плейлиста: {e}')
        
    def __update_table_playlist(self, cursor: sqlite3.Cursor, playlist_info: Dict[str, Any], existing_data: tuple) -> None:
        update_query = """
        UPDATE playlist_info SET
            kind = ?,
            etag = ?,
            publishedAt = ?,
            channelId = ?,
            title = ?,
            thumbnails_url = ?,
            thumbnails_width = ?,
            thumbnails_height = ?,
            channelTitle = ?,
            privacyStatus = ?,
            itemCount = ?,
            duration = ?
        WHERE id_playlist = ?
        """
        cursor.execute(update_query, (
            playlist_info.get('kind', ''),
            playlist_info.get('etag', ''),
            playlist_info.get('publishedAt', ''),
            playlist_info.get('channelId', ''),
            playlist_info.get('title', ''),
            playlist_info.get('thumbnails_url', ''),
            playlist_info.get('thumbnails_width', 0),
            playlist_info.get('thumbnails_height', 0),
            playlist_info.get('channelTitle', ''),
            playlist_info.get('privacyStatus', ''),
            playlist_info.get('itemCount', 0),
            playlist_info.get('duration', ''),
            playlist_info['id_playlist']
        ))
            
    def __insert_table_playlist(self, cursor: sqlite3.Cursor, playlist_info: Dict[str, Any]) -> None:
        insert_query = """
        INSERT INTO playlist_info (
            kind, etag, id_playlist, publishedAt, channelId, title,
            thumbnails_url, thumbnails_width, thumbnails_height, channelTitle,
            privacyStatus, itemCount, duration
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            playlist_info.get('kind', ''),
            playlist_info.get('etag', ''),
            playlist_info.get('id_playlist', ''),
            playlist_info.get('publishedAt', ''),
            playlist_info.get('channelId', ''),
            playlist_info.get('title', ''),
            playlist_info.get('thumbnails_url', ''),
            playlist_info.get('thumbnails_width', 0),
            playlist_info.get('thumbnails_height', 0),
            playlist_info.get('channelTitle', ''),
            playlist_info.get('privacyStatus', ''),
            playlist_info.get('itemCount', 0),
            playlist_info.get('duration', '')
        ))