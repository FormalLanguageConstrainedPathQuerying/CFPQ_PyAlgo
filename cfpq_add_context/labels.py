import graphblas

from graphblas.core.operator import Monoid, BinaryOp, SelectOp, UnaryOp
from graphblas import binary

'''
|---------------21 bit-----------|---------------21 bit-------------|---------------22 bit-----------|
|_open context (pass_i, ret_r_i)_|_ close context (ret_i, pass_r_i)_|____________other_______________|

64 bit total
'''

SIGMA =                       0b1111111111111111111111111111111111111111111111111111111111111111
SIGMA_WITHOUT_CONTEXTS =      0b0000000000000000000000000000000000000000001111111111111111111111
ALL_OPEN_CONTEXTS =           0b1111111111111111111110000000000000000000000000000000000000000000
ALL_CLOSE_CONTEXTS =          0b0000000000000000000001111111111111111111110000000000000000000000
SIGMA_WITHOUT_OPEN_CONTEXTS = 0b0000000000000000000001111111111111111111111111111111111111111111
NOTHING =                     0b0000000000000000000000000000000000000000000000000000000000000000

ASSIGN = 1
ASSIGN_R = 2
ALLOC = 3
ALLOC_R = 4
OFFSET = 5

def intersection_op (x:int, y:int) -> int:
    return (NOTHING - (x == y or (x & y == x and (y == SIGMA or y == SIGMA_WITHOUT_CONTEXTS or y == ALL_OPEN_CONTEXTS or y == SIGMA_WITHOUT_OPEN_CONTEXTS)))) & x

BinaryOp.register_new("intersection_op", intersection_op)
Monoid.register_new("labels_intersection", binary.intersection_op, identity=NOTHING)

#def mk_open_context(x:int) -> int : 
#    return NOTHING | (x << 43)
#def mk_close_context(x:int) -> int : 
#    return NOTHING | (x << 22)

def mk_open_context_from_pass(x:int) -> int : 
    return NOTHING | ((2 * (x + 1) + 1) << 43)
def mk_close_context_from_ret(x:int) -> int : 
    return NOTHING | ((2 * (x + 1) + 1) << 22)

def mk_open_context_from_ret_r(x:int) -> int : 
    return NOTHING | ((2 * (x + 1)) << 43)
def mk_close_context_from_pass_r(x:int) -> int : 
    return NOTHING | ((2 * (x + 1)) << 22)


def mk_other(x:int) -> int : 
    return NOTHING | x
def mk_load(i):
    return mk_other(4 * i + OFFSET)
def mk_load_r(i):
    return mk_other(4 * i + 1 + OFFSET)
def mk_store (i):
    return mk_other(4 * i + 2 + OFFSET)
def mk_store_r (i):
    return mk_other(4 * i + 3 + OFFSET)


def select_alloc_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS == ALLOC

def select_alloc_r_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS == ALLOC_R

def select_assign_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS == ASSIGN or (x & ALL_OPEN_CONTEXTS > 0 and ((x & ALL_OPEN_CONTEXTS) >> 43) % 2 == 1) or (x & ALL_CLOSE_CONTEXTS > 0 and ((x & ALL_CLOSE_CONTEXTS) >> 22) % 2 == 1)

def select_assign_r_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS == ASSIGN_R or (x & ALL_OPEN_CONTEXTS > 0 and ((x & ALL_OPEN_CONTEXTS) >> 43) % 2 == 0) or (x & ALL_CLOSE_CONTEXTS > 0 and ((x & ALL_CLOSE_CONTEXTS) >> 22) % 2 == 0)

def select_load_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS >= OFFSET and ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) % 4 == 0

def select_load_r_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS >= OFFSET and ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) % 4 == 1

def select_store_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS >= OFFSET and ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) % 4 == 2

def select_store_r_op(x,i,j,k):
    return x & SIGMA_WITHOUT_CONTEXTS >= OFFSET and ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) % 4 == 3

def select_not_reversed_op(x,i,j,k):
    return ( (x & SIGMA_WITHOUT_CONTEXTS == ALLOC) or 
             (x & SIGMA_WITHOUT_CONTEXTS == ASSIGN or (x & ALL_OPEN_CONTEXTS > 0 and ((x & ALL_OPEN_CONTEXTS) >> 43) % 2 == 1) or (x & ALL_CLOSE_CONTEXTS > 0 and ((x & ALL_CLOSE_CONTEXTS) >> 22) % 2 == 1)) or 
             (x & SIGMA_WITHOUT_CONTEXTS >= OFFSET and ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) % 4 == 0) or 
             (x & SIGMA_WITHOUT_CONTEXTS >= OFFSET and ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) % 4 == 2)
    )


SelectOp.register_new("select_alloc", select_alloc_op)
SelectOp.register_new("select_alloc_r", select_alloc_r_op)
SelectOp.register_new("select_assign", select_assign_op)
SelectOp.register_new("select_assign_r", select_assign_r_op)
SelectOp.register_new("select_load", select_load_op)
SelectOp.register_new("select_store", select_store_op)
SelectOp.register_new("select_load_r", select_load_r_op)
SelectOp.register_new("select_store_r", select_store_r_op)
SelectOp.register_new("select_not_reversed", select_not_reversed_op)

def decode_load_op(x):
    return ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET) // 4

def decode_load_r_op(x):
    return ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET - 1) // 4

def decode_store_op(x):
    return ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET - 2) // 4

def decode_store_r_op(x):
    return ((x & SIGMA_WITHOUT_CONTEXTS) - OFFSET - 3) // 4


UnaryOp.register_new("decode_load", decode_load_op)
UnaryOp.register_new("decode_load_r", decode_load_r_op)
UnaryOp.register_new("decode_store", decode_store_op)
UnaryOp.register_new("decode_store_r", decode_store_r_op)