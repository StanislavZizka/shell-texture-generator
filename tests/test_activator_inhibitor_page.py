import pytest

from app import create_app


@pytest.fixture()
def app_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_activator_inhibitor_page_exposes_static_preview_and_dynamic_panel(app_client):
    response = app_client.get("/activator_inhibitor")
    assert response.status_code == 200

    data = response.data
    assert b'nav-random-error' in data
    assert b'3d-visualization' in data
    assert b'select-shell-type' in data
    assert b'instruction-mouse' in data
    assert b'popup-zoom-info' in data
    assert b"random_error_preview" in data
    assert b"random_error_panel" in data
    assert b"random_error_state" in data
    assert b"re_strength" in data
    assert b"STATIC_PRESETS" in data
