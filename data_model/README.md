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

## Proposition de Data Model

On va avoir une collection par `category`.

Un document classique devrait ressembler à:

```python
{
    "author": "Analysis by Stephen Collinson, CNN",
    "date_published": datetime.datetime(2021, 12, 1, 14, 32, 33),
    "section": "golf",
    "url": "https://www.cnn.com/2021/12/01/golf/tiger-woods-end-of-era-meanwhile-spt-intl/index.html",
    "headline": "Tiger Woods: Is this the end of his era? - CNN",
    "keywords": ["golf", "tiger", "woods", "end", "era", "cnn"],
    "raw_text": "...",
    "automatic_anonymized_text": "...",
    "anonymized_text": "...",
    "events": {
        "insertion": {
            "date": datetime.datetime(2021, 12, 1, 14, 32, 33),
            "author": "paul_dechorgnat",
            "mode": "single" # or batch
            },
        "automatic_anonymization": {
            "date": datetime.datetime(2021, 12, 1, 14, 32, 33),
            "author": "pseudo_model:0.0.1",
        },
        "manual_anonymization": {
            "date": datetime.datetime(2021, 12, 1, 14, 32, 33),
            "author": "12343534",
        }
    },
    "auto_anonymized_tags": [
        {"text": "Donald Trump", "tag": "PER_0"},
        {}
    ],
    "manual_anonymized_tags" : [
        {"text": "Donald Trump", "tag": "PER_0"},
        {}
    ],
    "hash": 533794461304174741,
    "_id": ObjectId("633c6473b9daeb8a90169dcb")
}
```

On considérera pour l'exercice que les documents sont fournis au format `JSON` avec les attributs suivants:

- `author`
- `date_published`
- `category`
- `section`
- `url`
- `headline`
- `description`
- `keywords`
- `second_headline`
- `article_text`

Les autres champs seront générés lors de l'insertion ou lors de la correction manuelle. Le `hash` sera notamment le hash du text original de l'article.

## API

L'API doit donc avoir les points de terminaison suivants:

- [x] `GET /data/articles`: renvoie les articles. On ajoutera des possiblité d'ajouter des filtres.
- [x] `GET/data/articles/_id`: renvoie un article. On ajoutera des possiblité d'ajouter des filtres.
- [x] `POST /data/articles`: permet l'insertion d'un article.
- [x] `POST /data/articles/batch`: permet l'insertion massive d'articles (un seul fichier json).
- [x] `PUT /data/articles/_id`: permet la modification d'un article.
- [ ] `PUT /data/article/_id/auto`: déclenche la pseudonymisation automatique de l'article.
- [ ] `PUT /data/article/_id/manual`: permet la pseudonymisation de l'article manuelle.
- [x] `DELETE /data/articles/_id`: permet la suppression d'un article.
