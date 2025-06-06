"""
비트코인 일봉 차트 분석을 OpenAI o4-mini 모델에 질의합니다.
"""
from dotenv import load_dotenv
from module.messenger import send_discord_message
from openai import OpenAI
import module.db as db
import os
import pandas as pd
import json
from datetime import datetime

# 상수 --------------------------------------------------

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DISCORD_WEBHOOK_RSI_DIVERGENCE = os.getenv("DISCORD_WEBHOOK_RSI_DIVERGENCE")
PROMPT = os.getenv("PROMPT_QUERY_AI_15M")

# 전역변수 -----------------------------------------------

table = "btc_15m"

# 코드 --------------------------------------------------

if __name__ == "__main__":
    # 프롬프트 파싱
    prompt = PROMPT.replace('|n', '\n').replace('\\"', '"')
    
    # DB에서 비트코인 차트 데이터 가져오기
    db.init(POSTGRES_DB)
    rows = db.select(table, limit=50)
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
        "effort": "medium"  ## low, medium, high
      },
    )

    # 응답 파싱
    result = json.loads(response.output[1].content[0].text)
    decision = result.get('decision')
    reason = result.get('reason')
  
    # decision 값이 'bullish' 또는 'bearish'인 경우 한글로 변환
    if decision == 'bullish':
        decision = '📈 상승 다이버전스'
    elif decision == 'bearish':
        decision = '📉 하락 다이버전스'
    else:
        pass

    # 메신저로 보낼 메시지 작성
    message = f"""# {decision} 알림
* 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
* 판단이유: {reason}
"""
    print(message)

    # 다이버전스 발생 판단 시 디스코드로 메시지 전송
    if decision != "none":
        send_discord_message(DISCORD_WEBHOOK_RSI_DIVERGENCE, message)