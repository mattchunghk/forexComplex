
from datetime import datetime
import time
import MetaTrader5 as mt5
from telethon.sync import TelegramClient, events
import os
from telethon import TelegramClient
from dotenv import load_dotenv
from get_mt5_result.get_mt5_result import get_result

from group_select.group_select import tg_group_selector
from utils.inert_query import insert_msg_trade
from utils.select_query import get_order_id_by_msg_id
from utils.update_query import update_trade_message
load_dotenv()

import psycopg2
channel_index=0

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="forex",
    user="postgres",
    password="postgres"
)
# Create a cursor object to interact with the database
cur = conn.cursor()


path = "C:\Program Files\Vantage International MT5/terminal64.exe"
# path = "/Users/mattchung/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
server = 'VantageInternational-Demo'
# mt5_username = os.getenv('mt5_vantage_demo_2_username')
# password = os.getenv('mt5_vantage_demo_2_password')
mt5_username = os.getenv('mt5_vantage_demo_username')
password = os.getenv('mt5_vantage_demo_password')

deviation = 10
# def start_mt5(username, password, server, path):
def start_mt5(mt5_username,password,server,path):
    # Ensure that all variables are the correct type
    uname = int(mt5_username)  # Username must be an int
    pword = str(password)  # Password must be a string
    trading_server = str(server)  # Server must be a string
    filepath = str(path)  # Filepath must be a string

    # Attempt to start MT5
    if mt5.initialize(login=uname, password=pword, server=trading_server, path=filepath):
        # Login to MT5
        if mt5.login(login=uname, password=pword, server=trading_server):
            print("Login Successfully")
            return True
        else:
            print("Login Fail")
            # quit()
            return PermissionError
    else:
        print("MT5 Initialization Failed")
        # quit()
        return ConnectionAbortedError
    
                    
start_mt5(mt5_username,password,server,path)


positions = mt5.positions_get(symbol="XAUUSD")
position_id = None
for position in positions:
    if position.magic == 0 and position.sl == 0.0 and position.tp == 0.0:
        position_id =position.ticket



print('result: ', position_id)