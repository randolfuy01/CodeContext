import ast
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



class Python_Extractor:
    """Code extractor class in order to build on 
    """
    def __init__(self, root: str):
        self.root: str = root
        self.files = []
        self.total_files = 0
        self.total_functions = 0
        self.total_clases = 0
        self.total_imports = 0
        
    def traverse(self, path: str) -> int:
        """Collection for all of the files within a given directory

        Args:
            path (_type_): starting point for the traversal, can be passed in as root if necessary
        """
        for dirpath, _, filenames in os.walk(path):
            print("Directory: ", dirpath)
            for filename in filenames:
                self.files.append(os.path.join(dirpath, filename))
                
    def extract_functions_and_classes(self, file: str) -> tuple:
        """Extracts functions and classes from a python file and returns their names.

        Args:
            file (str): path of the file to analyze.
            
        Returns:
            tuple: lists of function names and class names.
        """
        
        if not os.path.exists(file):
            logging.error(f"Error: {file} does not exist.")
            return [], []
        
        if not file.endswith(".py"):
            logging.error(f"Error: {file} is not a python file.")
            return [], []
        
        try:
            with open(file) as f:
                file_content = f.read()
                
            parsed_ast = ast.parse(file_content)
            functions = []
            classes = []
            
            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)  
                    
            return functions, classes
        except Exception as e:
            logging.error(f"Error reading file {f}: e")
            return [], []      
         
    def  extract_imports(self, file: str) -> list:
        """Extract import statements from a python file.

        Args:
            file (str): path of the file to execute from.

        Returns:
            list: list of imported module names.
        """
        
        if not os.path.exists(file):
            logging.error(f"Error: {file} does not exist.")
            return []
        
        if not file.endswith(".py"):
            logging.error(f"Error: {file} is not a python file.")
            return []
        
        try:
            with open(file) as f:
                file_content = f.read()
                
                parsed_ast = ast.parse(file_content)
                imports = []
                
                for node in ast.walk(parsed_ast):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module)
                return imports
        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")
            return []
        
    def parse_file(self, file: str) -> str:
        """Parse a python file and return its AST dump

        Args:
            file (str): path of the file to execute from.

        Returns:
            str: file content as a dump
        """
        if not os.path.exists(file):
            logging.error(f"Error: {file} does not exist.")
            return
        
        if not file.endswith(".py"):
            logging.error(f"Error: {file} is not a python file.")
            return 
        
        try:
            with open(file) as f:
                file_content = f.read()
            
            parsed_ast = ast.parse(file_content)
            parsed_dump = ast.dump(parsed_ast, indent=4)
            
            return parsed_dump
        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")