# crypto-studio

가상화폐 거래 연구용(?) 리포지토리 입니다.

테스트 중인 코드이므로 정상적인 실행을 보장하지 않으며, 이 프로그램을 사용하여 발생하는 손해에 대한 책임은 사용자 본인에게 있습니다.

## 디렉터리 구조

### 최상위 경로

`.env`: 환경변수

```env
POSTGRES_HOST = 
POSTGRES_PORT = 
POSTGRES_USER = 
POSTGRES_PASSWORD = 
POSTGRES_DB = 
```

`insert_current_candle_data.py`: 현재 시점의 비트코인 캔들 데이터(시간, 시가, 고가, 저가, 종가, 거래량, RSI)를 DB에 저장합니다.

`insert_prev_candle_data.py`: 직전 시점의 비트코인 캔들 데이터(시간, 시가, 고가, 저가, 종가, 거래량, RSI)를 DB에 저장합니다.

### docker

도커 컨테이너 관련. PostgreSQL DB를 도커로 구축하는 코드 넣어봄.

### module

`aux_indicator.py`는 보조지표 관련 모듈

  * `calculate_rsi()`: RSI 값을 반환하는 함수