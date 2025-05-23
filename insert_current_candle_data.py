"""
현재 비트코인 캔들 데이터를 PostgreSQL DB에 저장합니다.
저장하는 데이터는 시간, 시가, 고가, 저가, 종가, 거래량, RSI 값입니다.
"""
import ccxt
import os
import pandas as pd
import psycopg2
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# 상수 --------------------------------------------------

load_dotenv()
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_TABLE = os.getenv("POSTGRES_TABLE")

SYMBOL = "BTC/USDT"
TIMEFRAME = "15m"
TIMEZONE = timezone(timedelta(hours=9))  ## GMT+9: 한국 시간

# 함수 --------------------------------------------------

def calculate_rsi(ohlcv_list: list, period: int = 14):
    """
    ccxt의 fetch_ohlcv() 함수가 반환하는 list 객체를 받아 RSI 값을 계산합니다.
    
    Args: 
        - ohlcv_list: list (ccxt의 fetch_ohlcv() 함수의 반환값)
        - period: 이동평균 길이 (기본: 14)
    
    Returns: <class 'numpy.float64'>
    """
    # DataFrame으로 변환
    df = pd.DataFrame(ohlcv_list)
    ohlc = df[4].astype(float)  # 종가 데이터

    # RSI 계산
    delta = ohlc.diff()
    gains, declines = delta.copy(), delta.copy()
    gains[gains < 0] = 0
    declines[declines > 0] = 0

    _gain = gains.ewm(com=(period - 1), min_periods=period).mean()
    _loss = declines.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss
    rsi = 100 - (100 / (1 + RS))
    
    return round(float(rsi.iloc[-1]), 2)

# 코드 --------------------------------------------------

# Binance 선물 거래소 초기화
exchange = ccxt.binance({
  'options': {
    'defaultType': 'future' ## 선물 거래소로 설정
  }
})

# 캔들 데이터 가져오기
ohlcvs = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=200)
unixtime = ohlcvs[-1][0]
time_ts = datetime.fromtimestamp(unixtime / 1000, tz=TIMEZONE) ##UNIX 밀리초 → datetime with UTC timezone
price_open = ohlcvs[-1][1]
price_high = ohlcvs[-1][2]
price_low = ohlcvs[-1][3]
price_close = ohlcvs[-1][4]
volume = ohlcvs[-1][5]
rsi = calculate_rsi(ohlcvs)

# DB 연결 정보 설정
conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT
)
cur = conn.cursor()

# DB에 데이터 INSERT(충돌 시 UPDATE) 쿼리
insert_sql = f"""
INSERT INTO {POSTGRES_TABLE} (time, open, high, low, close, volume, rsi)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (time) DO UPDATE
  SET open = EXCLUDED.open,
      high = EXCLUDED.high,
      low = EXCLUDED.low,
      close = EXCLUDED.close,
      volume = EXCLUDED.volume,
      rsi = EXCLUDED.rsi;
"""

# 쿼리 실행 및 커밋
try:
    cur.execute(insert_sql, (
        time_ts,
        price_open,
        price_high,
        price_low,
        price_close,
        volume,
        rsi
    ))
    conn.commit()
    print("데이터 삽입/업데이트 성공")
except Exception as e:
    conn.rollback()
    print("에러 발생:", e)
finally:
    cur.close()
    conn.close()