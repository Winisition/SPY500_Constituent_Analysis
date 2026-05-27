with spy_date_indexed as (

select
    ticker,
    date,
    adj_close,
    row_number() over ( partition by extract(year from date) order by date desc) as rn_reverse
from {{ ref('stg_snp500_spy_prices') }}

),

spy_annual_adj_close as (

select
    ticker,
    date,
    adj_close
from spy_date_indexed
where rn_reverse = 1
),

spy_annual_percentage_gain as (

SELECT
    ticker,
    year(DATE) as year,
    adj_close / lag(adj_close,1) over ( order by date asc) - 1 as pct_change_in_adj_close

from spy_annual_adj_close
)

select *
from spy_annual_percentage_gain
where pct_change_in_adj_close is not null