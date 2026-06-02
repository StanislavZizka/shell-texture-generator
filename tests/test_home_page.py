import pytest

from app import create_app


@pytest.fixture()
def app_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page_highlights_three_core_families(app_client):
    response = app_client.get("/")
    assert response.status_code == 200

    data = response.data
    assert b'data-i18n="nav-figure211"' in data
    assert b'data-i18n="nav-figure23"' in data
    assert b'data-i18n="nav-figure212"' in data
    assert b'data-i18n="home-figure211-title"' in data
    assert b'data-i18n="home-figure23-title"' in data
    assert b'data-i18n="home-figure212-title"' in data
    assert b'data-i18n="home-figure211-button"' in data
    assert b'data-i18n="home-figure23-button"' in data
    assert b'data-i18n="home-figure212-button"' in data
    assert b"js/components/appearance-switcher.js" in data
