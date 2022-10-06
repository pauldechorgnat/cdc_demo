import nltk
from flair.data import Sentence
from flair.models import SequenceTagger


def get_entities(
    tagger: SequenceTagger,
    raw_text: str,
    aliases_to_anonymize: list = ["LOC", "PER", "ORG"],
) -> dict:
    """Returns a dictionary of named entities with a unique ID

    Args:
        tagger (SequenceTagger): Flair SequenceTagger to perform NER
        raw_text (str): Sentence to alias
        aliases_to_anonymize (list, optional): List of aliases to keep.
            Defaults to ["LOC", "PER", "ORG"].

    Returns:
        dict: dictionary with unique entities as keys and unique alias as values
    """
    texts = [Sentence(s) for s in nltk.sent_tokenize(raw_text)]

    tagger.predict(texts)

    entities = {}

    for s in texts:
        for entity in s.get_spans("ner"):
            entities[entity.text] = entity.tag

    alias_counter = {}

    for text, alias in entities.items():
        if alias in aliases_to_anonymize:
            counter = alias_counter.get(alias, 0)
            entities[text] = f"{alias}_{counter}"
            alias_counter[alias] = counter + 1
    return entities


def replace_text(raw_text: str, entities: dict) -> str:
    """Returns a string with named entities replaced with alias ids
    Args:
        raw_text (str): string to anonymize
        entities (dict): dictionary with named entities as keys and unique ids
            as values

    Returns:
        str: an anonymized string
    """
    new_text = raw_text

    for text, alias in entities.items():
        new_text = new_text.replace(text, alias)

    return new_text


def anonymize_text(
    tagger: SequenceTagger,
    raw_text: str,
    aliases_to_anonymize: list = ["LOC", "PER", "ORG"],
) -> str:
    """Returns an anonymized string

    Args:
        tagger (SequenceTagger): Flair SequenceTagger to perform NER
        raw_text (str): Sentence to anonymize
        aliases_to_anonymize (list, optional): List of aliases to anonymize.
            Defaults to ["LOC", "PER", "ORG"].

    Returns:
        str: anonymized string
    """

    entities = get_entities(
        tagger=tagger, raw_text=raw_text, aliases_to_anonymize=aliases_to_anonymize
    )

    new_text = replace_text(raw_text=raw_text, entities=entities)
    return new_text


def format_aliases(aliases: dict):
    formatted_aliases = []
    for text, alias in aliases.items():
        formatted_aliases.append(
            {"text": text, "alias": alias, "alias_type": alias.split("_")[0]}
        )
    return formatted_aliases
