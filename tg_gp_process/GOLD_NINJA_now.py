# import configparser
import re
import MetaTrader5 as mt5

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

def GOLD_NINJA_msg_processor_now(event, lot=0.5):
    message = event.message
    magic = 12
    comment = "Gold_ninja_now"
    # print('message: ', message)
    channel_id = message.peer_id.channel_id
    ms_id = str(channel_id) + str(message.id)
    lot_size = 100000
    result = None
    
    if message.text and "BUY GOLD NOW" in message.text.upper() :
        result={
            "ms_id" : ms_id,
            "order_type" : "Buy",
            "mt5_order_type" : 0,
            "symbol": "XAUUSD",
            "lot" : lot,
            "lot_size" : lot_size,
            "order_price" : float(0),
            "tp1" : float(0),
            "tp2" : float(0),
            "tp3" : float(0),
            "stop_loss" : float(0),
            "magic":magic,
            "comment":comment,
            "action": "just",
            "reply_to_msg_id" : None,
            "acc":"demo"
        }
    if message.text and "SELL GOLD NOW" in message.text.upper() :
        result={
            "ms_id" : ms_id,
            "order_type" : "Sell",
            "mt5_order_type" : 1,
            "symbol": "XAUUSD",
            "lot" : lot,
            "lot_size" : lot_size,
            "order_price" : float(0),
            "tp1" : float(0),
            "tp2" : float(0),
            "tp3" : float(0),
            "stop_loss" : float(0),
            "magic":magic,
            "comment":comment,
            "action": "just",
            "reply_to_msg_id" : None,
            "acc":"demo"
        }
    # Process the new message
    if message.text and "TP1" in message.text and "SL" in message.text and "TP2" in message.text and "TP3" in message.text:
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


        order_type = message.text.split()[1].strip()
        mt5_order_type = 0 if "BUY" in order_type  else 1
        
        symbol = message.text.split()[0].strip()
        if  "GOLD" in symbol:
            symbol = "XAUUSD"
        elif "/"in symbol:
            symbol = message.text.split()[0].replace("🔔", "").strip().replace("/", "").replace("*", "")
        lot_size = 100000
        trade_volume = lot * lot_size
        if "TP1" in org_message and "TP2" in org_message and "TP3" in org_message :
            order_price = converted_data[0]
            tp1 = converted_data[3]
            tp2 = converted_data[4]
            tp3 = converted_data[5]
            stop_loss = converted_data[2]
        else:
            order_price = converted_data[0]
            tp1 = converted_data[3]
            tp2 = 0
            tp3 = 0
            stop_loss = converted_data[1]
            
        print('symbol: ', symbol)
        print('order_type: ', order_type)
        print('order_price: ', order_price)
        print('tp1: ', tp1)
        print('tp2: ', tp2)
        print('tp3: ', tp3)
        print('stop_loss: ', stop_loss)
        
        result={
            "ms_id" : ms_id,
            "order_type" : order_type,
            "mt5_order_type" : mt5_order_type,
            "symbol": symbol,
            "lot" : lot,
            "lot_size" : lot_size,
            "order_price" : float(order_price),
            "tp1" : float(tp1),
            "tp2" : float(tp2),
            "tp3" : float(tp3),
            "stop_loss" : float(stop_loss),
            "magic":magic,
            "comment":comment,
            "action": "mod",
            "reply_to_msg_id" : None,
            "acc":"demo"
        }
        
    return result
        
        
