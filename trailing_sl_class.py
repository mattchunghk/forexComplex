import json
import re
from datetime import datetime
import time
import threading
import socket
import os
import threading
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from mt5linux import MetaTrader5

load_dotenv()

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

start_mt5()


# Initialize PostgreSQL Connection
database_url = os.getenv('DATABASE_URL', "postgres://postgres:postgres@localhost/forex")

# Global threading lock for database operations
db_lock = threading.Lock()


def count_decimal_places(number):
    # Convert the number to a string
    number_str = str(number)

    # Check if the number has a decimal point
    if '.' in number_str:
        # Find the index of the decimal point
        decimal_index = number_str.index('.')

        # Count the number of characters after the decimal point
        decimal_places = len(number_str) - decimal_index - 1

        return decimal_places
    else:
        # The number does not have a decimal point
        return 0
    

class Mt5_position:
    def __init__(self,ticket):
        self.ticket = ticket
        self.symbol = None
        self.order_type = None
        self.order_price = None
        self.tp1 = None
        self.tp2 = None
        self.tp3 = None
        self.sl_price = None
        self.price_data = []
        
        self.OPM = None
        self.TP1M = None
        self.TP2M = None
        
        self.count = None
        
        self.mt5_tp = None
        self.mt5_sl = None
        self.mt5_order_price = None
        
        self.trailing_sl_price = None
        self.stop_flag = False
    
    # Custom encoder function for JSON serialization of datetime objects
    def _json_serial(self,obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def get_trade_decimal_point(self):
        price = mt5.symbol_info_tick(self.symbol).ask
        self.count = count_decimal_places(price)


    def get_trade_data_as_json(self):
        with db_lock, psycopg2.connect(database_url) as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM msg_trade WHERE order_id = %s;", (self.ticket,))
            trade_data = cur.fetchone()
            
            if trade_data:
                # print('trade_data: ', trade_data)
                columns = ['id', 'ms_id', 'order_type', 'symbol', 'order_price', 'tp1', 'tp2', 'tp3', 'sl', 'order_id', 'created_at']
                trade_dict = dict(zip(columns, trade_data))
                trade_json = json.dumps(trade_dict, default=self._json_serial)
                trade_data = json.loads(trade_json)
                self.symbol = trade_data['symbol']
                
                # print('self.count: ', self.symbol, " ",self.count)
                self.order_type = trade_data['order_type']
                self.order_price = float(trade_data['order_price'])
                self.tp1 = float(trade_data['tp1'])
                self.tp2 = float(trade_data['tp2'])
                self.tp3 = float(trade_data['tp3'])
                self.sl_price = float(trade_data['sl'])
                self.price_data = [float(self.order_price), self.tp1, self.tp2, self.tp3, self.sl_price]
                self.get_active_positions_price()
                self.OPM = round((self.mt5_order_price+self.tp1)/2,self.count)
                self.TP1M = round((self.tp1+self.tp2)/2,self.count)
                self.TP2M = round((self.tp2+self.tp3)/2,self.count)
                
            cur.close()
            
    def send_request(self,request):
        result = mt5.order_send(request)
        print(f"Trade request: {request}")
        print(f"Trade result: {result}")
        return result
    
    def get_active_positions_price(self):
    # try:
        positions = mt5.positions_get()
        if positions is not None:
            for position in positions:
                if position.ticket == self.ticket:
                    self.mt5_tp = position.tp
                    self.mt5_sl = position.sl
                    self.mt5_order_price = position.price_open
    # except:
    #     # start_mt5()
    #     print("Wait for MT5 restart")
            
    def modify_trade(self,sl, tp):
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": int(self.ticket),
            "symbol": str(self.symbol),
            "sl": float(sl),
            "tp": float(tp)
        }
        result = self.send_request(request)
        print('result: ', result)
        # Update the database with new stop loss and take profit values
        self.get_active_positions_price()
        return result
            
                
        
    def init_trailing_sl(self):
        if self.order_type == "BUY":
            self.trailing_sl_price = round(float(mt5.symbol_info_tick(self.symbol).ask) - ((self.tp3-self.tp2)*0.2),5)
        elif self.order_type == "SELL":
            self.trailing_sl_price = round(float(mt5.symbol_info_tick(self.symbol).ask) + ((self.tp3-self.tp2)*0.2),5)
    
    def check_positions_still_active(self):
        # try:
            positions = mt5.positions_get()
            if positions is not None:
                active_positions = [position.ticket for position in positions]
                if self.ticket not in active_positions:
                    self.stop_flag = True
        # except:
        #     # start_mt5()
        #     print("Wait for MT5 restart")
        
        
    
    def trade_update(self):
        
        # try:
            # self.OPM = round((self.mt5_order_price+self.tp1)/2,5)
            # self.TP1M = round((self.tp1+self.tp2)/2,5)
            # self.TP2M = round((self.tp2+self.tp3)/2,5)
            price = mt5.symbol_info_tick(self.symbol).ask
            # bid_price = mt5.symbol_info_tick(self.symbol).bid
            if self.order_type == "BUY":
                if price >= self.tp1 and self.mt5_sl < self.mt5_order_price:
                    self.modify_trade(self.mt5_order_price, self.tp3)
                    print(f"{self.ticket}-{self.symbol} TP1 hit, adjusting SL to BE - {self.mt5_order_price}.")
                    
                elif price >= self.TP1M and self.mt5_sl < self.OPM:
                    
                    self.modify_trade(self.OPM, self.tp3)
                    print(f"{self.ticket}-{self.symbol} self.TP1M hit, adjusting SL to OPM - {self.OPM}.")
                    
                elif price >= self.tp2 and self.mt5_sl < self.tp1:
                    self.modify_trade(self.tp1, self.tp3)
                    print(f"{self.ticket}-{self.symbol} TP2 hit, adjusting SL to to TP1 - {self.tp1}.")
                    
                elif price >= self.TP2M and self.mt5_sl < self.tp2:
                    self.modify_trade(self.tp2, self.tp3)
                    print(f"{self.ticket}-{self.symbol} self.TP2M hit, adjusting SL to TP2 - {self.tp2}.")
                    
                elif price >= self.tp3 :
                    print(f"{self.ticket}-{self.symbol} Final TP hit, closing trade.")
                    self.stop_flag = True
                    
            elif self.order_type == "SELL":
                if price <= self.tp1 and self.mt5_sl > self.mt5_order_price:
                    self.modify_trade(self.mt5_order_price, self.tp3)
                    print(f"{self.ticket}-{self.symbol} TP1 hit, adjusting SL to BE - {self.mt5_order_price}.")
                    
                elif price <= self.TP1M and self.mt5_sl > self.OPM:

                    self.modify_trade(self.OPM, self.tp3)
                    print(f"{self.ticket}-{self.symbol} self.TP1M hit, adjusting SL to self.OPM - {self.OPM}.")
                    
                elif price <= self.tp2 and self.mt5_sl > self.tp1:
                    self.modify_trade(self.tp1, self.tp3)
                    print(f"{self.ticket}-{self.symbol} TP2 hit, adjusting SL to to TP1 - {self.tp1}.")
                    
                elif price <= self.TP2M and self.mt5_sl > self.tp2:
                    self.modify_trade(self.tp2, self.tp3)
                    print(f"{self.ticket}-{self.symbol} TP2M hit, adjusting SL to TP2 - {self.tp2}.")
                    
                elif price <= self.tp3 :
                    print(f"{self.ticket}-{self.symbol} Final TP hit, closing trade.")
                    self.stop_flag = True
                    
    def trailing_sl(self):
    # try:
        # OPM =  (self.mt5_order_price+self.tp1)/2
        # self.TP1M = (self.tp1+self.tp2)/2
        # self.TP2M = (self.tp2+self.tp3)/2
        price = mt5.symbol_info_tick(self.symbol).ask
        print('price: ', price)
        bid_price = mt5.symbol_info_tick(self.symbol).bid
        # print('self.trailing_sl_price: ', self.trailing_sl_price)
        if self.order_type == "BUY":
            if self.trailing_sl_price < price - ((self.tp3-self.tp2)*0.2):
                self.trailing_sl_price = price - ((self.tp3-self.tp2)*0.2)

                
            if price >= self.tp1 and self.mt5_sl < self.mt5_order_price:
                self.modify_trade(self.mt5_order_price, self.tp3)
                print(f"{self.ticket}-{self.symbol} TP1 hit, adjusting SL to BE - {self.mt5_order_price}.")
                
            elif price >= self.TP1M and self.mt5_sl < self.OPM:
                self.modify_trade(self.OPM, self.tp3)
                print(f"{self.ticket}-{self.symbol} TP1M hit, adjusting SL to OPM - {self.OPM}.")
                
            elif price >= self.tp2 and self.mt5_sl < self.trailing_sl_price:
                self.modify_trade(self.trailing_sl_price, self.tp3)
                print(f"{self.ticket}-{self.symbol} TP2 hit, start trailing SL - adjusting SL tp - {self.trailing_sl_price}")
                
            elif price >= self.tp3 :
                print(f"{self.ticket}-{self.symbol} Final TP hit, closing trade.")
                self.stop_flag = True
                
        elif self.order_type == "SELL":
            if self.trailing_sl_price > price + 1:
                self.trailing_sl_price = price + 1
            print('self.trailing_sl_price: ', price * 1.02)
                

                
                
            if price <= self.tp1 and self.mt5_sl > self.mt5_order_price:
                self.modify_trade(self.mt5_order_price, self.tp3)
                print(f"{self.ticket}-{self.symbol} TP1 hit, adjusting SL to BE - {self.mt5_order_price}.")
                
            elif price <= self.TP1M and self.mt5_sl > self.OPM:
                self.modify_trade(self.OPM, self.tp3)
                print(f"{self.ticket}-{self.symbol} TP1M hit, adjusting SL to OPM - {self.OPM}.")
                
            elif price <= self.tp2 and self.mt5_sl > self.trailing_sl_price:
                self.modify_trade(self.trailing_sl_price, self.tp3)
                print(f"{self.ticket}-{self.symbol} TP2 hit, start trailing SL - adjusting SL - {self.trailing_sl_price}")
                
            elif price <= self.tp3 :
                print(f"{self.ticket}-{self.symbol} Final TP hit, closing trade.")
                self.stop_flag = True
        # except:
        #     # start_mt5()
        #     print("Wait for MT5 restart")
        
        
        
                
    def start_thread(self):
        start_mt5()
        self.get_active_positions_price()
        self.get_trade_data_as_json()
        self.init_trailing_sl()
        self.get_trade_decimal_point()
        print(f"Thread for {self.ticket}-{self.symbol} start running.")
        
        while not self.stop_flag:
            try:
                self.check_positions_still_active()
                self.get_trade_data_as_json()
                self.trade_update()
                # self.trailing_sl()
            except:
                print("New position updating. Wait for MT5 restart")
                mt5.shutdown()
                start_mt5()
                self.get_active_positions_price()
            time.sleep(1)
            
            
        mt5.shutdown()
        print(f"Thread for {self.ticket}-{self.symbol} stop running. Position is close.")
    

        
                
def start_forward_test_thread(test_instance):
    test_instance.stop_flag = False
    thread = threading.Thread(target=test_instance.start_thread)
    thread.start()        
                
def stop_forward_test_thread(test_instance):
    test_instance.stop_flag = True                

def get_active_positions():
    # Request the positions
    positions = mt5.positions_get()
    if positions is None or len(positions) == 0:
        # Handle the case when positions_get() returns None or an empty tuple
        return []
    
    # Using list comprehension for better efficiency
    active_positions = [position.ticket for position in positions]
    
    return active_positions



if __name__ == '__main__':
    try:

        order_id = get_active_positions()[0]        
        print('order_id: ', order_id)
        pos = Mt5_position(order_id)
        pos.get_trade_data_as_json()
        pos.get_active_positions()
        print(pos.symbol)
        print(pos.mt5_tp)
    finally:
        # Disconnect from MetaTrader 5
        mt5.shutdown()
        

