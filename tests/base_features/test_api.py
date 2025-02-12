def test_api_version(w3):
    expected_version = "1.4.1"
    if "beta" not in expected_version:
        assert w3.api.startswith(expected_version)
