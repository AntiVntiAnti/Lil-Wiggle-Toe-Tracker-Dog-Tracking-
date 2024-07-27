from PyQt6.QtCore import QDate, QTime
from logger_setup import logger
from typing import Dict, Any, Callable, Tuple, List


def add_lily_walk_data(main_window_instance: Any,
                       widget_names: Dict[str, str],
                       db_insert_method: Callable[..., None]) -> None:
    """
    Add Lily's walk data to the database.

    Args:
        main_window_instance: The instance of the main window.
        widget_names: A dictionary containing the names of the widgets used for data input.
        db_insert_method: The method used to insert data into the database.

    Returns:
        None

    Raises:
        Exception: If an error occurs while adding Lily's walk data.

    """
    widget_methods: Dict[str, Tuple[Any, str, str]] = {
        widget_names['lily_date']: (None, 'date', 'yyyy-MM-dd'),
        widget_names['lily_time']: (None, 'time', 'hh:mm:ss'),
        widget_names['lily_behavior_slider']: (None, 'value', None),
        widget_names['lily_gait_slider']: (None, 'value', None),
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
        reset_lily_walk_data(main_window_instance, widget_names)
    except Exception as e:
        logger.error(f"Error occurred while adding Lily mood data: {e}")


def reset_lily_walk_data(main_window_instance: Any, widget_names: Dict[str, str]) -> None:
    """
    Reset the data in the Lily walk form.

    Parameters:
    - main_window_instance: The instance of the main window.
    - widget_names: A dictionary containing the names of the widgets used in the form.

    Returns:
    None
    """
    try:
        getattr(main_window_instance, widget_names['lily_date']).setDate(QDate.currentDate())
        getattr(main_window_instance, widget_names['lily_time']).setTime(QTime.currentTime())
        getattr(main_window_instance, widget_names['lily_behavior_slider']).setValue(0)
        getattr(main_window_instance, widget_names['lily_gait_slider']).setValue(0)

        # Assuming there is a model for each day
        getattr(main_window_instance, widget_names['model']).select()
    except Exception as e:
        logger.error(f"Error occurred while resetting Lily mood form: {e}")
