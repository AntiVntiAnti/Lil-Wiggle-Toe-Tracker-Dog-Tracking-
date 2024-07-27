import tracker_config as tkc
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
import os
import shutil
from logger_setup import logger
from typing import List, Union, Tuple, Dict, Any, Optional

# from sexy_logger import logger

user_dir: str = os.path.expanduser('~')
db_path: str = os.path.join(os.getcwd(), tkc.DB_NAME)  # Database Name
target_db_path: str = os.path.join(user_dir, tkc.DB_NAME)  # Database Name


def initialize_database() -> None:
    try:
        if not os.path.exists(target_db_path):
            if os.path.exists(db_path):
                shutil.copy(db_path, target_db_path)
            else:
                db: QSqlDatabase = QSqlDatabase.addDatabase('QSQLITE')
                db.setDatabaseName(target_db_path)
                if not db.open():
                    logger.error("Error: Unable to create database")
                db.close()
    except Exception as e:
        logger.error("Error: Unable to create database", str(e))


class DataManager:
    """
    A class that manages the database operations for Lily's Micro Module.
    
    Attributes:
        db: The QSqlDatabase object representing the database connection.
        query: The QSqlQuery object for executing SQL queries.
    
    Methods:
        __init__(self, db_name): Initializes the DataManager object and opens the database connection.
        setup_tables(self): Sets up the required tables in the database.
        setup_lily_notes_table(self): Creates the lily_notes_table if it doesn't exist.
        insert_into_lily_notes_table(self, lily_date, lily_time, lily_notes): Inserts data into the lily_notes_table.
        setup_time_in_room_table(self): Creates the lily_in_room_table if it doesn't exist.
        insert_into_time_in_room_table(self, lily_date, lily_time, time_in_room_slider): Inserts data into the lily_in_room_table.
        setup_lily_diet_table(self): Creates the lily_diet_table if it doesn't exist.
        insert_into_lily_diet_table(self, lily_date, lily_time): Inserts data into the lily_diet_table.
        setup_lily_mood_table(self): Creates the lily_mood_table if it doesn't exist.
        insert_into_lily_mood_table(self, lily_date, lily_time, lily_mood_slider, lily_mood_activity_slider, lily_energy_slider): Inserts data into the lily_mood_table.
        setup_wiggles_walks_table(self): Creates the lily_walk_table if it doesn't exist.
        insert_into_wiggles_walks_table(self, lily_date, lily_time, lily_behavior, lily_gait, lily_walk_note): Inserts data into the lily_walk_table.
    """
    
    def __init__(self,
                 db_name: str = target_db_path) -> None:
        """
        Initializes the DataManager object and opens the database connection.

        Args:
            db_name (str): The path to the database file.

        Returns:
            None
        """
        try:
            self.db: QSqlDatabase = QSqlDatabase.addDatabase('QSQLITE')
            self.db.setDatabaseName(db_name)
            
            if not self.db.open():
                logger.error("Error: Unable to open database")
            logger.info("DB INITIALIZING")
            self.query: QSqlQuery = QSqlQuery()
            self.setup_tables()
        except Exception as e:
            logger.error(f"Error: Unable to open database {e}", exc_info=True)
    
    def setup_tables(self) -> None:
        """
        Sets up the necessary tables in the database.

        This method calls the individual setup methods for each table:
        - setup_lily_diet_table
        - setup_lily_mood_table
        - setup_wiggles_walks_table
        - setup_time_in_room_table
        - setup_lily_notes_table

        Returns:
            None
        """
        self.setup_lily_diet_table()
        self.setup_lily_mood_table()
        self.setup_wiggles_walks_table()
        self.setup_time_in_room_table()
        self.setup_lily_notes_table()
        self.setup_lily_walk_notes_table()
    
    def setup_lily_notes_table(self) -> None:
        """
        Sets up the 'lily_notes_table' in the database if it doesn't already exist.

        This method creates a table named 'lily_notes_table' with the following columns:
        - id: INTEGER (Primary Key, Auto Increment)
        - lily_date: TEXT
        - lily_time: TEXT
        - lily_notes: TEXT

        Returns:
        - None if the table is created successfully.
        - Logs an error message if there's an error creating the table.
        """
        if not self.query.exec(f"""
                CREATE TABLE IF NOT EXISTS lily_notes_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lily_date TEXT,
                lily_time TEXT,
                lily_notes TEXT
                )"""):
            logger.error(f"Error creating table: lily_notes_table", self.query.lastError().text())
    
    def insert_into_lily_notes_table(self,
                                     lily_date: str,
                                     lily_time: str,
                                     lily_notes: str) -> None:
        """
        Inserts a new record into the lily_notes_table.

        Args:
            lily_date (str): The date of the Lily note.
            lily_time (str): The time of the Lily note.
            lily_notes (str): The content of the Lily note.

        Raises:
            ValueError: If the number of bind values does not match the number of placeholders in the SQL query.

        Returns:
            None
        """
        sql: str = f"""INSERT INTO lily_notes_table(lily_date, lily_time, lily_notes) VALUES (?, ?, ?)"""
        bind_values: List[str] = [lily_date, lily_time, lily_notes]
        try:
            self.query.prepare(sql)
            for value in bind_values:
                self.query.addBindValue(value)
            if sql.count('?') != len(bind_values):
                raise ValueError(f"""Mismatch: lily_notes_table Expected {sql.count('?')}
                    bind values, got {len(bind_values)}.""")
            if not self.query.exec():
                logger.error(f"Error inserting data: lily_notes_table - {self.query.lastError().text()}")
        except ValueError as e:
            logger.error(f"ValueError lily_notes_table: {e}")
        except Exception as e:
            logger.error(f"Error during data insertion: lily_notes_table {e}", exc_info=True)
    
    ##################################################################################################################
    # Lily Diet Table
    ##################################################################################################################
    def setup_time_in_room_table(self) -> None:
        """
        Sets up the 'lily_in_room_table' table in the database if it doesn't exist.

        This method creates the 'lily_in_room_table' table with the following columns:
        - id: INTEGER (Primary Key, Autoincrement)
        - lily_date: TEXT
        - lily_time: TEXT
        - time_in_room_slider: INTEGER

        Returns:
        None
        """
        if not self.query.exec(f"""
                CREATE TABLE IF NOT EXISTS lily_in_room_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lily_date TEXT,
                lily_time TEXT,
                time_in_room_slider INTEGER
                )"""):
            logger.error(f"Error creating table: lily_in_room_table", self.query.lastError().text())
    
    def insert_into_time_in_room_table(self,
                                       lily_date: str,
                                       lily_time: str,
                                       time_in_room_slider: int) -> None:
        """
        Inserts a new record into the lily_in_room_table.

        Args:
            lily_date (str): The date of the record.
            lily_time (str): The time of the record.
            time_in_room_slider (int): The value of the time_in_room_slider.

        Raises:
            ValueError: If the number of bind values does not match the expected number of placeholders in the SQL query.

        Returns:
            None
        """
        sql: str = f"""INSERT INTO lily_in_room_table(lily_date, lily_time,
                                       time_in_room_slider) VALUES (?, ?, ?)"""
        bind_values: List[Union[str, int]] = [lily_date, lily_time, time_in_room_slider]
        try:
            self.query.prepare(sql)
            for value in bind_values:
                self.query.addBindValue(value)
            if sql.count('?') != len(bind_values):
                raise ValueError(f"""Mismatch: lily_in_room_table Expected {sql.count('?')}
                    bind values, got {len(bind_values)}.""")
            if not self.query.exec():
                logger.error(
                    f"Error inserting data: lily_in_room_table - {self.query.lastError().text()}")
        except ValueError as e:
            logger.error(f"ValueError lily_in_room_table: {e}")
        except Exception as e:
            logger.error(f"Error during data insertion: lily_in_room_table {e}", exc_info=True)
    
    ##################################################################################################################
    # Lily Diet Table
    ##################################################################################################################
    def setup_lily_diet_table(self) -> None:
        """
        Sets up the 'lily_diet_table' in the database if it doesn't already exist.

        This method creates a table named 'lily_diet_table' with the following columns:
        - id: INTEGER (Primary Key, Auto Increment)
        - lily_date: TEXT
        - lily_time: TEXT

        Returns:
        None
        """
        if not self.query.exec(f"""
                CREATE TABLE IF NOT EXISTS lily_diet_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lily_date TEXT,
                lily_time TEXT
                )"""):
            logger.error(f"Error creating table: lily_diet_table", self.query.lastError().text())
    
    def insert_into_lily_diet_table(self,
                                    lily_date: str,
                                    lily_time: str) -> None:
        """
        Inserts a new record into the lily_diet_table.

        Args:
            lily_date (str): The date of the record.
            lily_time (str): The time of the record.

        Raises:
            ValueError: If the number of bind values does not match the expected number of placeholders in the SQL query.

        Returns:
        None
        """
        sql: str = f"""INSERT INTO lily_diet_table(lily_date, lily_time) VALUES (?, ?)"""
        bind_values: List[str] = [lily_date, lily_time]
        try:
            self.query.prepare(sql)
            for value in bind_values:
                self.query.addBindValue(value)
            if sql.count('?') != len(bind_values):
                raise ValueError(f"""Mismatch: lily_eats_table Expected {sql.count('?')}
                    bind values, got {len(bind_values)}.""")
            if not self.query.exec():
                logger.error(
                    f"Error inserting data: lily_eats_table - {self.query.lastError().text()}")
        except ValueError as e:
            logger.error(f"ValueError lily_eats_table: {e}")
        except Exception as e:
            logger.error(f"Error during data insertion: lily_eats_table {e}", exc_info=True)
    
    ##################################################################################################################
    #       Lily MOOD table
    ##################################################################################################################
    def setup_lily_mood_table(self) -> None:
        if not self.query.exec(f"""
                CREATE TABLE IF NOT EXISTS lily_mood_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lily_date TEXT,
                lily_time TEXT,
                lily_mood_slider INTEGER,
                lily_mood_activity_slider INTEGER,
                lily_energy_slider INTEGER
                    )"""):
            logger.error(f"Error creating table: lily_mood_table", self.query.lastError().text())
    
    def insert_into_lily_mood_table(self,
                                    lily_date: str,
                                    lily_time: str,
                                    lily_mood_slider: int,
                                    lily_mood_activity_slider: int,
                                    lily_energy_slider: int) -> None:
        """
        Inserts a new record into the lily_mood_table.

        Args:
            lily_date (str): The date of the record.
            lily_time (str): The time of the record.
            lily_mood_slider (int): The mood slider value.
            lily_mood_activity_slider (int): The mood activity slider value.
            lily_energy_slider (int): The energy slider value.

        Raises:
            ValueError: If the number of bind values does not match the expected number in the SQL query.

        Returns:
        None
        """
        sql: str = f"""INSERT INTO lily_mood_table(
        lily_date, lily_time, lily_mood_slider, lily_mood_activity_slider, lily_energy_slider)
        VALUES (?, ?, ?, ?, ?)"""
        bind_values: List[Union[str, int]] = [lily_date, lily_time, lily_mood_slider,
                                              lily_mood_activity_slider, lily_energy_slider]
        try:
            self.query.prepare(sql)
            for value in bind_values:
                self.query.addBindValue(value)
            if sql.count('?') != len(bind_values):
                raise ValueError(f"""Mismatch: lily_mood_table Expected
                    {sql.count('?')} bind values, got {len(bind_values)}.""")
            if not self.query.exec():
                logger.error(
                    f"Error inserting data: lily_mood_table - {self.query.lastError().text()}")
        except ValueError as ve:
            logger.error(f"ValueError lily_mood_table: {str(ve)}")
        except Exception as e:
            logger.error(f"Error during data insertion: lily_mood_table {e}", exc_info=True)
    
    # Lily WALKS table
    def setup_wiggles_walks_table(self) -> None:
        """
        Sets up the 'lily_walk_table' in the database if it doesn't already exist.

        This method creates a table named 'lily_walk_table' with the following columns:
        - id: INTEGER (Primary Key, Autoincrement)
        - lily_date: TEXT
        - lily_time: TEXT
        - lily_behavior: INTEGER
        - lily_gait: INTEGER

        Returns:
        None
        """
        if not self.query.exec(f"""
                CREATE TABLE IF NOT EXISTS lily_walk_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lily_date TEXT,
                lily_time TEXT,
                lily_behavior INTEGER,
                lily_gait INTEGER
                )"""):
            logger.error(f"Error creating table: lily_walk_table", self.query.lastError().text())
    
    def insert_into_wiggles_walks_table(self,
                                        lily_date: str,
                                        lily_time: str,
                                        lily_behavior: int,
                                        lily_gait: int) -> None:
        """
        Inserts a new record into the lily_walk_table.

        Args:
            lily_date (str): The date of the walk.
            lily_time (str): The time of the walk.
            lily_behavior (str): The behavior during the walk.
            lily_gait (str): The gait during the walk.

        Raises:
            ValueError: If the number of bind values does not match the number of placeholders in the SQL query.

        Returns:
        None
        """
        sql: str = f"""INSERT INTO lily_walk_table(
            lily_date, lily_time, lily_behavior, lily_gait)
            VALUES (?, ?, ?, ?)"""
        
        bind_values: List[Union[str, int]] = [lily_date, lily_time, lily_behavior, lily_gait]
        try:
            self.query.prepare(sql)
            for value in bind_values:
                self.query.addBindValue(value)
            if sql.count('?') != len(bind_values):
                raise ValueError(
                    f"Mismatch: lily_walk_table Expected {sql.count('?')} bind values, got "
                    f"{len(bind_values)}.")
            if not self.query.exec():
                logger.error(
                    f"Error inserting data: lily_walk_table - {self.query.lastError().text()}")
        except ValueError as ve:
            logger.error(f"ValueError lily_walk_table: {str(ve)}")
        except Exception as e:
            logger.error(f"Error during data insertion: lily_walk_table", str(e))
    
    def setup_lily_walk_notes_table(self) -> None:
        """
        Sets up the 'lily_walk_table' in the database if it doesn't already exist.

        This method creates a table named 'lily_walk_table' with the following columns:
        - id: INTEGER (Primary Key, Autoincrement)
        - lily_date: TEXT
        - lily_time: TEXT
        - lily_walk_note: TEXT

        Returns:
        None
        """
        if not self.query.exec(f"""
                CREATE TABLE IF NOT EXISTS lily_walk_notes_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lily_date TEXT,
                lily_time TEXT,
                lily_walk_note TEXT
                )"""):
            logger.error(f"Error creating table: lily_walk_notes_table",
                         self.query.lastError().text())
    
    def insert_into_lily_walk_notes_table(self,
                                          lily_date: str,
                                          lily_time: str,
                                          lily_walk_note: str) -> None:
        """
        Inserts a new record into the lily_walk_notes_table.

        Args:
            lily_date (str): The date of the walk.
            lily_time (str): The time of the walk.
            lily_walk_note (str): Additional notes about the walk.

        Raises:
            ValueError: If the number of bind values does not match the number of placeholders in the SQL query.

        Returns:
        None
        """
        sql: str = f"""INSERT INTO lily_walk_notes_table(
            lily_date, lily_time, lily_walk_note)
            VALUES (?, ?, ?)"""
        
        bind_values: List[Union[str, int]] = [lily_date, lily_time, lily_walk_note]
        try:
            self.query.prepare(sql)
            for value in bind_values:
                self.query.addBindValue(value)
            if sql.count('?') != len(bind_values):
                raise ValueError(
                    f"Mismatch: lily_walk_notes_table Expected {sql.count('?')} bind values, got "
                    f"{len(bind_values)}.")
            if not self.query.exec():
                logger.error(
                    f"Error inserting data: lily_walk_notes_table - {self.query.lastError().text()}")
        except ValueError as ve:
            logger.error(f"ValueError lily_walk_notes_table: {str(ve)}")
        except Exception as e:
            logger.error(f"Error during data insertion: lily_walk_notes_table", str(e))


def close_database(self) -> None:
    """
    Closes the database connection if it is open.

    This function checks if the database connection is open and closes it if it is.
    If the database is already closed or an error occurs while closing the database,
    an exception is logged.

    Args:
        self: The instance of the database manager.

    Returns:
        None
    """
    try:
        logger.info("if database is open")
        if self.db.isOpen():
            logger.info("the database is closed successfully")
            self.db.close()
    except Exception as e:
        logger.exception(f"Error closing database: {e}")
