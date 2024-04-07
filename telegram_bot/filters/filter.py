from aiogram.filters import BaseFilter
from aiogram.types import Message
from urllib.parse import urlparse, parse_qs


class PlaylistIdentifierFilter(BaseFilter):
    """
    Фильтр для проверки сообщений на наличие ссылок на плейлисты YouTube и извлечения идентификаторов плейлистов.

    Attributes:
        message (Message): Объект сообщения для проверки.
    """

    async def __call__(self, message: Message) -> bool:
        """
        Проверяет сообщение на наличие ссылок на плейлисты YouTube и извлекает идентификаторы плейлистов.

        Args:
            message (Message): Объект сообщения для проверки.

        Returns:
            bool: True, если сообщение содержит ссылку на плейлист YouTube с правильным форматом идентификатора, в противном случае False.
        """
        parsed_url = urlparse(message.text)
        query_params = parse_qs(parsed_url.query)

        if 'list' in query_params:
            playlist_identifier = query_params['list'][0]
        else:
            return False

        if playlist_identifier and all(
            (
                isinstance(playlist_identifier, str), 
                playlist_identifier.startswith('PL'), 
                len(playlist_identifier) == 34)
        ):
            return True

        return False