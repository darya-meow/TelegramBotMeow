from datetime import timedelta
from urllib.parse import urlparse, parse_qs

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from isodate import parse_duration

from config.config import load_config_service_youtube
from utils.logger import logger

from custom_exceptions.custom_exception import InvalidPlaylistIdFormatError


class YouTubeAPIClientV3:
    def __init__(self) -> None:
        try:
            config = load_config_service_youtube()  # Загрузка конфигурации для сервиса YouTube
            # Инициализация ресурса YouTube API с использованием ключа разработчика из конфигурации
            self.__api_resource = build(
                serviceName='youtube',
                version='v3',
                developerKey=config.service_youtube.api_key_service_youtube_v3
            )
        except Exception as e:
            # Регистрация ошибки, если инициализация не удалась, и вызов исключения ValueError
            error_message = f'Произошла ошибка при создании ресурса YouTube API. Проверьте API_KEY_SERVICE_YOUTUBE: {e}'
            logger.error(error_message)
            raise ValueError(error_message)

        # Инициализация внутренних классов для взаимодействия с различными ресурсами
        self.playlist = YouTubeAPIClientV3.__Playlist(self.__api_resource)
        
        logger.info('Сервис YouTubeAPIClientV3 был успешно инициализирован')
    
    class __Playlist():
        """
        Класс для получения информации о плейлисте из YouTube API.

        Attributes:
            _access__api_resource: Ресурс доступа к YouTube API.

        Methods:
            get_info(playlist_identifier: str) -> dict:
                Получает информацию о плейлисте по его идентификатору.
            __get_info_playlists_duration(playlist_identifier) -> str:
                Получает общую продолжительность видео в плейлисте.
            __extract_playlist_identifier(playlist_identifier: str) -> str:
                Извлекает идентификатор плейлиста из переданной строки.

        Raises:
            HttpError: Если происходит HTTP-ошибка при запросе к YouTube API.
            ValueError: Если идентификатор плейлиста неверного формата или нет информации о плейлисте.

        """
        def __init__(self, access) -> None:
            """
            Инициализация объекта класса.

            Args:
                access: Ресурс доступа к YouTube API.

            """
            self._access__api_resource = access
        
        
        def get_info(self, playlist_identifier: str) -> dict:
            """
            Получает информацию о плейлисте из YouTube API по его идентификатору.

            Args:
                playlist_identifier: Идентификатор плейлиста (URL или ID).

            Returns:
                dict: Словарь с данными о плейлисте.

            Raises:
                HttpError: Если происходит HTTP-ошибка при запросе к YouTube API.
                ValueError: Если идентификатор плейлиста неверного формата или нет информации о плейлисте.

            """
            try:
                playlist_identifier: str = self.__extract_playlist_identifier(playlist_identifier)
                playlist_info_response: dict = self._access__api_resource.playlists().list(
                    part=['snippet', 'status', 'contentDetails'],
                    id=playlist_identifier
                ).execute()
                
                item: dict = playlist_info_response.get('items', [])[0]
                
                if not item:
                    raise ValueError('No video information found')
                
                snippet: dict = item.get('snippet', {})
                content_details: dict = item.get('contentDetails', {})
                status: dict = item.get('status', {})
                
                playlist_data: dict = {
                    'kind': item.get('kind', 'Нет данных'),
                    'etag': item.get('etag', 'Нет данных'),
                    'id_playlist': item.get('id', 'Нет данных'),
                    'publishedAt': snippet.get('publishedAt', 'Нет данных'),
                    'channelId': snippet.get('channelId', 'Нет данных'),
                    'title': snippet.get('title', 'Нет данных'),
                    'thumbnails_url': snippet['thumbnails'].get('standard', {}).get('url', 'Нет данных'),
                    'thumbnails_width': snippet['thumbnails'].get('standard', {}).get('width', 'Нет данных'),
                    'thumbnails_height': snippet['thumbnails'].get('standard', {}).get('height', 'Нет данных'),
                    'channelTitle': snippet.get('channelTitle', 'Нет данных'),
                    'privacyStatus': status.get('privacyStatus', 'Нет данных'),
                    'itemCount': content_details.get('itemCount', 'Нет данных'),
                    'duration': self.__get_info_playlists_duration(playlist_identifier)
                }
                
                return playlist_data
            
            
            except HttpError as e:
                logger.error(f'HTTP Error occurred: {e}')
                raise
            except ValueError as ve:
                logger.error(f'ValueError occurred: {ve}')
                raise
            except Exception as ex:
                logger.error(f'An unexpected error occurred: {ex}')
                raise
        
        
        def __get_info_playlists_duration(self, playlist_identifier) -> str:
            """
            Получает общую продолжительность видео в плейлисте.

            Args:
                playlist_identifier: Идентификатор плейлиста.

            Returns:
                str: Общая продолжительность видео в плейлисте в формате "часы:минуты:секунды".

            Raises:
                Exception: Если происходит ошибка при получении данных о видео.

            """
            try:
                next_page_token = None
                video_ids = []
                
                while True:
                    playlist_info_for_duration = self._access__api_resource.playlistItems().list(
                        part='contentDetails',
                        playlistId=playlist_identifier,
                        maxResults=50,
                        pageToken=next_page_token
                    ).execute()
                    
                    items = playlist_info_for_duration.get('items', [])
                    for item in items:
                        content_details = item.get('contentDetails', {})
                        video_id = content_details.get('videoId', '')
                        if video_id:
                            video_ids.append(video_id)

                    next_page_token = playlist_info_for_duration.get('nextPageToken')

                    if not next_page_token:
                        break
                    
            except Exception as e:
                print(f'Произошла ошибка при получении данных о странице плейлиста: {e}')
                return 'Нет данных'
            
            try:
                duration_formatted = 0
                
                for video in video_ids:
                    video_info = self._access__api_resource.videos().list(
                        part='contentDetails',
                        id=video
                    ).execute()
                    
                    content_details = video_info.get('items', [{}])[0].get('contentDetails', {})
                    duration_str = content_details.get('duration', 'PT0S')
                    duration_seconds = parse_duration(duration_str).total_seconds()
                    duration_formatted += duration_seconds
                
                hours = int(duration_formatted // 3600)
                minutes = int((duration_formatted % 3600) // 60)
                seconds = int(duration_formatted % 60)
                duration_formatted = f'{hours:}:{minutes:}:{seconds:}'
                
                return duration_formatted
            
            except Exception as e:
                print(f'Произошла ошибка при получении данных о видео!: {e}')
            

        def __extract_playlist_identifier(self, playlist_identifier: str) -> str:  
            """
            Извлекает идентификатор плейлиста из переданной строки.

            Args:
                playlist_identifier: Строка с URL или ID плейлиста.

            Returns:
                str: Идентификатор плейлиста.

            Raises:
                InvalidPlaylistIdFormatError: Если идентификатор плейлиста неверного формата.

            """          
            parsed_url = urlparse(playlist_identifier)
            query_params = parse_qs(parsed_url.query)

            if 'list' in query_params:
                playlist_identifier = query_params['list'][0]

            if playlist_identifier and all(
                (
                    isinstance(playlist_identifier, str), 
                    playlist_identifier.startswith('PL'), 
                    len(playlist_identifier) == 34)
            ):
                return playlist_identifier

            raise InvalidPlaylistIdFormatError(playlist_identifier)