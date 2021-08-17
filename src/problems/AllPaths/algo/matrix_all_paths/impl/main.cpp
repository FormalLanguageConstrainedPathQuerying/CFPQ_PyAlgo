#include <iostream>
#include <chrono>
#include <fstream>
#include <fstream>
extern "C" {
#include "GraphBLAS.h"
}
#include <stdio.h>
#include "Grammar.h"
#include "Graph.h"
#include "apmatrix.h"
#include "pathindex.h"
using namespace std;

extern "C" {

void string_del(char *elements)
{
    free(elements);
}

Grammar *grammar_new(char *name) {
    return new Grammar(name);
}

void grammar_del(Grammar* grammar)
{
    delete grammar;
}

Graph *graph_new(char *name) {
    return new Graph(name);
}

void graph_del(Graph* graph)
{
    delete graph;
}

void graphblas_init()
{
    GrB_init(GrB_NONBLOCKING);
    InitGBSemiring();
}

void graphblas_finalize()
{
    GrB_Semiring_free(&IndexType_Semiring);
    GrB_Monoid_free(&IndexType_Monoid);
    GrB_BinaryOp_free(&IndexType_Add);
    GrB_BinaryOp_free(&IndexType_Mul);
    GrB_Type_free(&PathIndexType);
    GrB_finalize();
}

void intersect(Grammar* grammar, Graph* graph)
{
    auto times = grammar->intersection_with_graph(*graph);
}

char* get_elements(Grammar* grammar, char *S)
{
    return grammar->get_elements(S);
}

int getpaths(Grammar* grammar, int i, int j, char *S, int current_len)
{
    std::vector<int> res = grammar->get_paths(i, j, S, current_len);
    int result = res.size();

    return result;
}

}

int main(int argc, char *argv[]) {
    return 0;
}
