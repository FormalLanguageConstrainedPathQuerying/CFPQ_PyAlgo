from load_graph import load_graph
from intersection import intersection
from gen_automata import generate
import time

def add_context(file_path):
    load_graph_start = time.perf_counter()
    
    graph,number_of_contexts = load_graph(file_path)
    
    load_graph_end = time.perf_counter()
    print("Graph loaded in ", load_graph_end - load_graph_start)
    
    automata = generate(number_of_contexts)
    
    automata_generation_end = time.perf_counter()
    print("Automata generated in ", automata_generation_end - load_graph_end)

    result = intersection(graph, automata)

    intersection_end = time.perf_counter()
    print("Graph and automata intersection competed in ", intersection_end - automata_generation_end)
    
    return result