import pytest
import os
from unittest.mock import MagicMock
from extractor import Python_Extractor


@pytest.fixture
def setup_files():
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)

    valid_python_file = os.path.join(test_dir, "valid.py")
    empty_python_file = os.path.join(test_dir, "empty.py")
    non_python_file = os.path.join(test_dir, "file.txt")
    invalid_python_file = os.path.join(test_dir, "invalid.py")

    with open(valid_python_file, "w") as f:
        f.write("def add(a, b):\n    return a + b")

    with open(empty_python_file, "w") as f:
        f.write("")

    with open(non_python_file, "w") as f:
        f.write("Just some text\n")

    with open(invalid_python_file, "w") as f:
        f.write("def add(a, b):\n    return a + ")

    yield {
        "test_dir": test_dir,
        "valid_python_file": valid_python_file,
        "empty_python_file": empty_python_file,
        "non_python_file": non_python_file,
        "invalid_python_file": invalid_python_file,
    }

    for file in os.listdir(test_dir):
        os.remove(os.path.join(test_dir, file))
    os.rmdir(test_dir)


def test_parse_valid_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    result = extractor.parse_file(setup_files["valid_python_file"])
    assert "FunctionDef" in result


def test_parse_empty_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    result = extractor.parse_file(setup_files["empty_python_file"])
    assert result == "Module(body=[], type_ignores=[])"


def test_parse_non_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    result = extractor.parse_file(setup_files["non_python_file"])
    assert result is None


def test_parse_file_not_exist():
    extractor = Python_Extractor("test_files")
    result = extractor.parse_file("non_existent_file.py")
    assert result is None


def test_parse_invalid_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    result = extractor.parse_file(setup_files["invalid_python_file"])
    assert result is None


@pytest.fixture
def mock_python_extractor():
    mock_extractor = MagicMock(spec=Python_Extractor)
    mock_extractor.parse_file.return_value = (
        "Module(\n    body=[\n        FunctionDef(\n"
        "            name='add',\n"
        "            args=arguments(\n"
        "                args=[arg(arg='a', annotation=None), "
        "arg(arg='b', annotation=None)],\n"
        "                vararg=None,\n"
        "                kwonlyargs=[],\n"
        "                kw_defaults=[],\n"
        "                kwarg=None,\n"
        "                defaults=[]),\n"
        "            body=[\n                Return(value=BinOp("
        "left=Name(id='a', ctx=Load()), op=Add(), right=Name(id='b', ctx=Load())))],\n"
        "            decorator_list=[]),\n"
        "    ],\n    type_ignores=[])\n"
    )
    return mock_extractor


def test_parse_valid_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.parse_file.return_value = (
        "Module(\n    body=[\n        FunctionDef(\n"
        "            name='add',\n"
        "            args=arguments(\n"
        "                args=[arg(arg='a', annotation=None), "
        "arg(arg='b', annotation=None)],\n"
        "                vararg=None,\n"
        "                kwonlyargs=[],\n"
        "                kw_defaults=[],\n"
        "                kwarg=None,\n"
        "                defaults=[]),\n"
        "            body=[\n                Return(value=BinOp("
        "left=Name(id='a', ctx=Load()), op=Add(), right=Name(id='b', ctx=Load())))],\n"
        "            decorator_list=[]),\n"
        "    ],\n    type_ignores=[])\n"
    )

    result = mock_python_extractor.parse_file(setup_files["valid_python_file"])
    mock_python_extractor.parse_file.assert_called_once_with(
        setup_files["valid_python_file"]
    )
    assert "FunctionDef" in result


def test_parse_empty_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.parse_file.return_value = "Module(body=[], type_ignores=[])"
    result = mock_python_extractor.parse_file(setup_files["empty_python_file"])
    mock_python_extractor.parse_file.assert_called_once_with(
        setup_files["empty_python_file"]
    )
    assert result == "Module(body=[], type_ignores=[])"


def test_parse_non_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.parse_file.return_value = None
    result = mock_python_extractor.parse_file(setup_files["non_python_file"])
    mock_python_extractor.parse_file.assert_called_once_with(
        setup_files["non_python_file"]
    )
    assert result is None


def test_parse_invalid_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.parse_file.return_value = None
    result = mock_python_extractor.parse_file(setup_files["invalid_python_file"])
    mock_python_extractor.parse_file.assert_called_once_with(
        setup_files["invalid_python_file"]
    )
    assert result is None


def test_parse_file_not_exist_with_mock(mock_python_extractor):
    mock_python_extractor.parse_file.return_value = None
    result = mock_python_extractor.parse_file("non_existent_file.py")
    mock_python_extractor.parse_file.assert_called_once_with("non_existent_file.py")
    assert result is None
