import tkinter as tk
from tkinter import ttk
import yfinance as yf #type: ignore
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd #type: ignore


def get_ticker_data(ticker_entry: ttk.Entry) -> pd.DataFrame:
    ticker_name = ticker_entry.get()
    ticker: yf.Ticker = yf.Ticker(ticker_name)
    ticker_data: pd.DataFrame = ticker.history(period='1mo')
    return ticker_data

def create_graph(data: pd.DataFrame) -> Figure:
    fig = Figure()
    ax = fig.add_subplot()
    ax.plot(data.index,data.Open)
    return fig

def main():
    window = tk.Tk()
    window.title('Personal Finance')
    window.geometry('800x500')

    ticker_name = tk.StringVar()

    ticker_entry = ttk.Entry(master=window, text='Ticker Name')
    ticker_entry.pack()

    button = ttk.Button(master=window,text='Confirm',command=lambda: get_ticker_data(ticker_entry))
    button.pack()

    fig: Figure = create_graph(button)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    window.mainloop()

if __name__ == "__main__":
    main()
