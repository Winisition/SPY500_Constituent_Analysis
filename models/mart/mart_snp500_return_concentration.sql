with with_benchmark_flag as (
    select
        a.ticker,
        a.sector,
        a.year,
        a.pct_change_in_adj_close,
        b.pct_change_in_adj_close as SPY_benchmark,
        case
            when a.pct_change_in_adj_close > b.pct_change_in_adj_close then 1
            else 0
        end as beat_benchmark_flag
    from {{ ref('int_snp500_constituent_returns') }} a
    inner join {{ ref('int_snp500_spy_returns') }} b
    on a.year = b.year
)

select * from with_benchmark_flag