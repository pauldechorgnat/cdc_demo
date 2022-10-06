# CDC Demo

Ce repo est un petit exercice qui consiste à créer un modèle d'anonymisation (très faible), à l'exposer via une API FastAPI.

## Tâches

- [x] Trouver un jeu de données contenant des articles avec des noms propres
- [x] Créer un modèle d'anonymisation en utilisant un modèle de NER
- [x] Créer une API qui permet d'exposer le modèle
- [x] Mettre une base de données MongoDB (dockerisée) pour exposer les données
- [x] Créer un modèle de données cohérent (cf [ce fichier](/data_model/README.md))
- [x] Créer un fichier `docker-compose.yml` pour lancer le service
- [ ] Créer les Github Actions de test + lint
- [ ] Trouver un support de déploiement (Azure, AWS ?)
- [ ] Créer les Github Actions de déploiement
- [ ] Gérer la sécurité de l'application
- [ ] Gérer les environnements de dev et de prod

## Source de données

Ma source de données est un ensemble d'articles du média américain [CNN](https://www.kaggle.com/datasets/hadasu92/cnn-articles-after-basic-cleaning?resource=download).

## Comment utiliser ce repo

Pour télécharger le contenu du repo, il faut tout d'abord le clôner:

```sh
git clone https://github.com/pauldechorgnat/cdc_demo.git
cd cdc_demo
```

_A partir de maintenant, toutes les commandes proposées sont lancées depuis la racine du repo._

Une fois téléchargé, on va créer deux environnements virtuels `venv` et `venv-dev`. Le premier est l'environnement de production alors que le second est l'environnement de développement. On y retrouve notamment les librairies de test et de linting (ainsi que `pre-commit`).

```sh
python3 -m venv venv
python3 -m venv venv-dev
```

Les fichiers `requirements` sont respectivement `requirements.txt` et `requirements-dev.txt`.

```sh
# dans un premier terminal
source venv/bin/activate
pip3 install -r requirements.txt

# dans un deuxième terminal
source venv-dev/bin/activate
pip3 install -r requirements-dev.txt
```

L'environnement `venv` ne devrait servir qu'à faire tourner l'API. `venv-dev` est utilisé pour tout le reste.

### Lancement de l'API

Pour lancer l'API, on va utiliser l'environnement `venv`:

```sh
source venv/bin/activate
```

Pour fonctionner, l'API a besoin d'une base MongoDB disponible sur le port 27017 de la machine. J'utilise Docker pour instancier une telle base:

```sh
docker container run --name my_mongo -d --rm -p 27017:27017 -v `pwd`/../mongo_docker/data:/data/db -p 27017:27017 mongo:latest
```

Une fois le container lancé, on peut lancer l'API:

```sh
python3 -m uvicorn api.main:api --reload
```

L'API est alors disponible sur le port `8000` de la [machine](http://localhost:8000). L'API étant construite avec FastAPI, la documentation est disponible à l'adresse [http://localhost:8000/docs](http://localhost:8000/docs).

### Développement

Pour développer l'API, il nous faut utiliser `pre-commit`. Pour l'installer, il faut exécuter la commande suivante:

```sh
source venv-dev/bin/activate
pre-commit install
```

Le [fichier de configuration](/.pre-commit-config.yaml) de `pre-commit` est déja présent dans le repo.

### Lancement des tests

Pour lancer les tests, on pourra utiliser l'environnement `venv-dev` et exécuter la commande suivante:

```sh
source venv-dev/bin/activate
python3 -m pytest tests

# ou pour lancer un seul ficher de test:
python3 -m pytest tests/test_model.py
```

### Docker

On peut facilement créer une image Docker contenant notre API en utilisant le fichier [build_api_image](/api_dockerl/build_api_image.sh):

```sh
sh api_docker/build_api_image.sh
```

Par défaut cette image s'appelle `pauldechorgnat/article_api`.

Pour lancer l'API via docker, il suffit de faire:

```sh
docker container run -p 8000:8000 pauldechorgnat/article_api:latest
```

### Docker-Compose

J'ai aussi créé un [fichier](docker-compose/docker-compose.yaml) `docker-compose.yaml` pour lancer les deux containers en même temps. Une fois l'image `pauldechorgnat/article_api` créée, on peut simplement lancer l'ensemble avec:

```sh
 docker-compose -f ./docker-compose/docker-compose.yaml up
```
