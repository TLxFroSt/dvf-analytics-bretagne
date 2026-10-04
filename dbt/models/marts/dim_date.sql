-- Dimension calendrier.
-- Grain : un jour, du 1er janvier de la première année de ventes au 31 décembre de la
-- dernière. Les bornes suivent les données : une nouvelle année publiée étend le calendrier.
-- Clé : la date elle-même (clé naturelle stable, attendue par Power BI pour une table de dates).

with

bornes as (
    select
        make_date(min(annee), 1, 1) as date_debut,
        make_date(max(annee), 12, 31) as date_fin
    from {{ ref('int_ventes_logement') }}
),

jours as (
    select cast(unnest(generate_series(date_debut, date_fin, interval 1 day)) as date) as date_jour
    from bornes
),

final as (
    select
        date_jour,
        year(date_jour) as annee,
        quarter(date_jour) as trimestre,
        year(date_jour) || ' T' || quarter(date_jour) as libelle_trimestre,
        year(date_jour) * 10 + quarter(date_jour) as tri_trimestre,
        cast(date_trunc('quarter', date_jour) as date) as date_debut_trimestre,
        month(date_jour) as mois,
        list_extract(
            [
                'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
            ],
            month(date_jour)
        ) as nom_mois,
        year(date_jour) * 100 + month(date_jour) as tri_mois
    from jours
)

select * from final
