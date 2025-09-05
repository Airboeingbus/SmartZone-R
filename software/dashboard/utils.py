# software/dashboard/utils.py
import mysql.connector
import pandas as pd
from mysql.connector import Error

def load_data():
    """
    Connect to MySQL database and fetch runway data as a DataFrame.
    Returns the same columns as the CSV version.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='smartzone_r',
            user='root',
            password='Shakti@2027'  # Replace with your actual password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT * FROM runway_data"  # Replace with your table name
            df = pd.read_sql(query, connection)
            return df

    except Error as e:
        st.error(f"Error connecting to MySQL Database: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()