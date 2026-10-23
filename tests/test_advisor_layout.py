import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from advisor_layout import load_metric_order, normalize_metric_order, save_metric_order


class NormalizeMetricOrderTests(unittest.TestCase):
    def test_defaults_precede_other_available_metrics(self):
        self.assertEqual(
            normalize_metric_order(
                ["total", "score", "kept", "fixed"], ["score", "fixed", "kept"]
            ),
            ["score", "fixed", "kept", "total"],
        )

    def test_saved_order_is_used_for_every_available_metric(self):
        self.assertEqual(
            normalize_metric_order(
                ["score", "fixed", "kept", "total"],
                ["score", "fixed", "kept"],
                ["kept", "score"],
            ),
            ["kept", "score", "fixed", "total"],
        )

    def test_duplicates_unknown_ids_and_non_strings_are_removed(self):
        self.assertEqual(
            normalize_metric_order(
                ["score", "fixed", "score", "kept", None],
                ["score", "fixed"],
                ["kept", "kept", "old", 7, None, ["score"], "score"],
            ),
            ["kept", "score", "fixed"],
        )

    def test_changed_columns_drop_old_ids_and_append_new_metrics(self):
        self.assertEqual(
            normalize_metric_order(
                ["score", "new_metric", "kept"],
                ["score", "fixed", "kept"],
                ["fixed", "kept", "score"],
            ),
            ["kept", "score", "new_metric"],
        )

    def test_unusable_saved_orders_fall_back_to_valid_defaults(self):
        for saved in (None, [], "kept", {"kept": 1}, ["old", None, 1]):
            with self.subTest(saved=saved):
                self.assertEqual(
                    normalize_metric_order(
                        ["extra", "score", "kept"],
                        ["kept", "kept", "missing", None, "score"],
                        saved,
                    ),
                    ["kept", "score", "extra"],
                )

    def test_empty_available_columns_produce_an_empty_order(self):
        self.assertEqual(normalize_metric_order([], ["score"], ["score"]), [])


class MetricOrderStorageTests(unittest.TestCase):
    def test_save_creates_parent_directory_and_reloads_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preferences" / "advisor_layout.json"
            save_metric_order(path, ["Kept informed", "Satisfaction Score"])

            self.assertEqual(
                load_metric_order(path), ["Kept informed", "Satisfaction Score"]
            )
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {
                    "version": 1,
                    "metric_order": ["Kept informed", "Satisfaction Score"],
                },
            )
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_a_later_save_replaces_the_previous_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "advisor_layout.json"
            save_metric_order(path, ["score", "kept"])
            save_metric_order(path, ["kept", "score"])
            self.assertEqual(load_metric_order(path), ["kept", "score"])

    def test_malformed_saved_data_returns_none(self):
        malformed = (
            "not json",
            "[]",
            "null",
            "{}",
            '{"version": 2, "metric_order": ["score"]}',
            '{"version": true, "metric_order": ["score"]}',
            '{"version": 1, "metric_order": "score"}',
            '{"version": 1, "metric_order": ["score", null]}',
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "advisor_layout.json"
            for contents in malformed:
                with self.subTest(contents=contents):
                    path.write_text(contents, encoding="utf-8")
                    self.assertIsNone(load_metric_order(path))
            path.write_bytes(b"\xff\xfe")
            self.assertIsNone(load_metric_order(path))

    def test_missing_or_unreadable_paths_return_none(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self.assertIsNone(load_metric_order(path / "missing.json"))
            self.assertIsNone(load_metric_order(path))

    def test_empty_saved_order_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "advisor_layout.json"
            save_metric_order(path, [])
            self.assertEqual(load_metric_order(path), [])

    def test_storage_failure_raises_oserror(self):
        with tempfile.TemporaryDirectory() as directory:
            blocked_parent = Path(directory) / "preferences"
            blocked_parent.write_text("a file prevents creating this directory")
            with self.assertRaises(OSError):
                save_metric_order(blocked_parent / "advisor_layout.json", ["score"])

    def test_failed_atomic_replace_preserves_saved_order_and_cleans_temp_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "advisor_layout.json"
            save_metric_order(path, ["score", "kept"])

            with patch("advisor_layout.os.replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    save_metric_order(path, ["kept", "score"])

            self.assertEqual(load_metric_order(path), ["score", "kept"])
            self.assertEqual(list(path.parent.iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
