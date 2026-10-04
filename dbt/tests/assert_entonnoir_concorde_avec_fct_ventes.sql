-- L'entonnoir de la page Méthodologie doit concorder avec la table de faits : les ventes de
-- logement (étape 3) sont toutes dans fct_ventes, et la population prix (étape 6) correspond
-- aux ventes marquées est_population_prix. Le test renvoie les étapes en écart.

with

entonnoir as (
    select
        etape_ordre,
        nb_mutations
    from {{ ref('mart_entonnoir_population') }}
),

faits as (
    select
        3 as etape_ordre,
        count(*) as nb_mutations
    from {{ ref('fct_ventes') }}

    union all

    select
        6 as etape_ordre,
        count(*) as nb_mutations
    from {{ ref('fct_ventes') }}
    where est_population_prix
)

select
    faits.etape_ordre,
    entonnoir.nb_mutations as nb_entonnoir,
    faits.nb_mutations as nb_fct_ventes
from faits
left join entonnoir
    on faits.etape_ordre = entonnoir.etape_ordre
where entonnoir.nb_mutations is distinct from faits.nb_mutations
