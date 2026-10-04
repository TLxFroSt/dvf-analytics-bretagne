-- Ventes de logement (règle R3) et classement dans la population prix (règles R4 et R5).
-- Grain : une vente de logement, soit une mutation de nature « Vente » comprenant au moins
-- une maison ou un appartement d'un seul type, et aucun local d'activité.
-- Chaque vente hors population prix porte le motif de son exclusion.

with

ventes_logement as (
    select
        id_mutation,
        date_mutation,
        code_commune_insee,
        code_departement,
        valeur_fonciere,
        nb_dependances,
        surface_bati_logements_m2,
        nb_pieces_logements,
        surface_terrain_m2,
        year(date_mutation) as annee,
        case when nb_maisons > 0 then 1 else 2 end as code_type_bien,
        nb_maisons + nb_appartements as nb_logements
    from {{ ref('int_mutations') }}
    where
        nature_mutation = 'Vente'
        and nb_locaux_activite = 0
        -- au moins un logement, et un seul type (que des maisons ou que des appartements)
        and (nb_maisons > 0) != (nb_appartements > 0)
),

-- Surface, pièces et prix au m² ne décrivent un bien que pour une vente d'un seul logement.
caracteristiques as (
    select
        *,
        case when nb_logements = 1 then surface_bati_logements_m2 end as surface_bati_m2,
        case when nb_logements = 1 then nb_pieces_logements end as nb_pieces,
        case
            when
                nb_logements = 1
                and valeur_fonciere is not null
                and surface_bati_logements_m2 >= {{ var('surface_bati_min_m2') }}
                then cast(valeur_fonciere as double) / surface_bati_logements_m2
        end as prix_m2
    from ventes_logement
),

-- Bornes d'exclusion des valeurs aberrantes, par type de bien × département × année.
bornes_prix_m2 as (
    select
        code_type_bien,
        code_departement,
        annee,
        quantile_cont(prix_m2, {{ var('prix_m2_percentile_bas') }}) as prix_m2_borne_basse,
        quantile_cont(prix_m2, {{ var('prix_m2_percentile_haut') }}) as prix_m2_borne_haute
    from caracteristiques
    where prix_m2 is not null
    group by code_type_bien, code_departement, annee
),

classees as (
    select
        caracteristiques.*,
        bornes_prix_m2.prix_m2_borne_basse,
        bornes_prix_m2.prix_m2_borne_haute,
        case
            when caracteristiques.nb_logements > 1 then 'plusieurs_logements'
            when caracteristiques.valeur_fonciere is null then 'valeur_absente'
            when
                caracteristiques.surface_bati_m2 is null
                or caracteristiques.surface_bati_m2 < {{ var('surface_bati_min_m2') }}
                then 'surface_insuffisante'
            when
                caracteristiques.prix_m2 not between bornes_prix_m2.prix_m2_borne_basse
                and bornes_prix_m2.prix_m2_borne_haute
                then 'prix_m2_aberrant'
        end as motif_exclusion_prix
    from caracteristiques
    left join bornes_prix_m2
        on
            caracteristiques.code_type_bien = bornes_prix_m2.code_type_bien
            and caracteristiques.code_departement = bornes_prix_m2.code_departement
            and caracteristiques.annee = bornes_prix_m2.annee
),

final as (
    select
        id_mutation,
        date_mutation,
        annee,
        code_commune_insee,
        code_departement,
        code_type_bien,
        valeur_fonciere,
        nb_logements,
        nb_dependances,
        surface_bati_m2,
        nb_pieces,
        surface_terrain_m2,
        prix_m2,
        prix_m2_borne_basse,
        prix_m2_borne_haute,
        motif_exclusion_prix,
        motif_exclusion_prix is null as est_population_prix
    from classees
)

select * from final
