import config
import requests


def test_get_articles():
    response = requests.get(
        url=f"{config.API_URL}/data/articles", params={"category": ["sport", "health"]}
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


def test_get_articles_section(article):
    articles = [article(section="fake_section") for _ in range(3)]

    response = requests.get(
        url=f"{config.API_URL}/data/articles", params={"sections": ["fake_section"]}
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert len(data) == len(articles)
    for i in data:
        assert i["section"] == "fake_section"


def test_update_article(article):

    my_article = article()

    object_id = str(my_article["object_id"])
    category = my_article["source"]

    new_data = {"author": "Paul"}

    response = requests.put(
        url=f"{config.API_URL}/data/articles/{category}/{object_id}", json=new_data
    )

    assert response.status_code == 200, response.content

    data = response.json()

    old_events = my_article.pop("events")
    new_events = data.pop("events")

    assert data == {**my_article, **new_data}
    assert len(old_events) == len(new_events) - 1


def test_auto_anonymize(article):
    category = "sport"
    my_article = article()

    my_article.pop("auto_anonymized_aliases")
    my_article.pop("automatic_anonymized_text")

    object_id = my_article["object_id"]

    response = requests.put(
        url=f"{config.API_URL}/data/articles/{category}/{object_id}/auto"
    )

    assert response.status_code == 200, response.content

    data = response.json()

    auto_anonymized_text = data.pop("automatic_anonymized_text")
    auto_anonymized_aliases = data.pop("auto_anonymized_aliases")
    new_events = data.pop("events")

    old_events = my_article.pop("events")

    assert data == my_article

    assert auto_anonymized_text == config.ANONYMIZED_TEXT
    assert len(new_events) == len(old_events) + 1

    assert auto_anonymized_aliases == config.FORMATTED_ALIASES
