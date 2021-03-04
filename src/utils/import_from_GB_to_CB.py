import pycubool


def import_to_cubool(matrices: dict) -> dict:
    new_matrices = dict()
    for label in matrices:
        matrix_list = matrices[label].to_lists()
        matrices_size = matrices[label].nrows
        new_matrices[label] = pycubool.Matrix.from_lists([matrices_size, matrices_size], matrix_list[0],
                                                         matrix_list[1])
        matrices[label].clear()
    return new_matrices