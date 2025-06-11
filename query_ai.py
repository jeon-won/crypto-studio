"""
비트코인 일봉 차트 분석을 OpenAI o4-mini 모델에 질의합니다.
"""
from datetime import datetime
from dotenv import load_dotenv
from module.messenger import send_discord_message
from openai import OpenAI
from prompt import QUERY_AI_RSI_DIVERGENCE
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
    # DB에서 비트코인 차트 데이터 가져오기
    db.init(POSTGRES_DB)
    rows_15m = db.select_close("btc_15m", limit=25)
    rows_1h = db.select_close("btc_1h", limit=25)
    rows_4h = db.select_close("btc_4h", limit=25)
    db.close()
    
    # 가져온 데이터를 Pandas.DataFrame으로 변환
    df_15m = pd.DataFrame(rows_15m, columns=["time", "close", "rsi"])
    df_15m['time'] = df_15m['time'].dt.tz_convert('Asia/Seoul')    ## 타임존 변환
    df_15m['time'] = df_15m['time'].dt.strftime('%Y-%m-%d %H:%M')  ## 시간 형식 변환
    df_15m['close'] = df_15m['close'].astype(int)
    
    df_1h = pd.DataFrame(rows_1h, columns=["time", "close", "rsi"])
    df_1h['time'] = df_1h['time'].dt.tz_convert('Asia/Seoul')
    df_1h['time'] = df_1h['time'].dt.strftime('%Y-%m-%d %H:%M')
    df_1h['close'] = df_1h['close'].astype(int)
    
    df_4h = pd.DataFrame(rows_4h, columns=["time", "close", "rsi"])
    df_4h['time'] = df_4h['time'].dt.tz_convert('Asia/Seoul')
    df_4h['time'] = df_4h['time'].dt.strftime('%Y-%m-%d %H:%M')
    df_4h['close'] = df_4h['close'].astype(int)

    current_time = datetime.now()
    hour   = current_time.hour
    minute = current_time.minute

    json_data = None
    # 4시간 봉 마감 직전인 경우 모든 캔들 데이터 포함
    if (hour % 4 == 0 and minute == 59):
        json_data = json.dumps({
        "15m": df_15m.to_dict(orient='records'),
        "1h":  df_1h.to_dict(orient='records'),
        "4h":  df_4h.to_dict(orient='records'),
    })
    # 1시간 봉 마감 직전인 경우 1시간, 15분 캔들 데이터 포함
    elif (minute == 59):
        json_data = json.dumps({
        "15m": df_15m.to_dict(orient='records'),
        "1h":  df_1h.to_dict(orient='records'),
    })
    # 15분 봉 마감 직전: 15분 캔들 데이터만 포함
    elif (minute % 15 == 14):
        json_data = json.dumps({
        "15m": df_15m.to_dict(orient='records'),
    })

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
              "text": QUERY_AI_RSI_DIVERGENCE
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "input_text",
              "text": json_data ## 데이터를 JSON으로 넘겨야 분석을 가장 잘 해준다는 미신이(?)
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
    time = result.get('time')
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
* 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
* 시간대: {time}
* 판단이유: {reason}"""
    # print(message)

    # 다이버전스 발생 판단 시 디스코드로 메시지 전송
    if decision != "none":
        send_discord_message(DISCORD_WEBHOOK_RSI_DIVERGENCE, message)