import logging, logging.handlers

def setup_custom_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)04d - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    filename = 'ftx_dn_bot_log-' + name + '.log'
    file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=2000000, backupCount=50)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger