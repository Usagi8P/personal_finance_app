CREATE TABLE IF NOT EXISTS ticker_data (
    ticker TEXT,
    date DATE,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    adj_close REAL,
    volume INTEGER,
    PRIMARY KEY (ticker, date)
);
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    date DATE,
    price REAL,
    volume INTEGER
);