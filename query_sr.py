"""
비트코인 일봉 차트 분석을 OpenAI o4-mini 모델에 질의합니다.
"""
from dotenv import load_dotenv
# from module.messenger import send_discord_message
from openai import OpenAI
from prompt import QUERY_AI_SR
import module.db as db
import pandas as pd
import json, os

# 상수 --------------------------------------------------

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DISCORD_WEBHOOK_RSI_DIVERGENCE = os.getenv("DISCORD_WEBHOOK_RSI_DIVERGENCE")

# 코드 --------------------------------------------------

if __name__ == "__main__":
    db.init(POSTGRES_DB)
    rows = db.select_all("btc_15m", 100)
    db.close()

    # 가져온 데이터를 Pandas.DataFrame으로 변환
    df = pd.DataFrame(rows, columns=[desc[0] for desc in db.cursor.description])
    df['time'] = df['time'].dt.tz_convert('Asia/Seoul')    ## 타임존 변환
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M')  ## 시간 형식 변환
    df['open'] = df['open'].astype(int)  ## OHLCV 값을 정수로 변환(OpenAI 질의 시 토큰 수 절약하기 위함)
    df['high'] = df['high'].astype(int)
    df['low'] = df['low'].astype(int)
    df['close'] = df['close'].astype(int)
    df['volume'] = df['volume'].astype(int)
    df.drop('rsi', axis=1, inplace=True)

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(
    model="o4-mini",
    input=[
        {
        "role": "developer",
        "content": [
            {
            "type": "input_text",
            "text": QUERY_AI_SR
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
        "effort": "medium"  ## low, medium, high
    },
    )

    # 응답 파싱
    result = json.loads(response.output[1].content[0].text)
    print(f"decision: {result.get('decision')}")
    print(f"time: {result.get('time')}")
    print(f"reason: {result.get('reason')}")
    print(f"take-profit: {result.get('take-profit')}")
    print(f"stop-loss: {result.get('stop-loss')}")