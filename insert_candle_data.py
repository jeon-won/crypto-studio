"""
현재와 직전 시점의 비트코인 캔들 데이터를 PostgreSQL DB에 저장합니다.
저장하는 데이터는 시간, 시가, 고가, 저가, 종가, 거래량, RSI 값입니다.
"""
import ccxt
import os
import psycopg2
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from module.aux_indicator import calculate_rsi

# 상수 --------------------------------------------------

load_dotenv()
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# 전역변수 -----------------------------------------------

symbol = "BTC/USDT"
timeframe = "15m"
time_zone = timezone(timedelta(hours=9))  ## GMT+9: 한국 시간
postgres_table = "btc_15m"

if __name__ == "__main__":
    # Binance 선물 거래소 초기화
    exchange = ccxt.binance({
    'options': {
        'defaultType': 'future' ## 선물 거래하므로 넣어봤음
    }
    })

    # 캔들 데이터 가져오기
    ohlcvs = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=201)
    ohlcvs_current = ohlcvs[1:] ## 현재 시점의 캔들 RSI 계산을 위한 배열
    ohlcvs_prev = ohlcvs[:-1]   ## 직전 시점의 캔들 RSI 계산을 위한 배열

    # 현재 캔들 데이터 가공
    ohlcv_current = [
        datetime.fromtimestamp(ohlcvs_current[-1][0] / 1000, tz=time_zone),  ## 시간(GMT+9 기준)
        ohlcvs_current[-1][1],         ## 시가
        ohlcvs_current[-1][2],         ## 고가
        ohlcvs_current[-1][3],         ## 저가
        ohlcvs_current[-1][4],         ## 종가
        ohlcvs_current[-1][5],         ## 거래량
        calculate_rsi(ohlcvs_current)  ## RSI 값
    ]

    # 직전 캔들 데이터 가공
    ohlcv_prev = [
        datetime.fromtimestamp(ohlcvs_prev[-1][0] / 1000, tz=time_zone),  ## 시간(GMT+9 기준)
        ohlcvs_prev[-1][1],         ## 시가
        ohlcvs_prev[-1][2],         ## 고가
        ohlcvs_prev[-1][3],         ## 저가
        ohlcvs_prev[-1][4],         ## 종가
        ohlcvs_prev[-1][5],         ## 거래량
        calculate_rsi(ohlcvs_prev)  ## RSI 값
    ]

    # DB 연결 정보 설정
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    cur = conn.cursor()

    # DB 데이터 INSERT 쿼리(충돌 시 UPDATE 수행)
    sql_insert = f"""
    INSERT INTO {postgres_table} (time, open, high, low, close, volume, rsi)
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
        cur.execute(sql_insert, (
            ohlcv_current[0],
            ohlcv_current[1],
            ohlcv_current[2],
            ohlcv_current[3],
            ohlcv_current[4],
            ohlcv_current[5],
            ohlcv_current[6]
        ))
        cur.execute(sql_insert, (
            ohlcv_prev[0],
            ohlcv_prev[1],
            ohlcv_prev[2],
            ohlcv_prev[3],
            ohlcv_prev[4],
            ohlcv_prev[5],
            ohlcv_prev[6]
        ))
        conn.commit()
        print("데이터 삽입/업데이트 성공")
    except Exception as e:
        conn.rollback()
        print("에러 발생:", e)
    finally:
        cur.close()
        conn.close()