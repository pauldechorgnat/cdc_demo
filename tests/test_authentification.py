from itertools import product

import config
import pytest
import requests
from pymongo import MongoClient

from api.config import ADMIN_DB
from api.config import ADMIN_ROLE_COLLECTION


@pytest.mark.parametrize(
    "role, route",
    list(product(["public", "contributor", "corrector", "admin"], config.ROUTES)),
)
def test_public_access(role, route, user, article):

    my_article = article()

    my_user = user(roles=[role])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}

    replacements = {
        "username": my_user["username"],
        "article_id": my_article["object_id"],
        "alias": "PER",
        "category": "sport",
    }

    role_collection = MongoClient()[ADMIN_DB][ADMIN_ROLE_COLLECTION]
    permissions = role_collection.find_one({"role": role})["permissions"]

    path = route["route"].format(**replacements)
    body = {} if route.get("body") else None
    response = requests.request(
        method=route["method"],
        url=f"{config.API_URL}{path}",
        headers=HEADERS,
        json=body,
    )
    if route["name"] in permissions:
        assert response.status_code in [200, 404, 422, 401], response.content
    else:
        assert response.status_code == 403, response.content
