import datetime

import config
import pytest
import requests
from pymongo import MongoClient

from api.authentication import encrypt_password
from api.config import ADMIN_DB
from api.config import ADMIN_USER_COLLECTION
from api.config import ARTICLE_DB


@pytest.fixture
def fake_article_data():
    data = {
        "author": "fake author",
        "date_published": (
            datetime.datetime.utcnow() - datetime.timedelta(days=-7)
        ).isoformat(),
        "section": "fake section",
        "url": "http://fake_url.com",
        "headline": "fake headline",
        "source": "sport",
        "keywords": ["fake", "keywords"],
        "raw_text": config.TEXT,
        "events": [
            {
                "type": "insertion",
                "author": "test",
                "date": datetime.datetime.utcnow(),
                "mode": "single",
            }
        ],
    }

    return data


@pytest.fixture
def article(request, fake_article_data):
    object_created_list = {}

    def create_article(**kwargs):
        data = {**fake_article_data, **kwargs}
        data["hash"] = hash(data["raw_text"])

        article_collection = MongoClient()[ARTICLE_DB][data["source"]]

        result = article_collection.insert_one(data)

        object_created_list[data["source"]] = object_created_list.get(
            data["source"], []
        ) + [result.inserted_id]

        data["object_id"] = str(result.inserted_id)

        return data

    def finalizer():
        for category in object_created_list:
            article_collection = MongoClient()[ARTICLE_DB][category]
            for object_id in object_created_list[category]:
                article_collection.delete_one({"_id": object_id})

    request.addfinalizer(finalizer)

    return create_article


@pytest.fixture
def fake_user_data():
    return {
        "username": "username",
        "password": "ComplexPassword1234!",
        "roles": ["admin"],
    }


@pytest.fixture
def user(request, fake_user_data):
    user_created_list = []
    col = MongoClient()[ADMIN_DB][ADMIN_USER_COLLECTION]

    def create_user(**kwargs):
        data = {**fake_user_data, **kwargs}
        clear_password = data["password"]
        data["password"] = encrypt_password(clear_password)

        col.insert_one(data)

        user_created_list.append(data["username"])
        response = requests.post(
            f"{config.API_URL}/users/signin",
            json={"username": data["username"], "password": clear_password},
        )
        response.raise_for_status()
        data["access_token"] = response.json()["access_token"]

        return data

    def finalizer():
        col.delete_many(filter={"username": {"$in": user_created_list}})

    request.addfinalizer(finalizer)

    return create_user
