"""
비트코인 일봉 차트 분석을 OpenAI o4-mini 모델에 질의합니다.
"""
from dotenv import load_dotenv
from module.messenger import send_discord_message
from openai import OpenAI
import module.db as db
import os
import pandas as pd

# 상수 --------------------------------------------------

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DISCORD_WEBHOOK_1D_ANALYSIS = os.getenv("DISCORD_WEBHOOK_1D_ANALYSIS")

# 전역변수 -----------------------------------------------

table = "btc_1d"
prompt = """You are a Bitcoin trading expert. Attached JSON data is Bitcoin daily chart data. Please analyze this as below.
1. Analysis of chart patterns (for example, head-and-shoulder, double-top, wedge, triangle, etc.)
2. RSI analysis (at the most recent time, whether RSI bullish or bearish divergence has occurred, etc.)
3. Main support, resistance point analysis(Whether the close price at the most recent time is in the support resistance point, etc.)
4. Investment prospects and strategy proposals (such as investment strategy proposals based on current market conditions)
Please translate the answer into Korean.
"""

if __name__ == "__main__":
    # DB에서 비트코인 차트 데이터 가져오기
    db.init(POSTGRES_DB)
    rows = db.select(table, limit=100)
    
    # 가져온 데이터를 Pandas.DataFrame으로 변환
    df = pd.DataFrame(rows, columns=[desc[0] for desc in db.cursor.description])
    df['time'] = df['time'].dt.tz_convert('Asia/Seoul')  ## 타임존 변환
    df['time'] = df['time'].dt.strftime('%Y-%m-%d')      ## 또는 %Y-%m-%d %H:%M
    df['open'] = df['open'].astype(int)                  ## OHLCV 값을 정수로 변환(OpenAI 질의 시 토큰 수 절약하기 위함)
    df['high'] = df['high'].astype(int)
    df['low'] = df['low'].astype(int)
    df['close'] = df['close'].astype(int)
    df['volume'] = df['volume'].astype(int)

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
              "text": prompt
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "input_text",
              "text": df.to_json(orient='records', date_format='iso') ## 데이터를 JSON으로 넘겨야 분석을 가장 잘 해준다는 미신이(?)
            }
          ]
        },
        # {
        #   "role": "assistant",
        #   "content": [
        #     {
        #       "type": "output_text",
        #       "text": "Long"
        #     }
        #   ]
        # },
      ],
      reasoning={
        "effort": "medium"
      },
    )

    send_discord_message(DISCORD_WEBHOOK_1D_ANALYSIS, response.output[1].content[0].text)
    # print(response.output[1].content[0].text)