import logging.handlers

logger = logging.getLogger('simlog')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

def today():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d")

console_formatter = logging.Formatter('\033[32m%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(funcName)s - %(levelname)s - \033[0m%(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

file_handler = logging.handlers.RotatingFileHandler(f'rot.log', encoding="utf-8", maxBytes=1024 * 1024,
                                                    backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)