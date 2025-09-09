import graphblas

from graphblas.core.operator import Monoid, BinaryOp
from graphblas import binary

'''
|---------------21 bit-----------|---------------21 bit-------------|---------------22 bit-----------|
|_open context (pass_i, ret_r_i)_|_ close context (ret_i, pass_r_i)_|____________other_______________|

64 bit total
'''

SIGMA =                       0b1111111111111111111111111111111111111111111111111111111111111111
SIGMA_WITHOUT_CONTEXTS =      0b0000000000000000000000000000000000000000001111111111111111111111
ALL_OPEN_CONTEXTS =           0b1111111111111111111110000000000000000000000000000000000000000000
SIGMA_WITHOUT_OPEN_CONTEXTS = 0b0000000000000000000001111111111111111111111111111111111111111111
NOTHING =                     0b0000000000000000000000000000000000000000000000000000000000000000

def intersection_op (x:int, y:int) -> int:
    return (NOTHING - (x == y or (x & y == x and (y == SIGMA or y == SIGMA_WITHOUT_CONTEXTS or y == ALL_OPEN_CONTEXTS or y == SIGMA_WITHOUT_OPEN_CONTEXTS)))) & x

BinaryOp.register_new("intersection_op", intersection_op)
Monoid.register_new("labels_intersection", binary.intersection_op, identity=NOTHING)

def mk_open_context(x:int) -> int : 
    return NOTHING | (x << 43)
def mk_close_context(x:int) -> int : 
    return NOTHING | (x << 22)
def mk_other(x:int) -> int : 
    return NOTHING | x