
#include "apmatrix.h"
#include <iostream>
#include "pathindex.h"

void ApMatrix::set_bit(unsigned int row, unsigned col) {
    PathIndex index;
    uint32_t *middles = static_cast<uint32_t *>(malloc(sizeof(uint32_t)));
    middles[0] = size; //size --- means that this is edge
    PathIndex_Init(&index, row, col, middles, 1);
    GrB_Matrix_setElement_UDT(m, (void *) &index, row, col);
}

PathIndex* ApMatrix::get_bit(unsigned int row, unsigned col) {
    PathIndex* index = new PathIndex;
    PathIndex_Init(index, 0, 0, 0, 0);
    GrB_Matrix_extractElement_UDT((void *) index, m, row, col);
    return index;
}

ApMatrix::~ApMatrix() {
    GrB_Matrix_clear(m);
    GrB_Matrix_free(&m);
}

uint32_t ApMatrix::get_nvals()
{
    GrB_Index count;
    GrB_Matrix_nvals(&count, m);
    return count;
}

char* ApMatrix::get_elements()
{
    GrB_Index nvals = get_nvals();
    GrB_Index *I = static_cast<GrB_Index *>(malloc(nvals * sizeof(GrB_Index)));
    GrB_Index *J = static_cast<GrB_Index *>(malloc(nvals * sizeof(GrB_Index)));
    PathIndex *X = static_cast<PathIndex *>(malloc(nvals * sizeof(PathIndex)));
    GrB_Matrix_extractTuples_UDT(I, J, X, &nvals, m);
    char* result = (char *)malloc(nvals*25*sizeof(char));    //???
    std::string start = "";
    strcpy(result, start.c_str());
    for (int k = 0; k < nvals; ++k)
    {

        std::string indexes = std::to_string(X[k].left) + " " + std::to_string(X[k].right) + "\n";
        strcat(result, indexes.c_str());
    }
    free(I);
    free(J);
    free(X);
    return result;
}

bool ApMatrix::add_mul(ApMatrix *A, ApMatrix *B) {
    GrB_Info info;
    GrB_Matrix m_old;
    GrB_Matrix_dup(&m_old, m);
    info = GrB_mxm(m, GrB_NULL, IndexType_Add, IndexType_Semiring, A->m, B->m, GrB_NULL);
    GrB_Index nvals_new, nvals_old;
    GrB_Matrix_nvals(&nvals_old, m_old);
    GrB_Index *I = static_cast<GrB_Index *>(malloc(nvals_old * sizeof(GrB_Index)));
    GrB_Index *J = static_cast<GrB_Index *>(malloc(nvals_old * sizeof(GrB_Index)));
    PathIndex *X = static_cast<PathIndex *>(malloc(nvals_old * sizeof(PathIndex)));
    int sum_old = 0;
    GrB_Matrix_extractTuples_UDT(I, J, X, &nvals_old, m_old);
    for (int k = 0; k < nvals_old; ++k) {
        sum_old += X[k].size;
    }
    free(I);
    free(J);
    free(X);

    GrB_Matrix_nvals(&nvals_new, m);
    I = static_cast<GrB_Index *>(malloc(nvals_new * sizeof(GrB_Index)));
    J = static_cast<GrB_Index *>(malloc(nvals_new * sizeof(GrB_Index)));
    X = static_cast<PathIndex *>(malloc(nvals_new * sizeof(PathIndex)));
    int sum_new = 0;
    GrB_Matrix_extractTuples_UDT(I, J, X, &nvals_new, m);
    for (int k = 0; k < nvals_new; ++k) {
        sum_new += X[k].size;
    }
    free(I);
    free(J);
    free(X);

    bool changed = sum_new != sum_old;
    GrB_Matrix_free(&m_old);
    return changed;
}
