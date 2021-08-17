#ifndef APMATRIX_H
#define APMATRIX_H

extern "C" {
#include "GraphBLAS.h"
}
#include "pathindex.h"

class ApMatrix
{
public:
    explicit ApMatrix(unsigned int n) {
        GrB_Matrix_new(&m, PathIndexType, n, n);
        size = n;
    }

    ~ApMatrix();

    void set_bit(unsigned int row, unsigned col);
    uint32_t get_nvals();
    char* get_elements();

    PathIndex* get_bit(unsigned int row, unsigned col);

    bool add_mul(ApMatrix *A, ApMatrix *B);

    unsigned int get_size()
    {
        return size;
    }

private:
    GrB_Matrix m;
    unsigned int size;

};

#endif // APMATRIX_H
