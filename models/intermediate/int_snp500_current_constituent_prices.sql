select
    a.ticker,
    a.date,
    a.adj_close,
    b.sector
from {{ ref('stg_snp500_raw_prices') }} a
inner join {{ ref('stg_snp500_current_constituents') }} b
on a.ticker = b.ticker