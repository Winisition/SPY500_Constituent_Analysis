# This script serves to incrementally scrape the daily prices for all S&P500 tickers ( Current + Historical )

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

def get_tickers(con):
    
    # Get all tickers that were ever included in the snp500

    return con.execute("""
        SELECT Symbol as ticker FROM snp500_current_constituents
        UNION
        SELECT Added_Ticker FROM snp500_changes_history WHERE Added_Ticker IS NOT NULL
        UNION
        SELECT Removed_Ticker FROM snp500_changes_history WHERE Removed_Ticker IS NOT NULL
    """).df()["ticker"].tolist()

def get_last_dates(con):
     
     # Returns a dict of {ticker: latest_date} from snp500_raw_prices
     # Returns an empty dict if table doesn't exist yet
    
    try:

        return dict(con.execute("SELECT Ticker, MAX(Date) as last_date FROM snp500_raw_prices GROUP BY Ticker").fetchall())
    
    except duckdb.CatalogException:

        return {} 

def fetch_ticker(ticker: str, last_date) -> pd.DataFrame | None:

    # Fetch price history for tickers from Yahoo Finance
    # If ticker already exists, fetch only new data. Otherwise, fetch full history

    t = yf.Ticker(ticker)

    if last_date is None:
        df = t.history(period = "max", auto_adjust=False)
    else:
        start = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        df = t.history(start=start, auto_adjust=False)

    if df.empty:
        return None
    
    df = df.reset_index()
    df.insert(0, "Ticker", ticker)
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    return df

def dedup(con):

    con.execute("""
        CREATE OR REPLACE TABLE snp500_raw_prices AS
        SELECT * FROM snp500_raw_prices
        QUALIFY ROW_NUMBER() OVER (PARTITION BY Ticker, Date ORDER BY Date) = 1
    """)

def main():

    with duckdb.connect(str(DB_PATH)) as con:

        tickers = [t.replace(".", "-") for t in get_tickers(con)]
        last_date = get_last_dates(con)
        first_run = len(last_date) == 0

        new_tickers = []
        not_updated = []

        for ticker in tqdm(tickers):

            try:
                df = fetch_ticker(ticker, last_date.get(ticker))

                if df is None:
                    not_updated.append((ticker, "no new data"))

                else:
                    new_tickers.append(df)
 


            except Exception as e:
                not_updated.append((ticker, str(e)[:100]))

        if new_tickers:

            new_prices = pd.concat(new_tickers, ignore_index=True)
            new_prices = new_prices.drop_duplicates(subset=["Ticker", "Date"])

            if first_run:
                con.execute("CREATE OR REPLACE TABLE snp500_raw_prices AS SELECT * FROM new_prices")

            else:
                con.execute("INSERT INTO snp500_raw_prices SELECT * FROM new_prices")
        
            print(f"Inserted {len(new_prices)} new rows")

        else:

            print("No new data to insert")

        dedup(con)
        not_updated_df = pd.DataFrame(not_updated, columns=["ticker", "error"])
        con.execute("CREATE OR REPLACE TABLE not_updated_tickers AS SELECT * FROM not_updated_df")

        total = con.execute("SELECT COUNT(*) FROM snp500_raw_prices").fetchone()[0]
        print(f"snp500_raw_prices total: {total} rows | failed: {len(not_updated)}")


if __name__ == "__main__":
    main()

