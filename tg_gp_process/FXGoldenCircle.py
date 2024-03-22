# import configparser
import re


def FXGoldenCircle_msg_processor(event, lot=0.5):
    message = event.message
    comment = "FXGoldenCircle"
    # print('message: ', message)
    channel_id = message.peer_id.channel_id
    ms_id = str(channel_id) + str(message.id)
    # Process the new message
    if message.text and "Enter now" in message.text:
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
        symbol = message.text.split()[1].strip()
        lot_size = 100000
        trade_volume = lot * lot_size
        if "Take Profit 1" in org_message and "Take Profit 2" in org_message and "Take Profit 3" in org_message :
            order_price = converted_data[0]
            tp1 = converted_data[1]
            tp2 = converted_data[2]
            tp3 = converted_data[3]
            stop_loss = converted_data[4]
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
            "tp1" : tp1,
            "tp2" : tp2,
            "tp3" : tp3,
            "stop_loss" : stop_loss,
            "magic":3,
            "comment":comment,
            "action": "order",
            "reply_to_msg_id" : None
        }
        
        return result
        
        
