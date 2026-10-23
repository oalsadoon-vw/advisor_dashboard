"""Shared advisor metric ordering and local preference storage."""

import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional, Union


def normalize_metric_order(
    available_columns: Iterable[str],
    default_columns: Iterable[str],
    saved_order=None,
) -> List[str]:
    """Reconcile a preferred order with the metrics in the current export."""
    available = list(dict.fromkeys(
        column for column in available_columns if isinstance(column, str)
    ))
    available_set = set(available)
    ordered = []
    seen = set()

    if isinstance(saved_order, list):
        for column in saved_order:
            if isinstance(column, str) and column in available_set and column not in seen:
                ordered.append(column)
                seen.add(column)

    if not ordered:
        for column in default_columns:
            if isinstance(column, str) and column in available_set and column not in seen:
                ordered.append(column)
                seen.add(column)

    ordered.extend(column for column in available if column not in seen)
    return ordered


def load_metric_order(path: Union[str, Path]) -> Optional[List[str]]:
    """Read a supported preference file, returning None when it cannot be used."""
    try:
        with Path(path).open(encoding="utf-8") as preference_file:
            data = json.load(preference_file)
    except (OSError, ValueError, UnicodeError):
        return None

    if not isinstance(data, dict) or type(data.get("version")) is not int:
        return None
    order = data.get("metric_order")
    if data["version"] != 1 or not isinstance(order, list):
        return None
    if any(not isinstance(column, str) for column in order):
        return None
    return order


def save_metric_order(path: Union[str, Path], order: List[str]) -> None:
    """Atomically replace a preference file; let storage errors reach the UI."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as preference_file:
            temporary_path = Path(preference_file.name)
            json.dump({"version": 1, "metric_order": order}, preference_file, indent=2)
            preference_file.write("\n")
            preference_file.flush()
            os.fsync(preference_file.fileno())
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                # Preserve the original write/replace error if cleanup also fails.
                pass
