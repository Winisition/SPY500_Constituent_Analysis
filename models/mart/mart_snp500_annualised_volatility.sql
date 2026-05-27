SELECT
    ticker,
    sector,
    year(date) as year,
    stddev_samp(daily_return) * sqrt(252) as annualised_volatility
    from {{ ref('int_snp500_daily_return') }}
    group by ticker, sector, year