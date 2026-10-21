"""Run: python -m unittest backend.test_server (requires httpx)."""
import unittest
from fastapi.testclient import TestClient
from backend.server import app, slvsh_index


class ApiSmokeTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_search_and_pagination(self):
        response = self.client.get("/api/search", params={"title_query": "", "page_size": 2})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertGreater(data["count"], 2)
        self.assertEqual(data["page"], 0)
        second = self.client.get("/api/search", params={"title_query": "", "page_size": 2, "page": 1}).json()
        self.assertNotEqual(data["results"], second["results"])

    def test_exact_search(self):
        response = self.client.get("/api/search", params={"title_query": "", "trick_query": slvsh_index[0]["components"][0], "allow_additions": "false"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["count"], 0)

    def test_page_size_validation(self):
        self.assertEqual(self.client.get("/api/search?page_size=101").status_code, 422)

    def test_common_data(self):
        for path in ("/api/common_tricks", "/api/common_tokens"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertGreater(len(response.json()), 0)

    def test_cors(self):
        response = self.client.options("/api/search", headers={"Origin": "https://slvshindex.ruwy.app", "Access-Control-Request-Method": "GET"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://slvshindex.ruwy.app")


if __name__ == "__main__":
    unittest.main()
