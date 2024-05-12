import logging

class CustomFormatter(logging.Formatter):
    def __init__(self, formats):
        self.formats = formats

    def format(self, record):
        log_fmt = self.formats.get(record.levelno, self.formats['DEFAULT'])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Определение форматов для каждого уровня
formats = {
    logging.INFO: '%(asctime)s [+] %(levelname)s %(message)s',
    logging.WARNING: '%(asctime)s [!] %(levelname)s %(message)s',
    'DEFAULT': '%(asctime)s [*] %(levelname)s %(message)s'
}

# Создание файлового обработчика с нужным форматтером
file_handler = logging.FileHandler('meshtastic.log') 
file_handler.setFormatter(CustomFormatter(formats))

# Добавление файлового обработчика к root logger
logging.root.addHandler(file_handler)
logging.root.setLevel(logging.INFO)