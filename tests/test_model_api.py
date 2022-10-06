import config
import requests

config.TEXT = "The UN is said to meet in New-York according to Donald Trump."

config.ALIASES = {"UN": "ORG_0", "New-York": "LOC_0", "Donald Trump": "PER_0"}

config.ANONYMIZED_TEXT = "The ORG_0 is said to meet in LOC_0 according to PER_0."


def test_get_index():
    response = requests.get(url=f"{config.API_URL}/")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["message"] == "Documentation is at /docs"
    assert "version" in data


def test_get_aliases():
    response = requests.get(url=f"{config.API_URL}/aliases")

    assert response.status_code == 200, response.content

    data = response.json()

    for i in data:
        assert "alias" in i, i
        assert "description" in i, i


def test_get_unique_alias():
    alias = "PER"
    response = requests.get(url=f"{config.API_URL}/aliases/{alias}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["alias"] == alias, data

    alias = "WRONG_ALIAS"
    response = requests.get(url=f"{config.API_URL}/aliases/{alias}")

    assert response.status_code == 404, response.content


def test_post_get_aliases():
    response = requests.post(
        url=f"{config.API_URL}/model/aliases", json={"text": config.TEXT}
    )

    assert response.status_code == 200, response.content

    data = response.json()

    for i in data:
        assert "text" in i, i
        assert "alias" in i, i


def test_post_anonymize_text():
    response = requests.post(
        url=f"{config.API_URL}/model/anonymize", json={"text": config.TEXT}
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["raw_text"] == config.TEXT

    assert data["anonymized_text"] == config.ANONYMIZED_TEXT

    assert data["aliases"] == [
        {"text": k, "alias": v, "alias_type": v.split("_")[0]}
        for k, v in config.ALIASES.items()
    ]
