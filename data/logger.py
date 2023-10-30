from loguru import logger

main_log = logger.add("logs/main_log.log", rotation="100 MB", encoding='utf-8', level="INFO")
error_log = logger.add("logs/errors.log", rotation="100 MB", encoding='utf-8', level="ERROR")