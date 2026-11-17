def test_health_ok(client):
    assert client.get("/api/health").json() == {"status": "ok"}
