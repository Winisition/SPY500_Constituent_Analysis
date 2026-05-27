# This script serves to incrementally scrape the daily prices the SPY ticker ( Current + Historical )

import pandas as pd
import duckdb
from pathlib import Path
import warnings
import yfinance as yf
import logging
from tqdm import tqdm
from project_config import DB_PATH


# pass warning messages

yf.set_tz_cache_location("/tmp/yf_cache_new")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

def get_last_date(con):
    
    # Returns ticker and latest_date from snp500_spy_prices
    # Returns an empty dict if table doesn't exist yet
    
    try:
        return con.execute("SELECT MAX(Date) FROM snp500_spy_prices").fetchone()[0]
    
    except duckdb.CatalogException:
        return None

def fetch_spy(last_date) -> pd.DataFrame | None:
    
    # Fetch price history for SPY from Yahoo Finance
    # If ticker already exists, fetch only new data. Otherwise, fetch full history

    t = yf.Ticker("SPY")

    if last_date is None:
        df = t.history(period = "max", auto_adjust=False)
    else:
        start = (pd.Timestamp(last_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        df = t.history(start=start, auto_adjust=False)

    if df.empty:
        return None

    df = df.reset_index()
    df.insert(0, "Ticker", "SPY")
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

def dedup(con):
    con.execute("""
        CREATE OR REPLACE TABLE snp500_spy_prices AS
        SELECT * FROM snp500_spy_prices
        QUALIFY ROW_NUMBER() OVER (PARTITION BY Date ORDER BY Date) = 1
    """)

def main():

    with duckdb.connect(str(DB_PATH)) as con:

        last_date = get_last_date(con)
        first_run = last_date is None
        print(f"Last date in DB: {last_date}")

        df = fetch_spy(last_date)

        if df is None:
            print("No new data")
        else:
            df = df.drop_duplicates(subset=["Ticker", "Date"])

            if first_run:
                con.execute("CREATE OR REPLACE TABLE snp500_spy_prices AS SELECT * FROM df")
            else:
                con.execute("INSERT INTO snp500_spy_prices SELECT * FROM df")

            print(f"Inserted {len(df)} new rows")

        dedup(con)
        total = con.execute("SELECT COUNT(*) FROM snp500_spy_prices").fetchone()[0]
        print(f"snp500_spy_prices total: {total} rows")


if __name__ == "__main__":
    main()
