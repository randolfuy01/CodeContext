from extractor import Python_Extractor, FileMetadata
from typing import Dict, Union
import networkx as nx
import matplotlib.pyplot as plt
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Knowledge_Graph(Python_Extractor):
    """Knowledege graph creation based on extracting code"""

    """
    Example Schema of the data extracted for a given file
    
            {
            "path/to/file1.py": {
                "metadata": {
                    "functions": [
                        {"name": "func1", "args": ["arg1", "arg2"]},
                        {"name": "func2", "args": ["arg1"]}
                    ],
                    "classes": [
                        {"class_name": "Class1", "bases": ["BaseClass"], "methods": ["method1", "method2"]},
                        {"class_name": "Class2", "bases": [], "methods": ["method1"]}
                    ],
                    "imports": ["os", "sys"],
                    "variables": ["var1", "var2"],
                    "inheritance": ["BaseClass"],
                    "syntax_error": False
                },
                "ast_dump": "Module(body=[FunctionDef(name='func1', args=arguments(args=[arg(arg='arg1', annotation=None), arg(arg='arg2', annotation=None)], vararg=None), body=[Expr(value=Call(func=Name(id='print', ctx=Load()), args=[Name(id='arg1', ctx=Load())], keywords=[])])])"
            }
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

    def add_class_node(self) -> bool:
        """Adds class nodes to the graph based on the given data from extraction

        Returns:
            bool: true if nodes are added successfully, false otherwise
        """
        try:
            logging.info("Adding class nodes to the graph")
            for file in self.data:
                for class_info in self.data[file]["metadata"]["classes"]:
                    class_name = f"{file}_{class_info['class_name']}"
                    self.graph.add_node(class_name, type="class")
                    for method_name in class_info["methods"]:

                        if not self.graph.has_node(method_name):
                            self.graph.add_node(method_name, type="function")

                        if not self.graph.has_edge(class_name, method_name):
                            self.graph.add_edge(
                                class_name, method_name, type="belongs_to_class"
                            )
            logging.info("Class nodes added successfully")
            return True
        except Exception as e:
            logging.error(f"Error adding class nodes: {e}")
            return False

    def add_function_node(self) -> bool:
        """Adds function nodes to the graph based on the given data from extraction

        Returns:
            bool: true if nodes are added successfully, false otherwise
        """
        try:
            logging.info("Adding function nodes to the graph")

            for file in self.data:
                for function_info in self.data[file]["metadata"]["functions"]:
                    function_name = function_info["name"]
                    self.graph.add_node(function_name, type="function")

            logging.info("Function nodes added successfully")
            return True

        except Exception as e:
            logging.error(f"Error adding function nodes: {e}")
            return False

    def add_inheritance_edges(self) -> bool:
        """Adds inheritance edges to the graph based on the given data from extraction

        Returns:
            bool: true if edges are added successfully, false otherwise
        """
        try:
            logging.info("Adding inheritance edges to the graph")
            for file in self.data:
                for class_info in self.data[file]["metadata"]["classes"]:
                    class_name = class_info["class_name"]
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
            self.add_class_node()
            self.add_function_node()
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
        