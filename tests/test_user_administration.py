import config
import requests


def test_user_creation(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    for role in ["public", "admin", "contributor", "corrector"]:

        user_data = {
            "username": config.generate_fake_username(),
            "password": config.FAKE_VALID_PASSWORD,
            "roles": ["public"],
        }

        response = requests.post(
            url=f"{config.API_URL}/users", headers=HEADERS, json=user_data
        )

        assert response.status_code == 200, response.content

        data = response.json()

        assert user_data["username"] == data["username"]
        assert user_data["roles"] == data["roles"]

        response = requests.delete(
            url=f"{config.API_URL}/users/{data['username']}",
            headers=HEADERS,
        )

        assert response.status_code == 200


def test_user_creation_password_not_valid(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    # wrong password
    user_data = {
        "username": config.generate_fake_username(),
        "password": config.FAKE_NOT_VALID_PASSWORD,
        "roles": ["public"],
    }

    response = requests.post(
        url=f"{config.API_URL}/users", headers=HEADERS, json=user_data
    )
    assert response.status_code == 401, response.content


def test_user_creation_role_not_valid(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    user_data = {
        "username": config.generate_fake_username(),
        "password": config.FAKE_VALID_PASSWORD,
        "roles": ["fake_role"],
    }

    response = requests.post(
        url=f"{config.API_URL}/users", headers=HEADERS, json=user_data
    )
    assert response.status_code == 422, response.content


def test_user_creation_username_already_taken(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}
    user_data = {
        "username": config.generate_fake_username(),
        "password": config.FAKE_VALID_PASSWORD,
        "roles": ["public"],
    }

    response = requests.post(
        url=f"{config.API_URL}/users", headers=HEADERS, json=user_data
    )

    assert response.status_code == 200, response.content

    response = requests.post(
        url=f"{config.API_URL}/users", headers=HEADERS, json=user_data
    )

    assert response.status_code == 409, response.content

    response = requests.delete(
        url=f"{config.API_URL}/users/{user_data['username']}",
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content


def test_user_update(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    public_user = user(username=config.generate_fake_username())

    new_user_data = {"password": config.FAKE_VALID_PASSWORD, "roles": ["contributor"]}
    response = requests.put(
        url=f"{config.API_URL}/users/{public_user['username']}",
        json=new_user_data,
        headers=HEADERS,
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["roles"] == new_user_data["roles"]

    response = requests.post(
        url=f"{config.API_URL}/users/signin",
        json={
            "username": public_user["username"],
            "password": new_user_data["password"],
        },
    )

    assert response.status_code == 200, response.content


def test_user_update_wrong_password(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    public_user = user(username=config.generate_fake_username())

    new_user_data = {
        "password": config.FAKE_NOT_VALID_PASSWORD,
    }
    response = requests.put(
        url=f"{config.API_URL}/users/{public_user['username']}",
        json=new_user_data,
        headers=HEADERS,
    )

    assert response.status_code == 401, response.content


def test_user_update_wrong_role(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    public_user = user(username=config.generate_fake_username())

    new_user_data = {"roles": ["fake_role"]}
    response = requests.put(
        url=f"{config.API_URL}/users/{public_user['username']}",
        json=new_user_data,
        headers=HEADERS,
    )

    assert response.status_code == 422, response.content


def test_user_upadate_wrong_user(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}
    response = requests.put(
        url=f"{config.API_URL}/users/fake_username", json={}, headers=HEADERS
    )

    assert response.status_code == 404, response.content


def test_user_delete(user):
    admin_user = user(roles=["admin"])
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    public_user = user(username=config.generate_fake_username())

    response = requests.delete(
        url=f"{config.API_URL}/users/{public_user['username']}", headers=HEADERS
    )

    assert response.status_code == 200, response.content


def test_user_wrong_user_delete(user):
    admin_user = user(roles=["admin"], username=config.generate_fake_username())
    HEADERS = {"Authorization": f"Bearer {admin_user['access_token']}"}

    response = requests.delete(
        url=f"{config.API_URL}/users/fake_username", headers=HEADERS
    )

    assert response.status_code == 404, response.content
