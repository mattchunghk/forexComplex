# import configparser
import re
import datetime


def ASTRATEQ_msg_processor_rev(event, lot=0.5):
    # print('event: ', event)
    message = event.message
    comment = "ASTRATEQ-Rev"
    # print('message: ', message)
    channel_id = message.peer_id.channel_id
    ms_id = str(channel_id) + str(message.id)
    # Process the new message
    if message.text and "Reserved" in message.text:
        # print(message)
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
        #!Edit
        mt5_order_type = 1 if "BUY" in order_type  else 0
        symbol = message.text.split()[2].strip()
        lot_size = 100000
        trade_volume = lot * lot_size
        order_price = converted_data[0]
        tp1 = converted_data[2]
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
            "order_price" : order_price,
            "tp1" : stop_loss, #!Edit
            "tp2" : tp2,
            "tp3" : tp3,
            "stop_loss" : tp1, #!Edit
            "magic":5,
            "comment":comment,
            "action": "order",
            "reply_to_msg_id" : None
        }
        
        return result
    
    
