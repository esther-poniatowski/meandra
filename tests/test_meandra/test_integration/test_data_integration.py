"""
test_meandra.test_integration.test_data_integration
===================================================

Tests for Morpha data integration adapters.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from meandra.core.node import Node
from meandra.integration.data import DataStructureIOHandler, create_typed_node


class TestDataStructureIOHandler:
    """Tests for DataStructureIOHandler."""

    def test_supports_common_extensions(self):
        """Test that handler supports expected extensions."""
        assert DataStructureIOHandler.supports("data.pkl")
        assert DataStructureIOHandler.supports("data.npy")
        assert DataStructureIOHandler.supports("data.npz")
        assert DataStructureIOHandler.supports("data.json")
        assert DataStructureIOHandler.supports("data.yaml")
        assert DataStructureIOHandler.supports("data.yml")
        assert DataStructureIOHandler.supports("data.h5")
        assert DataStructureIOHandler.supports("data.hdf5")

    def test_does_not_support_unknown_extensions(self):
        """Test that handler rejects unknown extensions."""
        assert not DataStructureIOHandler.supports("data.xyz")
        assert not DataStructureIOHandler.supports("data.csv")  # CSV handled differently
        assert not DataStructureIOHandler.supports("data.txt")

    def test_register_extension(self):
        """Test registering a custom extension mapping."""
        DataStructureIOHandler.register_extension(".foo", "SaverFoo", "LoaderFoo")
        assert DataStructureIOHandler.supports("data.foo")

    def test_read_with_explicit_loader(self):
        """Test reading with explicitly specified loader."""
        # Create a mock loader
        mock_loader_cls = MagicMock()
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = {"data": [1, 2, 3]}
        mock_loader_cls.return_value = mock_loader_instance

        handler = DataStructureIOHandler(loader_cls=mock_loader_cls)

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            temp_path = f.name

        try:
            result = handler.read(temp_path)
            assert result == {"data": [1, 2, 3]}
            mock_loader_cls.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_write_with_explicit_saver(self):
        """Test writing with explicitly specified saver."""
        mock_saver_cls = MagicMock()
        mock_saver_instance = MagicMock()
        mock_saver_cls.return_value = mock_saver_instance

        handler = DataStructureIOHandler(saver_cls=mock_saver_cls)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "output.pkl"

            handler.write(temp_path, {"data": [1, 2, 3]})

            mock_saver_cls.assert_called_once()
            mock_saver_instance.save.assert_called_once_with({"data": [1, 2, 3]})

    def test_write_creates_parent_directories(self):
        """Test that write creates parent directories if needed."""
        mock_saver_cls = MagicMock()
        mock_saver_instance = MagicMock()
        mock_saver_cls.return_value = mock_saver_instance

        handler = DataStructureIOHandler(saver_cls=mock_saver_cls)

        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "a" / "b" / "c" / "output.pkl"

            handler.write(nested_path, {"data": 1})

            # Parent directories should be created
            assert nested_path.parent.exists()

    def test_read_raises_for_unknown_extension_no_loader(self):
        """Test that read raises error for unknown extension without loader."""
        handler = DataStructureIOHandler()

        with pytest.raises(ValueError, match="No loader found"):
            handler.read("/some/path/file.xyz")

    def test_write_raises_for_unknown_extension_no_saver(self):
        """Test that write raises error for unknown extension without saver."""
        handler = DataStructureIOHandler()

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "file.xyz"

            with pytest.raises(ValueError, match="No saver found"):
                handler.write(temp_path, {"data": 1})


class TestCreateTypedNode:
    """Tests for create_typed_node factory function."""

    def test_creates_node_with_name(self):
        """Test that created node has correct name."""
        def dummy(inputs):
            return {}

        node = create_typed_node("test_node", dummy)

        assert node.name == "test_node"

    def test_input_contract_validates_types(self):
        """Test that input contract validates types correctly."""
        def process(inputs):
            return {"result": inputs["data"].sum()}

        node = create_typed_node(
            "processor",
            process,
            input_types={"data": np.ndarray},
        )

        # Should pass with correct type
        node.input_contract({"data": np.array([1, 2, 3])})

        # Should raise with incorrect type
        with pytest.raises(TypeError, match="expected"):
            node.input_contract({"data": [1, 2, 3]})

    def test_output_contract_validates_types(self):
        """Test that output contract validates types correctly."""
        def process(inputs):
            return {"result": inputs["data"] * 2}

        node = create_typed_node(
            "processor",
            process,
            output_types={"result": np.ndarray},
        )

        # Should pass with correct type
        node.output_contract({"result": np.array([2, 4, 6])})

        # Should raise with incorrect type
        with pytest.raises(TypeError, match="expected"):
            node.output_contract({"result": [2, 4, 6]})

    def test_contracts_require_keys(self):
        """Test that contracts raise on missing keys."""
        def dummy(inputs):
            return {}

        node = create_typed_node(
            "test",
            dummy,
            input_types={"data": np.ndarray},
            output_types={"result": np.ndarray},
        )

        with pytest.raises(KeyError):
            node.input_contract({})
        with pytest.raises(KeyError):
            node.output_contract({})

    def test_contracts_allow_missing_keys_when_configured(self):
        """Test that contracts allow missing keys when configured."""
        def dummy(inputs):
            return {}

        node = create_typed_node(
            "test",
            dummy,
            input_types={"data": np.ndarray},
            output_types={"result": np.ndarray},
            allow_missing_inputs=True,
            allow_missing_outputs=True,
        )

        node.input_contract({})
        node.output_contract({})

    def test_input_contract_optional_type(self):
        """Test that Optional types are accepted."""
        from typing import Optional

        def process(inputs):
            return {"result": inputs["data"]}

        node = create_typed_node(
            "processor",
            process,
            input_types={"data": Optional[int]},
            output_types={"result": Optional[int]},
        )

        node.input_contract({"data": None})
        node.output_contract({"result": None})

    def test_no_contracts_when_types_not_specified(self):
        """Test that no contracts are created when types not specified."""
        def dummy(inputs):
            return {}

        node = create_typed_node("test", dummy)

        assert node.input_contract is None
        assert node.output_contract is None

    def test_passes_additional_kwargs_to_node(self):
        """Test that additional kwargs are passed to Node constructor."""
        def dummy(inputs):
            return {"out": 1}

        node = create_typed_node(
            "test",
            dummy,
            dependencies=["other"],
            inputs=["a", "b"],
            outputs=["out"],
            is_checkpointable=True,
        )

        assert node.dependencies == ["other"]
        assert node.inputs == ["a", "b"]
        assert node.outputs == ["out"]
        assert node.is_checkpointable is True

    def test_contract_error_message_includes_details(self):
        """Test that contract errors include helpful details."""
        def dummy(inputs):
            return {}

        node = create_typed_node(
            "test",
            dummy,
            input_types={"value": int},
        )

        try:
            node.input_contract({"value": "not an int"})
            pytest.fail("Expected TypeError")
        except TypeError as e:
            assert "value" in str(e)
            assert "int" in str(e)
            assert "str" in str(e)


if __name__ == "__main__":
    pytest.main()
