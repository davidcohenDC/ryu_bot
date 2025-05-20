import logging

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        _format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        _format = _format.replace("(black)", self.black + self.bold)
        _format = _format.replace("(reset)", self.reset)
        _format = _format.replace("(levelcolor)", log_color)
        _format = _format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(_format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

