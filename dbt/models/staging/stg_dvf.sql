-- Staging des DVF géolocalisées : renommage et typage explicite, aucune jointure ni filtre.
-- Grain : une ligne source (un local ou une parcelle d'une disposition d'une mutation).
-- Les casts sont stricts (cast, pas try_cast) : une valeur inattendue dans une nouvelle
-- livraison fait échouer le build au lieu de devenir silencieusement null.

-- Exception à la convention « staging en view » : ce modèle est la frontière avec les CSV.
-- En table, les fichiers ne sont lus qu'une fois par build (et non à chaque lecture en aval),
-- et la base reste interrogeable depuis n'importe quel dossier : une vue conserverait le
-- chemin relatif des CSV, résolu depuis le dossier courant de celui qui l'interroge.
{{ config(materialized='table') }}

with

source as (
    select * from {{ source('dvf', 'geo_dvf') }}
),

renamed as (
    select
        -- Mutation
        id_mutation,
        cast(date_mutation as date) as date_mutation,
        cast(numero_disposition as integer) as numero_disposition,
        nature_mutation,
        cast(valeur_fonciere as decimal(15, 2)) as valeur_fonciere,

        -- Adresse
        cast(adresse_numero as integer) as adresse_numero,
        adresse_suffixe,
        adresse_nom_voie,
        adresse_code_voie,
        code_postal,

        -- Géographie administrative (codes conservés en texte : zéros et lettres significatifs)
        code_commune as code_commune_insee,
        nom_commune,
        code_departement,
        ancien_code_commune as ancien_code_commune_insee,
        ancien_nom_commune,

        -- Parcelle cadastrale
        id_parcelle,
        ancien_id_parcelle,
        numero_volume,

        -- Lots de copropriété (5 premiers lots seulement dans la source)
        lot1_numero,
        cast(lot1_surface_carrez as double) as lot1_surface_carrez_m2,
        lot2_numero,
        cast(lot2_surface_carrez as double) as lot2_surface_carrez_m2,
        lot3_numero,
        cast(lot3_surface_carrez as double) as lot3_surface_carrez_m2,
        lot4_numero,
        cast(lot4_surface_carrez as double) as lot4_surface_carrez_m2,
        lot5_numero,
        cast(lot5_surface_carrez as double) as lot5_surface_carrez_m2,
        cast(nombre_lots as integer) as nombre_lots,

        -- Local
        cast(code_type_local as integer) as code_type_local,
        type_local,
        cast(surface_reelle_bati as integer) as surface_bati_m2,
        cast(nombre_pieces_principales as integer) as nombre_pieces,

        -- Terrain
        code_nature_culture,
        nature_culture,
        code_nature_culture_speciale,
        nature_culture_speciale,
        cast(surface_terrain as integer) as surface_terrain_m2,

        -- Géolocalisation (WGS 84)
        cast(longitude as double) as longitude,
        cast(latitude as double) as latitude

    from source
)

select * from renamed
