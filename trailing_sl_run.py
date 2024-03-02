# %%
# Conncet MT5, conncet psql
import json
import re
from datetime import datetime
import time
import os
import trailing_sl_class as pos

    
# from mt5linux import MetaTrader5

# mt5 = MetaTrader5(
#     host = 'localhost',
#     # host = os.getenv('mt5_host'),
#     port = 18812      
# )  

running_instance = []
running_tickets = []


# %%

while True:
    active_positions = pos.get_active_positions()

    for active_position in active_positions:
        if active_position not in running_tickets:
            position = pos.Mt5_position(active_position)
            pos.start_forward_test_thread(position)
            running_tickets.append(active_position)
    
    
    time.sleep(1)





