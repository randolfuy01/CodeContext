from graph_generator import Knowledge_Graph as graph
from neo4j import GraphDatabase
import networkx as nx
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class builder:
    """
    Generates a knowledge graph and builds it into a Neo4j database
    """
    
    def __init__(self, root_path: str, uri: str, username: str, password: str):
        self.knowledge_graph: nx.DiGraph = graph(root_path).generate_unified_graph()
        self.driver= GraphDatabase.driver(uri, auth=(username, password))
                  
    def load_networkx_to_neo4j(self) -> None:
        """
        Loads a NetworkX graph into a Neo4j database.
        """
        try:
            logging.info("Loading NetworkX graph into Neo4j database.")
            with self.driver.session() as session:
            
                for node in self.knowledge_graph.nodes(data=True):
                    node_name = node[0]
                    node_type = node[1]['type']
                    session.run(f"CREATE (n:{node_type} {{name: '{node_name}'}})")
            
                for u, v in self.knowledge_graph.edges():
                    session.run("""
                        MATCH (a:Node {id: $id1}), (b:Node {id: $id2})
                        MERGE (a)-[:CONNECTED]->(b)
                    """, id1=u, id2=v)
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
                logging.info(f"Neo4j graph has {node_count} nodes and {edge_count} edges.")
        
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