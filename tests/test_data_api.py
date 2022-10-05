from pymongo import MongoClient
import requests
import config

client = MongoClient()
db = client["articles"]


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
    article1 = article(section="fake_section")
    article2 = article(section="fake_section")
    article3 = article(section="fake_section")
    
    response = requests.get(
        url=f"{config.API_URL}/data/articles", params={"sections": ["fake_section"]}
    )
    
    assert response.status_code == 200, response.content
    
    data = response.json()
    
    assert len(data) == 3
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
