from flair.models import SequenceTagger

from api.aliasing_model import anonymize_text
from api.aliasing_model import get_entities
from api.aliasing_model import replace_text


tagger = SequenceTagger.load("ner")


text1 = "The UN is said to meet in New-York according to Donald Trump."

entities1 = {"UN": "ORG_0", "New-York": "LOC_0", "Donald Trump": "PER_0"}

clean_text1 = "The ORG_0 is said to meet in LOC_0 according to PER_0."


def test_get_entities():
    entities = get_entities(tagger=tagger, raw_text=text1)

    assert entities == entities1


def test_replace_text():
    new_text = replace_text(raw_text=text1, entities=entities1)

    assert new_text == clean_text1


def test_anonymized_text():
    new_text = anonymize_text(tagger=tagger, raw_text=text1)

    assert new_text == clean_text1
