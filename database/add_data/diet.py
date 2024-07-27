from PyQt6.QtCore import QDate, QTime
from logger_setup import logger
from typing import Dict, Any, Callable, Tuple, List, Union

def add_lily_diet_data(main_window_instance: Any,
                       widget_names: Dict[str, str],
                       db_insert_method: Callable[..., None]) -> None:
    """
    Add Lily's diet data to the database.

    Args:
        main_window_instance: The instance of the main window.
        widget_names: A dictionary containing the names of the widgets.
        db_insert_method: The method used to insert data into the database.

    Returns:
        None

    Raises:
        Exception: If an error occurs while adding Lily's diet data.
    """
    widget_methods: Dict[str, Tuple[Any, str, str]] = {
        widget_names['lily_date']: (None, 'date', 'yyyy-MM-dd'),
        widget_names['lily_time']: (None, 'time', 'hh:mm:ss'),
    }
    
    data_to_insert: List[str] = []
    for widget_name, (widget_attr, method, format_type) in widget_methods.items():
        widget: Any = getattr(main_window_instance, widget_name)
        value: Any = getattr(widget, method)()
        if format_type:
            value = value.toString(format_type)
        data_to_insert.append(value)
    
    try:
        db_insert_method(*data_to_insert)
        reset_lily_diet_data(main_window_instance, widget_names)
    except Exception as e:
        logger.error(f"Error occurred while adding Lily mood data: {e}")


def reset_lily_diet_data(main_window_instance: Any,
                         widget_names: Dict[str, str]) -> None:
    """
    Resets the Lily diet data form by setting the date and time to current values and selecting the model.

    Args:
        main_window_instance: The instance of the main window.
        widget_names: A dictionary containing the names of the widgets used in the form.

    Returns:
        None

    Raises:
        Exception: If an error occurs while resetting the form.
    """
    try:
        getattr(main_window_instance, widget_names['lily_date']).setDate(QDate.currentDate())
        getattr(main_window_instance, widget_names['lily_time']).setTime(QTime.currentTime())
        # Assuming there is a model for each day
        getattr(main_window_instance, widget_names['model']).select()
    except Exception as e:
        logger.error(f"Error occurred while resetting Lily mood form: {e}")
