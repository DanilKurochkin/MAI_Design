from sqlalchemy import create_engine
from sqlalchemy import text
# or from sqlalchemy.sql import text
engine = create_engine("postgresql+psycopg2://postgres:postgres@db/archdb", echo=True)
with engine.connect() as con:
    with open("init_test_db.sql") as file:
        query = text(file.read())
        con.execute(query)