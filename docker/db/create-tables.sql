/*
- 도커 컨테이너로 sql 파일 전송: docker cp create-tables.sql db:/create-tables.sql
- sql 실행: docker exec -it db psql -U ${POSTGRES_USER} -d {POSTGRES_DB} -f /create-tables.sql
*/

CREATE TABLE btc_15m (
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE PRECISION NOT NULL,
    high   DOUBLE PRECISION NOT NULL,
    low    DOUBLE PRECISION NOT NULL,
    close  DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    rsi    DOUBLE PRECISION,
    PRIMARY KEY (time)
);

CREATE TABLE btc_1h (
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE PRECISION NOT NULL,
    high   DOUBLE PRECISION NOT NULL,
    low    DOUBLE PRECISION NOT NULL,
    close  DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    rsi    DOUBLE PRECISION,
    PRIMARY KEY (time)
);