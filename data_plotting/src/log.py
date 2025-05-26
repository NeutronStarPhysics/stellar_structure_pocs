import logging
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_for_object(object_name: str, message: str):
    """
    Log a message for a specific object.
    """
    log.info(f"[{object_name}] {message}")