-- Regroupement des lignes DVF au grain mutation (règle R1 du dictionnaire des KPI).
-- Grain : une mutation (acte notarié), toutes natures confondues.
-- La composition de chaque mutation (logements, dépendances, locaux d'activité) est comptée
-- ici ; le classement en populations d'analyse est fait dans int_ventes_logement.

with

lignes as (
    select
        dvf.*,
        -- Les codes d'anciennes communes (fusionnées depuis le géocodage) sont ramenés
        -- à la commune actuelle.
        coalesce(passage.code_commune_insee, dvf.code_commune_insee) as code_commune_actuelle
    from {{ ref('stg_dvf') }} as dvf
    left join {{ ref('communes_passage') }} as passage
        on dvf.code_commune_insee = passage.code_commune_ancienne
),

lignes_par_commune as (
    select
        id_mutation,
        code_commune_actuelle,
        count(*) filter (where type_local in ('Maison', 'Appartement')) as nb_logements,
        count(*) as nb_lignes
    from lignes
    group by id_mutation, code_commune_actuelle
),

-- Une mutation peut porter sur des parcelles de plusieurs communes. On retient la commune
-- qui porte le plus de logements, à défaut le plus de lignes, puis le plus petit code INSEE.
commune_principale as (
    select
        id_mutation,
        code_commune_actuelle as code_commune_insee
    from lignes_par_commune
    qualify row_number() over (
        partition by id_mutation
        order by nb_logements desc, nb_lignes desc, code_commune_actuelle asc
    ) = 1
),

-- Une parcelle est répétée sur chaque ligne de local qu'elle porte : sa surface n'est
-- comptée qu'une fois par subdivision fiscale (nature de culture).
parcelles as (
    select distinct
        id_mutation,
        id_parcelle,
        code_nature_culture,
        code_nature_culture_speciale,
        surface_terrain_m2
    from lignes
    where surface_terrain_m2 is not null
),

terrain as (
    select
        id_mutation,
        sum(surface_terrain_m2) as surface_terrain_m2
    from parcelles
    group by id_mutation
),

composition as (
    select
        id_mutation,
        min(date_mutation) as date_mutation,
        case
            when count(distinct nature_mutation) = 1 then min(nature_mutation)
            else 'Mixte'
        end as nature_mutation,
        -- Valeur répétée à l'identique sur chaque ligne (vérifié par un test) : prise une fois.
        min(valeur_fonciere) as valeur_fonciere,
        count(*) as nb_lignes,
        count(distinct numero_disposition) as nb_dispositions,
        count(distinct id_parcelle) as nb_parcelles,
        -- Les lignes strictement identiques comptent comme des locaux distincts (règle R4).
        count(*) filter (where type_local = 'Maison') as nb_maisons,
        count(*) filter (where type_local = 'Appartement') as nb_appartements,
        count(*) filter (where type_local = 'Dépendance') as nb_dependances,
        count(*) filter (
            where type_local = 'Local industriel. commercial ou assimilé'
        ) as nb_locaux_activite,
        sum(surface_bati_m2) filter (
            where type_local in ('Maison', 'Appartement')
        ) as surface_bati_logements_m2,
        sum(nombre_pieces) filter (
            where type_local in ('Maison', 'Appartement')
        ) as nb_pieces_logements
    from lignes
    group by id_mutation
),

final as (
    select
        composition.id_mutation,
        composition.date_mutation,
        composition.nature_mutation,
        commune_principale.code_commune_insee,
        communes.code_departement,
        composition.valeur_fonciere,
        composition.nb_lignes,
        composition.nb_dispositions,
        composition.nb_parcelles,
        composition.nb_maisons,
        composition.nb_appartements,
        composition.nb_dependances,
        composition.nb_locaux_activite,
        composition.surface_bati_logements_m2,
        composition.nb_pieces_logements,
        terrain.surface_terrain_m2
    from composition
    inner join commune_principale
        on composition.id_mutation = commune_principale.id_mutation
    left join {{ ref('communes_bretagne') }} as communes
        on commune_principale.code_commune_insee = communes.code_commune_insee
    left join terrain
        on composition.id_mutation = terrain.id_mutation
)

select * from final
