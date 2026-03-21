"""
Tests for DataCatalog functionality.
"""

import pytest
import numpy as np
from pathlib import Path

from meandra import DataCatalog


class TestDataCatalog:
    """Tests for DataCatalog."""

    @pytest.fixture
    def catalog(self, tmp_path):
        """Create a catalog with temporary base directory."""
        return DataCatalog(tmp_path)

    def test_register_dataset(self, catalog):
        """Test registering a dataset."""
        catalog.register("my_data", "data.pkl", description="Test dataset")

        assert "my_data" in catalog
        entry = catalog.get_entry("my_data")
        assert entry.name == "my_data"
        assert entry.description == "Test dataset"

    def test_register_duplicate_raises(self, catalog):
        """Test that registering duplicate name raises."""
        catalog.register("my_data", "data.pkl")

        with pytest.raises(ValueError, match="already registered"):
            catalog.register("my_data", "other.pkl")

    def test_unregister_dataset(self, catalog):
        """Test unregistering a dataset."""
        catalog.register("my_data", "data.pkl")
        catalog.unregister("my_data")

        assert "my_data" not in catalog

    def test_save_and_load_pickle(self, catalog):
        """Test saving and loading pickle data."""
        catalog.register("my_data", "data.pkl")
        data = {"key": "value", "numbers": [1, 2, 3]}

        catalog.save("my_data", data)
        loaded = catalog.load("my_data")

        assert loaded == data

    def test_save_and_load_numpy(self, catalog):
        """Test saving and loading numpy data."""
        catalog.register("array", "array.npy")
        data = np.array([1, 2, 3, 4, 5])

        catalog.save("array", data)
        loaded = catalog.load("array")

        assert np.array_equal(loaded, data)

    def test_save_and_load_json(self, catalog):
        """Test saving and loading JSON data."""
        catalog.register("config", "config.json")
        data = {"setting1": True, "setting2": "value"}

        catalog.save("config", data)
        loaded = catalog.load("config")

        assert loaded == data

    def test_path_template_with_run_id(self, catalog):
        """Test path template with run_id placeholder."""
        catalog.register("output", "{run_id}/output.pkl")

        path = catalog.get_path("output", run_id="run_001")
        assert "run_001" in str(path)

        data = {"result": 42}
        catalog.save("output", data, run_id="run_001")
        loaded = catalog.load("output", run_id="run_001")
        assert loaded == data

    def test_path_template_with_date(self, catalog):
        """Test path template with date placeholder."""
        catalog.register("daily", "{date}/data.pkl")

        path = catalog.get_path("daily")
        # Should contain today's date in YYYY-MM-DD format
        import datetime

        today = datetime.date.today().isoformat()
        assert today in str(path)

    def test_path_template_unresolved_raises(self, catalog):
        """Test that unresolved placeholders raise error."""
        catalog.register("data", "{custom_field}/data.pkl")

        with pytest.raises(ValueError, match="Unresolved placeholders"):
            catalog.get_path("data")

    def test_exists(self, catalog):
        """Test exists check."""
        catalog.register("data", "data.pkl")

        assert not catalog.exists("data")

        catalog.save("data", {"a": 1})
        assert catalog.exists("data")

    def test_list_datasets(self, catalog):
        """Test listing all registered datasets."""
        catalog.register("data1", "data1.pkl")
        catalog.register("data2", "data2.pkl")
        catalog.register("data3", "data3.json")

        datasets = catalog.list_datasets()
        assert len(datasets) == 3
        assert "data1" in datasets
        assert "data2" in datasets
        assert "data3" in datasets

    def test_len(self, catalog):
        """Test len() returns number of datasets."""
        assert len(catalog) == 0

        catalog.register("data1", "data1.pkl")
        assert len(catalog) == 1

        catalog.register("data2", "data2.pkl")
        assert len(catalog) == 2

    def test_get_nonexistent_raises(self, catalog):
        """Test that getting nonexistent dataset raises."""
        with pytest.raises(KeyError, match="not found"):
            catalog.get_entry("nonexistent")

    def test_load_nonexistent_raises(self, catalog):
        """Test that loading nonexistent dataset raises."""
        catalog.register("data", "data.pkl")

        with pytest.raises(FileNotFoundError):
            catalog.load("data")

    def test_metadata_stored(self, catalog):
        """Test that custom metadata is stored."""
        catalog.register(
            "data", "data.pkl", description="Test", format="pickle", version=1
        )

        entry = catalog.get_entry("data")
        assert entry.description == "Test"
        assert entry.metadata["format"] == "pickle"
        assert entry.metadata["version"] == 1

    def test_required_placeholders_for_entry(self, catalog):
        """Test required placeholders for a dataset entry."""
        catalog.register("data", "{run_id}/{date}/data.pkl")

        entry = catalog.get_entry("data")
        placeholders = entry.required_placeholders()

        assert "run_id" in placeholders
        assert "date" not in placeholders

    def test_required_placeholders_for_catalog(self, catalog):
        """Test required placeholders for catalog."""
        catalog.register("data", "{run_id}/data.pkl")
        catalog.register("other", "{experiment}/{timestamp}/data.pkl")

        placeholders = catalog.required_placeholders()

        assert placeholders["data"] == {"run_id"}
        assert placeholders["other"] == {"experiment"}
