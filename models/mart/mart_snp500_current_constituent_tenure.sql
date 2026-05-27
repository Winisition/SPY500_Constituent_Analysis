with combined_tenure_table as (

    select ticker, start_date, end_date
    from {{ ref('int_snp500_tenure_event_log_constructed') }}
    UNION ALL
    select ticker, start_date, end_date
    from {{ ref('int_snp500_tenure_current_constituents') }}

)

select
    a.ticker,
    b.sector,
    a.start_date,
    a.end_date,
    datediff('day', a.start_date, a.end_date) / 365.25 as tenure_in_years
from combined_tenure_table a
inner join {{ ref('stg_snp500_current_constituents') }} b
on a.ticker = b.ticker
where not (a.start_date = a.end_date)