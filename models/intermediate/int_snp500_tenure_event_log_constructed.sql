 -- if first event is an exit, we assume entry to be '1957-03-04'

with first_event_exit as (
    
    select
        ticker,
        cast('1957-03-04' as date) as start_date,
        event_date as end_date
    from {{ ref('int_snp500_tenure_event_log_ordered') }}
    where (event = 2 and event_order = 1)

),
-- if last event is an entry, we assume it to be available in int_snp500_tenure_current_constituents

remaining_event as (

    select
        event_date,
        ticker,
        event
        
from {{ ref('int_snp500_tenure_event_log_ordered') }}
where not
    ((event = 2 and event_order = 1)
    or
    (event = 1 and event_order = max_event_order)
)),

constructed_event_log as (

select
    r.ticker,
    r.event_date as start_date,
    r2.event_date as end_date
from remaining_event r
inner join remaining_event r2
on r.ticker = r2.ticker
where r.event_date <= r2.event_date

)

select *
from constructed_event_log
UNION ALL
select *
from first_event_exit