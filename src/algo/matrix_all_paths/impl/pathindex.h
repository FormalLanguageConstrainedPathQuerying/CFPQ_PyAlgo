#ifndef PATHINDEX_H
#define PATHINDEX_H
#include <stdint.h>
#include <iostream>
extern "C" {
#include "GraphBLAS.h"
}

typedef struct {
    uint32_t left;
    uint32_t right;
    uint32_t *middle;
    uint32_t size;
} PathIndex;

extern GrB_BinaryOp IndexType_Add;
extern GrB_BinaryOp IndexType_Mul;
extern GrB_Monoid IndexType_Monoid;
extern GrB_Semiring IndexType_Semiring;
extern GrB_Type PathIndexType;

void InitGBSemiring();

extern bool isChanged;
extern PathIndex PathIndex_Identity;

void PathIndex_Init(PathIndex *index, uint32_t left, uint32_t right, uint32_t* middle, uint32_t size);
void PathIndex_InitIdentity(PathIndex *index);
void PathIndex_Copy(const PathIndex *from, PathIndex *to);

bool PathIndex_IsIdentity(PathIndex *index);

void PathIndex_Mul(void *z, const void *x, const void *y);
void PathIndex_Add(void *z, const void *x, const void *y);

void PathIndex_ToStr(PathIndex *index);
void PathIndex_Show(PathIndex *index);

void PathIndex_MatrixShow(const GrB_Matrix *matrix);
#endif // PATHINDEX_H
