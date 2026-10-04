-- Dimension type de bien.
-- Grain : un type de bien (maison, appartement).

with

types_bien as (
    select * from {{ ref('types_bien') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['code_type_bien']) }} as type_bien_key,
        code_type_bien,
        libelle_type_bien,
        libelle_type_bien_pluriel,
        ordre_tri
    from types_bien
)

select * from final
