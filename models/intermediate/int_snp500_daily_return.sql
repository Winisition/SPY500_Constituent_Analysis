with daily_return_table as (
SELECT
    ticker,
    sector,
    date,
    adj_close,
    ln ( adj_close / lag(adj_close) over (partition by ticker order by date asc)) as daily_return
from {{ ref('int_snp500_current_constituent_prices') }}
)

select *
from daily_return_table
where adj_close is not null and daily_return is not null