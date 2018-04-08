import logging


def create_logger():
    logging.getLogger().addHandler(logging.StreamHandler())
    logFormatter = logging.Formatter('[%(levelname)s:%(asctime)-15s]:%(name)s: %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler('pygftlib.log')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    return rootLogger
