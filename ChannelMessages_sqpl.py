# import configparser
import json
import re
from datetime import datetime
import time

# from MetaTrader5 import mt5
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel
import os
from telethon import TelegramClient
from dotenv import load_dotenv
from get_mt5_result.get_mt5_result_local import get_result


from group_select.group_select import tg_group_selector
from utils.inert_query import insert_msg_trade
from utils.select_query import get_order_id_by_msg_id
from utils.update_query import update_trade_message
load_dotenv()

import psycopg2
from psycopg2 import sql
#0=TEXC, 3=test
channel_index=0

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="forex",
    user="postgres",
    password="postgres"
)



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
# mt5_username = os.getenv('mt5_vantage_demo_2_username')
# password = os.getenv('mt5_vantage_demo_2_password')
mt5_username = os.getenv('mt5_vantage_demo_username')
password = os.getenv('mt5_vantage_demo_password')
mt5_username = os.getenv('mt5_pepperstone_username')
password = os.getenv('mt5_pepperstone_password')

deviation = 10
# def start_mt5(username, password, server, path):
def start_mt5():
    # Ensure that all variables are the correct type
    uname = int(mt5_username)  # Username must be an int
    print('uname: ', uname)
    pword = str(password)  # Password must be a string
    print('pword: ', pword)
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
    
def connect():
    mt5.initialize()

# Create a cursor object to interact with the database
cur = conn.cursor()

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

api_hash = str(api_hash)

phone = os.getenv('phone')
tg_username = os.getenv('tg_username')

# Create the client and connect
client = TelegramClient(tg_username, api_id, api_hash)

def send_request(request):
    result = mt5.order_send(request)
    print(f"Trade request: {request}")
    print(f"Trade result: {result}")
    return result

def modify_trade(ticket, symbol, sl, tp):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": int(ticket),
        "symbol": str(symbol),
        "sl": float(sl),
        "tp": float(tp)
    }
    result = send_request(request)
    print('result: ', result)

    return result

with TelegramClient("forex_modify", api_id, api_hash) as client:
    # Replace 'YOUR_CHANNEL_USERNAME' with the username of the channel you want to monitor
    channel_username = "https://t.me/TFXC_FREE"
    channel_username = "1994209728"
    # channel_username = "https://t.me/test_it_tg"
    
    #*channel_id_list = [TFXC PREMIUM, TFXC SIGNALS, TFXC CHAT, Test Private]
    # channel_id_list = [1220837618,1541002369,1675658808,1994209728]
    channel_id_list = [1220837618,199420972,1967274081,1327949777,1327949777,2095861920]

    # Get information about the channel
    # channel = client.get_entity(channel_username)
    # client.send_message(-1001994209728, 'Hello, group!')
    # while  True:
    #     client.send_message(-1001994209728, "message")
    #     time.sleep(1)

    # @client.on(events.NewMessage(chats=channel))
    # @client.on(events.NewMessage(PeerChannel(channel_id=channel_id_list[channel_index])))
    @client.on(events.NewMessage(chats=channel_id_list))
    async def handle_new_message(event):
        
        channel_id = event.message.peer_id.channel_id
        message = event.message.text
        if channel_id == 2095861920:
            result = get_result(message)
            await client.send_message(-1002095861920, result)

        # print('event: ', event)

        if event.message.reply_to_msg_id == None and channel_id != 2095861920:
            processed_msg = tg_group_selector(event)
            if processed_msg :
            
                ms_id = processed_msg["ms_id"]
                order_type = processed_msg["order_type"]
                mt5_order_type = processed_msg["mt5_order_type"]
                symbol= processed_msg["symbol"]
                lot = processed_msg["lot"]
                lot_size = processed_msg["lot_size"]
                order_price = processed_msg["order_price"]
                tp1 = processed_msg["tp1"]
                tp2 = processed_msg["tp2"]
                tp3 = processed_msg["tp3"]
                stop_loss = processed_msg["stop_loss"]
                comment=processed_msg["comment"]
                
                start_mt5()
                connect()
                
                if not mt5.symbol_select(symbol, True):
                    print(f"{symbol} is not available, can not trade.")
                    mt5.shutdown()
                    # quit()
                account_info=mt5.account_info()
                # # 检查账户可用保证金
                # if account_info.balance < trade_volume * account_info.leverage:
                #     print('账户可用保证金不足')
                #     mt5.shutdown()
                order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot,
                    "type": mt5_order_type,
                    "price": order_price,
                    "sl": stop_loss,
                    "tp": tp1,
                    "deviation": 10,
                    "magic": 234000,
                    "comment": comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(order)
                print('result: ', result)
                
                # Check the execution result
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("order_send failed, retcode =", result.retcode)
                    # Request the result as a dictionary and display it
                    result_dict = result._asdict()
                    for field in result_dict.keys():
                        print("   {}={}".format(field, result_dict[field]))
                    print("   last_error={}".format(mt5.last_error()))
                else:
                    print("Order executed successfully, ticket =", result.order)
                    # Build the INSERT statement
                    insert_msg_trade(conn, cur, ms_id, order_type, symbol, order_price, tp1, tp2, tp3, stop_loss, result.order)

                # Shut down connection to MetaTrader 5
                mt5.shutdown()
            
    @client.on(events.MessageEdited(chats=channel_id_list))
    async def handle_edited_message(event):
        channel_id = event.message.peer_id.channel_id
        if event.message.reply_to_msg_id == None and channel_id != 2095861920:
            processed_msg = tg_group_selector(event)
            if processed_msg :
            
                ms_id = processed_msg["ms_id"]
                symbol= processed_msg["symbol"]
                tp1 = processed_msg["tp1"]
                tp2 = processed_msg["tp2"]
                tp3 = processed_msg["tp3"]
                stop_loss = processed_msg["stop_loss"]
                    
                start_mt5()
                connect()    
                try:

                    result = get_order_id_by_msg_id(conn, cur, ms_id)  # Fetch the result from the query
                    print('result: ', result)

                    if result is not None:
                        order_id = result  # Extract the order_id from the result
                        
                        update_trade_message(conn, cur,tp1, tp2, tp3, stop_loss, ms_id)
                        modify_trade(order_id, symbol, stop_loss, tp1)
                        
                    else:
                        print("No order_id found for the given ms_id.")
                except Exception as e:
                    conn.rollback()
                    print("Error occurred:", e)

                mt5.shutdown()
    # Start the client
    client.run_until_disconnected()
    
# Close the cursor and connection
cur.close()
conn.close()
