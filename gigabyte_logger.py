import logging

class GigabyteLogger():
    def __init__(self, log_output: str):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler(log_output))
        
    def log_info(self, message):
        self.logger.info(message)
        
    def log_error(self, message):
        self.logger.error(message)
        
    def log_debug(self, message):
        self.logger.debug(message)
