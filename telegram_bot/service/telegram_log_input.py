import io


def get_log_file_as_bytesio() -> io.BytesIO:
    """
    Читает содержимое файла bot.log и возвращает его в виде байтового потока.

    Returns:
        io.BytesIO: Байтовый поток с содержимым файла bot.log.
    """
    # Создаем байтовый поток для хранения данных из файла bot.log
    log_buffer = io.BytesIO()

    try:
        # Читаем содержимое файла bot.log
        with open('bot.log', 'rb') as log_file:
            log_buffer.write(log_file.read())
        
        # Перемещаем указатель в начало буфера
        log_buffer.seek(0)
    except Exception as e:
        # Если возникает ошибка, выводим ее
        print(f"An error occurred while reading log file: {e}")

    return log_buffer
