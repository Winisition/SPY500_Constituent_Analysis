{{ config(materialized='view') }}

with mart_snp500_sector_composition_1 as (
select 
    sector,
    count(*) as number_of_companies_in_sector,
    count(*) / sum(count(*)) over () as percentage_of_companies
from {{ ref('stg_snp500_current_constituents') }}
group by sector
)

select
    sector,
    number_of_companies_in_sector,
    round(percentage_of_companies,2) as percentage_of_companies
from mart_snp500_sector_composition_1