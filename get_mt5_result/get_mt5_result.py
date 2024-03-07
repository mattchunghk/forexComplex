from datetime import datetime, timedelta
import re
import pytz
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# from mt5linux import MetaTrader5
# mt5 = MetaTrader5(
#     host = 'localhost',
#     # host = os.getenv('mt5_host'),
#     port = 18812      
# )  
import MetaTrader5 as mt5


path = "C:\Program Files\Vantage International MT5/terminal64.exe"
# path = "/home/ubuntu/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
# path = "/Users/mattchung/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
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

# Define the mapping of magic numbers to names
magic_to_name_mapping = {
    1: 'TFXC',
    2: 'PIPXPERT',
    3: 'FXGoldenCircle',
    4: 'ASTRATEQ',
    5: 'ASTRATEQ(Rev)'
    # Add more mappings here if needed
}
def magic_number_to_name(magic_number):
    # Return the name corresponding to the magic number, or "Unknown" if not found
    return magic_to_name_mapping.get(magic_number, "testing")

# Function to sum profits by comment
def sum_profits_by_name(trades):
    results = {}
    for trade in trades:
        # print('trade: ', trade)
        magic_number = trade.magic  # Assuming that 'magic' is an attribute of 'trade'
        name = magic_number_to_name(magic_number)  # Get the name corresponding to the magic number
        profit = trade.profit
        if name in results:
            results[name] += profit
        else:
            results[name] = profit
    return results

def get_result(message):
    print('message: ', message)
    timezone = pytz.utc

    if "NOW" == message.upper():
        today = datetime.now(timezone)
        start = today - timedelta(days=today.weekday() + 7)
        print('start: ', start)
        end = today
        print('end: ', end)
    # Define the period based on user input or default to last week
    else:
        from_date_match = re.search(r"From: (\d{2}-\d{2}-\d{4})", message)
        to_date_match = re.search(r"To: (\d{2}-\d{2}-\d{4})", message)  
        if from_date_match and to_date_match:
            from_date_str = from_date_match.group(1)
            to_date_str = to_date_match.group(1)

            start_date = datetime.strptime(from_date_str, "%d-%m-%Y")
            end_date = datetime.strptime(to_date_str, "%d-%m-%Y")
            start = timezone.localize(start_date)
            end = timezone.localize(end_date)

    # Convert start and end dates to Unix timestamps
    start_timestamp = int(start.timestamp())
    end_timestamp = int(end.timestamp())
    
    start_mt5()

 

    # Retrieve trade history for the specified period and overall
    trades_period =  mt5.history_deals_get(start_timestamp, end_timestamp)

    # all_trades =  mt5.history_deals_get(start_timestamp, end_timestamp)

    message = ""

    if trades_period is None :
        print("No trades found or an error occurred.")
        message = "No trades in this period"
        mt5.shutdown()
    else:
        # Sum profits for the specified period and overall
        profits_period_by_magic_number = sum_profits_by_name(trades_period)
        # overall_profits_by_magic_number = sum_profits_by_name(all_trades)

        # Sort the results by profit from highest to lowest
        sorted_profits_period = dict(sorted(profits_period_by_magic_number.items(), key=lambda item: item[1], reverse=True))
        # sorted_overall_profits = dict(sorted(overall_profits_by_magic_number.items(), key=lambda item: item[1], reverse=True))

       # Prepare the results in a message format
        message = "Profits by TG Group:\n"
        for group_name, profit in sorted_profits_period.items():
           message += f"{group_name}: ${profit:.2f}\n"

        # message += "\nOverall profits by magic number:\n"
        # for magic_number, profit in sorted_overall_profits.items():
        #     message += f"{magic_number}: {profit}\n"

        # Shut down the MT5 connection
        mt5.shutdown()

    return message



