from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# OpenAI에 질의하기
client = OpenAI(api_key=OPENAI_API_KEY)
response = client.responses.create(
  model="o4-mini",
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "You're a crypto trading expert. Tell me how to invest in bitcoin and translate it to Korean."
        }
      ]
    },
    # {
    #   "role": "user",
    #   "content": [
    #     {
    #       "type": "input_text",
    #       "text": df.to_json()
    #     }
    #   ]
    # },
    {
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Long"
        }
      ]
    },
  ],
  reasoning={
    "effort": "medium"
  },
)

print(response.output[1].content[0].text)