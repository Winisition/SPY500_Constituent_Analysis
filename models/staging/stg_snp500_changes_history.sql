{{ config(materialized='view') }}

select
    cast(strptime("Effective Date_Effective Date", '%B %d, %Y') as date) as start_date,
    Added_Ticker                        as added_ticker,
    Added_Security                      as added_security,
    Removed_Ticker                      as removed_ticker,
    Removed_Security                    as removed_security,
    Reason_Reason                       as reason
from {{ source('raw', 'snp500_changes_history') }}
