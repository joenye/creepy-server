import os


def get_data_path(relative_path: str, filename: str = '') -> str:
    """Returns the absolute path to a file.

    :param relative_path: Path relative to the project root.
    :param filename: Optionally, the name of a file located at the file_path.
    :returns: Absolute path to the file.

    """
    return os.path.join(_data_directory_path(relative_path), filename)


def _data_directory_path(relative_path: str) -> str:
    dirname = os.path.abspath(os.path.dirname(__file__))

    tokens, path = dirname.split(os.sep), ['/']
    for token in tokens:
        if not token:
            continue
        path.append(token)

    path.append(relative_path)
    return os.path.join(*path)


def load_text_file(file_dir: str, filename: str) -> str:
    """Loads a text file into a string.

    :param file_dir: Directory of the file.
    :param filename: Name of the file.
    :returns: String containing the file's contents, absent newline characters.

    """
    with open(file_dir + '/' + filename, 'r') as myfile:
        data = myfile.read().replace('\n', '')

    return data
