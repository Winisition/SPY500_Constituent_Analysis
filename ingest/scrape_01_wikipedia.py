# This script serves to scrape the current constituent and constituent changes from wikipedia

import pandas as pd
import duckdb
from pathlib import Path
from project_config import DB_PATH

# Input Wikipedia URL here
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def main():

    # Sets path for database, creates folder for db_path

    with duckdb.connect(str(DB_PATH)) as con:
        
        tables = pd.read_html(WIKIPEDIA_URL, storage_options={"User-Agent": "Mozilla/5.0"})

        # Error - Handling, and check if the tables are as expected
        
        if len(tables) != 3:
            raise ValueError(f'Number of tables changed, there are {len(tables)} instead')

        print('snp500_current_constituents')
        print(tables[0].head())

        print('snp500_changes_history')
        print(tables[1].head())

        # Identify tables by their unique columns, and add timestamp

        snp500_current_constituents = tables[0]
        snp500_current_constituents['_scraped_at'] = pd.Timestamp.now()
        snp500_changes_history = tables[1]
        snp500_changes_history['_scraped_at'] = pd.Timestamp.now()

        # Flatten Multi-level header for snp500_changes_history

        flattened_columns = [ '_'.join(map(str, col)).strip() if isinstance(col, tuple) 
                    else col for col in snp500_changes_history.columns ]
        snp500_changes_history.columns = flattened_columns 

        # Save dataframe into duckdb warehouse

        con.execute("CREATE OR REPLACE TABLE snp500_current_constituents AS SELECT * FROM snp500_current_constituents")
        con.execute("CREATE OR REPLACE TABLE snp500_changes_history AS SELECT * FROM snp500_changes_history")


        # Check that the rows are not empty

        assert con.execute("SELECT count(*) FROM snp500_current_constituents").fetchone()[0] > 0
        assert con.execute("SELECT count(*) FROM snp500_changes_history").fetchone()[0] > 0

        # Print Output

        print(f"snp500_current_constituents: {con.execute('SELECT COUNT(*) FROM snp500_current_constituents').fetchone()[0]} rows successfully stored")
        print(f"snp500_changes_history: {con.execute('SELECT COUNT(*) FROM snp500_changes_history').fetchone()[0]} rows successfully stored")

if __name__ == "__main__":
    main()