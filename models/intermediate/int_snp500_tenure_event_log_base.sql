-- Event Code 1: Entry, Event Code 2: Exit

with entry_log as (

    select
        start_date as event_date,
        added_ticker as ticker,
        1 as event
    from {{ ref('stg_snp500_changes_history') }}
    where added_ticker is not null and len(trim(added_ticker)) > 0

),

exit_log as (

    select
        start_date as event_date,
        removed_ticker as ticker,
        2 as event
    from {{ ref('stg_snp500_changes_history') }}
    where removed_ticker is not null and len(trim(removed_ticker)) > 0

)


select *
from entry_log
UNION ALL
select *
from exit_log