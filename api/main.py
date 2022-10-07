import datetime
from typing import List

import bson
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from flair.models import SequenceTagger
from pymongo import MongoClient

from .aliasing_model import get_entities
from .aliasing_model import replace_text
from .authentication import check_user
from .authentication import check_valid_password
from .authentication import decodeJWT
from .authentication import JWTBearer
from .authentication import signJWT
from .authentication import User
from .authentication import UserLogin
from .config import ADMIN_DB
from .config import ADMIN_USER_COLLECTION
from .config import ANONYMIZED_ALIASES
from .config import ANONYMIZED_ALIASES_DESCRIPTION
from .config import ENVIRONMENT
from .config import MONGO_URL
from .models import Alias
from .models import AliasDescription
from .models import AnonymizedTextWithAliases
from .models import Article
from .models import ManualAnonymizedData
from .models import NewArticle
from .models import Text
from .models import UpdateArticleData
from .utils import format_aliases
from .utils import format_object_id

# from .config import ADMIN_ROLE_COLLECTION

tagger = SequenceTagger.load("ner")

VERSION = "0.0.1"

client = MongoClient(MONGO_URL)
article_db = client["articles"]
admin_db = client[ADMIN_DB]


CATEGORIES = article_db.list_collection_names()


api = FastAPI(title="Anonymized text", version=VERSION)

default_responses = {200: {"description": "OK"}}


@api.get(
    "/",
    tags=["Default"],
    responses=default_responses,
)
def get_index():
    """Returns a general message"""
    return {
        "message": "Documentation is at /docs",
        "version": VERSION,
        "environment": ENVIRONMENT,
    }


async def get_current_user(token: str = Depends(JWTBearer())):
    username = decodeJWT(token)["user_id"]
    user_data = admin_db[ADMIN_USER_COLLECTION].find_one(
        filter={"username": username}, projection={"password": 0}
    )

    if user_data:
        return User(**user_data)
    raise HTTPException(401, detail="Invalid Token.")


@api.get("/users/me", tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@api.post(
    "/users/signup",
    tags=["Users"],
    responses={
        200: {"description": "OK"},
        409: {"decription": "Username already taken."},
        401: {"description": "Password is not valid."},
    },
)
def create_user(user: UserLogin):
    new_user = user.dict()
    new_user["roles"] = ["public"]

    previous_user = admin_db[ADMIN_USER_COLLECTION].find_one(
        filter={"username": user.username}
    )
    if previous_user:
        raise HTTPException(409, detail=f"Username '{user.username}' already taken.")
    if not check_valid_password(user.password):
        raise HTTPException(401, detail="Password is not valid.")

    admin_db[ADMIN_USER_COLLECTION].insert_one(new_user)

    return signJWT(user.username)


@api.post(
    "/users/signin",
    tags=["Users"],
    responses={
        200: {"description": "OK"},
        401: {"description": "Username or credentials are not valid."},
    },
)
def user_login(user: UserLogin):
    if check_user(user, collection=admin_db[ADMIN_USER_COLLECTION]):
        return signJWT(user.username)
    raise HTTPException(401, detail="Username or credentials are not valid.")


@api.get(
    "/aliases",
    tags=["Model"],
    responses={200: {"description": "OK", "model": List[AliasDescription]}},
)
def get_aliases():
    """Returns the list of aliases that are anonymized and their description"""
    return [
        AliasDescription(text=k, alias=v)
        for k, v in ANONYMIZED_ALIASES_DESCRIPTION.items()
    ]


@api.get(
    "/aliases/{alias}",
    tags=["Model"],
    responses={
        200: {"description": "OK", "model": AliasDescription},
        404: {"description": "Not found"},
    },
)
def get_alias(alias: str):
    if alias not in ANONYMIZED_ALIASES_DESCRIPTION:
        raise HTTPException(404, detail=f"Alias ID '{alias}' not found")
    return AliasDescription(
        alias=alias, description=ANONYMIZED_ALIASES_DESCRIPTION[alias]
    )


@api.post(
    "/model/aliases",
    tags=["Model"],
    responses={200: {"description": "OK", "model": List[Alias]}},
)
def post_get_named_entities(text: Text):
    entities = get_entities(
        tagger=tagger, raw_text=text.text, aliases_to_anonymize=ANONYMIZED_ALIASES
    )
    return [Alias(text=k, alias=v) for k, v in entities.items()]


@api.post(
    "/model/anonymize",
    tags=["Model"],
    responses={200: {"description": "OK", "model": AnonymizedTextWithAliases}},
)
def post_anonymize_text(text: Text):
    raw_text = text.text

    aliases = get_entities(
        tagger=tagger, raw_text=raw_text, aliases_to_anonymize=ANONYMIZED_ALIASES
    )

    new_text = replace_text(raw_text=raw_text, entities=aliases)

    response = AnonymizedTextWithAliases(
        raw_text=raw_text,
        anonymized_text=new_text,
        aliases=[Alias(**a) for a in format_aliases(aliases)],
    )
    return response


@api.get(
    "/data/articles",
    tags=["Data"],
    responses={200: {"description": "OK", "model": List[Article]}},
)
def get_articles(
    category: List[str] = Query(default=None),
    date_start: datetime.datetime = Query(default=None),
    date_end: datetime.datetime = Query(default=None),
    sections: List[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
):

    collections = category if category else CATEGORIES

    mongo_filter = {}

    if sections:
        mongo_filter["section"] = {"$in": sections}

    if date_start:
        if date_end:

            mongo_filter["date_published"] = {"$gt": date_start, "$lt": date_end}
        else:
            mongo_filter["date_published"] = {"$gt": date_start}
    else:
        if date_end:
            mongo_filter["date_published"] = {"$lt": date_end}

    results = []
    for c in collections:
        results.extend(map(format_object_id, article_db[c].find(filter=mongo_filter)))

    results = [Article(**r) for r in results]

    return results


@api.get(
    "/data/articles/{category}/{object_id}",
    tags=["Data"],
    responses={
        200: {"description": "OK", "model": Article},
        404: {"description": "Article or category not found"},
    },
)
def get_article(
    category: str, object_id: str, current_user: User = Depends(get_current_user)
):
    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' not found.")
    try:
        result = article_db[category].find_one(
            {"_id": bson.objectid.ObjectId(object_id)}
        )
    except bson.errors.InvalidId:
        raise HTTPException(422, detail=f"Id '{object_id}' is not valid.")

    if not result:
        raise HTTPException(404, detail=f"Article with id '{object_id}' not found.")
    return Article(**format_object_id(result))


@api.post(
    "/data/articles",
    tags=["Data"],
    responses={200: {"description": "OK", "model": Article}},
)
def post_new_article(
    article: NewArticle, current_user: User = Depends(get_current_user)
):
    category = article.source
    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' does not exist.")
    insertion_date = datetime.datetime.utcnow()
    article_data = article.dict()
    article_data["hash"] = hash(article_data["raw_text"])
    article_data["events"] = [
        {
            "type": "insertion",
            "author": "paul_dechorgnat",  # TODO: change this
            "date": insertion_date,
            "mode": "single",
        }
    ]
    result = article_db[category].insert_one(article_data)
    new_article = article_db[category].find_one(result.inserted_id)

    return Article(**format_object_id(new_article))


@api.post(
    "/data/articles/batch",
    tags=["Data"],
    responses={200: {"description": "OK", "model": List[Article]}},
)
def post_new_articles_batch(
    articles_data: List[NewArticle], current_user: User = Depends(get_current_user)
):
    articles = {}
    insertion_date = datetime.datetime.utcnow()
    for article in articles_data:
        article_data = article.dict()
        category = article.source
        if category not in CATEGORIES:
            raise HTTPException(404, detail=f"Category '{category}' does not exist.")
        article_data = article.dict()
        article_data["hash"] = hash(article_data["raw_text"])
        article_data["events"] = [
            {
                "type": "insertion",
                "author": "paul_dechorgnat",  # TODO: change this
                "date": insertion_date,
                "mode": "batch",
            }
        ]
        articles[category] = articles.get(category, []) + [article_data]

    new_articles = []

    for c in articles:
        r = article_db[c].insert_many(articles[c])
        inserted_ids = r.inserted_ids
        new_articles.extend(article_db[c].find({"_id": {"$in": inserted_ids}}))

    return [Article(**format_object_id(a)) for a in new_articles]


@api.delete(
    "/data/articles/{category}/{object_id}",
    tags=["Data"],
    responses={
        200: {"description": "OK"},
        404: {"description": "Article or category not found"},
    },
)
def delete_article(
    category: str, object_id: str, current_user: User = Depends(get_current_user)
):
    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' not found.")
    result = article_db[category].delete_one(
        filter={"_id": bson.objectid.ObjectId(object_id)}
    )
    if result.deleted_count == 0:
        raise HTTPException(404, detail=f"Object with id '{object_id}' not found.")
    return {"message": "object deleted"}


@api.put(
    "/data/articles/{category}/{object_id}",
    tags=["Data"],
    responses={
        200: {"description": "OK", "model": Article},
        404: {"description": "Article or category not found"},
    },
)
def update_article_data(
    category: str,
    object_id: str,
    new_article: UpdateArticleData,
    current_user: User = Depends(get_current_user),
):

    object_id = bson.objectid.ObjectId(object_id)

    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' not found.")

    old_article_events = article_db[category].find_one(
        filter={"_id": object_id}, projection={"events": 1, "_id": 0}
    )

    if not old_article_events:
        raise HTTPException(404, detail=f"Object with id '{object_id}' not found.")

    new_article_data = {**new_article.dict(exclude_unset=True), **old_article_events}
    new_article_data["events"] += [
        {
            "type": "modification",
            "author": "paul_dechorgnat",  # TODO: change that
            "date": datetime.datetime.utcnow(),
        }
    ]

    from pprint import pprint

    pprint(new_article_data)

    article_db[category].update_one(
        filter={"_id": object_id}, update={"$set": new_article_data}
    )

    final_data = article_db[category].find_one(filter={"_id": object_id})

    return Article(**format_object_id(final_data))


@api.put(
    "/data/articles/{category}/{object_id}/auto",
    tags=["Data"],
    responses={
        200: {"description": "OK", "model": Article},
        404: {"description": "Article or category not found"},
    },
)
def put_auto_anonymized_article(
    object_id: str, category: str, current_user: User = Depends(get_current_user)
):
    """Generates the automatic anonymization of the specified article"""
    object_id = bson.objectid.ObjectId(object_id)

    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' not found.")

    old_article = article_db[category].find_one(
        filter={"_id": object_id}, projection={"raw_text": 1, "events": 1, "_id": 0}
    )

    if not old_article:
        raise HTTPException(404, detail=f"Object with id '{object_id}' not found.")

    aliases = get_entities(tagger=tagger, raw_text=old_article["raw_text"])

    auto_anonymized_text = replace_text(
        raw_text=old_article["raw_text"], entities=aliases
    )

    new_data = {
        **old_article,
        "auto_anonymized_text": auto_anonymized_text,
        "auto_anonymized_aliases": format_aliases(aliases),
    }
    new_data["events"] = old_article["events"] + [
        {
            "type": "auto_anonymization",
            "date": datetime.datetime.utcnow(),
            "author": "paul_dechorgnat",  # TODO: change that
        }
    ]

    article_db[category].update_one(
        filter={"_id": object_id}, update={"$set": new_data}
    )

    result = article_db[category].find_one(filter={"_id": object_id})

    return Article(**format_object_id(result))


@api.put(
    "/data/articles/{category}/{object_id}/manual",
    tags=["Data"],
    responses={
        200: {"description": "OK", "model": Article},
        404: {"description": "Article or category not found"},
    },
)
def put_manual_anonymized_article(
    object_id: str,
    category: str,
    anonymized_data: ManualAnonymizedData,
    current_user: User = Depends(get_current_user),
):
    """Generates the automatic manual of the specified article"""
    object_id = bson.objectid.ObjectId(object_id)

    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' not found.")

    old_article = article_db[category].find_one(
        filter={"_id": object_id}, projection={"events": 1, "_id": 0}
    )

    if not old_article:
        raise HTTPException(404, detail=f"Object with id '{object_id}' not found.")

    new_data = {
        "manual_anonymized_text": anonymized_data.manual_anonymized_text,
        "manual_anonymized_aliases": anonymized_data.dict()[
            "manual_anonymized_aliases"
        ],
    }
    new_data["events"] = old_article["events"] + [
        {
            "type": "manual_anonymization",
            "date": datetime.datetime.utcnow(),
            "author": "paul_dechorgnat",  # TODO: change that
        }
    ]

    article_db[category].update_one(
        filter={"_id": object_id}, update={"$set": new_data}
    )

    result = article_db[category].find_one(filter={"_id": object_id})

    return Article(**format_object_id(result))
