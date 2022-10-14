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


def mask_texts(record, roles):
    for r in roles:
        if r in ["admin", "contributor", "corrector"]:
            return record

    new_record = record.copy()
    new_record["raw_text"] = "***"
    new_record["auto_anonymized_text"] = "***"

    new_record["auto_anonymized_aliases"] = [
        {"alias": a["alias"], "alias_type": a["alias_type"], "text": "***"}
        for a in new_record.get("auto_anonymized_aliases", [])
    ]
    new_record["manual_anonymized_aliases"] = [
        {"alias": a["alias"], "alias_type": a["alias_type"], "text": "***"}
        for a in new_record.get("manual_anonymized_aliases", [])
    ]
    return new_record
