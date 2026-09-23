"""Tests for authorized source and rubro catalog navigation."""
from unittest.mock import patch
from .test_access import FixtureBase
from corpus.access import CorpusError


class CatalogTests(FixtureBase):
    """Catalog metadata must remain behind the same server-side authorization."""

    @patch("corpus.services.browse_snapshot")
    def test_browse_passes_authorized_uid_versions_and_filters(self, browse):
        """Browse delegates eligible uids with their own exact versions."""
        browse.return_value = {"items": ({"uid": "fixture-1"},), "sources": (),
                               "rubros": (), "tipos": (), "next_offset": None}
        result = self.app.browse(self.p, "tarija_gaceta", "Civil", "Ley", 0, 20)
        self.assertEqual(result["items"][0]["uid"], "fixture-1")
        browse.assert_called_once()
        args = browse.call_args.args
        self.assertEqual(args[1], {"fixture-1": self.row.version_sha256})
        self.assertEqual(args[2:], ("tarija_gaceta", "Civil", "Ley", 0, 20))

    def test_browse_denies_unknown_principal(self):
        """A forged or missing principal cannot enumerate catalog metadata."""
        with self.assertRaises(CorpusError):
            self.app.browse(type(self.p)(999999, 1))
