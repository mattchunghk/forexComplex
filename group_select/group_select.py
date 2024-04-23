

from tg_gp_process.ASTRATEQ import ASTRATEQ_msg_processor
from tg_gp_process.ASTRATEQ_Rev import ASTRATEQ_msg_processor_rev
from tg_gp_process.FOREXERO import FOREXERO_msg_processor
from tg_gp_process.FXGoldenCircle import FXGoldenCircle_msg_processor
from tg_gp_process.GOLD_NINJA import GOLD_NINJA_msg_processor
from tg_gp_process.GOLD_NINJA_now import GOLD_NINJA_msg_processor_now
from tg_gp_process.PIPXPERT import PIPXPERT_msg_processor
from tg_gp_process.TFXC import TFXC_msg_processor
from tg_gp_process.TFXC_Rev import TFXC_msg_processor_rev


def tg_group_selector(event):
    message = event.message
    channel_id = message.peer_id.channel_id
    lot = 0.1
    
    #TFXC
    if  channel_id == 1220837618:
        return [TFXC_msg_processor(event,lot),TFXC_msg_processor_rev(event,lot)]
    
    #ASTRATEQ
    if  channel_id == 1967274081 :
        return [ASTRATEQ_msg_processor(event,lot), ASTRATEQ_msg_processor_rev(event,lot)]
        # return [ASTRATEQ_msg_processor(event,lot)]
        
    
    #FXGoldenCircle
    if  channel_id == 1327949777 :
        return [FXGoldenCircle_msg_processor(event,lot)]
    
    #PIPXPERT
    if  channel_id == 1821216397  :
        return [PIPXPERT_msg_processor(event,lot)]
    
    #FOREXERO
    if  channel_id == 1758700941:
        return [FOREXERO_msg_processor(event,lot)]
    
    #Gold Ninja
    if  channel_id == 1850974680 or channel_id == 1994209728:
        # return [GOLD_NINJA_msg_processor(event,lot)]
        return [GOLD_NINJA_msg_processor_now(event,lot)]