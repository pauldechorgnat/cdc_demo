import config
import requests


def test_get_articles(user):
    my_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}

    response = requests.get(
        url=f"{config.API_URL}/data/articles",
        params={"category": ["sport", "health"]},
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content
    data = response.json()

    for i in data:
        assert i["source"] in ["sport", "health"]


# def test_get_articles_wrong_category():
#     response = requests.get(
#         url=f"{config.API_URL}/data/articles",
#         params={"category": ["wrong_category"]}
#     )

#     assert response.status_code == 404, response.content


def test_get_articles_section(article, user):
    my_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}

    articles = [article(section="fake_section") for _ in range(3)]

    response = requests.get(
        url=f"{config.API_URL}/data/articles",
        params={"sections": ["fake_section"]},
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert len(data) == len(articles)
    for i in data:
        assert i["section"] == "fake_section"


def test_update_article(article, user):
    my_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}

    my_article = article()

    object_id = str(my_article["object_id"])
    category = my_article["source"]

    new_data = {"author": "Paul"}

    response = requests.put(
        url=f"{config.API_URL}/data/articles/{category}/{object_id}",
        json=new_data,
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content

    data = response.json()

    old_events = my_article.pop("events")
    new_events = data.pop("events")

    assert data["author"] == "Paul"
    assert len(old_events) == len(new_events) - 1


def test_auto_anonymize(article, user):
    my_user = user(roles=["contributor"])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}
    category = "sport"
    my_article = article()

    object_id = my_article["object_id"]

    response = requests.put(
        url=f"{config.API_URL}/data/articles/{category}/{object_id}/auto",
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content

    data = response.json()

    auto_anonymized_text = data.pop("auto_anonymized_text")
    auto_anonymized_aliases = data.pop("auto_anonymized_aliases")
    new_events = data.pop("events")

    old_events = my_article.pop("events")

    assert auto_anonymized_text == config.ANONYMIZED_TEXT
    assert len(new_events) == len(old_events) + 1

    assert auto_anonymized_aliases == config.FORMATTED_ALIASES


def test_manual_anonymize(article, user):
    my_user = user(roles=["corrector"])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}
    category = "sport"
    my_article = article()

    object_id = my_article["object_id"]

    response = requests.put(
        url=f"{config.API_URL}/data/articles/{category}/{object_id}/manual",
        json={
            "manual_anonymized_aliases": config.FORMATTED_ALIASES,
            "manual_anonymized_text": config.ANONYMIZED_TEXT,
        },
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content

    data = response.json()

    manual_anonymized_text = data.pop("manual_anonymized_text")
    manual_anonymized_aliases = data.pop("manual_anonymized_aliases")
    new_events = data.pop("events")

    old_events = my_article.pop("events")

    assert manual_anonymized_text == config.ANONYMIZED_TEXT
    assert len(new_events) == len(old_events) + 1

    assert manual_anonymized_aliases == config.FORMATTED_ALIASES


def test_public_user_masks(user, article):
    my_user = user(username=config.generate_fake_username(), roles=["public"])
    my_other_user = user(username=config.generate_fake_username(), roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {my_user['access_token']}"}

    my_article = article()
    article_id = my_article["object_id"]
    category = my_article["source"]

    response = requests.get(
        url=f"{config.API_URL}/data/articles/{category}/{article_id}", headers=HEADERS
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["raw_text"] == "***"
    assert data["auto_anonymized_text"] == "***"
    for a in data.get("manual_anonymized_aliases", []):
        assert a["text"] == "***"
    for a in data.get("auto_anonymized_aliases", []):
        assert a["text"] == "***"

    HEADERS = {"Authorization": f"Bearer {my_other_user['access_token']}"}
    response = requests.get(
        url=f"{config.API_URL}/data/articles/{category}/{article_id}", headers=HEADERS
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["raw_text"] == my_article["raw_text"], my_other_user
