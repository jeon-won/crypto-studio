"""
현재와 직전 시점의 비트코인 캔들 데이터를 PostgreSQL DB에 저장합니다.
저장하는 데이터는 시간, 시가, 고가, 저가, 종가, 거래량, RSI 값입니다.
"""
import argparse, ccxt, os, psycopg2, sys
import module.db as db
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
time_zone = timezone(timedelta(hours=9))  ## GMT+9: 한국 시간
timeframe = ""       ## 5m, 15m, 1h, 4h, 1d 등(아래 argparse 코드에 의해 값이 결정됨)
postgres_table = ""  ## btc_{timeframe} 형태(아래 argparse 코드에 의해 값이 결정됨)

# 코드 --------------------------------------------------

if __name__ == "__main__":
    # argparse 설정
    parser = argparse.ArgumentParser(
        prog="insert_candle_data.py",
        usage="%(prog)s 15m|1h|1d 와 같은 형식으로 입력해주세요"
    )
    parser.add_argument("timeframe", help="TimeFrame")
    ## args가 비어있을 때 에러 처리
    parser.error = lambda msg: (
        parser.print_usage(sys.stderr),
        sys.stderr.write(f"에러: {msg}\n"),
        sys.exit(2)
    )
    args = parser.parse_args()
    ## 전역변수 값 설정
    timeframe = args.timeframe
    postgres_table = f"btc_{args.timeframe}"

    # CCXT 및 DB 초기화
    exchange = ccxt.binance({
        'options': {
            'defaultType': 'future' ## 선물 거래하므로 넣어봤음
        }
    })
    db.init(POSTGRES_DB)

    # 캔들 데이터(Open, High, Low, Close, Volume) 가져오기
    ohlcvs = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=201)
    ohlcvs_current = ohlcvs[1:] ## 현재 시점의 캔들 RSI 계산을 위한 배열
    ohlcvs_prev = ohlcvs[:-1]   ## 직전 시점의 캔들 RSI 계산을 위한 배열

    # 직전 및 현재 캔들 데이터 가공
    ohlcv_prev = [
        datetime.fromtimestamp(ohlcvs_prev[-1][0] / 1000, tz=time_zone),  ## 시간(GMT+9 기준)
        ohlcvs_prev[-1][1],         ## 시가
        ohlcvs_prev[-1][2],         ## 고가
        ohlcvs_prev[-1][3],         ## 저가
        ohlcvs_prev[-1][4],         ## 종가
        ohlcvs_prev[-1][5],         ## 거래량
        calculate_rsi(ohlcvs_prev)  ## RSI 값
    ]
    ohlcv_current = [
        datetime.fromtimestamp(ohlcvs_current[-1][0] / 1000, tz=time_zone),
        ohlcvs_current[-1][1], 
        ohlcvs_current[-1][2], 
        ohlcvs_current[-1][3], 
        ohlcvs_current[-1][4], 
        ohlcvs_current[-1][5], 
        calculate_rsi(ohlcvs_current)
    ]

    # DB에 데이터 삽입 후 연결 종료
    db.insert(postgres_table, ohlcv_prev)
    db.insert(postgres_table, ohlcv_current)
    db.close()