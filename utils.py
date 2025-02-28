import logging
def log_error(message: str, error: Exception):
    logging.error(f"{message}: {error}", exc_info=True)
