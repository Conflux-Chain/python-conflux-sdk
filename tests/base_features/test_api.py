def test_api_version(w3):
    assert w3.api.startswith("1.3.0-beta.1")
