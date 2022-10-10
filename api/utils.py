def format_object_id(record):
    record["object_id"] = str(record["_id"])
    return record


def format_aliases(aliases: dict):
    formatted_aliases = []
    for text, alias in aliases.items():
        formatted_aliases.append(
            {"text": text, "alias": alias, "alias_type": alias.split("_")[0]}
        )
    return formatted_aliases
