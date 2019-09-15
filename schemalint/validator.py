import jsonschema


def get_validator(schema: dict, *, check_schema=True) -> jsonschema.Draft7Validator:
    cls = jsonschema.Draft7Validator
    if check_schema:
        cls.check_schema(schema)
    validator = cls(schema=schema)
    return validator
