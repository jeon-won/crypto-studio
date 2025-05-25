# crypto-studio

가상화폐 거래 연구용(?) 리포지토리 입니다.

테스트 중인 코드이므로 정상적인 실행을 보장하지 않으며, 이 프로그램을 사용하여 발생하는 손해에 대한 책임은 사용자 본인에게 있습니다.

## 디렉터리 구조

### 최상위 경로

`insert_candle_data.py`: 현재와 바로 직전 시점의 비트코인 캔들 데이터(시간, 시가, 고가, 저가, 종가, 거래량, RSI) 저장

`test-query-ai.py(코딩 중)`: DB에 저장된 비트코인 데이터를 꺼내온 후 OpenAI에 질의

### docker

도커 컨테이너 관련. PostgreSQL DB를 도커로 구축하는 코드 넣어봄.

### module

`aux_indicator.py`는 보조지표 관련 모듈

  * `calculate_rsi()`: RSI 값을 반환하는 함수

`messenger.py`는 특정 메신저로 메시지를 보내는 모듈

  * `send_telegram_message()`: 텔레그램 메시지 전송
  * `send_discord_message()`: 디스코드 메시지 전송