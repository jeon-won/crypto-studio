/*
- 도커 컨테이너로 sql 파일 전송: docker cp create-tables.sql db:/create-tables.sql
- sql 실행: docker exec -it db psql -U ${POSTGRES_USER} -d {POSTGRES_DB} -f /create-tables.sql
*/

-- CREATE TABLE btc_5m (
--     time   TIMESTAMPTZ NOT NULL,  -- TIMESTAMPTZ: 타임존이 포함된 타임스탬프
--     open   REAL NOT NULL,         -- REAL: 소수점 최대 6자리 타입(Float4)
--     high   REAL NOT NULL,
--     low    REAL NOT NULL,
--     close  REAL NOT NULL,
--     volume REAL NOT NULL,
--     rsi    REAL,
--     PRIMARY KEY (time)
-- );

CREATE TABLE btc_15m (
    time   TIMESTAMPTZ NOT NULL,
    open   REAL NOT NULL,
    high   REAL NOT NULL,
    low    REAL NOT NULL,
    close  REAL NOT NULL,
    volume REAL NOT NULL,
    rsi    REAL,
    PRIMARY KEY (time)
);

CREATE TABLE btc_30m (
    time   TIMESTAMPTZ NOT NULL,
    open   REAL NOT NULL,
    high   REAL NOT NULL,
    low    REAL NOT NULL,
    close  REAL NOT NULL,
    volume REAL NOT NULL,
    rsi    REAL,
    PRIMARY KEY (time)
);

CREATE TABLE btc_1h (
    time   TIMESTAMPTZ NOT NULL,
    open   REAL NOT NULL,
    high   REAL NOT NULL,
    low    REAL NOT NULL,
    close  REAL NOT NULL,
    volume REAL NOT NULL,
    rsi    REAL,
    PRIMARY KEY (time)
);

CREATE TABLE btc_2h (
    time   TIMESTAMPTZ NOT NULL,
    open   REAL NOT NULL,
    high   REAL NOT NULL,
    low    REAL NOT NULL,
    close  REAL NOT NULL,
    volume REAL NOT NULL,
    rsi    REAL,
    PRIMARY KEY (time)
);

CREATE TABLE btc_4h (
    time   TIMESTAMPTZ NOT NULL,
    open   REAL NOT NULL,
    high   REAL NOT NULL,
    low    REAL NOT NULL,
    close  REAL NOT NULL,
    volume REAL NOT NULL,
    rsi    REAL,
    PRIMARY KEY (time)
);

CREATE TABLE btc_1d (
    time   TIMESTAMPTZ NOT NULL,
    open   REAL NOT NULL,
    high   REAL NOT NULL,
    low    REAL NOT NULL,
    close  REAL NOT NULL,
    volume REAL NOT NULL,
    rsi    REAL,
    PRIMARY KEY (time)
);