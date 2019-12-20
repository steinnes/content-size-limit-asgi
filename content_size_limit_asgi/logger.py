import logging


def setup_logging(logger, level=None):
    if level is None:
        level = logging.INFO

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def get_logger(name):
    logger = logging.getLogger(name)
    setup_logging(logger)
    return logger
