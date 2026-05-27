# Checks for any anomalies in data
from pathlib import Path
import duckdb
from project_config import DB_PATH

def tables_and_fields_check(table, columns:list):

    issues = []

    with duckdb.connect(str(DB_PATH)) as con: 

        count = con.execute(f"select count(*) from {table}").fetchone()[0]
        
        if count == 0:
            issues.append(f"{table} is empty")
        
        for col in columns:
            null_count = con.execute(f"""select count(*) from {table} where "{col}" is null""").fetchone()[0]

            if null_count > 0:
                issues.append(f"{table}.{col} has {null_count} null rows")

        return issues


def duplicate_date_check(table, col, tic=None):
    issues = []
    with duckdb.connect(str(DB_PATH)) as con:
        group_by = f'"{tic}", "{col}"' if tic else f'"{col}"'
        duplicates = con.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT {group_by}
                FROM {table}
                GROUP BY {group_by}
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]
        if duplicates > 0:
            issues.append(f"{table} contains duplicate ({tic + ', ' if tic else ''}{col})")
        return issues
        


def main():

    issues = []

    issues += tables_and_fields_check('snp500_current_constituents', ['Symbol','Date added', 'GICS Sector'])
    issues += tables_and_fields_check('snp500_changes_history', ['Effective Date_Effective Date','Reason_Reason'])
    issues += tables_and_fields_check('snp500_raw_prices', ['Ticker','Date','Adj Close'])
    issues += tables_and_fields_check('snp500_spy_prices', ['Ticker','Date','Adj Close'])
    issues += duplicate_date_check('snp500_raw_prices', 'Date', 'Ticker')
    issues += duplicate_date_check('snp500_spy_prices', 'Date')
    if issues:
        print(issues)
    else:
        print("\n No data issues detected")

if __name__ == "__main__":
    main()