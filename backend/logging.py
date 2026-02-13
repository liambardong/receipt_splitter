import logging
import owes

def configure():
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level, logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

class Logger:

    def __init__(self, object_name):
        self.logger = logging.getLogger(object_name)


    
    def info(self,message, **kwargs):
        self.logger.info(message, extra=kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, extra=kwargs)

    def debug(self,message, **kwargs):
        self.logger.debug(message, extra=kwargs)