
#ifndef CFPQ_GRAPH_H
#define CFPQ_GRAPH_H

#include <string>
#include <vector>

using edge = std::pair<std::string, std::pair<unsigned int, unsigned int>>;

class Graph {
public:
    explicit Graph(const std::string &graph_filename);

    virtual ~Graph() = default;

    std::vector<edge> edges;

    unsigned int vertices_count = 0;
};

#endif //CFPQ_GRAPH_H
