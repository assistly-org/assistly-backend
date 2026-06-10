import logging
import sys

class EmojiFormatter(logging.Formatter):
    """Custom formatter to inject emojis based on log level."""
    
    EMOJIS = {
        logging.DEBUG: "🐛",
        logging.INFO: "✅",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def format(self, record):
        # Attach the correct emoji to the record object
        record.emoji = self.EMOJIS.get(record.levelno, "🔹")
        return super().format(record)

def setup_logger(name: str = "assistly"):
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Note the new %(emoji)s tag in the fmt string
    formatter = EmojiFormatter(
        fmt="%(asctime)s [%(emoji)s %(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()