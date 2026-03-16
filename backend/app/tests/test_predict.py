"""
Tests for /api/v1/predict endpoints:
  POST   /predict/
  GET    /predict/history
  DELETE /predict/history/{id}
"""

SAMPLE_TEXT = "Scientists discover new method to generate clean energy from seawater."


class TestPredict:

    def test_predict_success(self, client, auth_headers):
        response = client.post("/api/v1/predict/", json={"text": SAMPLE_TEXT},
                               headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "top_3" in data
        assert isinstance(data["top_3"], list)
        assert len(data["top_3"]) == 3
        assert data["saved"] is True
        assert 0.0 <= data["confidence"] <= 1.0

    def test_predict_unauthenticated(self, client):
        response = client.post("/api/v1/predict/", json={"text": SAMPLE_TEXT})
        assert response.status_code in (401, 403)

    def test_predict_text_too_short(self, client, auth_headers):
        response = client.post("/api/v1/predict/", json={"text": "Hi"},
                               headers=auth_headers)
        assert response.status_code == 422

    def test_predict_empty_text(self, client, auth_headers):
        response = client.post("/api/v1/predict/", json={"text": ""},
                               headers=auth_headers)
        assert response.status_code == 422

    def test_predict_text_too_long(self, client, auth_headers):
        response = client.post("/api/v1/predict/", json={"text": "a" * 10001},
                               headers=auth_headers)
        assert response.status_code == 422

    def test_predict_missing_text_field(self, client, auth_headers):
        response = client.post("/api/v1/predict/", json={},
                               headers=auth_headers)
        assert response.status_code == 422


class TestPredictHistory:

    def _make_prediction(self, client, auth_headers):
        return client.post("/api/v1/predict/", json={"text": SAMPLE_TEXT},
                           headers=auth_headers)

    def test_history_empty(self, client, auth_headers):
        response = client.get("/api/v1/predict/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["predictions"] == []

    def test_history_after_prediction(self, client, auth_headers):
        self._make_prediction(client, auth_headers)
        response = client.get("/api/v1/predict/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["predictions"]) == 1
        item = data["predictions"][0]
        assert "id" in item
        assert "input_text" in item
        assert "prediction" in item
        assert "confidence" in item
        assert "created_at" in item

    def test_history_pagination(self, client, auth_headers):
        for _ in range(3):
            self._make_prediction(client, auth_headers)

        response = client.get("/api/v1/predict/history?limit=2&offset=0",
                              headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["predictions"]) == 2

        response2 = client.get("/api/v1/predict/history?limit=2&offset=2",
                               headers=auth_headers)
        assert len(response2.json()["predictions"]) == 1

    def test_history_unauthenticated(self, client):
        response = client.get("/api/v1/predict/history")
        assert response.status_code in (401, 403)

    def test_history_isolated_between_users(self, client, auth_headers):
        self._make_prediction(client, auth_headers)

        client.post("/api/v1/auth/register", json={
            "email": "userb@example.com",
            "username": "userb",
            "password": "Password123",
        })
        login = client.post("/api/v1/auth/login", json={
            "email": "userb@example.com",
            "password": "Password123",
        })
        assert login.status_code == 200
        headers_b = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.get("/api/v1/predict/history", headers=headers_b)
        assert response.status_code == 200
        assert response.json()["total"] == 0


class TestDeletePrediction:

    def _create_prediction(self, client, auth_headers):
        resp = client.post("/api/v1/predict/", json={"text": SAMPLE_TEXT},
                           headers=auth_headers)
        assert resp.status_code == 200
        history = client.get("/api/v1/predict/history", headers=auth_headers)
        assert history.status_code == 200
        return history.json()["predictions"][0]["id"]

    def test_delete_success(self, client, auth_headers):
        pred_id = self._create_prediction(client, auth_headers)
        response = client.delete(f"/api/v1/predict/history/{pred_id}",
                                 headers=auth_headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        history = client.get("/api/v1/predict/history", headers=auth_headers)
        assert history.json()["total"] == 0

    def test_delete_not_found(self, client, auth_headers):
        response = client.delete("/api/v1/predict/history/99999",
                                 headers=auth_headers)
        assert response.status_code == 404

    def test_delete_another_users_prediction(self, client, auth_headers):
        pred_id = self._create_prediction(client, auth_headers)

        client.post("/api/v1/auth/register", json={
            "email": "userb@example.com",
            "username": "userb",
            "password": "Password123",
        })
        login = client.post("/api/v1/auth/login", json={
            "email": "userb@example.com",
            "password": "Password123",
        })
        assert login.status_code == 200
        headers_b = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.delete(f"/api/v1/predict/history/{pred_id}",
                                 headers=headers_b)
        assert response.status_code == 404

    def test_delete_unauthenticated(self, client):
        response = client.delete("/api/v1/predict/history/1")
        assert response.status_code in (401, 403)