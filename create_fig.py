import tkinter
import customtkinter as ctk #type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Union, Optional
from datetime import datetime, timedelta
import sqlite3
import yfinance as yf #type:ignore
import pandas as pd #type:ignore
import matplotlib.pyplot as plt


class Graph(ctk.CTkScrollableFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color='transparent')
        self.pack(fill='both', expand=True)

        TickerLookup(self) 

        fig = self.create_fig()

        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both',expand='True')

    def create_fig(self):
        con = sqlite3.connect("db/personal_finance.db")

        data = pd.read_sql("SELECT * FROM ticker_data", con)
        con.close()

        fig = Figure()
        ax = fig.add_subplot()
        ax.plot(data['date'],data['open'])
        ax.set_xlabel('Date')
        ax.set_ylabel('Price Open')
        
        return fig 


class TickerLookup(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent, fg_color='transparent')
        self.pack(fill='x')

        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.ticker_name = ctk.CTkEntry(self,placeholder_text='Ticker',font=self.small_font)
        self.lookup_button = ctk.CTkButton(self,text='Download',command=lambda:self.add_ticker_data(self.ticker_name.get()))

        self.lookup_button.pack(side='right',pady=5)
        self.ticker_name.pack(side='right',pady=5,padx=5)

    def add_ticker_data(self,ticker:str) -> None:
        if ticker == '':
            return None

        historic_records = self.get_ticker_data(ticker)
        if historic_records is None:
            self.ticker_name.delete(0,len(self.ticker_name.get()))
            return None
        
        con = sqlite3.connect("db/personal_finance.db")
        cur = con.cursor()

        cur.executemany("""INSERT OR REPLACE INTO ticker_data 
                        VALUES (:ticker,:Date,:Open,:High,:Low,:Close,:adj_close,:Volume)""",
                        historic_records)

        con.commit()
        con.close()

        self.ticker_name.delete(0,len(self.ticker_name.get()))

    def get_ticker_data(self,ticker:str) -> Optional[dict]:
        start_date = '2022-01-01'
        saved_date = self.check_start_date(ticker)
        if saved_date is not None:
            date_format = datetime.strptime(saved_date, '%Y-%m-%d') + timedelta(days=1)
            start_date = date_format.strftime('%Y-%m-%d')
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

    def check_start_date(self,ticker:str) -> Optional[str]:
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
