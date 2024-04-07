class InvalidPlaylistIdFormatError(Exception):
    """
    Исключение, возникающее при неверном формате идентификатора плейлиста.

    Attributes:
        playlist_identifier (str): Необязательный параметр, содержащий неверный идентификатор плейлиста.
    """

    def __init__(self, playlist_identifier: str = None) -> None:
        """
        Инициализирует объект InvalidPlaylistIdFormatError.

        Args:
            playlist_identifier (str, optional): Неверный идентификатор плейлиста. По умолчанию None.
        """
        if playlist_identifier is not None:
            message = f'Неверный формат идентификатора плейлиста: {playlist_identifier}'
        else:
            message = 'Неверный формат идентификатора плейлиста'
        super().__init__(message)