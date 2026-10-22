import unittest

from helix_rag.bm25 import BM25
from helix_rag.text import stem, tokenize


class TokenizerTest(unittest.TestCase):
    def test_keeps_identifiers_whole_and_split(self):
        toks = tokenize("Check X-Helix-Signature and HX-1267 via pg_last_wal_receive_lsn")
        for t in ("x-helix-signature", "signature", "hx-1267", "1267", "pg_last_wal_receive_lsn", "lsn"):
            self.assertIn(t, toks)

    def test_numbers_prices_and_stopwords(self):
        toks = tokenize("What is the price? $299 per month, 429 errors")
        self.assertIn("$299", toks)
        self.assertIn("299", toks)
        self.assertIn("429", toks)
        self.assertNotIn("the", toks)

    def test_light_stemming(self):
        self.assertEqual(stem("retries"), stem("retried"))
        self.assertEqual(stem("webhooks"), "webhook")
        self.assertEqual(stem("access"), "access")  # no "ss" stripping
        self.assertEqual(stem("v1"), "v1")


class BM25Test(unittest.TestCase):
    def test_ranks_exact_match_first(self):
        docs = ["rate limit is 600 requests per minute", "webhook retries use backoff", "sso with okta"]
        bm = BM25(docs)
        self.assertEqual(bm.top("how many requests per minute", 3)[0][0], 0)
        self.assertEqual(bm.top("okta", 3)[0][0], 2)
        self.assertEqual(bm.top("nothing matches here zzz", 3), [])


if __name__ == "__main__":
    unittest.main()
