import sqlite3
import yfinance as yf #type:ignore
import pandas as pd #type:ignore
from datetime import datetime, timedelta
from typing import Optional


def add_ticker_data(ticker:str) -> None: 
    historic_records = get_ticker_data(ticker)
    if historic_records is None:
        return None
    
    con = sqlite3.connect("db/personal_finance.db")
    cur = con.cursor()

    cur.executemany("""INSERT OR REPLACE INTO ticker_data 
                    VALUES (:ticker,:Date,:Open,:High,:Low,:Close,:adj_close,:Volume)""",
                    historic_records)

    con.commit()
    con.close()

def get_ticker_data(ticker:str) -> Optional[dict]:
    start_date = '2022-01-01'
    saved_date = check_start_date(ticker)
    if saved_date is not None:
        start_date = add_day(saved_date)
    if saved_date == datetime.today().strftime('%Y-%m-%d'):
        return None

    historic_data: pd.DataFrame = yf.download(ticker, start=start_date, end=None)

    if historic_data.empty:
        return None

    historic_data['ticker'] = ticker
    historic_data.index = historic_data.index.map(lambda timestamp: timestamp.strftime('%Y-%m-%d'))
    historic_data.rename(columns={'Adj Close':'adj_close'},inplace=True)

    historic_records = historic_data.reset_index().to_dict(orient='records')
    
    return historic_records

def check_start_date(ticker:str) -> Optional[str]:
    con = sqlite3.connect('db/personal_finance.db')
    cur = con.cursor()

    cur.execute("""
                SELECT MAX(date) from ticker_data
                WHERE ticker = ?
                GROUP BY ticker;
                """,(ticker,))

    result = cur.fetchone()

    if result is None:
        return result
    
    date, = result
    return date

def add_day(date:str) -> str:
    date_format = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
    return date_format.strftime('%Y-%m-%d')


if __name__ == "__main__":
    pass