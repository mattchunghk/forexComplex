import psycopg2
from psycopg2 import sql

def update_trade_message(conn, cur, tp1, tp2, tp3, stop_loss, ms_id):
    """
    Updates a trade message in the database with given take profits and stop loss values.
    Rolls back the transaction if an error occurs.

    Parameters:
    - conn: The database connection object.
    - cur: The cursor object for database operation.
    - tp1: The first take profit value.
    - tp2: The second take profit value.
    - tp3: The third take profit value.
    - stop_loss: The stop loss value.
    - ms_id: The message ID of the trade message to update.
    """
    try:
        # Define the update query
        update_query = sql.SQL("""
            UPDATE msg_trade
            SET tp1 = %s, tp2 = %s, tp3 = %s, sl = %s
            WHERE ms_id = %s
        """)

        # Execute the update query with the provided parameters
        cur.execute(update_query, (tp1, tp2, tp3, stop_loss, ms_id))

        # Commit the transaction
        conn.commit()
    except Exception as e:
        # An error occurred, rollback the transaction
        conn.rollback()
        print(f"UPDATE - An error occurred: {e}")
        # Optionally, re-raise the exception if you want to propagate the error
        raise

# Example usage:
# Assuming conn is your database connection object and cur is the cursor object.
# try:
#     update_trade_message(conn, cur, 1.123, 1.234, 1.345, 1.010, 42)
# except Exception as e:
#     print(f"Failed to update trade message: {e}")