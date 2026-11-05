"""URL safety tests for generate_openrouter_schematic.py (no network access)."""

from __future__ import annotations

import base64
import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCHEMATIC = load_module("nature_figure_schematic_url_test", SKILL / "scripts" / "generate_openrouter_schematic.py")


def _args(tmpdir: str) -> Namespace:
    return Namespace(outdir=tmpdir, basename="schematic", output_format="png", timeout=10, api_url="https://api.example/v1")


class ResponseUrlSafetyTests(unittest.TestCase):
    """ART adaptation: response-supplied image URLs are recorded, never fetched."""

    def _assert_url_not_fetched(self, url: str) -> None:
        response = {"data": [{"media_type": "image/png", "url": url}]}
        tmpdir = tempfile.mkdtemp()
        with patch("urllib.request.urlopen", side_effect=AssertionError("must not fetch")) as opened:
            with self.assertRaisesRegex(SystemExit, "No image bytes"):
                SCHEMATIC.save_outputs(response, {"prompt": "x"}, _args(tmpdir))
        opened.assert_not_called()
        self.assertFalse((Path(tmpdir) / "schematic.png").exists())
        metadata = json.loads((Path(tmpdir) / "schematic_request_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["unfetched_image_urls"], [{"item": 1, "url": url}])

    def test_save_outputs_does_not_fetch_file_url(self):
        self._assert_url_not_fetched("file:///etc/hosts")

    def test_save_outputs_does_not_fetch_loopback_url(self):
        self._assert_url_not_fetched("http://127.0.0.1/x.png")

    def test_save_outputs_does_not_fetch_hostname_url(self):
        # A public-looking hostname may resolve to a private address or redirect there.
        self._assert_url_not_fetched("https://cdn.example.com/x.png")

    def test_save_outputs_keeps_bytes_and_records_urls(self):
        response = {
            "data": [
                {"media_type": "image/png", "b64_json": base64.b64encode(b"PNGDATA").decode("ascii")},
                {"media_type": "image/png", "url": "http://169.254.169.254/latest/meta-data"},
            ]
        }
        tmpdir = tempfile.mkdtemp()
        with patch("urllib.request.urlopen", side_effect=AssertionError("must not fetch")) as opened:
            SCHEMATIC.save_outputs(response, {"prompt": "x"}, _args(tmpdir))
        opened.assert_not_called()
        self.assertEqual((Path(tmpdir) / "schematic_01.png").read_bytes(), b"PNGDATA")
        self.assertFalse((Path(tmpdir) / "schematic_02.png").exists())
        metadata = json.loads((Path(tmpdir) / "schematic_request_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(
            metadata["unfetched_image_urls"], [{"item": 2, "url": "http://169.254.169.254/latest/meta-data"}]
        )


if __name__ == "__main__":
    unittest.main()
