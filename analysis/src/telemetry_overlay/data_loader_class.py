"""DataLoader module for querying and processing sensor data from a PostgreSQL database.


Provides a class-based interface for fetching time-series sensor data,
cleaning DataFrames, and building analysis-ready datasets with unit metadata.

Usage:
    df, unit, name = DataLoader.query_builder(
        sensor='DTI/Power/AC_Current',
        start_time='2025-06-08 15:17:09.00',
        end_time='2025-06-08 15:17:23.00'
    )
    Thanks to claude code for this documentation.
"""
__all__ = ['DataLoader']

import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
import time


class DataLoader():
    """Handles database connections, queries, and data cleaning for sensor data.

    Connects to a PostgreSQL database on class load using the DATABASE_URL
    environment variable. All methods are class-level — no instantiation required.

    Class Attributes:
        link (str): Database connection URL loaded from the .env file.
        conn (psycopg2.connection): Shared database connection used by all methods.
    """

    @staticmethod
    def time_calls(func):
        """Decorator that measures and prints the execution time of a function.

        Args:
            func (callable): The function to be timed.

        Returns:
            callable: Wrapped function that prints execution time after each call.
        """
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            to_return = func(*args, **kwargs)
            end = time.perf_counter()
            print(f'The function {func.__name__} took {end-start} second')
            return to_return
        return wrapper
    
    conn = None
    # Database connection — established once at class load time.
    
    load_dotenv()
    link = os.getenv(key='DATABASE_URL')
    
    if link:
      try:
        conn = psycopg2.connect(link)
      except:
        raise psycopg2.OperationalError("Couldnt connect to the database")
    
    else:
      raise Exception("No ENV file was found, please write the database url inside an ENV file")
    @classmethod
    def get_data(cls, sensor_topic, table='data', start_time=None, end_time=None):
        """Queries the database for sensor data or sensor metadata.

        Args:
            sensor_topic (str): Full sensor path (e.g. 'DTI/Power/AC_Current').
            table (str): Table to query — 'data' for time-series readings,
                'data_type' for sensor metadata (name, unit). Defaults to 'data'.
            start_time (str, optional): Start of time range (e.g. '2025-06-08 15:17:09.00').
                Required when table='data'.
            end_time (str, optional): End of time range.
                Required when table='data'.

        Returns:
            pd.DataFrame: Raw query results as a DataFrame.
        """
        if table == 'data_type':
            q = "SELECT * FROM data_type WHERE data_type.\"name\" = %s"
            df = pd.read_sql_query(q, cls.conn,params=[sensor_topic])
        else:
            q = "SELECT * FROM data WHERE data.\"dataTypeName\" = %s AND time BETWEEN %s AND %s ORDER BY time ASC"
            df = pd.read_sql_query(q, cls.conn,params=[sensor_topic,start_time,end_time])
        return df

    @classmethod
    def data_cleaner(cls, dataframe, dropping=None, time=None, format_list_to_float=None):
        """Cleans and transforms a sensor DataFrame.

        Performs optional column dropping, time normalization, and type conversion.
        Operations are applied in order: drop columns -> convert time -> convert floats.

        Note:
            This method modifies the DataFrame in-place. Pass a copy if you
            need to preserve the original.

        Args:
            dataframe (pd.DataFrame): The DataFrame to clean.
            dropping (list[str], optional): Column names to remove.
            time (bool, optional): If True, converts the 'time' column to seconds
                elapsed from the earliest timestamp.
            format_list_to_float (list[str], optional): Column names where values are
                stored as single-element lists (e.g. [1.5]) that should be
                extracted and converted to floats.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        df = dataframe
        if dropping:
            df.drop(dropping, axis=1, inplace=True)
        if time:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            df['time'] = (df['time'] - df['time'].min()).dt.total_seconds()

        if format_list_to_float:
            for val in format_list_to_float:
                df[val] = df[val].apply(lambda x: float(x[0]))
        return df

    @classmethod
    def query_builder(cls, sensor, start_time, end_time):
        """Fetches, cleans, and returns sensor data ready for analysis.

        Queries both the metadata and time-series tables, then cleans the
        data by removing unnecessary columns, normalizing timestamps to
        seconds from start, and converting list-wrapped values to floats.

        Args:
            sensor (str): Full sensor path (e.g. 'DTI/Power/AC_Current').
            start_time (str): Start of time range (e.g. '2025-06-08 15:17:09.00').
            end_time (str): End of time range (e.g. '2025-06-08 15:17:23.00').

        Returns:
            tuple: A 3-tuple of (df, unit, sensor_name) where:
                - df (pd.DataFrame): Cleaned DataFrame with 'time' (float, seconds)
                  and 'values' (float) columns.
                - unit (str): The measurement unit for this sensor (e.g. 'A', 'm/s').
                - sensor_name (str): The full sensor name from the database.
        """
        q_unit = cls.get_data(sensor=sensor, table='data_type')
        unit = q_unit['unit'][0]
        df = cls.get_data(sensor=sensor, table='data', start_time=start_time, end_time=end_time)
        df = cls.data_cleaner(df, dropping=['runId', 'dataTypeName'], time=True, format_list_to_float=['values'])
        sensor_name = q_unit['name'][0]
        return df, unit, sensor_name
