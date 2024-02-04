import tkinter as tk
from tkinter import ttk

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import(FigureCanvasTkAgg)

window = tk.Tk()
window.title('Personal Finance')
window.geometry('800x500')

window.mainloop()
