from colorlog import ColoredFormatter
import logging


custom_logger = logging.getLogger("custom_logger")
custom_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = ColoredFormatter(
    "%(log_color)s[%(asctime)s] - [%(levelname)s] - def %(funcName)s - %(message)s - (%(filename)s:%(lineno)d)",  # Add %(log_color)s
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,  # Reset the color after the log message
    log_colors={  # Define colors for different log levels
        "DEBUG": "green",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",  # White background for critical errors
    },
)
handler.setFormatter(formatter)
custom_logger.addHandler(handler)

logger = custom_logger
