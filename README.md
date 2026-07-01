# AgriStat-BF

AgriStat-BF est un logiciel Python orienté objet destiné à centraliser, traiter et visualiser les statistiques de production céréalière des différentes régions du Burkina Faso.

## Fonctionnalités disponibles

- centralisation de données de production par région, céréale et année ;
- calcul d'indicateurs simples d'aide à la décision ;
- visualisation textuelle rapide des productions régionales.

## Exemple d'utilisation

```python
from agristat_bf import AgriStatBF, ProductionRecord

tool = AgriStatBF()
tool.add_record(ProductionRecord("Boucle du Mouhoun", "Maïs", 1200, 400, 2024))
tool.add_record(ProductionRecord("Hauts-Bassins", "Mil", 900, 300, 2024))

print(tool.total_production_by_region())
print(tool.render_region_production_chart())
```
