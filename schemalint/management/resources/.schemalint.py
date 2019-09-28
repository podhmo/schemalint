from schemalint.management import resolve


def get_schema(filepath: str) -> str:
    return resolve(schema="./schemalint-resources-schema.json")
