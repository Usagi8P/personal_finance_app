import customtkinter as ctk #type: ignore
import os
import sqlite3
import re
from create_db import create_database
from colors import *


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
       
        self.title('Personal Finane')
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")
        
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=0)

        if not self.database_exists():
            create_database()

        IncomeSpendingView(self)
        SavingsView(self)

    def database_exists(self) -> bool:
        if not os.path.isfile('db/personal_finance.db'):
            return False

        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        income = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='income'").fetchone() is not None
        investments = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='investments'").fetchone() is not None
        spending = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='spending'").fetchone() is not None
        ticker_data = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='ticker_data'").fetchone() is not None
        con.close()

        return income and investments and spending and ticker_data

    def mainloop(self, n: int = 0) -> None:
        return super().mainloop(n)
    
class SavingsView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent)
        self.grid(column=0, row=1, sticky='nsew')

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Total Excess', font=self.font)
        self.title.pack()

        self.income_var = ctk.StringVar(self)
        self.spending_var = ctk.StringVar(self)
        self.savings_var = ctk.StringVar(self)
        self.refresh_savings() 

        self.income = ctk.CTkLabel(self, textvariable=self.income_var,font=self.small_font)
        self.income.pack()
        self.spending = ctk.CTkLabel(self, textvariable=self.spending_var,font=self.small_font)
        self.spending.pack()
        self.savings = ctk.CTkLabel(self, textvariable=self.savings_var,font=self.font)
        self.savings.pack()
        
        self.refresh_button = ctk.CTkButton(self, text='Refresh',command=lambda:self.refresh_savings())
        self.refresh_button.pack(pady=5)

    def refresh_savings(self):
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        get_income = cur.execute("SELECT SUM(amount) FROM income")
        income = get_income.fetchone()[0]
        get_spending = cur.execute("SELECT SUM(amount) FROM spending")
        spending = get_spending.fetchone()[0]
        
        if income is None:
            income = 0.00
        if spending is None:
            spending = 0.00
        
        total_savings = income - spending

        con.close()

        self.income_var.set(f"{income:,.2f}")
        self.spending_var.set(f"-{spending:,.2f}")
        self.savings_var.set(f"{total_savings:,.2f}")


class IncomeSpendingView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent)
        self.grid(column=0, row=0, sticky='nsew')

        self.columnconfigure((0,1),weight=1, uniform='a')
        self.rowconfigure(0,weight=1)

        IncomeView(self)
        SpendingView(self)

class IncomeView(ctk.CTkScrollableFrame):
    def __init__(self,parent):
        super().__init__(master=parent)
        self.grid(column=0, row=0, sticky='nsew', padx=5, pady=5)
        self.validate_command = self.register(self.on_validate)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Income', font=self.font)
        self.title.pack(anchor='nw',padx=5)

        self.row_labels = ctk.CTkFrame(self, fg_color='transparent')
        self.row_labels.pack(anchor='nw', fill='x')
        ctk.CTkLabel(self.row_labels,text='').pack(pady=2)

        self.income_name = ctk.CTkEntry(self.row_labels, placeholder_text='Income Name', font=self.small_font)
        self.income_name.place(relx=0/5,relwidth=2/5)
        self.income_amount = ctk.CTkEntry(self.row_labels, placeholder_text='123.45', validate='key',validatecommand=(self.validate_command, '%P'),
                                          font=self.small_font)
        self.income_amount.place(relx=2/5,relwidth=2/5)
        self.confirm_button = ctk.CTkButton(self.row_labels, text='Confirm',command=lambda:self.store_entry(self.income_name,self.income_amount))
        self.confirm_button.place(relx=4/5,relwidth=1/5)


        self.entries = []
        self.entries_view()

    def entries_view(self):
        font = ctk.CTkFont(family='Calibri', size=16)

        entries = self.get_entries()

        for i,entry in enumerate(entries):
            self.row_entries = ctk.CTkFrame(self,fg_color='transparent')
            self.row_entries.pack(side='top',anchor='nw',fill='x')
            ctk.CTkLabel(self.row_entries,text='').pack(pady=2)

            self.entry_name = ctk.CTkLabel(self.row_entries,text=f'{entry[1]}',font=font, justify='right')
            self.entry_name.place(relx=0/5)
            self.entry_amount = ctk.CTkLabel(self.row_entries,text=f'{entry[2]:,.2f}',font=font, justify='right')
            self.entry_amount.place(relx=2/5)
            self.delete = ctk.CTkButton(self.row_entries, text='Delete',command=lambda index=i:self.delete_entry(index, entries))
            self.delete.place(relx=4/5,relwidth=1/5)
            
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
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        selection = cur.execute("SELECT * FROM income").fetchall()
        con.close()

        return selection

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

class SpendingView(ctk.CTkScrollableFrame):
    def __init__(self,parent):
        super().__init__(master=parent)
        self.grid(column=1, row=0, sticky='nsew', padx=5, pady=5)
        self.validate_command = self.register(self.on_validate)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Spending', font=self.font)
        self.title.pack(anchor='nw', padx=5)

        self.row_labels = ctk.CTkFrame(self, fg_color='transparent')
        self.row_labels.pack(anchor='nw', fill='x')
        ctk.CTkLabel(self.row_labels,text='').pack(pady=2)


        self.spending_name = ctk.CTkEntry(self.row_labels, placeholder_text='Spending Name', font=self.small_font)
        self.spending_name.place(relx=0/5,relwidth=2/5)
        self.spending_amount = ctk.CTkEntry(self.row_labels, placeholder_text='123.45', validate='key',validatecommand=(self.validate_command, '%P'),
                                            font=self.small_font)
        self.spending_amount.place(relx=2/5,relwidth=2/5)
        self.confirm_button = ctk.CTkButton(self.row_labels, text='Confirm',command=lambda:self.store_entry(self.spending_name,self.spending_amount), width=100)
        self.confirm_button.place(relx=4/5,relwidth=1/5)

        self.entries = []
        self.entries_view()

    def entries_view(self):
        font = ctk.CTkFont(family='Calibri', size=16)

        entries = self.get_entries()

        for i,entry in enumerate(entries):
            self.row_entries = ctk.CTkFrame(self, fg_color='transparent')
            self.row_entries.pack(side='top',anchor='nw',fill='x')
            ctk.CTkLabel(self.row_entries,text='').pack(pady=2)

            self.entry_name = ctk.CTkLabel(self.row_entries,text=f'{entry[1]}',font=font, justify='right')
            self.entry_name.place(relx=0/5)
            self.entry_amount = ctk.CTkLabel(self.row_entries,text=f'{entry[2]:,.2f}',font=font, justify='right')
            self.entry_amount.place(relx=2/5)
            self.delete = ctk.CTkButton(self.row_entries, text='Delete',command=lambda index=i:self.delete_entry(index, entries), width=50)
            self.delete.place(relx=4/5,relwidth=1/5)

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
        con = sqlite3.connect('db/personal_finance.db')
        cur = con.cursor()
        selection = cur.execute("SELECT * FROM spending").fetchall()          
        con.close()

        return selection

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


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
