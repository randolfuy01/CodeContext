from graph_generator import Knowledge_Graph as graph
import logging

def main():
    """
        End to end testing for code to understand how the dependencies are working
    """
    knowledge_graph = graph('./test_src')
    knowledge_graph.generate_unified_graph()
    knowledge_graph.visualize_graph()
    knowledge_graph.print_graph_data()
    
if __name__ == '__main__':
    main()