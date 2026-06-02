from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def app_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "path",
    [
        "/spots_211",
        "/figure_23",
        "/activator_212",
    ],
)
def test_key_pages_expose_static_and_dynamic_parameter_labels(app_client, path):
    response = app_client.get(path)
    assert response.status_code == 200
    data = response.data
    assert b"Static parameters" in data or b"Statick\xc3\xa9 parametry" in data
    assert b"Dynamic parameters" in data or b"Dynamick\xc3\xa9 parametry" in data


def test_home_page_exposes_thesis_context(app_client):
    response = app_client.get("/")
    assert response.status_code == 200

    data = response.data
    assert b"page-title-home" in data
    assert b"page-subtitle-home" in data
    assert b"home-thesis-badge" in data
    assert b"Natural Texture Generator for Sea Shells" in data
    assert b"Master's thesis focused on modeling patterns using reaction-diffusion systems" in data


def test_random_error_accordion_is_not_auto_opened():
    repo_root = Path(__file__).resolve().parents[1]
    js_212 = (repo_root / "static" / "js" / "activator_212.js").read_text(encoding="utf-8")
    js_23 = (repo_root / "static" / "js" / "activator_23.js").read_text(encoding="utf-8")

    assert "randomErrorAccordion.open = enabled" not in js_212
    assert "randomErrorAccordion.open = enabled" not in js_23
