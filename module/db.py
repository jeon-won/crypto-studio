from dotenv import load_dotenv
import os, psycopg2, sys

# 상수 --------------------------------------------------
load_dotenv()
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def init(dbname):
    """
    PostgreSQL 데이터베이스 연결을 초기화합니다.
    
    :param dbname: 데이터베이스 이름
    """
    global conn, cursor
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"DB 연결 실패: {e}")
        sys.exit(1)

def insert(table, data):
    """
    지정된 테이블에 데이터를 삽입합니다. 만약 데이터가 이미 존재한다면 업데이트합니다."

    :param table: 데이터베이스 테이블 이름
    :param data: 삽입할 List 타입 데이터(예: [time(datetime), open(float), high(float), low(float), close(float), volume(float), rsi(float)])
    """
    global conn, cursor
    try:
        if not conn or not cursor:
            raise Exception("DB 연결이 초기화되지 않았습니다.")
        
        query = f"""
        INSERT INTO {table} (time, open, high, low, close, volume, rsi)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (time) DO UPDATE
        SET open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            rsi = EXCLUDED.rsi;
        """

        cursor.execute(query, (
            data[0], 
            data[1], 
            data[2], 
            data[3],
            data[4], 
            data[5], 
            data[6]
        ))
        
        conn.commit()
        print(f"데이터 삽입 성공: {data}")
    except Exception as e:
        print(f"데이터 삽입 실패: {e}")
        conn.rollback()

def select(table, limit=50):
    """
    지정된 테이블에서 데이터를 조회합니다.

    :param table: 데이터베이스 테이블 이름
    :param limit: 조회할 데이터의 최대 개수
    :return: 조회된 데이터의 리스트
    """
    global conn, cursor
    
    try:
        if not conn or not cursor:
            raise Exception("DB 연결이 초기화되지 않았습니다.")
        
        query = f"SELECT * FROM {table} ORDER BY time DESC LIMIT %s;"
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"데이터 조회 실패: {e}")
        return []

def close():
    """
    데이터베이스 연결을 종료합니다.

    :return: None
    """
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# if __name__ == "__main__":
#     init("binance")
#     insert("btc_15m", [time, open, high, low, close, volume, rsi])
#     rows = select("btc_4h", limit=50)
#     print(rows)