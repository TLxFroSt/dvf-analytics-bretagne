-- mart_metadonnees alimente des cartes et des textes du dashboard : elle doit contenir
-- exactement une ligne. Le test échoue sinon.

select count(*) as nb_lignes
from {{ ref('mart_metadonnees') }}
having count(*) != 1
