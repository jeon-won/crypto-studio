"""
비트코인 일봉 차트 분석을 OpenAI o4-mini 모델에 질의합니다.
"""
from datetime import datetime
from dotenv import load_dotenv
from module.messenger import send_discord_message, send_telegram_message
from openai import OpenAI
from prompt import QUERY_AI_RSI_DIVERGENCE
import module.aux_indicator as aux
import module.db as db
import pandas as pd
import asyncio, ccxt, json, os

# 상수 --------------------------------------------------

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DISCORD_WEBHOOK_RSI_DIVERGENCE = os.getenv("DISCORD_WEBHOOK_RSI_DIVERGENCE")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

# 함수 --------------------------------------------------

def get_cr_dataframe(timeframe: str, limit: int = 25):
    """
    Pandas.DataFrame 형태의 비트코인 데이터(종가, RSI)를 반환합니다.
    
    Args: 
        - timeframe: str (예: 15m은 15분봉, 1h는 1시간 봉)
        - limit: 가져올 캔들 데이터 개수 (기본: 25)
    
    Returns: DataFrame
    """
    # DB에서 비트코인 차트 데이터 가져오기
    db.init(POSTGRES_DB)
    rows = db.select_close(f'"btc_{timeframe}"', limit)
    db.close()

    # 비트코인 차트 데이터를 Pandas.DataFrame 데이터로 변환
    df = pd.DataFrame(rows, columns=["time", "close", "rsi"])
    df['time'] = df['time'].dt.tz_convert('Asia/Seoul')    ## 타임존 변환
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M')  ## 시간 형식 변환
    df['close'] = df['close'].astype(int)

    return df

# 코드 --------------------------------------------------

if __name__ == "__main__":
    # 변수
    current_time = datetime.now()  ## 현재 시간
    hour   = current_time.hour     ## 현재 시
    minute = current_time.minute   ## 현재 분
    second = current_time.second   ## 현재 초
    minute = 59
    json_data = ""                 ## OpenAI에 질의할 비트코인 데이터

    # 타임프레임 결정
    timeframes = []
    if minute % 15 == 14:  ## 15분 봉 마감 직전(매 14, 29, 44, 59분)
        timeframes.append("15m")
    if minute % 30 == 29:  ## 30분 봉 마감 직전(매 29, 59분)
        timeframes.append("30m")
    if minute == 59:       ## 1시간 봉 마감 직전(매 59분)
        timeframes.append("1h")
        if hour % 2 == 0:  ## 2시간 봉 마감 직전(매 2배수 시 59분)
            timeframes.append("2h")
        if hour % 4 == 0:  ## 4시간 봉 마감 직전(매 4배수 시 59분)
            timeframes.append("4h")
        if hour == 8:      ## 1일봉 마감 직전 (매 8시 59분)
            timeframes.append("1d")

    # 포함할 타임프레임이 있으면 한꺼번에 JSON을 생성하되, 최신 RSI 값에 40 이하 60 이상일 떄만 키를 생성함
    if timeframes:
        json_data = json.dumps({
            tf: data
            for tf in timeframes
            if (data := get_cr_dataframe(tf, 25).to_dict(orient="records"))
                and (data[0]["rsi"] <= 40 or data[0]["rsi"] >= 60)
        })

    # 타임프레임별 데이터가 있다면 OpenAI에 질의하기
    if json_data != "" and json_data != "{}":
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
        model="gpt-5-nano",
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
        print(message)

        # 다이버전스 발생 판단 시 디스코드로 메시지 전송
        if decision != "none":
            send_discord_message(DISCORD_WEBHOOK_RSI_DIVERGENCE, message)
            asyncio.run(send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_ID, message))