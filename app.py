import tkinter as tk
from tkinter import ttk
import customtkinter as ctk #type: ignore
import sqlite3
import re
from colors import *


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color=DARK)
       
        self.title('Personal Finane')
        self.geometry("800x500")
        
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=0)

        IncomeSpendingView(self)
        SavingsView(self)

    def mainloop(self, n: int = 0) -> None:
        return super().mainloop(n)
    
class SavingsView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent, fg_color=FOREGROUND)
        self.grid(column=0, row=1, sticky='nsew', padx= 7, pady=7)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Total Excess', font=self.font, text_color=DARK)
        self.title.pack()

        self.savings_var = ctk.StringVar(self)
        self.refresh_savings() 

        self.savings = ctk.CTkLabel(self, textvariable=self.savings_var,font=self.font, text_color=DARK)
        self.savings.pack()
        
        self.refresh_button = ctk.CTkButton(self, text='Refresh',command=lambda:self.refresh_savings(),
                                     fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK)
        self.refresh_button.pack(pady=5)

    def refresh_savings(self):
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        get_income = cur.execute("SELECT SUM(amount) FROM income")
        income = get_income.fetchone()[0]
        get_spending = cur.execute("SELECT SUM(amount) FROM spending")
        spending = get_spending.fetchone()[0]
        
        total_savings = income - spending

        con.close()

        self.savings_var.set(str(total_savings))


class IncomeSpendingView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent, fg_color=MIDGROUND)
        self.grid(column=0, row=0, sticky='nsew', padx=7, pady=7)

        self.columnconfigure((0,1),weight=1, uniform='a')
        self.rowconfigure(0,weight=1)

        IncomeView(self)
        SpendingView(self)

class IncomeView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent,fg_color=FOREGROUND)
        self.grid(column=0, row=0, sticky='nsew', padx=5, pady=5)
        self.validate_command = self.register(self.on_validate)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Income', font=self.font, text_color=DARK)
        self.title.pack(anchor='nw',padx=5)

        self.add_entry = ctk.CTkLabel(self, text='Add Entry', font=self.small_font, text_color=DARK)
        self.add_entry.pack(anchor='nw',padx=5)

        self.row_labels = ctk.CTkFrame(self,fg_color=FOREGROUND)
        self.row_labels.columnconfigure(0, weight=2)
        self.row_labels.columnconfigure(1, weight=2)
        self.row_labels.columnconfigure(2, weight=1)
        self.row_labels.rowconfigure(0)
        self.row_labels.pack(anchor='nw', fill='x')

        self.income_name = ctk.CTkEntry(self.row_labels, placeholder_text='Income Name', font=self.small_font, text_color=DARK)
        self.income_name.grid(row=0,column=0,padx=5,sticky='ew')
        self.income_amount = ctk.CTkEntry(self.row_labels, placeholder_text='123.45', validate='key',validatecommand=(self.validate_command, '%P'),
                                          font=self.small_font, text_color=DARK)
        self.income_amount.grid(row=0,column=1,padx=5,sticky='ew')
        self.confirm_button = ctk.CTkButton(self.row_labels, text='Confirm',command=lambda:self.store_entry(self.income_name,self.income_amount),
                                            fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK,width=100)
        self.confirm_button.grid(row=0,column=2,padx=5,pady=5,sticky='ew')

        self.entries = []
        self.entries_view()

    def entries_view(self):
        font = ctk.CTkFont(family='Calibri', size=16)

        entries = self.get_entries()

        for i,entry in enumerate(entries):
            self.row_entries = ctk.CTkFrame(self,fg_color=FOREGROUND)
            self.row_entries.columnconfigure(0, weight=2)
            self.row_entries.columnconfigure(1, weight=2)
            self.row_entries.columnconfigure(2, weight=1)
            self.row_entries.rowconfigure(0)
            self.row_entries.pack(side='top',anchor='nw',fill='x')

            self.entry_name = ctk.CTkLabel(self.row_entries,text=f'{entry[1]}',font=font, text_color=DARK, justify='right')
            self.entry_name.grid(row=0,column=0,padx=10,sticky='w')
            self.entry_amount = ctk.CTkLabel(self.row_entries,text=f'{entry[2]}',font=font, text_color=DARK, justify='right')
            self.entry_amount.grid(row=0,column=1,padx=10,sticky='w')
            self.delete = ctk.CTkButton(self.row_entries, text='Delete',command=lambda index=i:self.delete_entry(index, entries),
                                        fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK,width=50)
            self.delete.grid(row=0,column=2,padx=5,pady=5,sticky='ew')
            
            self.entries.append(self.entry_name)
            self.entries.append(self.entry_amount)
            self.entries.append(self.delete)
            self.entries.append(self.row_entries)

    def store_entry(self,income_name,income_amount):
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO income (name, amount)
                    VALUES (?,?)""",(income_name.get(),float(income_amount.get())))
        con.commit()
        con.close()

        self.refresh_entries()

    def get_entries(self) -> list[tuple]:
        entries = []
        
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        selection = cur.execute("SELECT * FROM income")
        for i in selection:
            entries.append(i)            
        con.close()

        return entries

    def delete_entry(self,index,entries):
        to_delete = entries[index][0]

        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        cur.execute('DELETE FROM income WHERE id = ?', (to_delete,))
        con.commit()
        con.close()

        self.refresh_entries()

    def refresh_entries(self):
        for entry in self.entries:
            entry.destroy()
        self.entries_view()

    def on_validate(self,P):
        return self.validate_entry(P) or P == ''
    
    def validate_entry(self,text):
        return re.match(r'^\d+(\.\d{0,2})?$', text) is not None

class SpendingView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent,fg_color=FOREGROUND)
        self.grid(column=1, row=0, sticky='nsew', padx=5, pady=5)
        self.validate_command = self.register(self.on_validate)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Spending', font=self.font, text_color=DARK)
        self.title.pack(anchor='nw', padx=5)

        self.add_entry = ctk.CTkLabel(self, text='Add Entry', font=self.small_font, text_color=DARK)
        self.add_entry.pack(anchor='nw', padx=5)

        self.row_labels = ctk.CTkFrame(self,fg_color=FOREGROUND)
        self.row_labels.columnconfigure(0, weight=2)
        self.row_labels.columnconfigure(1, weight=2)
        self.row_labels.columnconfigure(2, weight=1)
        self.row_labels.rowconfigure(0)
        self.row_labels.pack(anchor='nw', fill='x')

        self.spending_name = ctk.CTkEntry(self.row_labels, placeholder_text='Spending Name', font=self.small_font, text_color=DARK)
        self.spending_name.grid(row=0, column=0, padx=5,pady=5, sticky='ew')
        self.spending_amount = ctk.CTkEntry(self.row_labels, placeholder_text='123.45', validate='key',validatecommand=(self.validate_command, '%P'),
                                            font=self.small_font, text_color=DARK)
        self.spending_amount.grid(row=0, column=1, padx=5,pady=5, sticky='ew')
        self.confirm_button = ctk.CTkButton(self.row_labels, text='Confirm',command=lambda:self.store_entry(self.spending_name,self.spending_amount),
                                            fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK, width=100)
        self.confirm_button.grid(row=0,column=2, padx=5,pady=5, sticky='ew')

        self.entries = []
        self.entries_view()

    def entries_view(self):
        font = ctk.CTkFont(family='Calibri', size=16)

        entries = self.get_entries()

        for i,entry in enumerate(entries):
            self.row_entries = ctk.CTkFrame(self,fg_color=FOREGROUND)
            self.row_entries.columnconfigure(0, weight=2)
            self.row_entries.columnconfigure(1, weight=2)
            self.row_entries.columnconfigure(2, weight=1)
            self.row_entries.rowconfigure(0)
            self.row_entries.pack(side='top',anchor='nw',fill='x')

            self.entry_name = ctk.CTkLabel(self.row_entries,text=f'{entry[1]}',font=font, text_color=DARK, justify='right')
            self.entry_name.grid(row=0,column=0,padx=10,sticky='w')
            self.entry_amount = ctk.CTkLabel(self.row_entries,text=f'{entry[2]}',font=font, text_color=DARK, justify='right')
            self.entry_amount.grid(row=0,column=1,padx=10,sticky='w')
            self.delete = ctk.CTkButton(self.row_entries, text='Delete',command=lambda index=i:self.delete_entry(index, entries),
                                        fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK, width=50)
            self.delete.grid(row=0,column=2,padx=5,pady=5,sticky='ew')
            self.entries.append(self.entry_name)
            self.entries.append(self.entry_amount)
            self.entries.append(self.delete)
            self.entries.append(self.row_entries)

    def store_entry(self,spending_name,spending_amount):
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO spending (name, amount)
                    VALUES (?,?)""",(spending_name.get(),float(spending_amount.get())))
        con.commit()
        con.close()

        self.refresh_entries()

    def get_entries(self) -> list[tuple]:
        entries = []
        
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        selection = cur.execute("SELECT * FROM spending")
        for i in selection:
            entries.append(i)            
        con.close()

        return entries

    def delete_entry(self,index,entries):
        to_delete = entries[index][0]

        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        cur.execute('DELETE FROM spending WHERE id = ?', (to_delete,))
        con.commit()
        con.close()

        self.refresh_entries()

    def refresh_entries(self):
        for entry in self.entries:
            entry.destroy()
        self.entries_view()

    def on_validate(self,P):
        return self.validate_entry(P) or P == ''
    
    def validate_entry(self,text):
        return re.match(r'^\d+(\.\d{0,2})?$', text) is not None


class Menu(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
