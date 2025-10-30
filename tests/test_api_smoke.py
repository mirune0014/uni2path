import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.main import app


class ApiSmokeTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        r = self.client.get("/healthz")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_pathways_bad_request(self):
        r = self.client.post("/v1/pathways", json={"ids": []})
        self.assertEqual(r.status_code, 400)

    @patch("app.api.main.kegg_pathways_for_uniprot", return_value=[{"pathway_id": "hsa00010", "source": "kegg", "name": "Glycolysis / Gluconeogenesis", "url": "https://www.kegg.jp/pathway/hsa00010"}])
    @patch("app.api.main.reactome_pathways_for_uniprot", return_value=[{"pathway_id": "R-HSA-199420", "source": "reactome", "name": "Glycolysis", "url": "https://reactome.org/PathwayBrowser/#/R-HSA-199420"}])
    @patch("app.api.main.normalize_ids", return_value=([type("N", (), {"accession": "P31946", "organism_id": 9606})()], []))
    def test_pathways_ok(self, *_):
        r = self.client.post("/v1/pathways", json={"ids": ["P31946"]})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("pathways", data)
        self.assertGreaterEqual(len(data["pathways"]), 1)


if __name__ == "__main__":
    unittest.main()

