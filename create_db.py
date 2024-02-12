import sqlite3


def read_sql(filename:str) -> str:
    with open(filename) as f:
        sql_script = f.read()
    return sql_script

def create_database() -> None:
    con = sqlite3.connect("db/personal_finance.db")
    cur = con.cursor()

    create_db = read_sql('create_db.sql')
    cur.execute(create_db)

    con.commit()
    con.close()


if __name__=="__main__":
    create_database()
