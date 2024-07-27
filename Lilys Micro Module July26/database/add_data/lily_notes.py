from PyQt6.QtCore import QDate, QTime
from logger_setup import logger
from typing import Dict, Any, Callable, Tuple, List

def add_lily_note_data(main_window_instance: Any,
                       widget_names: Dict[str, str],
                       db_insert_method: Callable[..., None]) -> None:
    """
    Add Lily note data to the database.

    Args:
        main_window_instance: The instance of the main window.
        widget_names: A dictionary containing the names of the widgets.
        db_insert_method: The method used to insert data into the database.

    Returns:
        None

    Raises:
        Exception: If an error occurs while adding Lily note data.

    """
    widget_methods: Dict[str, Tuple[str, str, str]] = {
        widget_names['lily_date']: (None, 'date', 'yyyy-MM-dd'),
        widget_names['lily_time']: (None, 'time', 'hh:mm:ss'),
        widget_names['lily_notes']: (widget_names['lily_notes'], 'toPlainText', ""),
        
    }
    
    data_to_insert: List[Any] = []
    for widget_name, (widget_attr, method, format_type) in widget_methods.items():
        widget = getattr(main_window_instance, widget_name)
        value = getattr(widget, method)()
        if format_type:
            value = value.toString(format_type)
        data_to_insert.append(value)
    
    try:
        db_insert_method(*data_to_insert)
        reset_lily_note_data(main_window_instance, widget_names)
    except Exception as e:
        logger.error(f"Error occurred while adding Lily note data: {e}")


def reset_lily_note_data(main_window_instance: Any, widget_names: Dict[str, str]) -> None:
    """
    Resets the Lily note data in the main window.

    Args:
        main_window_instance: An instance of the main window.
        widget_names: A dictionary containing the names of the widgets.

    Returns:
        None

    Raises:
        Exception: If an error occurs while resetting the Lily mood form.
    """
    try:
        getattr(main_window_instance, widget_names['lily_date']).setDate(QDate.currentDate())
        getattr(main_window_instance, widget_names['lily_time']).setTime(QTime.currentTime())
        getattr(main_window_instance, widget_names['lily_notes']).clear()
        # Assuming there is a model for each day
        getattr(main_window_instance, widget_names['model']).select()
    except Exception as e:
        logger.error(f"Error occurred while resetting Lily mood form: {e}")
