import sqlite3
import yfinance as yf #type:ignore
import pandas as pd #type:ignore

def read_sql(filename:str) -> str:
    with open(filename) as f:
        sql_script = f.read()
    return sql_script

def timestamp_to_date(timestamp):
    return timestamp.strftime('%Y-%m-%d')

def create_database() -> None:
    con = sqlite3.connect("db/personal_finance.db")
    cur = con.cursor()

    create_db = read_sql('create_db.sql')
    cur.execute(create_db)

    con.commit()
    con.close()

def add_ticker_data(ticker:str) -> None:
    # TODO: Check from when to start downloading data. 

    historic_data = yf.download(ticker,start='2022-01-01', end=None)
    historic_data['ticker'] = ticker
    historic_data.index = historic_data.index.map(timestamp_to_date)
    historic_data.rename(columns={'Adj Close':'adj_close'},inplace=True)

    historic_records = historic_data.reset_index().to_dict(orient='records')
    
    con = sqlite3.connect("db/personal_finance.db")
    cur = con.cursor()

    cur.executemany("INSERT INTO ticker_data VALUES(:ticker,:Date,:Open,:High,:Low,:Close,:adj_close,:Volume)",
                    historic_records)

    con.commit()
    con.close()


if __name__=="__main__":
    create_database()
    add_ticker_data('VOO')
