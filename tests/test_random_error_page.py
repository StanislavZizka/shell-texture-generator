import pytest

from app import create_app


@pytest.fixture()
def app_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_random_error_page_exposes_localized_3d_and_header(app_client):
    response = app_client.get("/random_error")
    assert response.status_code == 200

    data = response.data
    assert b"page-title-re" in data
    assert b"page-subtitle-re" in data
    assert b"nav-random-error" in data
    assert b"3d-visualization" in data
    assert b"select-shell-type" in data
    assert b"instruction-mouse" in data
    assert b"popup-zoom-info" in data
