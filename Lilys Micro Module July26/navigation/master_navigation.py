# from sexy_logger import logger
from logger_setup import logger
from typing import Any


def change_lily_stack(lilyStack: Any, index: int) -> None:
    """
    Change the current index of the alpha stack.

    Args:
    stack_alpha (Any): The alpha stack object.
    index (int): The new index to set.

    Returns:
    None
    """
    try:
        lilyStack.setCurrentIndex(index)
        logger.info("Alpha Stack Page Change")
    except Exception as e:
        logger.error(f"Alpha Stack Page Change Error: {e}", exc_info=True)
        
        
