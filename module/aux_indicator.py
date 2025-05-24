import pandas as pd

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