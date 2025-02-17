import ast
import os
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Python_Extractor:
    """
    Initializes the Python_Extractor with a given root directory.

    Args:
        root (str): The root directory to start collecting Python files from.
    """

    def __init__(self, root: str):
        self.root: str = root
        self.files = []

    def traverse(self, path: str) -> None:
        """
        Traverses the directory at the given path and collects all Python files.

        Args:
            path (str): The directory to traverse for Python files.
        """

        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".py"):
                    self.files.append(os.path.join(dirpath, filename))

    def track_metadata(self, file: str) -> dict:
        """
        Track metadata for functions, classes, imports, and variables in a Python file

        Args:
            file (str): The path to the Python file to be parsed.
        Returns:
            str: metadata dictionary containing the data about the file.
        """

        metadata = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "inheritance": [],
            "syntax_error": False,
        }

        if not os.path.exists(file):
            logging.error(f"Error: {file} does not exist.")
            return metadata

        if not file.endswith(".py"):
            logging.error(f"Error: {file} is not a Python file.")
            return metadata

        try:
            with open(file) as f:
                file_content = f.read()

            parsed_ast = ast.parse(file_content)

            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.FunctionDef):
                    function_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                    }
                    metadata["functions"].append(function_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "class_name": node.name,
                        "bases": [
                            base.id for base in node.bases if isinstance(base, ast.Name)
                        ],
                        "methods": [
                            method.name
                            for method in node.body
                            if isinstance(method, ast.FunctionDef)
                        ],
                    }
                    metadata["classes"].append(class_info)
                    metadata["inheritance"].extend(class_info["bases"])

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    metadata["imports"].append(node.module)

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            metadata["variables"].append(target.id)

            return metadata

        except SyntaxError as e:
            logging.error(f"Syntax Error reading file {file}: {e}")
            metadata["syntax_error"] = True  # Flag the file as having a syntax error
            return metadata
        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")
            return metadata

    def parse_file(self, file: str) -> str:
        """
        Parses a Python file and returns its AST dump as a string.

        Args:
            file (str): The path to the Python file to be parsed.

        Returns:
            str: A string representation of the Abstract Syntax Tree (AST) dump of the Python file.
        """
        if not os.path.exists(file):
            logging.error(f"Error: {file} does not exist.")
            return

        if not file.endswith(".py"):
            logging.error(f"Error: {file} is not a Python file.")
            return

        try:
            with open(file) as f:
                file_content = f.read()

            parsed_ast = ast.parse(file_content)
            parsed_dump = ast.dump(parsed_ast, indent=4)
            return parsed_dump

        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")
            return

    def collect_metadata_and_ast(self, file: str) -> dict:
        """
        Collects both metadata and AST dump for a given Python file.

        Args:
            file (str): The path to the Python file for metadata and AST extraction.

        Returns:
            dict: A dictionary containing both the metadata and the AST dump:
                - "metadata" (dict): Metadata of the file, including functions, classes, imports, and inheritance, and syntax.
                - "ast_dump" (str): The AST dump of the file as a string.
        """

        metadata = self.track_metadata(file)
        ast_dump = self.parse_file(file)

        return {"metadata": metadata, "ast_dump": ast_dump}

    def process_codebase(self) -> dict:
        """
        Collects data from all files within a given root directory / subdirectories (codebase)

        Returns:
            dict: A dictionary containing the data associated with a given filepath
        """
        dataset = {}

        try:
            self.traverse(self.root)
            for file in self.files:
                data = self.collect_metadata_and_ast(file)
                dataset[file] = data
            return dataset

        except Exception as e:
            logging.error(f"Error collecting codebase data: {e}")
            return {}
