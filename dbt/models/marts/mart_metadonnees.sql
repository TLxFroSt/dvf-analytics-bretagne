-- Métadonnées de fraîcheur, pour le pied de page et la page Méthodologie du dashboard.
-- Grain : une seule ligne.

with

fichiers as (
    select
        max(date_publication) as date_publication_donnees,
        count(*) as nb_fichiers_sources
    from {{ ref('stg_dvf_manifest') }}
),

ventes as (
    select
        min(date_mutation) as date_premiere_vente,
        max(date_mutation) as date_derniere_vente
    from {{ ref('int_mutations') }}
),

final as (
    select
        -- Date de publication par la DGFiP, ramenée au jour (heure de Paris).
        cast(timezone('Europe/Paris', fichiers.date_publication_donnees) as date)
            as date_publication_donnees,
        ventes.date_premiere_vente,
        ventes.date_derniere_vente,
        fichiers.nb_fichiers_sources,
        cast(current_timestamp as timestamp) as date_construction
    from fichiers
    cross join ventes
)

select * from final
