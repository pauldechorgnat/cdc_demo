# Data Model

## Réflexions autour du Data Model

Le Data Model devrait inclure:

- les métadonnées des articles
- les différentes version de l'article

Les articles sont disponibles en 3 versions:

1. Une version brute non anonymisée
2. Une version anonymisée automatiquement
3. Une version relue à la main et éventuellement modifiée

Il faudra contrôler les accès aux données en fonction de ces versions.

Pour simuler les différentes juridictions, on va créer une collection par `category`.

Il serait aussi intéressant de conserver le nom des auteurs des modifications sur les différents articles et de trouver une façon de les identifier de manière unique au delà du simple `_id`.
