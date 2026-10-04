{#
    Par défaut, dbt préfixe les schémas personnalisés par le schéma cible (main_staging, main_marts).
    Cette surcharge utilise le nom de schéma tel quel : staging, intermediate, marts.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
