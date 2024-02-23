import os


def find_single_file_with_extension(directory_path, extension):
    if not extension.startswith('.'):
        extension = '.' + extension

    files_with_extension = [f for f in os.listdir(directory_path)
                            if os.path.isfile(os.path.join(directory_path, f)) and f.endswith(extension)]

    if len(files_with_extension) == 1:
        return os.path.join(directory_path, files_with_extension[0])
    elif len(files_with_extension) == 0:
        raise FileNotFoundError(f"No files with extension '{extension}' found in {directory_path}")
    else:
        raise Exception(
            f"Multiple files with extension '{extension}' found in {directory_path}")


def find_graph_file(pocr_data_path):
    return find_single_file_with_extension(pocr_data_path, ".g")


def find_grammar_file(pocr_data_path):
    return find_single_file_with_extension(pocr_data_path, ".cnf")


def read_tuples_set(file):
    return set(tuple(line.split()) for line in file.readlines() if line != "")
