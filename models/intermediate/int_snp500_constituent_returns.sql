with constituent_date_indexed as (

select
    ticker,
    sector,
    date,
    adj_close,
    row_number() over ( partition by ticker, extract(year from date) order by date desc) as rn_reverse
from {{ ref('int_snp500_current_constituent_prices') }}
),

constituent_annual_adj_close as (

SELECT
    ticker,
    sector,
    date,
    adj_close
from constituent_date_indexed
where rn_reverse = 1
),

constituent_annual_percentage_gain as (

SELECT
    ticker,
    sector,
    year(DATE) as year,
    adj_close / lag(adj_close,1) over ( partition by ticker order by date asc) - 1 as pct_change_in_adj_close

from constituent_annual_adj_close
)

select *
from constituent_annual_percentage_gain
where pct_change_in_adj_close is not null
and year in ( select year from {{ ref('int_snp500_spy_returns') }})