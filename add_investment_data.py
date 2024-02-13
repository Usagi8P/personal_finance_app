import sqlite3
from typing import Union


def add_investment(investment_data:Union[list[dict],dict]) -> None:
    data = investment_data
    if type(investment_data) is dict:
        data = [investment_data]

    con = sqlite3.connect('db/personal_finance.db')
    cur = con.cursor()

    cur.executemany("""
                    INSERT INTO investments (ticker, date, price, volume) 
                    VALUES (:ticker,:date,:price,:volume)""",data)

    con.commit()
    con.close()

if __name__=="__main__":
    pass
