with daily_return_table as (

select
    ticker,
    sector,
    date,
    daily_return,
    case
        when daily_return > 0 then 'up_days'
        when daily_return < 0 then 'down_days'
        when daily_return = 0 then 'flat_days'
        else 'not applicable'
        end as daily_return_category
    from {{ ref('int_snp500_daily_return') }}

),

sum_of_gain_loss_by_ticker as (

SELECT
    ticker,
    sector,
    sum ( case when daily_return_category = 'up_days' then daily_return end) as sum_of_up_days,
    sum ( case when daily_return_category = 'down_days' then daily_return end) as sum_of_down_days
from daily_return_table
group by ticker, sector

),

sum_of_gain_loss_ratio_by_ticker as (

SELECT
    ticker,
    sector,
    sum_of_up_days / abs(sum_of_down_days) as win_loss_ratio
from sum_of_gain_loss_by_ticker
)

select *
from sum_of_gain_loss_ratio_by_ticker
