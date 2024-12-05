from sqlalchemy import create_engine
from sqlalchemy import text
import time


engine = create_engine("postgresql+psycopg2://postgres:postgres@db/archdb", echo=True)
def wait_for_db(retries=10, delay=5):
    for _ in range(retries):
        try:
            engine.connect()
            print("PostgreSQL is ready!")
            return
        except Exception as e:
            print(f"PostgreSQL not ready yet: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to PostgreSQL")

if __name__ == "__main__":
    wait_for_db()
    with engine.connect() as con:
        with open("init_db/init_test_db.sql") as file:
            query = text(file.read())
            con.execute(query)
            con.commit()