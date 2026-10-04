{#
    Exporte le modèle courant en Parquet pour Power BI : exports/{nom_du_modèle}.parquet.
    Utilisée en post-hook des marts (voir dbt_project.yml).

    Les marts restent des tables DuckDB et l'export est une copie. La matérialisation
    `external` de dbt-duckdb créerait une vue sur le fichier Parquet avec un chemin relatif,
    résolu depuis le dossier courant de celui qui interroge la base (même problème que pour
    stg_dvf). Le chemin est ici rendu absolu à partir du dossier du projet dbt.
#}
{% macro export_parquet() -%}
    {%- set chemin = invocation_args_dict.project_dir ~ '/' ~ var('exports_path') ~ '/'
        ~ this.identifier ~ '.parquet' -%}
    copy (select * from {{ this }}) to '{{ chemin }}' (format parquet, compression zstd)
{%- endmacro %}
