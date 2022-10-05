# CDC Demo

Ce repo est un petit exercice qui consiste à créer un modèle d'anonymisation (très faible), à l'exposer via une API FastAPI.

## Tâches

- [x] Trouver un jeu de données contenant des articles avec des noms propres
- [x] Créer un modèle d'anonymisation en utilisant un modèle de NER
- [x] Créer une API qui permet d'exposer le modèle
- [ ] Mettre une base de données MongoDB (dockerisée) pour exposer les données
- [ ] Créer un modèle de données cohérent
- [ ] Créer un fichier `docker-compose.yml` pour lancer le service
- [ ] Créer les Github Actions de test + lint
- [ ] Trouver un support de déploiement (Azure, AWS ?)
- [ ] Créer les Github Actions de déploiement
- [ ] Gérer la sécurité de l'application
- [ ] Gérer les environnements de dev et de prod

## Source de données

Ma source de données est un ensemble d'articles du média américain [CNN](https://www.kaggle.com/datasets/hadasu92/cnn-articles-after-basic-cleaning?resource=download).
