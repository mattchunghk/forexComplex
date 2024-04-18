import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import MetaTrader5 as mt5
import time
import os

# Set the path and login details for MT5
path = r"C:\Program Files\Vantage International MT5\terminal64.exe"
server = 'VantageInternational-Demo'
mt5_username = os.getenv('mt5_vantage_demo_username')
password = os.getenv('mt5_vantage_demo_password')

# Trading parameters
deviation = 10
symbol = 'BTCUSD'
yf_symbol = 'BTC-USD'
lot_size = 0.1
sl_pips = 50000
tp_pips = 50000
check_interval = 60 * 5 * 12 

# Initialize MT5 connection
def start_mt5():
    if not mt5.initialize(login=int(mt5_username), password=str(password), server=str(server), path=str(path)):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

# Ensure MT5 is started
start_mt5()

# Download historical data from Yahoo Finance
df = yf.download(yf_symbol, start="2023-01-01", end=datetime.today().strftime('%Y-%m-%d'))

# SuperTrend calculation function
def supertrend(df, atr_period=7, multiplier=3):
    high = df['High']
    low = df['Low']
    close = df['Close']
    atr_name = 'ATR_' + str(atr_period)
    st_name = 'SuperTrend_' + str(atr_period) + '_' + str(multiplier)
    
    df[atr_name] = df['High'].rolling(atr_period).std()
    df[st_name] = np.nan
    
    for i in range(atr_period, len(df)):
        if (close.iloc[i-1] <= df.at[df.index[i-1], st_name]) or pd.isna(df.at[df.index[i-1], st_name]):
            df.at[df.index[i], st_name] = (high.iloc[i] + low.iloc[i]) / 2 + multiplier * df.at[df.index[i], atr_name]
        else:
            df.at[df.index[i], st_name] = (high.iloc[i] + low.iloc[i]) / 2 - multiplier * df.at[df.index[i], atr_name]
    
    return df

# Apply SuperTrend calculation to the dataframe
df = supertrend(df)

# Define the trade function
def trade(action, symbol, lot, sl_points, tp_points, deviation=20):
    # Get the current market information
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Failed to find symbol: {symbol}")
        return False

    # Check if the symbol is available for trading
    if not symbol_info.visible:
        print(f"Symbol {symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select failed, exit")
            return False
    trade_type = None
    # Get the current ask/bid prices
    if action == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
        sl = round(price - sl_points * symbol_info.point, 2)  # Rounded Stop loss for a buy order
        tp = round(price + tp_points * symbol_info.point, 2)  # Rounded Take profit for a buy order
    elif action == 'sell':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
        sl = round(price + sl_points * symbol_info.point, 2)  # Rounded Stop loss for a sell order
        tp = round(price - tp_points * symbol_info.point, 2)  # Rounded Take profit for a sell order
    else:
        print("Trade action must be 'buy' or 'sell'")
        return False

    # Define the trade request dictionary with rounded SL and TP
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": round(price, 2),  # Round entry price to 1 decimal place if required
        "sl": float(sl),
        "tp": float(tp),
        "deviation": deviation,
        "magic": 234000,
        "comment": "Supertrend",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send the trade request
    result = mt5.order_send(request)
    print('result: ', result)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to send order :( Retcode={result.retcode}")
        return False
    else:
        print("Order sent successfully!")
        return True

# Main trading loop
try:
    while True:
        # Download the latest data
        df = yf.download(yf_symbol, period="1d", interval="1h")
        
        # Check if the DataFrame is not empty
        if df.empty:
            print("Failed to download data or data is empty.")
            continue
        
        # Apply SuperTrend calculation
        df = supertrend(df)
        
        # Add a 'signal' column based on a simple crossover strategy
        st_col = 'SuperTrend_' + str(7) + '_' + str(3)  # Adjust if you change the default parameters
        df['signal'] = np.where(df['Close'] > df[st_col], 'buy', 'sell')
        
        # Get the latest signal
        latest_signal = df['signal'].iloc[-1]
        print(f"The latest signal is: {latest_signal}")


        if latest_signal == 'buy':
            print("Received BUY signal.")
            trade('buy', symbol, lot=lot_size, sl_points=sl_pips, tp_points=tp_pips)
        elif latest_signal == 'sell':
            print("Received SELL signal.")
            trade('sell', symbol, lot=lot_size, sl_points=sl_pips, tp_points=tp_pips)
        
        # Wait before checking again
        time.sleep(check_interval)

except KeyboardInterrupt:
    print("\nScript interrupted by user.")

finally:
    # Shutdown MT5 connection
    mt5.shutdown()