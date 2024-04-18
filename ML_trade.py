# %%
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import MetaTrader5 as mt5
import time
import os

from dotenv import load_dotenv

import pandas as pd

load_dotenv()

# Set the path and login details for MT5
path = r"C:\Program Files\Vantage International MT5\terminal64.exe"
server = 'VantageInternational-Demo'
mt5_username = os.getenv('mt5_vantage_demo_username')
password = os.getenv('mt5_vantage_demo_password')

# server = 'VantageInternational-Live'
# mt5_username = os.getenv('mt5_vantage_live_username')
# password = os.getenv('mt5_vantage_live_password')

# Trading parameters
deviation = 20
# symbol = 'BTCUSD'
# yf_symbol = 'BTC-USD'
lot_size = 0.1

check_interval = 60 * 5 *12

# Initialize MT5 connection
def start_mt5():
    if not mt5.initialize(login=int(mt5_username), password=str(password), server=str(server), path=str(path)):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

# Ensure MT5 is started
# print(mt5.terminal_info())




# %%
# Define parameters
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1  # Hourly data
n_points = 10000  # Number of data points to download

while True:
    # Get historical data
    start_mt5()
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_points)



    # Convert to a pandas DataFrame
    data = pd.DataFrame(rates)

    # Convert time in seconds to the datetime format
    data['time'] = pd.to_datetime(data['time'], unit='s')

    # %%
    # Check for missing values
    if data.isnull().values.any():
        data = data.dropna()

    # Reset index to be the time column
    data.set_index('time', inplace=True)

    # %%
    # Calculate simple moving average as an example feature
    data['SMA'] = data['close'].rolling(window=50).mean()

    # Calculate the logarithmic return of the closing price
    data['log_return'] = np.log(data['close'] / data['close'].shift(1))

    # %%
    from sklearn.preprocessing import MinMaxScaler

    # Select features to use
    features = ['close', 'SMA', 'log_return']
    data = data[features].dropna()  # Drop rows with NaN values

    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Create X, y datasets
    sequence_length = 60
    X, y = [], []

    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i - sequence_length:i])
        y.append(scaled_data[i, 0])  # Assuming you are predicting the close price

    X = np.array(X)
    y = np.array(y)

    # %%
    # Split the data into training and testing sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # %%
    from sklearn.preprocessing import MinMaxScaler
    import numpy as np

    # Assume 'data' is your DataFrame and you're predicting the closing price
    dataset = data['close'].values
    dataset = dataset.reshape(-1, 1)

    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)

    # Create a dataset where X is the number of past time steps you want to use to predict the future
    # and y is the value at the future time step you want to predict
    sequence_length = 60  # number of past time steps to use to predict the future

    X = []
    y = []

    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)

    # Split into train and test datasets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Reshape data to fit the LSTM layer input requirements [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # %%

    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, LSTM, Dropout

    # Initialize the RNN
    model = Sequential()

    # Adding the first LSTM layer and some Dropout regularization
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))

    # Adding a second LSTM layer and some Dropout regularization
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))

    # Adding a third LSTM layer
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))

    # Adding the output layer
    model.add(Dense(units=1))

    # Compiling the RNN
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Fitting the RNN to the Training set
    model.fit(X_train, y_train, epochs=100, batch_size=32)

    model.save('forex_prediction_model.keras')

    # Import necessary libraries
    from sklearn.metrics import mean_squared_error, r2_score
    import matplotlib.pyplot as plt

    # Assuming 'model' is your trained model and 'X_test', 'y_test' is your test dataset
    predicted_prices = model.predict(X_test)

    # Calculate performance metrics
    mse = mean_squared_error(y_test, predicted_prices)
    r2 = r2_score(y_test, predicted_prices)

    # Visualize the predicted vs actual prices
    # plt.figure(figsize=(15, 5))
    # plt.plot(y_test, label='Actual Price')
    # plt.plot(predicted_prices, label='Predicted Price', alpha=0.7)
    # plt.title('Model Evaluation - Actual vs Predicted Prices')
    # plt.xlabel('Time')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.show()

    # Print out the performance metrics
    print(f'Mean Squared Error: {mse}')
    print(f'R^2 Score: {r2}')

    # Now, let's assume that 'predicted_prices' are the predictions for the next period
    # We need to define the trading strategy parameters:
    threshold_percentage = 0.01
    stop_loss_percentage = 0.02
    take_profit_percentage = 0.04

    # Assuming the last value of 'y_test' is the last known price
    current_market_price = y_test[-1]

    # Function to calculate SL and TP based on the entry price
    def calculate_sl_tp(entry_price, sl_pct, tp_pct, action):
        sl_price = entry_price * (1 - sl_pct) if action == 'BUY' else entry_price * (1 + sl_pct)
        tp_price = entry_price * (1 + tp_pct) if action == 'BUY' else entry_price * (1 - tp_pct)
        return sl_price, tp_price

    # Function to generate trading signal based on the prediction
    def generate_signal(predicted_price, current_price, threshold_perc, sl_perc, tp_perc):
        if predicted_price > current_price * (1 + threshold_perc):
            action = 'BUY'
            entry_price = current_price
            sl_price, tp_price = calculate_sl_tp(entry_price, sl_perc, tp_perc, action)
        elif predicted_price < current_price * (1 - threshold_perc):
            action = 'SELL'
            entry_price = current_price
            sl_price, tp_price = calculate_sl_tp(entry_price, sl_perc, tp_perc, action)
        else:
            action = 'HOLD'
            entry_price = sl_price = tp_price = None
        return action, entry_price, sl_price, tp_price

    # Now let's assume we're only looking at the latest prediction for the next trade signal
    latest_prediction = predicted_prices[-1]
    action, entry_price, sl_price, tp_price = generate_signal(
        latest_prediction,
        current_market_price,
        threshold_percentage,
        stop_loss_percentage,
        take_profit_percentage
    )


    def trade(action, symbol, lot, sl, tp,magic,comment, deviation=20):
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
            sl = round(sl, 2)  # Rounded Stop loss for a buy order
            tp = round(tp, 2)  # Rounded Take profit for a buy order
        elif action == 'sell':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            sl = round(sl, 2)  # Rounded Stop loss for a sell order
            tp = round(tp, 2)  # Rounded Take profit for a sell order
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
            "magic": magic,
            "comment": comment,
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
        
    if action == 'BUY':
        print("Received BUY signal.")
        trade('buy', symbol, lot=lot_size, sl=sl_price, tp=tp_price,magic=12,comment="Tensorflow")
    elif action == 'SELL':
        print("Received SELL signal.")
        trade('sell', symbol, lot=lot_size, sl=sl_price, tp=tp_price,magic=12,comment="Tensorflow")
    else:
        print("No trade signal generated. HOLD.")

    # Shut down MetaTrader 5 connection
    mt5.shutdown()
    time.sleep(check_interval)
