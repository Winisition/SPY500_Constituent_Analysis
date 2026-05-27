{{ config(materialized='view') }}

select
    Symbol                          as ticker,
    Security                        as company_name,
    "GICS Sector"                   as sector,
    "GICS Sub-Industry"             as sub_industry,
    "Headquarters Location"         as headquarters,
    "Date added"                    as date_added,
    CIK                             as cik,
    Founded                         as founded
from {{ source('raw', 'snp500_current_constituents') }}