import logging
from pathlib import Path
from rich.logging import RichHandler


# Create a function to set up the logger.
def setup_logging(name="r2e", level=logging.WARNING, log_file=None, console=True):
    # Create a logger with the name provided.
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    logger.propagate = False

    if console:
        # Create a RichHandler for colored console output with default formatting.
        rich_handler = RichHandler(rich_tracebacks=True)
        rich_handler.setLevel(level)
        logger.addHandler(rich_handler)

    # Optionally, set up a file handler to log to a file if a filename is provided.
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


### usage
# from r2e.logger import logger
# logger.info("This is an info message.")
# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.critical("This is a critical message.")
# logger.debug("This is a debug message.")
