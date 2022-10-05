import os

ANONYMIZED_TAGS_DESCRIPTION = {
    "LOC": "Location, place, town, country, ...",
    "PER": "Person",
    "ORG": "Organization, Company, ...",
}

ANONYMIZED_TAGS = list(ANONYMIZED_TAGS_DESCRIPTION.keys())

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
# ENVIRONMENT should be one of dev, prod or docker-compose

MONGO_URL = "mongodb://localhost:27017"

if ENVIRONMENT == "docker-compose":
    MONGO_URL = "mongodb://my_mongo:27017"
