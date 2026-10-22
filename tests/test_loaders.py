import unittest

from helix_rag.loaders import load_corpus, load_pdf, load_ticket

from .helpers import CORPUS, has_ocr, settings


class CorpusLoadingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load_corpus(CORPUS, settings().cache_dir)
        cls.by_source = {d.source: d for d in cls.docs}

    def test_loads_every_format(self):
        types = [d.doc_type for d in self.docs]
        self.assertEqual(types.count("markdown"), 60)
        self.assertEqual(types.count("ticket"), 15)
        # Scanned PDFs are skipped (not crashed on) when OCR is unavailable.
        self.assertEqual(types.count("pdf"), 25 if has_ocr() else 20)

    def test_test_set_and_readme_are_not_indexed(self):
        self.assertNotIn("test_set.json", self.by_source)
        self.assertNotIn("README.md", self.by_source)

    def test_markdown_title_from_h1(self):
        self.assertEqual(self.by_source["product-docs/api/errors.md"].title, "API Errors")

    def test_native_pdf_keeps_section_headings(self):
        doc = self.by_source["runbooks/customer-ops/refund-processing.pdf"]
        self.assertEqual(doc.title, "Refund Processing")
        self.assertFalse(doc.metadata["scanned"])
        self.assertIn("\nAPPROVAL REQUIRED FOR\n", doc.text)
        self.assertIn("Any refund over $1,000.", doc.text)

    @unittest.skipUnless(has_ocr(), "tesseract/poppler not installed")
    def test_scanned_pdfs_are_ocrd(self):
        scanned = sorted(d.source for d in self.docs if d.metadata.get("scanned"))
        self.assertEqual(len(scanned), 5)
        vip = self.by_source["runbooks/customer-ops/vip-escalation.pdf"]
        self.assertIn("30 minutes", vip.text)
        self.assertIn("ESCALATION PATH", vip.text)


class TicketParsingTest(unittest.TestCase):
    def test_turns_roles_and_resolution(self):
        path = CORPUS / "tickets/ticket-1267-integration-disconnect.html"
        doc = load_ticket(path, "tickets/ticket-1267-integration-disconnect.html")
        self.assertEqual(doc.metadata["ticket_id"], "HX-1267")
        self.assertEqual(doc.metadata["category"], "Integrations")
        turns = doc.metadata["turns"]
        self.assertEqual(turns[0]["role"], "Customer")
        self.assertEqual(turns[1]["role"], "Agent")
        self.assertIn("refresh until revoked", doc.metadata["resolution"])
        self.assertIn("[Agent] Sandra Liu:", doc.text)
        self.assertNotIn("font-family", doc.text)  # no CSS leaking into the text


class PdfFallbackTest(unittest.TestCase):
    def test_scanned_pdf_without_ocr_returns_empty_not_error(self):
        from unittest import mock

        with mock.patch("helix_rag.loaders._ocr_pdf", return_value=""):
            doc = load_pdf(CORPUS / "runbooks/csm/qbr-template.pdf", "x.pdf", None)
        self.assertTrue(doc.metadata["scanned"])
        self.assertEqual(doc.text, "")


if __name__ == "__main__":
    unittest.main()
