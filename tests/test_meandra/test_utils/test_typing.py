"""
test_meandra.test_utils.test_typing
===================================

Tests for meandra.utils.typing module.
"""

import pytest
from typing import Any, Dict, List, Optional, Tuple, Union, Annotated, Literal, Protocol, runtime_checkable

from meandra.utils.typing import check_type


class TestCheckType:
    """Tests for check_type function."""

    def test_basic_types(self):
        """Test checking basic Python types."""
        assert check_type(42, int)
        assert check_type(3.14, float)
        assert check_type("hello", str)
        assert check_type(True, bool)
        assert not check_type(42, str)
        assert not check_type("hello", int)

    def test_any_type(self):
        """Test that Any accepts everything."""
        assert check_type(42, Any)
        assert check_type("hello", Any)
        assert check_type(None, Any)
        assert check_type([1, 2, 3], Any)

    def test_optional_type(self):
        """Test Optional type checking."""
        assert check_type(None, Optional[int])
        assert check_type(42, Optional[int])
        assert not check_type("hello", Optional[int])

    def test_union_type(self):
        """Test Union type checking."""
        assert check_type(42, Union[int, str])
        assert check_type("hello", Union[int, str])
        assert not check_type(3.14, Union[int, str])

    def test_list_type(self):
        """Test List type checking."""
        assert check_type([1, 2, 3], List[int])
        assert check_type([], List[int])
        assert not check_type([1, "two", 3], List[int])
        assert not check_type("not a list", List[int])

    def test_list_without_args(self):
        """Test List type without type arguments."""
        assert check_type([1, 2, 3], list)
        assert check_type(["a", "b"], list)
        assert not check_type("not a list", list)

    def test_dict_type(self):
        """Test Dict type checking."""
        assert check_type({"a": 1, "b": 2}, Dict[str, int])
        assert check_type({}, Dict[str, int])
        assert not check_type({"a": "one"}, Dict[str, int])
        assert not check_type({1: 1}, Dict[str, int])
        assert not check_type("not a dict", Dict[str, int])

    def test_dict_without_args(self):
        """Test Dict type without type arguments."""
        assert check_type({"a": 1}, dict)
        assert check_type({1: "one"}, dict)
        assert not check_type("not a dict", dict)

    def test_tuple_fixed_length(self):
        """Test Tuple with fixed-length heterogeneous types."""
        assert check_type((1, "two"), Tuple[int, str])
        assert not check_type((1, 2), Tuple[int, str])
        assert not check_type((1,), Tuple[int, str])
        assert not check_type((1, "two", 3), Tuple[int, str])

    def test_tuple_variable_length(self):
        """Test Tuple with variable-length homogeneous types."""
        assert check_type((1, 2, 3), Tuple[int, ...])
        assert check_type((), Tuple[int, ...])
        assert not check_type((1, "two", 3), Tuple[int, ...])

    def test_tuple_without_args(self):
        """Test Tuple type without type arguments."""
        assert check_type((1, 2, 3), tuple)
        assert check_type(("a", 1), tuple)
        assert not check_type([1, 2, 3], tuple)

    def test_nested_generics(self):
        """Test nested generic types."""
        assert check_type([[1, 2], [3, 4]], List[List[int]])
        assert check_type({"a": [1, 2]}, Dict[str, List[int]])
        assert not check_type([[1, "two"]], List[List[int]])

    def test_none_value(self):
        """Test None value handling."""
        assert check_type(None, type(None))
        assert not check_type(None, int)
        assert check_type(None, Optional[int])

    def test_annotated_type(self):
        """Test Annotated type handling."""
        assert check_type(42, Annotated[int, "meta"])
        assert not check_type("x", Annotated[int, "meta"])

    def test_literal_type(self):
        """Test Literal type handling."""
        assert check_type("a", Literal["a", "b"])
        assert not check_type("c", Literal["a", "b"])

    def test_runtime_protocol(self):
        """Test runtime-checkable Protocol handling."""
        @runtime_checkable
        class HasName(Protocol):
            name: str

        class Obj:
            def __init__(self):
                self.name = "x"

        assert check_type(Obj(), HasName)


if __name__ == "__main__":
    pytest.main()
