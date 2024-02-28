

from tg_gp_process.TFXC import TFXC_msg_processor


def tg_group_selector(event):
    message = event.message
    channel_id = message.peer_id.channel_id
    
    if  channel_id == 1994209728 or channel_id == 1220837618:
        return TFXC_msg_processor(event)