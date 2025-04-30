"""
Custom logger configuration using `colorlog` for enhanced terminal output.

This logger:
- Uses stream output with color formatting.
- Supports all standard logging levels.
- Displays function names, file names, and line numbers.
- Can be reused as `logger` across the application for consistent logging.
"""

import logging
from colorlog import ColoredFormatter

# Create and configure the logger
custom_logger = logging.getLogger("custom_logger")
custom_logger.setLevel(logging.DEBUG)  # Capture all log levels DEBUG and above

# Create a stream handler to output logs to stdout
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)  # Handle all logs from DEBUG and above

# Define colored formatter with custom log format
formatter = ColoredFormatter(
    fmt="%(log_color)s[%(asctime)s] - [%(levelname)s] - def %(funcName)s - %(message)s - (%(filename)s:%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,  # Resets color after each log
    log_colors={
        "DEBUG": "green",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",  # High-visibility for CRITICAL logs
    },
)

# Attach formatter to handler and handler to logger
handler.setFormatter(formatter)
custom_logger.addHandler(handler)

# Expose the configured logger as `logger` for reuse
logger = custom_logger
