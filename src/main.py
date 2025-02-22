from graph.builder import builder
from dotenv import load_dotenv
import logging
import os

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger('neo4j').setLevel(logging.WARNING)

load_dotenv()

def main():
    root_path = "./test_src"
    try:
        logging.info("Loading data and generating driver")
        graph_builder = builder(
            root_path, 
            uri=os.getenv("NEO_URI"),
            username=os.getenv("NEO_USERNAME"),
            password=os.getenv("NEO_PASSWORD")
        )
        
        with graph_builder.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

        graph_builder.build()
    
        logging.info(f"Initialized graph based on on the directory {root_path}")
    except Exception as e:
        logging.error(f"Unable to initiate graph builder and generate graph {e}")
        return 


if __name__ == "__main__":
    main()
