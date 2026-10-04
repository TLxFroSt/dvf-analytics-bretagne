-- Staging du manifeste d'ingestion : typage, aucune jointure ni filtre.
-- Grain : un fichier source (année × département).

-- En table, comme stg_dvf : une vue conserverait le chemin relatif du fichier source.
{{ config(materialized='table') }}

with

source as (
    select * from {{ source('dvf', 'manifest') }}
),

renamed as (
    select
        cast(annee as integer) as annee,
        code_departement,
        url,
        cast(date_publication as timestamptz) as date_publication,
        cast(taille_octets as bigint) as taille_octets,
        cast(date_telechargement as timestamptz) as date_telechargement
    from source
)

select * from renamed
