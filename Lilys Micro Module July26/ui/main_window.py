import datetime
from PyQt6 import QtWidgets
from PyQt6.QtCore import QDate, QSettings, QTime, Qt, QByteArray, QDateTime
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QDialog, QFormLayout, QLineEdit
from PyQt6.QtPrintSupport import QPrintDialog

import tracker_config as tkc

#############################################################################
# UI
from ui.main_ui.gui import Ui_MainWindow

#############################################################################
# LOGGER
#############################################################################
from logger_setup import logger

#############################################################################
# NAVIGATION
#############################################################################
from navigation.master_navigation import change_lily_stack
#############################################################################
# UTILITY
#############################################################################
from utility.app_operations.save_generic import (
    TextEditSaver)

# Window geometry and frame
from utility.app_operations.frameless_window import (
    FramelessWindow)
from utility.app_operations.window_controls import (
    WindowController)
from utility.widgets_set_widgets.slider_spinbox_connections import (
    connect_slider_spinbox)

##############################################################################
# DATABASE Magicks w/ Wizardry & Necromancy
##############################################################################
# Database connections
from database.database_manager import (
    DataManager)

# Delete Records
from database.database_utility.delete_records import (
    delete_selected_rows)

# setup Models
from database.database_utility.model_setup import (
    create_and_set_model)

# add lily mods walk diet and mood
from database.add_data.time_in_room import add_time_in_room_data
from database.add_data.mood import add_lily_mood_data
from database.add_data.diet import add_lily_diet_data
from database.add_data.walks import add_lily_walk_data
from database.add_data.lily_notes import add_lily_note_data
from database.add_data.walk_notes import add_lily_walk_notes


class MainWindow(FramelessWindow, QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self,
                 *args,
                 **kwargs):
        """
        Initializes the main window of the application.

        This class inherits from `FramelessWindow`, `QtWidgets.QMainWindow`, and `Ui_MainWindow`.
        It sets up the UI, database manager, QSettings, and various other operations.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.lily_note_model = None
        self.lily_walk_note_model = None
        self.lily_room_model = None
        self.lily_walk_model = None
        self.lily_mood_model = None
        self.lily_mood_model = None
        self.lily_diet_model = None
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        # Database init
        self.db_manager = DataManager()
        self.setup_models()
        # QSettings settings_manager setup
        self.settings = QSettings(tkc.ORGANIZATION_NAME, tkc.APPLICATION_NAME)
        self.restore_state()
        self.text_edit_saver = TextEditSaver()
        self.window_controller = WindowController()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.widget_operations()
        self.setup_database_commits()
        self.app_operations()
        self.setup_delete_actions()
        self.switch_to_input_page_size_setter()
    
    def switch_to_input_page_size_setter(self):
        """
        Switches the current widget to the lilyInputPage and resizes the window to 300x300.
        """
        self.lilyStack.setCurrentWidget(self.lilyInputPage)
        self.resize(240, 275)
        self.setFixedSize(240, 275)
    
    def switch_to_dataview_size_setter(self):
        self.lilyStack.setCurrentWidget(self.lilydataView)
        self.resize(850, 450)
        self.setFixedSize(850, 450)
    
    def setup_database_commits(self):
        try:
            # setup lily commits (diet, mood, walk)
            self.lily_diet_data_commit()
            self.add_lily_mood_data()
            self.lily_walk_commit()
            self.lily_in_room_commit()
            self.add_lily_notes_data()
            self.add_lily_walk_notes_data()
        
        except Exception as e:
            logger.error(f"Error occurred setting up commits {e}", exc_info=True)
    
    ##########################################################################################
    # Primary OPS
    ##########################################################################################
    def widget_operations(self):
        try:
            self.slider_set_spinbox()
            self.auto_date_time()
            self.stack_navigation()
        except Exception as e:
            logger.error(f"Error setting up primary operations {e}", exc_info=True)
    
    ##########################################################################################
    # APP-OPERATIONS setup
    ##########################################################################################
    def app_operations(self):
        try:
            self.action_input_page.triggered.connect(self.switch_to_input_page_size_setter)
            self.action_data_view_page.triggered.connect(self.switch_to_dataview_size_setter)
            self.lilyStack.currentChanged.connect(self.on_page_changed)
            last_index = self.settings.value("lastPageIndex", 0, type=int)
            self.lilyStack.setCurrentIndex(last_index)
        except Exception as e:
            logger.error(f"Error occurred while setting up app_operations : {e}", exc_info=True)
    
    #######################################################################
    # auto-DATE TIME
    #######################################################################
    def auto_date_time(self) -> None:
        try:
            widget_date_edit = [self.lily_date]
            widget_time_edit = [self.lily_time]
            
            for widget in widget_date_edit:
                widget.setDate(QDate.currentDate())
            for widget in widget_time_edit:
                widget.setTime(QTime.currentTime())
        except Exception as e:
            logger.exception(f"Auto-Date time failed to be so auto... {e}", exc_info=True)
    
    def on_page_changed(self,
                        index):
        """
        Callback method triggered when the page is changed in the UI.

        Args:
            index (int): The index of the new page.
        """
        self.settings.setValue("lastPageIndex", index)
    
    #########################################################################
    # UPDATE TIME support
    #########################################################################
    @staticmethod
    def update_time(state,
                    time_label):
        try:
            if state == 2:  # checked state
                current_time = QTime.currentTime()
                time_label.setTime(current_time)
        except Exception as e:
            logger.error(f"Error updating time. {e}", exc_info=True)
    
    #######################################################################################
    # SLIDER UPDATES SPINBOX/VICE VERSA SETUP
    #######################################################################################
    def slider_set_spinbox(self):
        connect_slider_to_spinbox = {
            self.lily_time_in_room_slider: self.lily_time_in_room,
            self.lily_mood_slider: self.lily_mood,
            self.lily_mood_activity_slider: self.lily_activity,
            self.lily_gait_slider: self.lily_gait,
            self.lily_behavior_slider: self.lily_behavior,
            self.lily_energy_slider: self.lily_energy,
        }
        
        for slider, spinbox in connect_slider_to_spinbox.items():
            connect_slider_spinbox(slider, spinbox)
    
    #############################################################################################
    # Agenda Journal Navigation
    #############################################################################################
    def stack_navigation(self):
        try:
            # Mapping actions and buttons to stack page indices for the agenda journal
            lilyStack_nav = {
                self.action_input_page: 0, self.action_data_view_page: 1
            }
            
            # Main Stack Navigation
            for action, page in lilyStack_nav.items():
                action.triggered.connect(
                    lambda _, p=page: change_lily_stack(self.lilyStack, p))
        
        except Exception as e:
            logger.error(f"An error has occurred: {e}", exc_info=True)

    def lily_diet_data_commit(self):
        try:
            self.lily_ate_check.clicked.connect(lambda: add_lily_diet_data(self, {
                "lily_date": "lily_date", "lily_time": "lily_time",
                "model": "lily_diet_model",
            }, self.db_manager.insert_into_lily_diet_table, ))
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def add_lily_mood_data(self):
        try:
            self.action_commit_mood.triggered.connect(lambda: add_lily_mood_data(self, {
                "lily_date": "lily_date",
                "lily_time": "lily_time",
                "lily_mood_slider": "lily_mood_slider",
                "lily_energy_slider": "lily_energy_slider",
                "lily_mood_activity_slider": "lily_mood_activity_slider",
                "model": "lily_mood_model",
            }, self.db_manager.insert_into_lily_mood_table, ))
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def add_lily_notes_data(self):
        try:
            self.action_commit_lily_notes.triggered.connect(lambda: add_lily_note_data(self, {
                "lily_date": "lily_date", "lily_time": "lily_time",
                "lily_notes": "lily_notes",
                "model": "lily_note_model",
            }, self.db_manager.insert_into_lily_notes_table, ))
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def lily_walk_commit(self):
        try:
            self.lily_walk_btn.clicked.connect(lambda: add_lily_walk_data(self, {
                "lily_date": "lily_date", "lily_time": "lily_time",
                "lily_behavior_slider": "lily_behavior_slider",
                "lily_gait_slider": "lily_gait_slider",
                "model": "lily_walk_model"
            }, self.db_manager.insert_into_wiggles_walks_table, ))
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def lily_in_room_commit(self):
        try:
            self.action_commit_room_time.triggered.connect(lambda: add_time_in_room_data(self, {
                "lily_date": "lily_date", "lily_time": "lily_time", "lily_time_in_room_slider":
                    "lily_time_in_room_slider", "model": "lily_room_model"
            }, self.db_manager.insert_into_time_in_room_table))
        except Exception as e:
            logger.error(f"Error occurring during in_room commit main_window.py loc. {e}",
                         exc_info=True)
    
    def add_lily_walk_notes_data(self):
        try:
            self.lily_walk_btn.clicked.connect(lambda: add_lily_walk_notes(self, {
                "lily_date": "lily_date", "lily_time": "lily_time",
                "lily_walk_note": "lily_walk_note", "model": "lily_walk_note_model"
            }, self.db_manager.insert_into_lily_walk_notes_table, ))
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def setup_models(self) -> None:
        try:
            self.lily_diet_model = create_and_set_model("lily_diet_table", self.lily_diet_table)
            self.lily_mood_model = create_and_set_model("lily_mood_table", self.lily_mood_table)
            self.lily_walk_model = create_and_set_model("lily_walk_table", self.lily_walk_table)
            self.lily_room_model = create_and_set_model("lily_in_room_table",
                                                        self.time_in_room_table)
            self.lily_note_model = create_and_set_model("lily_notes_table", self.lily_notes_table)
            self.lily_walk_note_model = create_and_set_model("lily_walk_notes_table",
                                                             self.lily_walk_note_table)
        except Exception as e:
            logger.error(f"Error setting up models: {e}", exc_info=True)
    
    def setup_delete_actions(self):
        try:
            self.action_delete_record.triggered.connect(
                lambda: delete_selected_rows(
                    self,
                    'lily_walk_table',
                    'lily_walk_model'
                )
            )
            self.action_delete_record.triggered.connect(
                lambda: delete_selected_rows(
                    self,
                    'lily_diet_table',
                    'lily_diet_model'
                )
            )
            self.action_delete_record.triggered.connect(
                lambda: delete_selected_rows(
                    self,
                    'lily_mood_table',
                    'lily_mood_model'
                )
            )
            self.action_delete_record.triggered.connect(
                lambda: delete_selected_rows(
                    self,
                    'time_in_room_table',
                    'lily_room_model'
                )
            )
            self.action_delete_record.triggered.connect(
                lambda: delete_selected_rows(
                    self,
                    'lily_notes_table',
                    'lily_note_model'
                )
            )
            self.action_delete_record.triggered.connect(
                lambda: delete_selected_rows(
                    self,
                    'lily_walk_note_table',
                    'lily_walk_note_model'
                )
            )
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
    
    def save_state(self):
        """
        Saves the state of various components in the main window.

        This method saves the state of different components in the main window, including Lily's mood settings,
        Lily's walk modules settings, Lily's diet module settings, and the window geometry state.

        Raises:
            Exception: If there is an error while saving the state.

        """
        try:
            self.settings.setValue('lily_time_in_room_slider', self.lily_time_in_room_slider.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_mood_slider', self.lily_mood_slider.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_mood_activity_slider',
                                   self.lily_mood_activity_slider.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_energy_slider', self.lily_energy_slider.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_time_in_room', self.lily_time_in_room.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_mood', self.lily_mood.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_activity', self.lily_activity.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.settings.setValue('lily_energy', self.lily_energy.value())
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
            # save window geometry state
        try:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def restore_state(self) -> None:
        """
        Restores the state of various settings and managers, including sun,
        moon, and weekday journals, diet settings, Lily's mood and walk settings,
        sleep state, basics, wellbeing tracker, physical pain rate, and mental breakup.
        Also restores window geometry and pushbutton disabled/enabled state.
        """
        try:
            # restore window geometry state
            self.restoreGeometry(self.settings.value("geometry", QByteArray()))
        except Exception as e:
            logger.error(f"Error restoring the minds module : stress state {e}")
        try:
            self.lily_time_in_room_slider.setValue(self.settings.value('lily_time_in_room_slider', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.lily_mood_slider.setValue(self.settings.value('lily_mood_slider', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.lily_mood_activity_slider.setValue(self.settings.value('lily_mood_activity_slider', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
            
        try:
            self.lily_energy_slider.setValue(self.settings.value('lily_energy_slider', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.lily_time_in_room.setValue(self.settings.value('lily_time_in_room', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.lily_mood.setValue(self.settings.value('lily_mood', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.lily_activity.setValue(self.settings.value('lily_activity', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.lily_energy.setValue(self.settings.value('lily_energy', 0, type=int))
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        try:
            self.restoreState(self.settings.value("windowState", QByteArray()))
        except Exception as e:
            logger.error(f"Error restoring WINDOW STATE {e}", exc_info=True)
    
    def closeEvent(self,
                   event: QCloseEvent) -> None:
        """
        Event handler for the close event of the main window.

        Saves the state before closing the window.

        Args:
            event (QCloseEvent): The close event object.

        Returns:
            None
        """
        try:
            self.save_state()
        except Exception as e:
            logger.error(f"error saving state during closure: {e}", exc_info=True)
