with daily_return_table as (

select
    ticker,
    sector,
    date,
    case
        when daily_return > 0 then 'up_days'
        when daily_return < 0 then 'down_days'
        when daily_return = 0 then 'flat_days'
        else 'not applicable'
        end as daily_return_category
    from {{ ref('int_snp500_daily_return') }}

),

win_rate as (

select
    ticker,
    sector,
    daily_return_category,
    count(*) as number_of_days,
    sum(number_of_days) over (partition by ticker) as total_number_of_days
    from daily_return_table
    group by ticker, sector, daily_return_category

),

win_rate_percentage as (

select
    ticker,
    sector,
    number_of_days / total_number_of_days as win_rate
    from win_rate
    where daily_return_category = 'up_days'

)

select *
from win_rate_percentage