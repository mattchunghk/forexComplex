# import configparser
import re
import datetime


def ASTRATEQ_msg_processor(event, lot=0.5):
    print('event: ', event)
    message = event.message
    comment = "ASTRATEQ"
    print('message: ', message)
    channel_id = message.peer_id.channel_id
    ms_id = str(channel_id) + str(message.id)
    # Process the new message
    if message.text and "Reserved" in message.text:
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
            "tp1" : tp1,
            "tp2" : tp2,
            "tp3" : tp3,
            "stop_loss" : stop_loss,
            "comment":comment
        }
        
        return result
    
    
if  __name__ == '__main__':


    class PeerChannel:
        def __init__(self, channel_id):
            self.channel_id = channel_id

    class MessageEntityBold:
        def __init__(self, offset=0, length=0):
            self.offset = offset
            self.length = length

    class Message:
        def __init__(self, id=0, peer_id=None, date=datetime.datetime.now(datetime.timezone.utc), 
                    message='', out=False, mentioned=False, media_unread=False, silent=False, 
                    post=False, from_scheduled=False, legacy=False, edit_hide=False, pinned=False, 
                    noforwards=False, invert_media=False, from_id=None, saved_peer_id=None, 
                    fwd_from=None, via_bot_id=None, reply_to=None, media=None, reply_markup=None, 
                    entities=None, views=0, forwards=0, replies=None, edit_date=None, 
                    post_author=None, grouped_id=None, reactions=None, restriction_reason=None, 
                    ttl_period=None):
            if entities is None:
                entities = []
            if restriction_reason is None:
                restriction_reason = []
            self.id = id
            self.peer_id = peer_id  # Must be provided, no default value
            self.date = date
            self.message = message
            self.out = out
            self.mentioned = mentioned
            self.media_unread = media_unread
            self.silent = silent
            self.post = post
            self.from_scheduled = from_scheduled
            self.legacy = legacy
            self.edit_hide = edit_hide
            self.pinned = pinned
            self.noforwards = noforwards
            self.invert_media = invert_media
            self.from_id = from_id
            self.saved_peer_id = saved_peer_id
            self.fwd_from = fwd_from
            self.via_bot_id = via_bot_id
            self.reply_to = reply_to
            self.media = media
            self.reply_markup = reply_markup
            self.entities = entities
            self.views = views
            self.forwards = forwards
            self.replies = replies
            self.edit_date = edit_date
            self.post_author = post_author
            self.grouped_id = grouped_id
            self.reactions = reactions
            self.restriction_reason = restriction_reason
            self.ttl_period = ttl_period

    class UpdateNewChannelMessage:
        def __init__(self, message=None, pts=0, pts_count=0):
            if message is None:
                message = Message(peer_id=PeerChannel(channel_id=0))  # Default peer_id must be provided
            self.message = message
            self.pts = pts
            self.pts_count = pts_count

    class NewMessageEvent:
        def __init__(self, original_update=None, pattern_match=None, message=None):
            if original_update is None:
                original_update = UpdateNewChannelMessage()
            if message is None:
                message = Message(peer_id=PeerChannel(channel_id=0))  # Default peer_id must be provided
            self.original_update = original_update
            self.pattern_match = pattern_match
            self.message = message

    # Example usage:
    entities = [MessageEntityBold(offset=0, length=5), MessageEntityBold(offset=43, length=23)]
    msg = Message(
        peer_id=PeerChannel(channel_id=1994209728),  # Mandatory field
        message='👨\u200d💻 SELL XAUUSD 2084\n🔸SL 2092\n🔹TP 2060\nAll Copyright© Reserved.',
        entities=entities
    )
    update_new_channel_message = UpdateNewChannelMessage(message=msg)
    new_message_event = NewMessageEvent(original_update=update_new_channel_message, message=msg)

    ASTRATEQ_msg_processor(new_message_event)
    # TFXC_msg_processor(event)
    
        
        
