from datetime import datetime, timedelta
import pytz
import os

from mt5linux import MetaTrader5
mt5 = MetaTrader5(
    host = 'localhost',
    # host = os.getenv('mt5_host'),
    port = 18812      
)  

# path = "C:\Program Files\Vantage International MT5/terminal64.exe"
# path = "/home/ubuntu/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
path = "/Users/mattchung/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
# server = 'Pepperstone-Demo'
server = 'VantageInternational-Demo'
mt5_username = os.getenv('mt5_vantage_demo_2_username')
password = os.getenv('mt5_vantage_demo_2_password')
# mt5_username = os.getenv('mt5_vantage_demo_username')
# password = os.getenv('mt5_vantage_demo_password')

deviation = 10
# def start_mt5(username, password, server, path):
def start_mt5():
    # Ensure that all variables are the correct type
    uname = int(mt5_username)  # Username must be an int
    pword = str(password)  # Password must be a string
    trading_server = str(server)  # Server must be a string
    filepath = str(path)  # Filepath must be a string

    # Attempt to start MT5
    if mt5.initialize(login=uname, password=pword, server=trading_server, path=filepath):
        # Login to MT5
        if mt5.login(login=uname, password=pword, server=trading_server):
            return True
        else:
            print("Login Fail")
            # quit()
            return PermissionError
    else:
        print("MT5 Initialization Failed")
        # quit()
        return ConnectionAbortedError
    
def connect():
    mt5.initialize()
    
start_mt5()
connect()
mt5.initialize()
print('mt5.initialize(): ', mt5.initialize())
# mt5.terminal_info()
# print('mt5.terminal_info(): ', mt5.terminal_info())
# Set time zone to UTC for consistency
# timezone = pytz.utc
timezone = pytz.timezone("Asia/Hong_Kong")

# Define the period for last week
today = datetime.now(timezone)
last_week_start = today - timedelta(days=today.weekday() + 14)
last_week_end = today
# last_week_end = last_week_start + timedelta(days=6)

# Convert last_week_start and last_week_end to Unix timestamps
last_week_start_timestamp = int(last_week_start.timestamp())
last_week_end_timestamp = int(last_week_end.timestamp())

# Retrieve trade history from last week and overall
trades_last_week = mt5.history_deals_get(last_week_start_timestamp, last_week_end_timestamp)
all_trades = mt5.history_deals_get()
print('all_trades: ', all_trades)

if trades_last_week is None or all_trades is None:
    print("No trades found or an error occurred.")
    mt5.shutdown()
    quit()

# Function to sum profits by comment
def sum_profits_by_comment(trades):
    results = {}
    for trade in trades:
        comment = trade.comment
        profit = trade.profit
        if comment in results:
            results[comment] += profit
        else:
            results[comment] = profit
    return results

# Sum profits for last week and overall
profits_last_week_by_comment = sum_profits_by_comment(trades_last_week)
overall_profits_by_comment = sum_profits_by_comment(all_trades)

# Print the results
print("Profits for last week by comment:")
for comment, profit in profits_last_week_by_comment.items():
    print(f"{comment}: {profit}")

print("\nOverall profits by comment:")
for comment, profit in overall_profits_by_comment.items():
    print(f"{comment}: {profit}")

# Shut down the MT5 connection
mt5.shutdown()