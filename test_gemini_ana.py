import yfinance as yf
import requests
import json
import os
import time

import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import textwrap
# from openai import OpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()



# # import MetaTrader5 as mt5
# client = OpenAI(
#     # This is the default and can be omitted
#     api_key=os.getenv('OPENAI_API_KEY'),
# )

# Define the symbol and the lot size
def gemini_singals():
    GOOGLE_API_KEY = os.getenv('gemini_API')
    genai.configure(api_key=GOOGLE_API_KEY)
    
    def to_markdown(text):
        text = text.replace('•', '  *')
        print('text: ', text)
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
    
    symbol = "BTC-USD"

    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    # Format the dates in a way that yfinance understands
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Download the data
    df = yf.download(tickers=symbol, start=start_date_str, end=end_date_str, interval='1h')

    # 2. Use OpenAI API to analyze the dataframe and provide the signal to trade
    # Prepare the prompt for the OpenAI API
    prompt = f"I want to make a trade every hours. Analyze with supertrend indicator for the following stocks/forex/crypto data for {symbol} and no need any comment and just return recommend a trade action for next hour(buy, sell, hold): {json.dumps(df.to_json())}"
    model = genai.GenerativeModel('gemini-pro')
    # model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        # Only one candidate for now.
     
        temperature=0)
    )
    # response = chat.send_message("Basic on the data, Should I buy " + ticker + "?" + "Give me 1 - 100 mark."+ "just give the mark, no need other context")

    to_markdown(response.text)
    print('response.text: ', response.text)
 
gemini_singals()

# print('company_impact: ', company_impact)


# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": f"{prompt}"}],
#     temperature=0,
#     response_format={"type": "json"},
# )
# print('response: ', response)
# print('response: ', response.content)


# Step 3: Trade on MT5
# mt5.initialize()

# Get the current price
# symbol_info = mt5.symbol_info(symbol)
# current_price = symbol_info.ask

# # Set the stop loss and take profit levels (50 pips)
# pip_size = symbol_info.trade_tick_size
# stop_loss = current_price - 50 * pip_size
# take_profit = current_price + 50 * pip_size

# # Determine the trade type based on the signal
# trade_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL

# # Prepare the trade request
# request = {
#     "action": mt5.TRADE_ACTION_DEAL,
#     "symbol": symbol,
#     "volume": 0.1,  # Adjust the volume as needed
#     "type": trade_type,
#     "price": current_price,
#     "sl": stop_loss,
#     "tp": take_profit,
#     "magic": 123456,
#     "comment": "Gemini AI Trade",
#     "type_time": mt5.ORDER_TIME_GTC,
#     "type_filling": mt5.ORDER_FILLING_FOK,
# }

# # Send the trade request
# result = mt5.order_send(request)

# # Check the trade result
# if result.retcode == mt5.TRADE_RETCODE_DONE:
#     print("Trade executed successfully!")
# else:
#     print(f"Trade failed with error: {result.comment}")

# mt5.shutdown()