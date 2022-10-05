import requests

sentence1 = "The UN is said to meet in New-York according to Donald Trump."

entities1 = {"UN": "ORG_0", "New-York": "LOC_0", "Donald Trump": "PER_0"}

clean_sentence1 = "The ORG_0 is said to meet in LOC_0 according to PER_0."

API_URL = "http://localhost:8000"


def test_get_index():
    response = requests.get(url=f"{API_URL}/")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["message"] == "Documentation is at /docs"
    assert "version" in data


def test_get_tags():
    response = requests.get(url=f"{API_URL}/tags")

    assert response.status_code == 200, response.content

    data = response.json()

    for i in data:
        assert "tag" in i, i
        assert "description" in i, i


def test_get_unique_tag():
    tag = "PER"
    response = requests.get(url=f"{API_URL}/tags/{tag}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["tag"] == tag, data

    tag = "WRONG_TAG"
    response = requests.get(url=f"{API_URL}/tags/{tag}")

    assert response.status_code == 404, response.content


def test_post_get_tags():
    response = requests.post(url=f"{API_URL}/model/tags", json={"sentence": sentence1})

    assert response.status_code == 200, response.content

    data = response.json()

    for i in data:
        assert "text" in i, i
        assert "tag" in i, i


def test_post_anonymize_text():
    response = requests.post(
        url=f"{API_URL}/model/anonymize", json={"sentence": sentence1}
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["raw_text"] == sentence1

    assert data["anonymized_text"] == clean_sentence1

    assert data["tags"] == [{"text": k, "tag": v} for k, v in entities1.items()]
