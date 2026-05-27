from ingest import scrape_01_wikipedia, scrape_02_yfinance_tickers, scrape_03_yfinance_spy, check_01
import subprocess
from pathlib import Path
from project_config import DB_PATH, PROJECT_ROOT

def run_dbt():
    subprocess.run(["dbt", "run"], check=True, cwd=PROJECT_ROOT)
    subprocess.run(["dbt", "test"], check=True, cwd=PROJECT_ROOT)

def main():
    
    # Setup

    DB_PATH.parent.mkdir(exist_ok = True)

    # Run ingest
    
    scrape_01_wikipedia.main()
    scrape_02_yfinance_tickers.main()
    scrape_03_yfinance_spy.main()
    check_01.main()
    

    # Check ingested files for errors

    # Run dbt layer

    run_dbt()



if __name__ == "__main__":
    main()