with int_snp500_tenure_event_log_ordered_1 as (

select
    event_date,
    ticker,
    event,
    row_number() over (partition by ticker order by event_date, event asc) as event_order
from {{ ref('int_snp500_tenure_event_log_base') }}

), int_snp500_tenure_event_log_ordered_2 as (

select
    *,
    max(event_order) over (partition by ticker) as max_event_order
from int_snp500_tenure_event_log_ordered_1
)

select *
from int_snp500_tenure_event_log_ordered_2
where not ((ticker = 'FOX' and event_date = '2019-03-19 00:00:00' and event = 1)
    or 
    (ticker = 'GAS' and event_date = '2011-12-12 00:00:00' and event = 2)
    or 
    ticker in ('Q','UA','AGN','SUN','IR','AN','AA'))

-- Tickers removed because they have incomplete entry and exit entries 