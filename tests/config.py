import random
from string import printable

API_URL = "http://localhost:8000"


TEXT = "The UN is said to meet in New-York according to Donald Trump."

ALIASES = {"UN": "ORG_0", "New-York": "LOC_0", "Donald Trump": "PER_0"}

ANONYMIZED_TEXT = "The ORG_0 is said to meet in LOC_0 according to PER_0."

FORMATTED_ALIASES = [
    {"text": k, "alias": v, "alias_type": v.split("_")[0]} for k, v in ALIASES.items()
]

FAKE_USERNAME = "ian_itor"
FAKE_USERNAME_ALTER = "hello_world"
FAKE_VALID_PASSWORD = "ComplexPassword1234!"
FAKE_NOT_VALID_PASSWORD = "weak"


ROUTES = [
    # {
    #     "route": "/",
    #     "method": "GET",
    #     "name": "index"
    # },
    # {
    #     "route": "",
    #     "method": "",
    #     "name": ""
    # },
    # {
    #     "route": "/users/me",
    #     "method": "GET",
    #     "name": "users.me"
    # },
    # {
    #     "route": "/aliases",
    #     "method": "GET",
    #     "name": "alias.get"
    # },
    # {
    #     "route": "/model/aliases",
    #     "method": "POST",
    #     "name": "public.model.alias"
    # },
    # {
    #     "route": "/model/anonymize",
    #     "method": "POST",
    #     "name": "public.model.anonymize"
    # },
    {"route": "/data/articles", "method": "GET", "name": "articles.read.multiple"},
    {
        "route": "/data/articles/{category}/{article_id}",
        "method": "GET",
        "name": "articles.read",
    },
    {
        "route": "/data/articles",
        "method": "POST",
        "body": True,
        "name": "articles.create",
    },
    {
        "route": "/data/articles/{category}/{article_id}",
        "method": "PUT",
        "body": True,
        "name": "articles.update",
    },
    {
        "route": "/data/articles/{category}/{article_id}",
        "method": "DELETE",
        "name": "articles.delete",
    },
    {
        "route": "/data/articles/{category}/{article_id}/auto",
        "method": "PUT",
        "name": "articles.auto_alias",
    },
    {
        "route": "/data/articles/{category}/{article_id}/manual",
        "method": "PUT",
        "body": True,
        "name": "articles.manual_alias",
    },
    {
        "route": "/data/articles",
        "method": "POST",
        "body": True,
        "name": "articles.create.multiple",
    },
    {"route": "/users", "method": "GET", "name": "users.read.multiple"},
    {"route": "/users/{username}", "method": "GET", "name": "users.read"},
    {"route": "/users", "method": "POST", "body": True, "name": "users.create"},
    {
        "route": "/users/{username}",
        "method": "PUT",
        "body": True,
        "name": "users.update",
    },
    {"route": "/users/{username}", "method": "DELETE", "name": "users.delete"},
]


def generate_fake_username():
    username = "".join(random.sample(population=printable[:63], k=50))
    return username
