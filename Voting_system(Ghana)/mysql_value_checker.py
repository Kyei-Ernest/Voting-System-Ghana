import mysql.connector
from mysql.connector import Error


def check_value_exists(db_config, table, column, user_input):
    """
    Checks whether a specific value exists in a given table column.
    Returns True if found, False otherwise.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(buffered=True)

        query = f"SELECT COUNT(*) FROM {table} WHERE {column} = %s"
        cursor.execute(query, (user_input,))
        result = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return result > 0

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return False


def check_column_exists(db_config, table_name, column_name):
    """
    Checks whether a specific column exists in a given table.
    Returns True if found, False otherwise.
    """
    try:
        conn = mysql.connector.connect(**db_config)

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(f"SHOW COLUMNS FROM {table_name};")
            columns = cursor.fetchall()

            column_exists = any(col[0] == column_name for col in columns)

            cursor.close()
            conn.close()

            return column_exists

    except Error as e:
        print(f"Error: {e}")
        return False
