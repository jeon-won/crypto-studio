from openai import OpenAI
from dotenv import load_dotenv
from module.aux_indicator import calculate_rsi
import os
import psycopg2
import pandas as pd
from pprint import pprint
from module.messenger import send_discord_message

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

prompt = """You're a crypto trading expert. Please analyze the attached JSON data and answer the request below.

- Can I buy bitcoin position(Long or Short) now?
- Is there currently RSI bearish or bullish divergence?

Please translate the answer into Korean.
"""

# prompt = "You're a crypto trading expert. Please analyze the attached JSON data and let me know when the rsi divergence occurred. Translate the answer into Korean."
conn_info = {
    'dbname': POSTGRES_DB,
    'user': POSTGRES_USER,
    'password': POSTGRES_PASSWORD,
    'host': POSTGRES_HOST,
    'port': POSTGRES_PORT
}
postgres_table = "btc_1d"
rows_limit = 200  ## 가져올 데이터의 개수

# 코드 --------------------------------------------------

if __name__ == "__main__":
    try:
        # PostgreSQL 접속 및 데이터 가져오기
        conn = psycopg2.connect(**conn_info)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {postgres_table} ORDER BY time DESC LIMIT %s", (rows_limit,))
        rows = cur.fetchall()

        # 가져온 데이터를 Pandas.DataFrame으로 변환 후 JSON으로 변환
        df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
        df['time'] = df['time'].dt.tz_convert('Asia/Seoul')     ## 타임존 변환
        df['time'] = df['time'].dt.strftime('%Y-%m-%d')   ## 또는 %Y-%m-%d %H:%M
        df['open'] = df['open'].astype(int)                     ## OHLCV 값을 정수로 변환(OpenAI 질의 시 토큰 수 절약하기 위함)
        df['high'] = df['high'].astype(int)
        df['low'] = df['low'].astype(int)
        df['close'] = df['close'].astype(int)
        df['volume'] = df['volume'].astype(int)

        print(df.to_json(orient='records', date_format='iso'))

    except psycopg2.DatabaseError as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        cur.close()
        conn.close()

    # # OpenAI에 질의하기
    # client = OpenAI(api_key=OPENAI_API_KEY)
    # response = client.responses.create(
    #   model="o4-mini",
    #   input=[
    #     {
    #       "role": "developer",
    #       "content": [
    #         {
    #           "type": "input_text",
    #           "text": prompt
    #         }
    #       ]
    #     },
    #     {
    #       "role": "user",
    #       "content": [
    #         {
    #           "type": "input_text",
    #           "text": df.to_json(orient='records', date_format='iso')
    #         }
    #       ]
    #     },
    #     # {
    #     #   "role": "assistant",
    #     #   "content": [
    #     #     {
    #     #       "type": "output_text",
    #     #       "text": "Long"
    #     #     }
    #     #   ]
    #     # },
    #   ],
    #   reasoning={
    #     "effort": "medium"
    #   },
    # )

    # print(response.output[1].content[0].text)
    # send_discord_message(DISCORD_WEBHOOK_1D_ANALYSIS, response.output[1].content[0].text)