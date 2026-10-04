-- Entonnoir des règles de population (dictionnaire des KPI, R1 à R5), pour la page
-- Méthodologie : nombre de mutations restant après chaque règle.
-- Grain : une étape de l'entonnoir.

with

mutations as (
    select * from {{ ref('int_mutations') }}
),

ventes_logement as (
    select * from {{ ref('int_ventes_logement') }}
),

etapes as (
    select
        1 as etape_ordre,
        'R1' as regle,
        'Mutations publiées' as etape_libelle,
        count(*) as nb_mutations
    from mutations

    union all

    select
        2 as etape_ordre,
        'R2' as regle,
        'Ventes' as etape_libelle,
        count(*) as nb_mutations
    from mutations
    where nature_mutation = 'Vente'

    union all

    select
        3 as etape_ordre,
        'R3' as regle,
        'Ventes de logement' as etape_libelle,
        count(*) as nb_mutations
    from ventes_logement

    union all

    select
        4 as etape_ordre,
        'R4' as regle,
        'Ventes d''un seul logement' as etape_libelle,
        count(*) as nb_mutations
    from ventes_logement
    where nb_logements = 1

    union all

    select
        5 as etape_ordre,
        'R4' as regle,
        'Valeur et surface renseignées' as etape_libelle,
        count(*) as nb_mutations
    from ventes_logement
    where motif_exclusion_prix is null or motif_exclusion_prix = 'prix_m2_aberrant'

    union all

    select
        6 as etape_ordre,
        'R5' as regle,
        'Population prix (hors valeurs aberrantes)' as etape_libelle,
        count(*) as nb_mutations
    from ventes_logement
    where est_population_prix
),

final as (
    select
        etape_ordre,
        regle,
        etape_libelle,
        nb_mutations,
        lag(nb_mutations) over (order by etape_ordre) - nb_mutations as nb_exclues,
        nb_mutations / first_value(nb_mutations) over (order by etape_ordre) as part_des_mutations
    from etapes
)

select * from final
