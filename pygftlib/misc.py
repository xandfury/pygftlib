import logging


def create_logger():
    logger = logging.getLogger('pygftlib')
    hdlr = logging.FileHandler('pygftlib.log')
    formatter = logging.Formatter('[%(levelname)s:%(asctime)-15s]:%(name)s: %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger
