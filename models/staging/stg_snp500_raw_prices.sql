{{ config(materialized='view') }}

select *
from (
    select
        Ticker as ticker,
        Date as date,
        Open as open,
        High as high,
        Low as low,
        Close as close,
        "Adj Close" as adj_close,
        Volume as volume,
        Dividends as dividends,
        "Stock Splits" as stock_splits,
        row_number() over (partition by Ticker, Date order by Date) as rn
    from {{ source('raw', 'snp500_raw_prices') }}
)
where rn = 1