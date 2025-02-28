from .graph_generator import Knowledge_Graph
from neo4j import GraphDatabase
import networkx as nx
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("numexpr").setLevel(logging.WARNING)


class builder:
    """
    Generates a knowledge graph and builds it into a Neo4j database as well as store dump into postgres
    """

    def __init__(self, root_path: str, uri: str, username: str, password: str):
        self.knowledge_graph: nx.DiGraph = Knowledge_Graph(root_path)
        self.knowledge_graph.generate_unified_graph()
        self.knowledge_graph = self.knowledge_graph.graph
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def load_networkx_to_neo4j(self) -> None:
        """
        Loads a NetworkX graph into a Neo4j database.
        """
        try:
            logging.info("Loading NetworkX graph into Neo4j database.")
            with self.driver.session() as session:

                for node_name, attrs in self.knowledge_graph.nodes(data=True):
                    node_type = attrs.get("type", "Node")

                    # Prepare dynamic properties dictionary for Cypher query
                    properties = {
                        key: value for key, value in attrs.items() if key != "type"
                    }

                    # Convert the properties into a Neo4j-friendly format (Cypher)
                    set_properties = ", ".join([f"{key}: ${key}" for key in properties])

                    # MERGE to avoid creating duplicates
                    session.run(
                        f"MERGE (n:{node_type} {{name: $name}}) SET n += {{ {set_properties} }}",
                        name=node_name,
                        **properties,
                    )

                for u, v in self.knowledge_graph.edges():
                    session.run(
                        """
                        MATCH (a {name: $name1}), (b {name: $name2})
                        MERGE (a)-[:CONNECTED]->(b)
                        """,
                        name1=u,
                        name2=v,
                    )

            logging.info("NetworkX graph loaded into Neo4j database successfully.")

        except Exception as e:
            logging.error(f"Error loading NetworkX graph into Neo4j database: {e}")

    def verify_neo4j_graph(self) -> None:
        """
        Verifies the Neo4j graph by checking the number of nodes and edges.
        """
        try:
            logging.info("Verifying Neo4j graph.")
            with self.driver.session() as session:

                result = session.run("MATCH (n) RETURN count(n) as count")
                node_count = result.single()[0]

                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                edge_count = result.single()[0]
                logging.info(
                    f"Neo4j graph has {node_count} nodes and {edge_count} edges."
                )

        except Exception as e:
            logging.error(f"Error verifying Neo4j graph: {e}")

    def close(self) -> None:
        """
        Closes the Neo4j driver.
        """
        self.driver.close()

    def build(self) -> None:
        """
        Builds the knowledge graph into a Neo4j database.
        """
        self.load_networkx_to_neo4j()
        self.verify_neo4j_graph()
        self.close()
