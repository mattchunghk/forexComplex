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
# mt5_username = os.getenv('mt5_vantage_demo_2_username')
# password = os.getenv('mt5_vantage_demo_2_password')
mt5_username = os.getenv('mt5_vantage_demo_username')
password = os.getenv('mt5_vantage_demo_password')

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
    5: 'ASTRATEQ(Rev)',
    6: 'TFXC(Rev)'
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

# Function to sum profits and count wins/losses by name
def sum_profits_and_count_wins_by_name(trades):
    results = {}
    for trade in trades:
        magic_number = trade.magic  # Assuming 'magic' is an attribute of 'trade'
        name = magic_number_to_name(magic_number)  # Get the name corresponding to the magic number
        profit = trade.profit
        win = int(profit > 0)  # 1 if win, 0 if loss or break-even
        loss = int(profit <= 0)  # 1 if loss or break-even, 0 if win

        if name in results:
            results[name]['profit'] += profit
            results[name]['wins'] += win
            results[name]['losses'] += loss
        else:
            results[name] = {'profit': profit, 'wins': win, 'losses': loss}
    return results

# Function to calculate winning percentage
def calculate_winning_percentage(wins, total_trades):
    if total_trades == 0:
        return 0
    return (wins / total_trades) * 100

def get_result(message):
    timezone = pytz.utc
    start = None
    end = None
    today = datetime.now().astimezone(timezone)
    
    message_upper = message.upper()
    
    if "N" == message_upper:
        print('Now')
        start = today - timedelta(days=7)
        end = today + timedelta(days=2)
    elif "M" == message_upper:
        print('Month')
        start = today - timedelta(days=30)
        end = today + timedelta(days=2)
    elif "Y" == message_upper:
        print('Year')
        start = today - timedelta(days=365)
        end = today + timedelta(days=2)
 
    # Define the period based on user input or default to last week
    else:
        print('period')
        from_date_match = re.search(r"From: (\d{2}-\d{2}-\d{4})", message)
        to_date_match = re.search(r"To: (\d{2}-\d{2}-\d{4})", message)  
        if from_date_match and to_date_match:
            from_date_str = from_date_match.group(1)
            to_date_str = to_date_match.group(1)

            start_date = datetime.strptime(from_date_str, "%d-%m-%Y")
            end_date = datetime.strptime(to_date_str, "%d-%m-%Y") + timedelta(days=2)
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
       # Inside your main function or where you format your message
        profits_period_by_group = sum_profits_and_count_wins_by_name(trades_period)

        sorted_profits_period = dict(sorted(
            profits_period_by_group.items(),
            key=lambda item: item[1]['profit'],
            reverse=True))

        message = "Profits and Winning % by TG Group:\n"
        for group_name, data in sorted_profits_period.items():
            total_trades = data['wins'] + data['losses']
            winning_percentage = calculate_winning_percentage(data['wins'], total_trades)
            message += f"{group_name}: ${data['profit']:.2f}, {winning_percentage:.2f}%\n"


        # message += "\nOverall profits by magic number:\n"
        # for magic_number, profit in sorted_overall_profits.items():
        #     message += f"{magic_number}: {profit}\n"

        # Shut down the MT5 connection
        mt5.shutdown()

    return message



