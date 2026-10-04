-- Table de faits des ventes de logement (règle R3 du dictionnaire des KPI).
-- Grain : une vente de logement (une mutation). Les ventes hors population prix restent
-- dans la table, pour les indicateurs de volume ; est_population_prix les distingue.
-- Les tranches (surface, pièces, prix au m²) alimentent la page Typologie : Power BI n'a pas
-- d'histogramme natif, et chaque libellé a sa colonne de tri.

with

ventes as (
    select * from {{ ref('int_ventes_logement') }}
),

tranches as (
    select
        *,
        case
            when surface_bati_m2 < 30 then 1
            when surface_bati_m2 < 50 then 2
            when surface_bati_m2 < 70 then 3
            when surface_bati_m2 < 90 then 4
            when surface_bati_m2 < 120 then 5
            when surface_bati_m2 < 150 then 6
            when surface_bati_m2 >= 150 then 7
        end as tranche_surface_ordre,
        case
            when nb_pieces = 0 then 9  -- 0 pièce principale : information non renseignée
            when nb_pieces >= 6 then 6
            else nb_pieces
        end as tranche_pieces_ordre,
        -- Borne basse de la tranche de 250 €/m², plafonnée à 8 000 €/m² (dernière tranche
        -- ouverte). Seules les ventes de la population prix sont réparties en tranches.
        case
            when est_population_prix then least(floor(prix_m2 / 250) * 250, 8000)
        end as tranche_prix_m2_ordre
    from ventes
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['id_mutation']) }} as vente_key,
        id_mutation,
        date_mutation,
        {{ dbt_utils.generate_surrogate_key(['code_commune_insee']) }} as commune_key,
        {{ dbt_utils.generate_surrogate_key(['code_type_bien']) }} as type_bien_key,
        valeur_fonciere,
        nb_logements,
        nb_dependances,
        surface_bati_m2,
        nb_pieces,
        surface_terrain_m2,
        prix_m2,
        est_population_prix,
        motif_exclusion_prix,
        tranche_surface_ordre,
        case tranche_surface_ordre
            when 1 then 'Moins de 30 m²'
            when 2 then '30 à 49 m²'
            when 3 then '50 à 69 m²'
            when 4 then '70 à 89 m²'
            when 5 then '90 à 119 m²'
            when 6 then '120 à 149 m²'
            when 7 then '150 m² et plus'
        end as tranche_surface,
        cast(tranche_pieces_ordre as integer) as tranche_pieces_ordre,
        case
            when tranche_pieces_ordre = 9 then 'Non renseigné'
            when tranche_pieces_ordre = 1 then '1 pièce'
            when tranche_pieces_ordre = 6 then '6 pièces et plus'
            when tranche_pieces_ordre is not null then tranche_pieces_ordre || ' pièces'
        end as tranche_pieces,
        cast(tranche_prix_m2_ordre as integer) as tranche_prix_m2_ordre,
        -- Libellé au format français : espace fine insécable comme séparateur de milliers.
        case
            when tranche_prix_m2_ordre = 8000
                then replace(format('{:,}', 8000), ',', chr(8239)) || ' €/m² et plus'
            when tranche_prix_m2_ordre is not null
                then
                    replace(format('{:,}', cast(tranche_prix_m2_ordre as integer)), ',', chr(8239))
                    || ' à '
                    || replace(
                        format('{:,}', cast(tranche_prix_m2_ordre as integer) + 249), ',', chr(8239)
                    )
                    || ' €/m²'
        end as tranche_prix_m2
    from tranches
)

select * from final
