import psycopg2
from psycopg2 import sql

def get_order_id_by_msg_id(conn, cur, ms_id):
    """
    Retrieves the order_id from the msg_trade table for a given ms_id.
    Prints the result and returns it.

    Parameters:
    - conn: The database connection object.
    - cur: The cursor object for database operation.
    - ms_id: The message ID to query the order_id for.
    
    Returns:
    - The order_id corresponding to the provided ms_id, or None if not found.
    """
    try:
        # Define the select query
        select_query = sql.SQL("""
            SELECT order_id
            FROM msg_trade
            WHERE ms_id = %s
        """)

        # Execute the select query with the provided ms_id
        cur.execute(select_query, (ms_id,))

        # Fetch the result from the query
        result = cur.fetchone()
        print('result: ', result)

        # Return the result (order_id or None)
        return result[0] if result else None

    except Exception as e:
        # An error occurred, print the error message
        print(f"SELECT - An error occurred: {e}")
        # Optionally, re-raise the exception if you want to propagate the error
        raise

# Example usage:
# Assuming conn is your database connection object and cur is the cursor object.
# try:
#     order_id = get_order_id_by_msg_id(conn, cur, 42)
#     if order_id is not None:
#         print(f"Order ID: {order_id}")
#     else:
#         print("No order found for the given message ID.")
# except Exception as e:
#     print(f"Failed to retrieve order ID: {e}")