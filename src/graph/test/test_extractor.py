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


def test_track_metadata_valid_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    metadata = extractor.track_metadata(setup_files["valid_python_file"])
    assert "functions" in metadata
    assert "classes" in metadata
    assert "imports" in metadata
    assert "variables" in metadata
    assert "inheritance" in metadata
    assert len(metadata["functions"]) == 1
    assert len(metadata["classes"]) == 0


def test_track_metadata_empty_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    metadata = extractor.track_metadata(setup_files["empty_python_file"])
    assert "functions" in metadata
    assert "classes" in metadata
    assert "imports" in metadata
    assert "variables" in metadata
    assert "inheritance" in metadata
    assert len(metadata["functions"]) == 0
    assert len(metadata["classes"]) == 0


def test_track_metadata_non_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    metadata = extractor.track_metadata(setup_files["non_python_file"])
    assert "functions" in metadata
    assert "classes" in metadata
    assert "imports" in metadata
    assert "variables" in metadata
    assert "inheritance" in metadata
    assert len(metadata["functions"]) == 0
    assert len(metadata["classes"]) == 0


def test_track_metadata_invalid_python_file(setup_files):
    extractor = Python_Extractor(setup_files["test_dir"])
    metadata = extractor.track_metadata(setup_files["invalid_python_file"])
    assert "functions" in metadata
    assert "classes" in metadata
    assert "imports" in metadata
    assert "variables" in metadata
    assert "inheritance" in metadata
    assert "syntax_error" in metadata
    assert len(metadata["functions"]) == 0
    assert metadata["syntax_error"] is True


def test_parse_file_not_exist():
    extractor = Python_Extractor("test_files")
    result = extractor.parse_file("non_existent_file.py")
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


def test_track_metadata_valid_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.track_metadata.return_value = {
        "functions": [{"name": "add", "args": ["a", "b"]}],
        "classes": [],
        "imports": [],
        "variables": [],
        "inheritance": [],
    }

    result = mock_python_extractor.track_metadata(setup_files["valid_python_file"])
    mock_python_extractor.track_metadata.assert_called_once_with(
        setup_files["valid_python_file"]
    )
    assert len(result["functions"]) == 1
    assert len(result["classes"]) == 0


def test_track_metadata_empty_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.track_metadata.return_value = {
        "functions": [],
        "classes": [],
        "imports": [],
        "variables": [],
        "inheritance": [],
    }

    result = mock_python_extractor.track_metadata(setup_files["empty_python_file"])
    mock_python_extractor.track_metadata.assert_called_once_with(
        setup_files["empty_python_file"]
    )
    assert len(result["functions"]) == 0
    assert len(result["classes"]) == 0


def test_track_metadata_non_python_file_with_mock(mock_python_extractor, setup_files):
    mock_python_extractor.track_metadata.return_value = {
        "functions": [],
        "classes": [],
        "imports": [],
        "variables": [],
        "inheritance": [],
    }

    result = mock_python_extractor.track_metadata(setup_files["non_python_file"])
    mock_python_extractor.track_metadata.assert_called_once_with(
        setup_files["non_python_file"]
    )
    assert len(result["functions"]) == 0
    assert len(result["classes"]) == 0


def test_track_metadata_invalid_python_file_with_mock(
    mock_python_extractor, setup_files
):
    mock_python_extractor.track_metadata.return_value = {
        "functions": [{"name": "add", "args": ["a", "b"]}],
        "classes": [],
        "imports": [],
        "variables": [],
        "inheritance": [],
    }

    result = mock_python_extractor.track_metadata(setup_files["invalid_python_file"])
    mock_python_extractor.track_metadata.assert_called_once_with(
        setup_files["invalid_python_file"]
    )
    assert len(result["functions"]) == 1
    assert len(result["classes"]) == 0
