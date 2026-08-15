def test_login_existed_user(client, registered_user):
    """Verify login and password using OAuth2 Form"""
    response = client.post(
        "/auth/token",
        data={"username": registered_user["email"], "password": registered_user["password"]},    
    )

    assert response.status_code == 200

    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"    


def test_correct_email_wrong_password(client, registered_user):
    response = client.post(
        "/auth/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"] + "a",
        }
    )

    assert response.status_code == 401

def test_non_existent_user(client):
    """Check if everything will be fine, if I try to login with email, which is not in db"""
    response = client.post(
        "/auth/token",
        data={
            "username": "abba@gmail.com",
            "password": "abba",
        }
    )
    assert response.status_code == 401

def test_login_with_empty_data(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "",
            "password": "",
        }
    )
    assert response.status_code == 422




