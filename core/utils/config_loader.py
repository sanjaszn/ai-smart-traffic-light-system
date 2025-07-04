import json
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def load_zone_config(path: str | Path) -> Dict[str, Any]:
    """
    Safely load zone configuration from JSON file.
    
    Args:
        path: Path to JSON configuration file
        
    Returns:
        Parsed zone configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If JSON is invalid
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"Successfully loaded config from {path}")
            return config
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {path} - {str(e)}")
        raise ValueError(f"Invalid JSON in {path}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading {path}: {str(e)}")
        raise