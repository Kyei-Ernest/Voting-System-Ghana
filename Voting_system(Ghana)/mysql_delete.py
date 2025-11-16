import mysql.connector


def delete_column(db_config, table, column):
    """
    Deletes a column from a given database table.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"ALTER TABLE {table} DROP COLUMN {column}"
        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()

        print(f"Column '{column}' deleted successfully from '{table}'.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")


def delete_row(db_config, table, condition):
    """
    Deletes a row from a given database table based on a condition.
    Example condition: "id = 5" or "username = 'john'"
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"DELETE FROM {table} WHERE {condition}"
        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()

        print(f"Row deleted successfully from '{table}'.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")
