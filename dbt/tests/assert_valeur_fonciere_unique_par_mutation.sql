-- Règle R1 : la valeur foncière est répétée à l'identique sur chaque ligne d'une mutation,
-- ce qui permet de la prendre une seule fois au grain mutation (int_mutations).
-- Le test échoue si une mutation porte plusieurs valeurs différentes.

select
    id_mutation,
    count(distinct valeur_fonciere) as nb_valeurs
from {{ ref('stg_dvf') }}
group by id_mutation
having count(distinct valeur_fonciere) > 1
