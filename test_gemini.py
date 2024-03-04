import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
import os
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

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
    
model = genai.GenerativeModel('gemini-pro')


response = model.generate_content("What is ChatGPT?")

# to_markdown(response.text)

chat = model.start_chat(history=[])
chat

while True:
    user_input = input("Question: ")
    response = chat.send_message(user_input)
    to_markdown(response.text)



    # chat.history
