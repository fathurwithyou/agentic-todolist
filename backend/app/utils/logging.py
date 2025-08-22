"""
Logging configuration utilities.
"""

import logging


def setup_logging(level: str = "INFO") -> None:
    """
    Set up application logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
