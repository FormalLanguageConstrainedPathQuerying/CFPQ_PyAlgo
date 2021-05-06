#include "pathindex.h"

bool isChanged = false;

PathIndex PathIndex_Identity = {
        .left = 0,
        .right = 0,
        .middle = 0,
        .size = 0,
};

// Identity = невыводимый путь

GrB_BinaryOp IndexType_Add;
GrB_BinaryOp IndexType_Mul;
GrB_Monoid IndexType_Monoid;
GrB_Semiring IndexType_Semiring;
GrB_Type PathIndexType;

void InitGBSemiring()
{
    GrB_Type_new (&PathIndexType, sizeof(PathIndex));
    GrB_BinaryOp_new(&IndexType_Add, PathIndex_Add, PathIndexType, PathIndexType, PathIndexType);
    GrB_BinaryOp_new(&IndexType_Mul, PathIndex_Mul, PathIndexType, PathIndexType, PathIndexType);
    GrB_Monoid_new_UDT(&IndexType_Monoid, IndexType_Add, (void *) &PathIndex_Identity);
    GrB_Semiring_new(&IndexType_Semiring, IndexType_Monoid, IndexType_Mul);
}

void PathIndex_Init(PathIndex *index, uint32_t left, uint32_t right, uint32_t* middle, uint32_t size) {
    index->left = left;
    index->right = right;
    index->middle = middle;
    index->size = size;
    //index->isEdge = isEdge;
}

void PathIndex_InitIdentity(PathIndex *index) {
    index->left = 0;
    index->right = 0;
    index->middle = 0;
    index->size = 0;
}

bool PathIndex_IsIdentity(PathIndex *index) {
    return (index->size == 0);
}

void PathIndex_Copy(const PathIndex *from, PathIndex *to) {
    to->left = from->left;
    to->right = from->right;
    to->middle = static_cast<uint32_t *>(malloc(from->size * sizeof(uint32_t)));
    for (uint32_t i = 0; i < from->size; ++i)
    {
        to->middle[i] = from->middle[i];
    }
    to->size = from->size;
}

void PathIndex_Mul(void *z, const void *x, const void *y) {
    //std::cout << "MUL" << std::endl;
    PathIndex *left = (PathIndex *) x;
    PathIndex *right = (PathIndex *) y;
    PathIndex *res = (PathIndex *) z;

    if (!PathIndex_IsIdentity(left) && !PathIndex_IsIdentity(right)) {
        uint32_t *middle = static_cast<uint32_t *>(malloc(sizeof(uint32_t)));
        middle[0] = left->right;
        PathIndex_Init(res, left->left, right->right, middle, 1/*, false*/);
    } else {
        PathIndex_InitIdentity(res);
    }
}

uint32_t Merge_Middles(uint32_t *res, uint32_t* left, uint32_t lsize, uint32_t* right, uint32_t rsize)
{
    uint32_t pres = 0, pl = 0, pr = 0;
    while(pl != lsize || pr != rsize)
    {
        if (pl == lsize)
        {
            res[pres] = right[pr];
            pres++;
            pr++;
        }
        else if (pr == rsize)
        {
            res[pres] = left[pl];
            pres++;
            pl++;
        }
        else
        {
            uint32_t x1 = left[pl];
            uint32_t x2 = right[pr];
            if(x1 == x2)
            {
                res[pres] = x1;
                pres++;
                pr++;
                pl++;
            }
            else if (x1 < x2)
            {
                res[pres] = x1;
                pres++;
                pl++;
            }
            else
            {
                res[pres] = x2;
                pres++;
                pr++;
            }
        }
    }
    return pres;
}

void PathIndex_Add(void *z, const void *x, const void *y) {
    //std::cout << "ADD" << std::endl;
    PathIndex *left = (PathIndex *) x;
    PathIndex *right = (PathIndex *) y;
    PathIndex *res = (PathIndex *) z;

    if (!PathIndex_IsIdentity(left) && !PathIndex_IsIdentity(right)) {
        uint32_t* middle = static_cast<uint32_t *>(malloc((left->size + right->size)*sizeof(uint32_t)));
        uint32_t res_size = Merge_Middles(middle, left->middle, left->size, right->middle, right->size);
        uint32_t* new_res = static_cast<uint32_t *>(malloc(res_size*sizeof(uint32_t)));
        for (uint32_t i = 0; i < res_size; ++i)
        {
            new_res[i] = middle[i];
        }
        free(middle);
        middle = new_res;
        PathIndex_Init(res, left->left, right->right, middle, res_size);
    } else if (PathIndex_IsIdentity(left)) {
        PathIndex_Copy(right, res);
    } else {
        PathIndex_Copy(left, res);
    }
}


void PathIndex_ToStr(PathIndex *index) {
    if (PathIndex_IsIdentity(index)) {
        std::cout << "(     Identity      )";
    } else {
        std::cout << "(i:" << index->left << ",j:" << index->right << ",k:[";
        for (uint32_t i = 0; i < index->size; ++i)
        {
            std::cout << index->middle[i] << ",";
        }
        std::cout << "],size=" << index->size << ")";
    }
}

void PathIndex_Show(PathIndex *index) {
    PathIndex_ToStr(index);
}


void PathIndex_MatrixShow(const GrB_Matrix *matrix) {
    GrB_Index n, m;
    GrB_Matrix_nrows(&n, *matrix);
    GrB_Matrix_ncols(&m, *matrix);


    for (GrB_Index i = 0; i < n; i++) {
        for (GrB_Index j = 0; j < m; j++) {
            PathIndex index;
            PathIndex_InitIdentity(&index);

            GrB_Matrix_extractElement_UDT((void *) &index, *matrix, i, j);
            std::cout << "(i: " << i << ", j: " << j << ", index: ";
            PathIndex_ToStr(&index);
            std::cout << ")" << std::endl;
        }
        std::cout << std::endl;
    }
}
