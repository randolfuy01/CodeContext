from .extractor import Python_Extractor, FileMetadata
from typing import Dict, Union
import networkx as nx
import matplotlib.pyplot as plt
import logging
import ast
import astor
import pickle

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Knowledge_Graph(Python_Extractor):
    """Knowledege graph creation based on extracting code"""

    """
    Example Schema of the data extracted for a given file
    
            [
            "path/to/file1.py": {
                "metadata": {
                    "functions": [
                        {"name": "func1", "args": ["arg1", "arg2"]},
                        {"name": "func2", "args": ["arg1"]}
                    ],
                    "classes": [
                        {"name": "Class1", "bases": ["BaseClass"], "methods": ["method1", "method2"]},
                        {"name": "Class2", "bases": [], "methods": ["method1"]}
                    ],
                    "imports": ["os", "sys"],
                    "variables": ["var1", "var2"],
                    "inheritance": ["BaseClass"],
                    "syntax_error": False
                },
                "ast_dump": "Module(body=[FunctionDef(name='func1', args=arguments(args=[arg(arg='arg1', annotation=None), arg(arg='arg2', annotation=None)], vararg=None), body=[Expr(value=Call(func=Name(id='print', ctx=Load()), args=[Name(id='arg1', ctx=Load())], keywords=[])])])"
            ]
    """

    def __init__(self, root_path: str):
        """Initializes the knowledge graph and extracts the data from the given root path

        Args:
            root_path (str): root path of the project
        """
        super().__init__(root_path)
        self.data: Dict[str, Dict[str, Union[FileMetadata, str]]] = (
            self.process_codebase()
        )

        self.graph = nx.DiGraph()

    def add_nodes(self) -> bool:
        """Adds class and function nodes to the graph, ensuring no duplication and includes references to AST dump."""
        try:
            logging.info("Adding function and class nodes to the graph")

            for file, file_data in self.data.items():
                classes = file_data["metadata"]["classes"]
                functions = file_data["metadata"]["functions"]
                ast_dump = file_data["ast_dump"]
                pickled_load = pickle.loads(ast_dump)
                function_to_class = {}

                for class_info in classes:
                    class_name = class_info["name"]
                    methods_in_class = class_info["methods"]
                    for method in methods_in_class:
                        function_to_class[method] = class_name

                for class_info in classes:
                    class_name = class_info["name"]
                    source = self.get_class_source(pickled_load, class_name)
                    self.graph.add_node(
                        class_name,
                        type="class",
                        file=file,
                        source=source,
                    )

                for function_info in functions:
                    function_name = function_info["name"]
                    class_name = function_to_class.get(function_name)
                    source = self.get_function_source(pickled_load, function_name)
                    if class_name:
                        self.graph.add_node(
                            function_name,
                            type="function",
                            parent_object=class_name,
                            file=file,
                            source=source,
                        )

                        self.graph.add_edge(
                            class_name,
                            function_name,
                            type="belongs_to_class",
                            file=file,
                        )
                    else:
                        self.graph.add_node(
                            function_name,
                            type="function",
                            object=None,
                            file=file,
                            source=source,
                        )

            logging.info("Nodes added successfully")
            return True

        except Exception as e:
            logging.error(f"Error adding nodes: {e}")
            return False

    def get_function_source(self, tree: ast.AST, name: str) -> str:
        """Recursively obtain the source code of a function by navigating the AST."""
        if tree is None or name is None:
            logging.error("No tree or function name provided")
            return ""

        if isinstance(tree, ast.FunctionDef) and tree.name == name:
            return astor.to_source(tree)

        # Recursively search the body
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_source = self.get_function_source(node, name)
                if class_source:
                    return class_source
            elif isinstance(node, ast.FunctionDef):
                if node.name == name:
                    return astor.to_source(node)

        logging.warning(f"No matching function found in file for function {name}")
        return ""

    def get_class_source(self, tree: ast.AST, name: str) -> str:
        """Recursively obtain the source code of a class by navigating the AST."""
        if tree is None or name is None:
            logging.error("No tree or class name provided")
            return ""

        if isinstance(tree, ast.ClassDef) and tree.name == name:
            return astor.to_source(tree)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_source = self.get_class_source(node, name)
                if class_source:
                    return class_source
            elif isinstance(node, ast.FunctionDef):
                continue

        logging.warning(f"No matching class found in file for Class {name}")
        return ""

    def add_inheritance_edges(self) -> bool:
        """Adds inheritance edges to the graph based on the given data from extraction

        Returns:
            bool: true if edges are added successfully, false otherwise
        """
        try:
            logging.info("Adding inheritance edges to the graph")
            for file in self.data:
                for class_info in self.data[file]["metadata"]["classes"]:
                    class_name = class_info["name"]
                    for base in class_info["bases"]:
                        self.graph.add_edge(base, class_name, type="inheritance")
            logging.info("Inheritance edges added successfully")
            return True
        except Exception as e:
            logging.error(f"Error adding inheritance edges: {e}")
            return False

    def add_function_edges(self) -> bool:
        """Adds function argument edges to the graph, excluding `self`"""
        try:
            logging.info("Adding function argument edges to the graph")
            for file in self.data:
                for function_info in self.data[file]["metadata"]["functions"]:
                    function_name = function_info["name"]

                    for arg in function_info["args"]:
                        if arg != "self":
                            if not self.graph.has_node(arg):
                                self.graph.add_node(arg, type="argument")

                            self.graph.add_edge(arg, function_name, type="function_arg")

            logging.info("Function argument edges added successfully")
            return True

        except Exception as e:
            logging.error(f"Error adding function argument edges: {e}")
            return False

    def generate_unified_graph(self) -> bool:
        """Generates a unified graph based on the given data from extraction

        Returns:
            bool: true if the graph is generated, false otherwise
        """
        try:
            logging.info("Generating unified graph")
            self.add_nodes()
            self.add_inheritance_edges()
            self.add_function_edges()
            logging.info("Unified graph generated successfully")
            return True

        except Exception as e:
            logging.error(f"Error generating unified graph: {e}")
            return False

    def visualize_graph(self) -> bool:
        """Visualizes the graph using matplotlib with different colors for each node type

        Returns:
            bool: true if the graph is visualized, false otherwise
        """
        try:
            logging.info("Visualizing graph")

            node_colors = []
            for node in self.graph.nodes:
                node_type = self.graph.nodes[node].get("type", "")
                if node_type == "class":
                    node_colors.append("lightblue")
                elif node_type == "function":
                    node_colors.append("lightgreen")
                elif node_type == "argument":
                    node_colors.append("lightcoral")
                else:
                    node_colors.append("gray")

            pos = nx.spring_layout(self.graph)
            nx.draw(
                self.graph,
                pos,
                with_labels=True,
                node_color=node_colors,
                font_weight="bold",
                node_size=3000,
                font_size=10,
            )
            plt.show()
            logging.info("Graph visualized successfully")
            return True

        except Exception as e:
            logging.error(f"Error visualizing graph: {e}")
            return False

    def print_graph_data(self):
        """Prints the graph data"""
        try:
            logging.info("Printing graph data")
            for node in self.graph.nodes:
                print(f"Node: {node}, Data: {self.graph.nodes[node]}")
            for edge in self.graph.edges:
                print(f"Edge: {edge}, Data: {self.graph.edges[edge]}")
            logging.info("Graph data printed successfully")
        except Exception as e:
            logging.error(f"Error printing graph data: {e}")
            return False
