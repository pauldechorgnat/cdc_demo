import sys

sys.path.append(".")

from api.model import get_entities, anonymize_sentence, replace_text

from flair.data import Sentence
from flair.models import SequenceTagger

tagger = SequenceTagger.load("ner")


sentence1 = "The UN is said to meet in New-York according to Donald Trump."

entities1 = {"UN": "ORG_0", "New-York": "LOC_0", "Donald Trump": "PER_0"}

clean_sentence1 = "The ORG_0 is said to meet in LOC_0 according to PER_0."


def test_get_entities():
    entities = get_entities(tagger=tagger, raw_sentence=sentence1)

    assert entities == entities1


def test_replace_text():
    new_sentence = replace_text(raw_sentence=sentence1, entities=entities1)

    assert new_sentence == clean_sentence1


def test_anonymized_text():
    new_sentence = anonymize_sentence(tagger=tagger, raw_sentence=sentence1)

    assert new_sentence == clean_sentence1
