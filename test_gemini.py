import pathlib
import textwrap
import yfinance as yf
import google.generativeai as genai
import datetime
from IPython.display import display
from IPython.display import Markdown
import os
import time
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv('gemini_API')

def to_markdown(text):
  text = text.replace('•', '  *')
  print('text: ', text)
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Used to securely store your API key
# from google.colab import userdata

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.

genai.configure(api_key=GOOGLE_API_KEY)

# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)
    
# model = genai.GenerativeModel('gemini-pro')


# response = model.generate_content("What is ChatGPT?")

# # to_markdown(response.text)

# chat = model.start_chat(history=[])
# chat

# while True:
#     user_input = input("Question: ")
#     response = chat.send_message(user_input)
#     to_markdown(response.text)

# Get the stock price data from yfinance
ticker = 'TSLA'
# df = yf.download(ticker, period='1d')
start_date = datetime.date.today() - datetime.timedelta(days=90)
end_date = datetime.date.today() - datetime.timedelta(days=1)
df = yf.download(ticker, start=start_date, end=end_date,period='1d')


# Create a Generative AI model
model = genai.GenerativeModel('gemini-pro')
# model = genai.GenerativeModel('gemini-1.5-pro')
chat = model.start_chat(history= [])
# Generate a summary of the stock price data
# summary = model.generate_content(df.to_string())
# print('summary.text: ', summary.text)
response = chat.send_message(df.to_string())
# to_markdown(response.text)
time.sleep(3)
# response = chat.send_message("Basic on the data combine with supertrend, Should I buy " + ticker + "?" + "Give me 1 - 100 mark."+ "just give the mark, no need other context")
# response = chat.send_message("Basic on the data and MACD, Should I buy " + ticker + "?" + "Give me 1 - 100 mark."+ "just give the mark, no need other context")
response = chat.send_message("Basic on the data and combine with supertrend" + "Give me back the best ATR and mulitpler")
# response = chat.send_message("Basic on the data, Should I buy " + ticker + "?" + "Give me 1 - 100 mark."+ "just give the mark, no need other context")

to_markdown(response.text)
# Print the summary
# print(summary.text)

# Get the model's recommendation on whether to buy the stock
# recommendation = model.generate_content("Should I buy " + ticker + "?")

# Print the recommendation
# print(recommendation.text)
