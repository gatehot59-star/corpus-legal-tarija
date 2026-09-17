"""Execute isolated B01/I05 contracts with stdlib unittest, no production data."""
import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provenance_v2", ROOT / "contracts/provenance_v2.py")
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
ID = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
RAW = b"%PDF-synthetic"
TEXT = "Artículo 3: texto sintético".encode()


def artifact(**overrides):
    """Build a fully synthetic valid contract for each test."""
    values = dict(version_id=ID, source_url="https://example.org/law.pdf",
                  authority=m.Authority.OFFICIAL, method=m.Method.OCR,
                  original_sha256=hashlib.sha256(RAW).hexdigest(),
                  text_sha256=hashlib.sha256(TEXT).hexdigest(),
                  engine="synthetic", engine_version="1.0.0", language="es")
    values.update(overrides)
    return m.Extraction(**values)


class ContractTests(unittest.TestCase):
    def test_valid_exact_hash(self):
        self.assertEqual(m.verify_bytes(RAW, hashlib.sha256(RAW).hexdigest()), hashlib.sha256(RAW).hexdigest())

    def test_changed_bytes_rejected(self):
        with self.assertRaises(m.ContractError):
            m.verify_bytes(RAW + b"x", hashlib.sha256(RAW).hexdigest())

    def test_missing_short_uppercase_and_nonhex_hash_rejected(self):
        for value in [None, "", "a" * 12, "A" * 64, "z" * 64, 42]:
            with self.subTest(value=value), self.assertRaises(m.ContractError):
                m.verify_bytes(RAW, value)

    def test_wrong_payload_type_rejected(self):
        with self.assertRaises(m.ContractError):
            m.verify_bytes("text", "a" * 64)

    def test_same_prefix_different_suffix_rejected(self):
        digest = hashlib.sha256(RAW).hexdigest()
        with self.assertRaises(m.ContractError):
            m.verify_bytes(RAW, digest[:12] + "0" * 52)

    def test_valid_id(self):
        self.assertEqual(m.require_id(ID), ID)

    def test_nil_noncanonical_invalid_ids_rejected(self):
        for value in ["00000000-0000-0000-0000-000000000000", ID.replace("-", ""), None, "483"]:
            with self.subTest(value=value), self.assertRaises(m.ContractError):
                m.require_id(value)

    def test_same_legal_number_different_work_retained(self):
        a = m.Work(ID, "issuer-a", "department", "law", "001")
        b = m.Work(OTHER, "issuer-b", "municipal", "law", "001")
        self.assertNotEqual(a.work_id, b.work_id)

    def test_unknown_status_is_default(self):
        self.assertEqual(m.Version(ID, OTHER, "historical source, review pending").status, m.LegalStatus.UNKNOWN)

    def test_legal_assessment_needs_review(self):
        for state in [m.LegalStatus.VERIFIED, m.LegalStatus.HISTORICAL, m.LegalStatus.PARTIAL]:
            with self.subTest(state=state), self.assertRaises(m.ContractError):
                m.Version(ID, OTHER, "edition", state)
        self.assertEqual(m.Version(ID, OTHER, "edition", m.LegalStatus.HISTORICAL, ID).legal_review_id, ID)

    def test_string_status_not_accepted(self):
        with self.assertRaises(m.ContractError):
            m.Version(ID, OTHER, "edition", "verified", ID)

    def test_official_ocr_and_secondary_html_independent(self):
        self.assertEqual(artifact().authority, m.Authority.OFFICIAL)
        self.assertEqual(artifact(authority=m.Authority.SECONDARY, method=m.Method.HTML).authority, m.Authority.SECONDARY)
        self.assertIsNone(artifact().fidelity_review_id)

    def test_original_and_derived_digests_both_checked(self):
        a = artifact()
        a.verify(RAW, TEXT)
        for raw, text in [(RAW + b"x", TEXT), (RAW, TEXT + b"x")]:
            with self.subTest(raw=raw), self.assertRaises(m.ContractError):
                a.verify(raw, text)

    def test_invalid_utf8_rejected_even_with_matching_hash(self):
        a = artifact(text_sha256=hashlib.sha256(b"\xff").hexdigest())
        with self.assertRaises(m.ContractError):
            a.verify(RAW, b"\xff")

    def test_annex_and_body_do_not_overwrite(self):
        body = artifact()
        annex = artifact(source_url="https://example.org/annex.pdf",
                         original_sha256=hashlib.sha256(b"annex").hexdigest())
        self.assertEqual(len(json.loads(m.manifest_bytes((body, annex)))["artifacts"]), 2)

    def test_manifest_order_deterministic(self):
        a, b = artifact(), artifact(version_id=OTHER)
        self.assertEqual(m.manifest_bytes((a, b)), m.manifest_bytes((b, a)))
        self.assertTrue(m.manifest_bytes((a,)).endswith(b"\n"))

    def test_duplicate_source_is_not_silently_replaced(self):
        with self.assertRaises(m.ContractError):
            m.manifest_bytes((artifact(), artifact()))

    def test_empty_invalid_manifest_rejected(self):
        for v in [(), [], ("invalid",)]:
            with self.subTest(value=v), self.assertRaises(m.ContractError):
                m.manifest_bytes(v)

    def test_url_credentials_nonhttp_fragments_rejected(self):
        for u in ["file:///etc/passwd", "https://user:pass@example.org/a", "https://example.org/a#x",
                  "https://example.org:99999/a", "https://example.org/a\nx", "https://bad host/a"]:
            with self.subTest(u=u), self.assertRaises(m.ContractError):
                m.require_url(u)
        self.assertEqual(m.require_url("https://example.org/a?download=1"), "https://example.org/a?download=1")

    def test_separate_dates(self):
        a = m.DatedEvidence("sanction", "2024-04-22", "https://example.org/law", "p2")
        b = m.DatedEvidence("promulgation", "2024-06-05", "https://example.org/law", "p2")
        self.assertNotEqual(a, b)

    def test_invalid_date_and_semantics_rejected(self):
        for kind, value in [("guessed", "2024-01-01"), ("session", "2024-02-30"),
                            ("session", "20240101"), ("session", None)]:
            with self.subTest(value=value), self.assertRaises(m.ContractError):
                m.DatedEvidence(kind, value, "https://example.org/a", "p1")

    def test_frozen_artifact(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            artifact().authority = m.Authority.SECONDARY

    def test_invalid_metadata_and_enums_rejected(self):
        for override in [{"engine": ""}, {"language": "x\n"}, {"engine_version": "x" * 2049},
                         {"authority": "official"}, {"method": "ocr"}, {"text_sha256": None},
                         {"fidelity_review_id": "review"}]:
            with self.subTest(override=override), self.assertRaises(m.ContractError):
                artifact(**override)


if __name__ == "__main__":
    unittest.main(verbosity=2)
