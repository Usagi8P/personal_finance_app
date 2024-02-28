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
        self.rowconfigure((0,1),weight=1)

        IncomeSpendingView(self)
        SavingsView(self)

    def mainloop(self, n: int = 0) -> None:
        return super().mainloop(n)
    
class SavingsView(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(master=parent, fg_color=FOREGROUND)
        self.grid(column=0, row=1, sticky='nsew', padx= 7, pady=7)

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

        self.columnconfigure(0,weight=3)
        self.columnconfigure(1,weight=2)
        self.columnconfigure(2,weight=1)
        
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Income', font=self.font, text_color=DARK)
        self.title.grid(row=0, column=0, padx=5, sticky='ew')

        self.add_entry = ctk.CTkLabel(self, text='Add Entry', font=self.small_font, text_color=DARK)
        self.add_entry.grid(row=1, column=0, padx=5, sticky='ew')

        self.income_name = ctk.CTkEntry(self, placeholder_text='Income Name', font=self.small_font, text_color=DARK)
        self.income_name.grid(row=2, column=0, padx=5,pady=5, sticky='ew')
        self.income_amount = ctk.CTkEntry(self, placeholder_text='123.45', validate='key',validatecommand=(self.validate_command, '%P'),
                                     font=self.small_font, text_color=DARK)
        self.income_amount.grid(row=2, column=1, padx=5,pady=5, sticky='ew')
        self.confirm_button = ctk.CTkButton(self, text='Confirm Entry',command=lambda:self.store_entry(self.income_name,self.income_amount),
                                       fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK)
        self.confirm_button.grid(row=2,column=2, padx=5,pady=5, sticky='ew')

        self.entries = []
        self.entries_view()

    def entries_view(self):
        font = ctk.CTkFont(family='Calibri', size=16)

        entries = self.get_entries()

        for i,entry in enumerate(entries):
            self.entry_name = ctk.CTkLabel(self,text=f'{entry[1]}',font=font, text_color=DARK)
            self.entry_name.grid(row=3+i,column=0,padx=5,pady=5,sticky='w')
            self.entry_amount = ctk.CTkLabel(self,text=f'{entry[2]}',font=font, text_color=DARK)
            self.entry_amount.grid(row=3+i,column=1,padx=5,pady=5,sticky='w')
            self.delete = ctk.CTkButton(self, text='Delete',command=lambda index=i:self.delete_entry(index, entries),
                                        fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK)
            self.delete.grid(row=3+i,column=2,padx=5,pady=5,sticky='w')
            self.entries.append(self.entry_name)
            self.entries.append(self.entry_amount)
            self.entries.append(self.delete)

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

        self.columnconfigure(0,weight=3)
        self.columnconfigure(1,weight=2)
        self.columnconfigure(2,weight=1)
        
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.font = ctk.CTkFont(family='Calibri', weight='bold', size=26)
        self.small_font = ctk.CTkFont(family='Calibri', size=16)

        self.title = ctk.CTkLabel(self, text='Spending', font=self.font, text_color=DARK)
        self.title.grid(row=0, column=0, padx=5, sticky='ew')

        self.add_entry = ctk.CTkLabel(self, text='Add Entry', font=self.small_font, text_color=DARK)
        self.add_entry.grid(row=1, column=0, padx=5, sticky='ew')

        self.spending_name = ctk.CTkEntry(self, placeholder_text='Spending Name', font=self.small_font, text_color=DARK)
        self.spending_name.grid(row=2, column=0, padx=5,pady=5, sticky='ew')
        self.spending_amount = ctk.CTkEntry(self, placeholder_text='123.45', validate='key',validatecommand=(self.validate_command, '%P'),
                            font=self.small_font, text_color=DARK)
        self.spending_amount.grid(row=2, column=1, padx=5,pady=5, sticky='ew')
        self.confirm_button = ctk.CTkButton(self, text='Confirm Entry',command=lambda:self.store_entry(self.spending_name,self.spending_amount),
                                       fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK)
        self.confirm_button.grid(row=2,column=2, padx=5,pady=5, sticky='ew')

        self.entries = []
        self.entries_view()

    def entries_view(self):
        font = ctk.CTkFont(family='Calibri', size=16)

        entries = self.get_entries()

        for i,entry in enumerate(entries):
            self.entry_name = ctk.CTkLabel(self,text=f'{entry[1]}',font=font, text_color=DARK)
            self.entry_name.grid(row=3+i,column=0,padx=5,pady=5,sticky='w')
            self.entry_amount = ctk.CTkLabel(self,text=f'{entry[2]}',font=font, text_color=DARK)
            self.entry_amount.grid(row=3+i,column=1,padx=5,pady=5,sticky='w')
            self.delete = ctk.CTkButton(self, text='Delete',command=lambda index=i:self.delete_entry(index, entries),
                                        fg_color=LIGHT,hover_color=DARKLIGHT,text_color=DARK)
            self.delete.grid(row=3+i,column=2,padx=5,pady=5,sticky='w')
            self.entries.append(self.entry_name)
            self.entries.append(self.entry_amount)
            self.entries.append(self.delete)

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
