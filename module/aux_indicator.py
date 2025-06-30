import pandas as pd

def calculate_pivot_std(ohlcv):
    """
    피봇 포인트(Pivot Point)와 지지/저항선(Support/Resistance)을 표준(Standard) 산출법을 사용하여 계산합니다.

    Args:
        - ohlcv (list): OHLCV 데이터의 리스트. 각 행은 [timestamp, open, high, low, close, volume] 형식입니다. 이 데이터는 ccxt.fetch_ohlcv() 함수로 가져온 데이터입니다.
    
    Returns:
        - dict: 피봇 포인트와 지지/저항선의 딕셔너리(pp: 피봇 포인트, s1: 첫번째 지지선, s2: 두번째 지지선, r1: 첫번째 저항선, r2: 두번째 저항선)
    """
    # 각 행의 2~5번째(인덱스 1~4) 요소(시가, 고가, 저가, 종가)만 뽑아서 하나의 리스트로 평탄화
    values = [val
            for row in ohlcv
            for val in row[1:5]]
    
    # 고가, 저가, 종가, 피봇포인트 값 계산
    high = max(values)
    low = min(values)
    close = ohlcv[-1][4]
    pp = (high + low + close) / 3

    # 피봇포인트 값과 지지/저항선 값을 딕셔너리에 저장 및 리턴
    std = {
        'pp': pp,  ## 피봇포인트
        's1': (2 * pp) - high,    ## 1차 지지선
        's2': pp - (high - low),  ## 2차 지지선
        'r1': (2 * pp) - low,     ## 1차 저항선
        'r2': pp + (high - low)   ## 2차 저항선
    }
    return std


def calculate_pivot_fibo(ohlcv):
    """
    피봇 포인트(Pivot Point)와 지지/저항선(Support/Resistance)을 피보나치(Fibonacci) 비율을 사용하여 계산합니다.

    Args:
        - ohlcv (list): OHLCV 데이터의 리스트. 각 행은 [timestamp, open, high, low, close, volume] 형식입니다. 이 데이터는 ccxt.fetch_ohlcv() 함수로 가져온 데이터입니다.
    
    Returns:
        - dict: 피봇 포인트와 지지/저항선의 딕셔너리(pp: 피봇 포인트, s1: 첫번째 지지선, s2: 두번째 지지선, s3: 세번째 지지선, r1: 첫번째 저항선, r2: 두번째 저항선, r3: 세번째 저항선)
    """
    # 각 행의 2~5번째(인덱스 1~4) 요소(시가, 고가, 저가, 종가)만 뽑아서 하나의 리스트로 평탄화
    values = [val
            for row in ohlcv
            for val in row[1:5]]

    # 각 행의 2~5번째(인덱스 1~4) 요소(시가, 고가, 저가, 종가)만 뽑아서 하나의 리스트로 평탄화
    high = max(values)
    low = min(values)
    close = ohlcv[-1][4]
    pp = (high + low + close) / 3

    # 피봇포인트 값과 지지/저항선 값을 딕셔너리에 저장 및 리턴
    fibo = {
        'pp': pp,  ## 피봇포인트
        's1': pp - 0.382 * (high - low), ## 1차 지지선
        's2': pp - 0.618 * (high - low), ## 2차 지지선
        's3': pp - 1 * (high - low),     ## 3차 지지선
        'r1': pp + 0.382 * (high - low), ## 1차 저항선
        'r2': pp + 0.618 * (high - low), ## 2차 저항선
        'r3': pp + 1 * (high - low),     ## 3차 저항선
    }
    return fibo


def calculate_pivot_camarilla(ohlcv):
    """
    피봇 포인트(Pivot Point)와 지지/저항선(Support/Resistance)을 카마릴라(Camarilla) 산출법을 사용하여 계산합니다.

    Args:
        - ohlcv (list): OHLCV 데이터의 리스트. 각 행은 [timestamp, open, high, low, close, volume] 형식입니다. 이 데이터는 ccxt.fetch_ohlcv() 함수로 가져온 데이터입니다.
    
    Returns:
        - dict: 피봇 포인트와 지지/저항선의 딕셔너리(pp: 피봇 포인트, s1: 첫번째 지지선, s2: 두번째 지지선, s3: 세번쨰 지지선, s4: 네번째 지지선, r1: 첫번째 저항선, r2: 두번째 저항선, r3: 세번째 저항선, r4: 네번째 저항선)
    """
    # 각 행의 2~5번째(인덱스 1~4) 요소(시가, 고가, 저가, 종가)만 뽑아서 하나의 리스트로 평탄화
    values = [val
            for row in ohlcv
            for val in row[1:5]]

    # 각 행의 2~5번째(인덱스 1~4) 요소(시가, 고가, 저가, 종가)만 뽑아서 하나의 리스트로 평탄화
    high = max(values)
    low = min(values)
    close = ohlcv[-1][4]
    pp = (high + low + close) / 3

    # 피봇포인트 값과 지지/저항선 값을 딕셔너리에 저장 및 리턴
    camarilla = {
        'pp': pp,  ## 피봇포인트
        's1': close - 1.1 * (high - low) / 12, ## 1차지지선
        's2': close - 1.1 * (high - low) / 6,  ## 2차지지선
        's3': close - 1.1 * (high - low) / 4,  ## 3차지지선
        's4': close - 1.1 * (high - low) / 2,  ## 4차지지선
        'r1': close + 1.1 * (high - low) / 12, ## 1차저항선
        'r2': close + 1.1 * (high - low) / 6,  ## 2차저항선
        'r3': close + 1.1 * (high - low) / 4,  ## 3차저항선
        'r4': close + 1.1 * (high - low) / 2,  ## 4차저항선
    }
    return camarilla


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