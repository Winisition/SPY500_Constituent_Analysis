{{ config(materialized='view') }}

select
    Ticker                          as ticker,
    Date                            as date,
    Open                            as open,
    High                            as high,
    Low                             as low,
    Close                           as close,
    "Adj Close"                     as adj_close,
    Volume                          as volume,
    Dividends                       as dividends,
    "Stock Splits"                  as stock_splits,
    "Capital Gains"                 as capital_gains
from {{ source('raw', 'snp500_spy_prices') }}