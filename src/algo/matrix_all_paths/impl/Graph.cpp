
#include <fstream>
#include <iostream>
#include "Graph.h"

using std::string;
using std::ifstream;
using std::max;

Graph::Graph(const string &graph_filename) {
    auto graph_stream = ifstream(graph_filename, ifstream::in);
    unsigned int from, to;
    string terminal;
    while (graph_stream >> from >> terminal >> to) {
        edges.push_back({terminal, {from, to}});
        vertices_count = max(vertices_count, max(from, to) + 1);
    }
    graph_stream.close();
}
