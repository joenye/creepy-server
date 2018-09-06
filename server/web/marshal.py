import json

from marshmallow import Schema


def marshal(data, schema: Schema = None, is_json: bool = True):
    if schema:
        is_list = isinstance(data, list)
        data = schema.dump(data, many=is_list)
    return json.dumps(data) if is_json else data
