-- Dimension commune, département et EPCI compris (dénormalisés : schéma en étoile).
-- Grain : une commune actuelle de Bretagne.

with

communes as (
    select * from {{ ref('communes_bretagne') }}
),

departements as (
    select * from {{ ref('departements') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['communes.code_commune_insee']) }} as commune_key,
        communes.code_commune_insee,
        communes.nom_commune,
        -- Libellé désambiguïsé pour les listes : plusieurs communes bretonnes portent le
        -- même nom dans des départements différents.
        communes.nom_commune || ' (' || communes.code_departement || ')' as libelle_commune,
        communes.code_departement,
        departements.nom_departement,
        departements.libelle_du_departement,
        communes.code_epci,
        communes.nom_epci,
        communes.population
    from communes
    inner join departements
        on communes.code_departement = departements.code_departement
)

select * from final
