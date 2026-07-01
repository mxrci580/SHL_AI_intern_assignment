import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.build_documents import normalize_product, create_page_content, create_metadata, build_documents, save_documents




class TestNormalizeProduct(unittest.TestCase):
    def test_valid_product(self):
        prod = {
            "entity_id": "123",
            "name": "Test Product",
            "link": "https://example.com/test",
            "duration": " 30 minutes ",
            "languages": ["English", "French"],
            "job_levels": "Manager, Graduate",
            "keys": "Ability & Aptitude",
            "remote": "yes",
            "adaptive": "no"
        }
        norm = normalize_product(prod)
        self.assertEqual(norm["entity_id"], "123")
        self.assertEqual(norm["name"], "Test Product")
        self.assertEqual(norm["link"], "https://example.com/test")
        self.assertEqual(norm["duration"], "30 minutes")
        self.assertEqual(norm["languages"], ["English", "French"])
        self.assertEqual(norm["job_levels"], ["Manager", "Graduate"])
        self.assertEqual(norm["keys"], ["Ability & Aptitude"])

    def test_missing_entity_id(self):
        prod = {
            "name": "Test Product",
            "link": "https://example.com/test"
        }
        with self.assertRaises(ValueError):
            normalize_product(prod)

    def test_missing_name(self):
        prod = {
            "entity_id": "123",
            "link": "https://example.com/test"
        }
        with self.assertRaises(ValueError):
            normalize_product(prod)

    def test_missing_link(self):
        prod = {
            "entity_id": "123",
            "name": "Test Product"
        }
        with self.assertRaises(ValueError):
            normalize_product(prod)

    def test_empty_duration(self):
        prod = {
            "entity_id": "123",
            "name": "Test",
            "link": "https://test.com",
            "duration": "  "
        }
        norm = normalize_product(prod)
        self.assertEqual(norm["duration"], "-")


class TestCreatePageContent(unittest.TestCase):
    def test_page_content_creation(self):
        prod = {
            "name": "Verify G+",
            "description": "Measures general mental ability.",
            "keys": ["Ability & Aptitude"],
            "job_levels": ["Graduate", "Manager"]
        }
        content = create_page_content(prod)
        expected = (
            "Name: Verify G+\n"
            "Description: Measures general mental ability.\n"
            "Category: Ability & Aptitude\n"
            "Job Levels: Graduate, Manager"
        )
        self.assertEqual(content, expected)


class TestCreateMetadata(unittest.TestCase):
    def test_metadata_creation(self):
        prod = {
            "entity_id": "123",
            "name": "Verify G+",
            "link": "https://example.com/verify-g",
            "duration": "30 minutes",
            "languages": ["English"],
            "remote": "yes",
            "adaptive": "no",
            "job_levels": ["Graduate", "Manager"]
        }
        meta = create_metadata(prod)
        self.assertEqual(meta["entity_id"], "123")
        self.assertEqual(meta["url"], "https://example.com/verify-g")
        self.assertEqual(meta["duration"], "30 minutes")
        self.assertEqual(meta["languages"], ["English"])
        self.assertTrue(meta["remote"])
        self.assertFalse(meta["adaptive"])
        self.assertEqual(meta["job_levels"], ["Graduate", "Manager"])


class TestBuildAndSave(unittest.TestCase):
    def test_build_and_save_flow(self):
        docs = build_documents()
        self.assertEqual(len(docs), 377)
        for doc in docs:
            self.assertIsNotNone(doc.page_content)
            self.assertIsNotNone(doc.metadata)
            self.assertIn("Name:", doc.page_content)
            self.assertIn("Description:", doc.page_content)
            self.assertIn("Category:", doc.page_content)
            self.assertIn("Job Levels:", doc.page_content)
            self.assertIn("duration", doc.metadata)
            self.assertIn("languages", doc.metadata)
            self.assertIn("remote", doc.metadata)
            self.assertIn("adaptive", doc.metadata)
            self.assertIn("url", doc.metadata)
            self.assertIn("entity_id", doc.metadata)
            self.assertIn("job_levels", doc.metadata)
            
        # Test saving
        save_documents(docs)
        output_file = Path(__file__).parent.parent / "data" / "processed" / "processed_catalog.json"
        self.assertTrue(output_file.exists())
        
        # Verify JSON content
        import json
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 377)
        self.assertEqual(data[0]["page_content"], docs[0].page_content)
        self.assertEqual(data[0]["metadata"], docs[0].metadata)

if __name__ == "__main__":
    unittest.main()
