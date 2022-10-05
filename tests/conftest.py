import pytest
import requests
import datetime
import config


@pytest.fixture
def fake_article_data():
    data = {
        "author": "fake author",
        "date_published": (datetime.datetime.utcnow() - datetime.timedelta(days=-7)).isoformat(),
        "section": "fake section",
        "url": "http://fake_url.com",
        "headline": "fake headline",
        "source": "sport",
        "keywords": ["fake", "keywords"],
        "raw_text": "The UN is said to meet in New-York according to Donald Trump.",
    }

    return data


@pytest.fixture
def article(request, fake_article_data):
    object_created_list = []

    def create_article(**kwargs):
        data = {**fake_article_data, **kwargs}
        response = requests.post(url=f"{config.API_URL}/data/articles", json=data)

        response.raise_for_status()
        article = response.json()
        
        object_created_list.append(str(article["object_id"]))

        return article

    def finalizer():
        for object_id in object_created_list:
            requests.delete(
                url=f"{config.API_URL}/data/articles/sport/{object_id}"
            ).raise_for_status()

    request.addfinalizer(finalizer)

    return create_article
