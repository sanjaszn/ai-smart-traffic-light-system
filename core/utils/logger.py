import logging
from typing import Optional
import sys

def get_logger(
    name: str,
    level: int = logging.INFO,
    format_str: Optional[str] = None,
    stream = sys.stdout
) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)
        format_str: Custom log format string
        stream: Output stream (default: stdout)
        
    Returns:
        Configured logger instance
    """
    if format_str is None:
        format_str = '%(asctime)s | %(levelname)8s | %(name)s: %(message)s'
        
    formatter = logging.Formatter(format_str)
    
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    # Prevent duplicate handlers
    if len(logger.handlers) > 1:
        logger.handlers = [handler]
        
    return logger