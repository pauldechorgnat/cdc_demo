from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from flair.models import SequenceTagger
from .config import ANONYMIZED_TAGS_DESCRIPTION, ANONYMIZED_TAGS
from .model import get_entities, anonymize_sentence, replace_text

tagger = SequenceTagger.load("ner")


class Sentence(BaseModel):
    sentence: str = "The UN is said to meet in New-York according to Donald Trump."


class Tag(BaseModel):
    text: str = "Paul Déchorgnat"
    tag: str = "PER_0"


class TagDescription(BaseModel):
    tag: str = "PER"
    description: str = "Person"


class AnonymizedTextWithTags(BaseModel):
    raw_text: str
    anonymized_text: str
    tags: List[Tag]
    
VERSION = "0.0.1"


api = FastAPI(title="Anonymized text", version=VERSION)

default_responses = {200: {"description": "OK"}}


@api.get("/", tags=["Default"], responses=default_responses)
def get_index():
    """Returns a general message"""
    return {"message": "Documentation is at /docs", "version": VERSION}


@api.get(
    "/tags",
    tags=["Default"],
    responses={200: {"description": "OK", "model": List[TagDescription]}},
)
def get_tags():
    """Returns the list of tags that are anonymized and their description"""
    return [
        TagDescription(text=k, tag=v) for k, v in ANONYMIZED_TAGS_DESCRIPTION.items()
    ]


@api.get(
    "/tags/{tag}",
    tags=["Default"],
    responses={
        200: {"description": "OK", "model": TagDescription},
        404: {"description": "Not found"},
    },
)
def get_tag(tag: str):
    if tag not in ANONYMIZED_TAGS_DESCRIPTION:
        raise HTTPException(404, detail=f"Tag ID '{tag}' not found")
    return TagDescription(tag=tag, description=ANONYMIZED_TAGS_DESCRIPTION[tag])


@api.post(
    "/model/tags",
    tags=["Model"],
    responses={200: {"description": "OK", "model": List[Tag]}},
)
def post_get_named_entities(sentence: Sentence):
    entities = get_entities(
        tagger=tagger, raw_sentence=sentence.sentence, tags_to_anonymize=ANONYMIZED_TAGS
    )
    return [Tag(text=k, tag=v) for k, v in entities.items()]


@api.post(
    "/model/anonymize",
    tags=["Model"],
    responses={200: {"description": "OK", "model": AnonymizedTextWithTags}},
)
def post_anonymize_sentence(sentence: Sentence):
    raw_sentence = sentence.sentence

    entities = get_entities(
        tagger=tagger, raw_sentence=raw_sentence, tags_to_anonymize=ANONYMIZED_TAGS
    )

    new_sentence = replace_text(raw_sentence=raw_sentence, entities=entities)

    response = AnonymizedTextWithTags(
        raw_text=raw_sentence,
        anonymized_text=new_sentence,
        tags=[Tag(text=k, tag=v) for k, v in entities.items()],
    )
    return response
