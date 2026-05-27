SELECT
    ticker,
    sector,
    cast(date_added as date) as start_date,
    current_date as end_date
from {{ ref('stg_snp500_current_constituents') }}
