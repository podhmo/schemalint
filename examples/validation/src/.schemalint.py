import pathlib


def get_schema(filepath: str):
    path = pathlib.Path(filepath).parent / ("schema.json")
    return str(path.absolute())
