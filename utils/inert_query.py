import psycopg2
from psycopg2 import sql

def insert_msg_trade(conn, cur, ms_id, order_type, symbol, order_price, tp1, tp2, tp3, sl, order_id):
    """
    Inserts a new record into the msg_trade table with the provided parameters.

    Parameters:
    - conn: The database connection object.
    - cur: The cursor object for database operation.
    - ms_id: The message ID.
    - order_type: The type of the order (e.g., 'BUY', 'SELL').
    - symbol: The trading symbol (e.g., 'EURUSD').
    - order_price: The price at which the order was placed.
    - tp1: The first take profit value.
    - tp2: The second take profit value.
    - tp3: The third take profit value.
    - sl: The stop loss value.
    - order_id: The order ID.
    """
    try:
        # Define the insert query
        insert_query = sql.SQL("""
            INSERT INTO msg_trade (ms_id, order_type, symbol, order_price, tp1, tp2, tp3, sl, order_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

        # Execute the insert query with the provided parameters
        cur.execute(insert_query, (ms_id, order_type, symbol, order_price, tp1, tp2, tp3, sl, order_id))

        # Commit the transaction
        conn.commit()

    except psycopg2.Error as e:
        # An error occurred, rollback the transaction
        print(f"Database error: {e}")
        conn.rollback()
        # Optionally, re-raise the exception if you want to propagate the error
        raise
    except Exception as e:
        # Any other exception occurred, rollback the transaction
        print(f"INSERT - An error occurred: {e}")
        conn.rollback()
        # Optionally, re-raise the exception if you want to propagate the error
        raise

# Example usage:
# Assuming conn is your database connection object and cur is the cursor object.
# try:
#     insert_msg_trade(conn, cur, 42, 'BUY', 'EURUSD', 1.1234, 1.1300, 1.1350, 1.1400, 1.1100, 123456)
#     print("Trade message inserted successfully.")
# except Exception as e:
#     print(f"Failed to insert trade message: {e}")