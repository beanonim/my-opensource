import unittest

from api import build_bigbase_headers, normalize_search_type


class SearchTypeNormalizationTests(unittest.TestCase):
    def test_map_common_osint_types(self):
        self.assertEqual(normalize_search_type("phone"), "phone")
        self.assertEqual(normalize_search_type("fio"), "name")
        self.assertEqual(normalize_search_type("nickname"), "username")
        self.assertEqual(normalize_search_type("instagram"), "username")
        self.assertEqual(normalize_search_type("telegram"), "username")
        self.assertEqual(normalize_search_type("vk"), "username")
        self.assertEqual(normalize_search_type("car"), "vehicle")

    def test_build_bigbase_headers_includes_direct_and_bearer_variants(self):
        headers = build_bigbase_headers("secret-token")
        self.assertEqual(headers[0]["Authorization"], "secret-token")
        self.assertEqual(headers[1]["Authorization"], "Bearer secret-token")
        self.assertEqual(headers[2]["X-API-Key"], "secret-token")


if __name__ == "__main__":
    unittest.main()
