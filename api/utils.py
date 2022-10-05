def format_object_id(record):
    record["object_id"] = str(record["_id"])
    return record
