# import configparser
import json
import re
from datetime import datetime

# from MetaTrader5 import mt5
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel
import os
from telethon import TelegramClient
from dotenv import load_dotenv
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
# path = "/home/ubuntu/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
path = "/Users/mattchung/.wine/drive_c/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
# server = 'Pepperstone-Demo'
server = 'VantageInternational-Demo'
# mt5_username = os.getenv('mt5_vantage_demo_2_username')
# password = os.getenv('mt5_vantage_demo_2_password')
mt5_username = os.getenv('mt5_vantage_demo_username')
password = os.getenv('mt5_vantage_demo_password')

deviation = 10
# start_date = datetim
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

# Create a cursor object to interact with the database
cur = conn.cursor()
# # Reading Configs
# config = configparser.ConfigParser()
# config.read("tg_config.ini")

# api_id = config["Telegram"]['api_id']
# api_hash = config['Telegram']['api_hash']
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

api_hash = str(api_hash)

# phone = config['Telegram']['phone']
# username = config['Telegram']['username']
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
    channel_id_list = [1220837618,1994209728]

    # Get information about the channel
    # channel = client.get_entity(channel_username)

    # @client.on(events.NewMessage(chats=channel))
    # @client.on(events.NewMessage(PeerChannel(channel_id=channel_id_list[channel_index])))
    @client.on(events.NewMessage(chats=channel_id_list))
    async def handle_new_message(event):
        message = event.message
        print('message: ', message)
        print('edited_msg: ', message.id)
        channel_id = message.peer_id.channel_id
        ms_id = str(channel_id) + str(message.id)
        if  channel_id == 1994209728 or channel_id == 1220837618:
        # Process the new message
            if message.text and "SIGNAL ALERT" in message.text:
                print(message)
                channel_id = message.peer_id.channel_id
                org_message = message.text
                message.text = re.sub(r'(?<!\d)(\.\d+)', r'0\1', message.text)
                price_data = re.findall(r'\d+\.\d+', message.text)
                converted_data = [float(item) if "." in item else int(item) for item in price_data]
                if len(price_data) == 0:
                    price_data = re.findall(r'\b\d+\b', org_message)
                    print('price_data: ', price_data)
                    converted_data = [float(num) for num in price_data]
                
                print('converted_data: ', converted_data)
    

                order_type = message.text.split()[2].strip()
                mt5_order_type = 0 if "BUY" in order_type  else 1
                symbol = message.text.split()[3].strip()
                lot = 0.5
                lot_size = 100000
                trade_volume = lot * lot_size
                if "TP1" in org_message and "TP2" in org_message and "TP3" in org_message :
                    order_price = converted_data[0]
                    tp1 = converted_data[1]
                    tp2 = converted_data[2]
                    tp3 = converted_data[3]
                    stop_loss = converted_data[4]
                    print('symbol: ', symbol)
                    print('order_type: ', order_type)
                    print('order_price: ', order_price)
                    print('tp1: ', tp1)
                    print('tp2: ', tp2)
                    print('tp3: ', tp3)
                    print('stop_loss: ', stop_loss)
                else:
                    order_price = converted_data[0]
                    tp1 = converted_data[1]
                    tp2 = 0
                    tp3 = 0
                    stop_loss = converted_data[2]
                    print('symbol: ', symbol)
                    print('order_type: ', order_type)
                    print('order_price: ', order_price)
                    print('tp1: ', tp1)
                    print('stop_loss: ', stop_loss)
                
            

            
            start_mt5()
            connect()
            
            if not mt5.symbol_select(symbol, True):
                print(f"{symbol} is not available, can not trade.")
                mt5.shutdown()
                # quit()
            account_info=mt5.account_info()
            print('account_balance: ', account_info.balance)
            print('account_leverage: ', account_info.leverage)
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
                "comment": "forex testing",
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
                insert_query = sql.SQL("""INSERT INTO msg_trade (ms_id, order_type, symbol, order_price, tp1, tp2, tp3, sl, order_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)

                # Execute the INSERT statement
                try:
                    
                    cur.execute(insert_query, (ms_id, order_type, symbol, order_price, tp1, tp2, tp3, stop_loss, result.order))
                    conn.commit()
                    print("Data inserted successfully!")
                except Exception as e:
                    conn.rollback()
                    print("Error occurred:", e)



            # Shut down connection to MetaTrader 5
            mt5.shutdown()
            
    @client.on(events.MessageEdited(chats=channel_id_list))
    async def handle_edited_message(event):
        message = event.message
        print('message: ', message)
        print('edited_msg: ', message.id)
        channel_id = message.peer_id.channel_id
        ms_id = str(channel_id) + str(message.id)
        if  channel_id == 1994209728 or channel_id == 1220837618:
         # Process the new message
            if message.text and "SIGNAL ALERT" in message.text:
                print(message)
                channel_id = message.peer_id.channel_id
                
                org_message = message.text
                message.text = re.sub(r'(?<!\d)(\.\d+)', r'0\1', message.text)
                price_data = re.findall(r'\d+\.\d+', message.text)
                converted_data = [float(item) if "." in item else int(item) for item in price_data]
                if len(price_data) == 0:
                    price_data = re.findall(r'\b\d+\b', org_message)
                    print('price_data: ', price_data)
                    converted_data = [float(num) for num in price_data]
                
                print('converted_data: ', converted_data)
    

                order_type = message.text.split()[2].strip()
                mt5_order_type = mt5.ORDER_TYPE_BUY if "BUY" in order_type  else mt5.ORDER_TYPE_SELL
                symbol = message.text.split()[3].strip()
                lot = 0.5
                lot_size = 100000
                trade_volume = lot * lot_size
                if "TP1" in org_message and "TP2" in org_message and "TP3" in org_message :
                    order_price = converted_data[0]
                    tp1 = converted_data[1]
                    tp2 = converted_data[2]
                    tp3 = converted_data[3]
                    stop_loss = converted_data[4]
                    print('symbol: ', symbol)
                    print('order_type: ', order_type)
                    print('order_price: ', order_price)
                    print('tp1: ', tp1)
                    print('tp2: ', tp2)
                    print('tp3: ', tp3)
                    print('stop_loss: ', stop_loss)
                else:
                    order_price = converted_data[0]
                    tp1 = converted_data[1]
                    tp2 = 0
                    tp3 = 0
                    stop_loss = converted_data[2]
                    print('symbol: ', symbol)
                    print('order_type: ', order_type)
                    print('order_price: ', order_price)
                    print('tp1: ', tp1)
                    print('stop_loss: ', stop_loss)
                
            start_mt5()
            connect()    
            try:
                select_query = sql.SQL("""SELECT order_id
                                        FROM msg_trade
                                        WHERE ms_id = %s
                                    """)

                cur.execute(select_query, (ms_id,))
                conn.commit()

                result = cur.fetchone()  # Fetch the result from the query
                print('result: ', result)

                if result is not None:
                    order_id = result[0]  # Extract the order_id from the result
                    update_query = sql.SQL("""UPDATE msg_trade 
                                SET tp1 = %s, tp2 = %s, tp3 = %s, sl = %s WHERE ms_id = %s""")
                
                    cur.execute(update_query, (tp1, tp2, tp3, stop_loss, ms_id))
                    conn.commit()
                    modify_trade(order_id, symbol, stop_loss, tp1)
                else:
                    print("No order_id found for the given ms_id.")
            except Exception as e:
                conn.rollback()
                print("Error occurred:", e)
                


    # Start the client
    mt5.shutdown()
    client.run_until_disconnected()
    
# Close the cursor and connection
cur.close()
conn.close()
