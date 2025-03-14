import logging
from pathlib import Path

def setup_logging():
    Path('logs').mkdir(exist_ok=True)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    info_logger = logging.getLogger('info_logger')
    info_logger.setLevel(logging.INFO)
    info_handler = logging.FileHandler('logs/info.log')
    info_handler.setFormatter(formatter)
    info_logger.addHandler(info_handler)
    info_logger.propagate = False
    
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)
    error_logger.propagate = False
    
    return info_logger, error_logger

info_logger, error_logger = setup_logging() 