import nltk
from flair.data import Sentence
from flair.models import SequenceTagger


def get_entities(
    tagger: SequenceTagger,
    raw_sentence: str,
    tags_to_anonymize: list = ["LOC", "PER", "ORG"],
) -> dict:
    """Returns a dictionary of named entities with a unique ID

    Args:
        tagger (SequenceTagger): Flair SequenceTagger to perform NER
        raw_sentence (str): Sentence to tag
        tags_to_anonymize (list, optional): List of tags to keep.
            Defaults to ["LOC", "PER", "ORG"].

    Returns:
        dict: dictionary with unique entities as keys and unique tag as values
    """
    sentences = [Sentence(s) for s in nltk.sent_tokenize(raw_sentence)]

    tagger.predict(sentences)

    entities = {}

    for s in sentences:
        for entity in s.get_spans("ner"):
            entities[entity.text] = entity.tag

    tag_counter = {}

    for text, tag in entities.items():
        if tag in tags_to_anonymize:
            counter = tag_counter.get(tag, 0)
            entities[text] = f"{tag}_{counter}"
            tag_counter[tag] = counter + 1
    return entities


def replace_text(raw_sentence: str, entities: dict) -> str:
    """Returns a string with named entities replaced with tag ids
    Args:
        raw_sentence (str): string to anonymize
        entities (dict): dictionary with named entities as keys and unique ids
            as values

    Returns:
        str: an anonymized string
    """
    new_sentence = raw_sentence

    for text, tag in entities.items():
        new_sentence = new_sentence.replace(text, tag)
        
    return new_sentence


def anonymize_sentence(
    tagger: SequenceTagger,
    raw_sentence: str,
    tags_to_anonymize: list = ["LOC", "PER", "ORG"],
) -> str:
    """Returns an anonymized string

    Args:
        tagger (SequenceTagger): Flair SequenceTagger to perform NER
        raw_sentence (str): Sentence to anonymize
        tags_to_anonymize (list, optional): List of tags to anonymize.
            Defaults to ["LOC", "PER", "ORG"].

    Returns:
        str: anonymized string
    """

    entities = get_entities(
        tagger=tagger, raw_sentence=raw_sentence, tags_to_anonymize=tags_to_anonymize
    )

    new_sentence = replace_text(raw_sentence=raw_sentence, entities=entities)
    return new_sentence
