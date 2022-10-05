from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
from flair.models import SequenceTagger
from .config import ANONYMIZED_TAGS_DESCRIPTION, ANONYMIZED_TAGS
from .model import get_entities, anonymize_sentence, replace_text
from pymongo import MongoClient
import datetime
from .utils import format_object_id
import bson

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
    
    
    
class Article(BaseModel):
    object_id: str = "633c6473b9daeb8a90169dcb"
    hash: int = 533794461304174741
    author: str = "Analysis by Stephen Collinson, CNN"
    date_published: datetime.datetime = datetime.datetime(2021, 12, 1, 14, 32, 33)
    section: str = "golf"
    url:str = "https://www.cnn.com/2021/12/01/golf/tiger-woods-end-of-era-meanwhile-spt-intl/index.html",
    headline:str = "Tiger Woods: Is this the end of his era? - CNN",
    keywords:List[str] = ["golf", "tiger", "woods", "end", "era", "cnn"],
    raw_text:str = "...",
    automatic_anonymized_text:str = "...",
    anonymized_text:str = "...",
    events:dict = {
        "insertion": {
            "date": datetime.datetime(2021, 12, 1, 14, 32, 33),
            "author": "paul_dechorgnat",
            "mode": "single" # or batch
            },
        "automatic_anonymization": {
            "date": datetime.datetime(2021, 12, 1, 14, 32, 33),
            "author": "pseudo_model:0.0.1",
        },
        "manual_anonymization": {
            "date": datetime.datetime(2021, 12, 1, 14, 32, 33),
            "author": "12343534",
        }
    }
    auto_anonymized_tags : List[Tag] = []
    manual_anonymized_tags: List[Tag] = []
    source: str = "sport"
    
    
VERSION = "0.0.1"

client = MongoClient()
db = client["articles"]

CATEGORIES = db.list_collection_names()


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


@api.get(
    "/data/articles",
    tags=["Data"],
    responses={
        200: {
            "description":"OK",
            "model": List[Article]
        }
    }
    )
def get_articles(
    category: List[str] = Query(default=None),
    date_start: datetime.datetime = Query(default=None),
    date_end: datetime.datetime = Query(default=None),
    sections: List[str] = Query(default=None),
):

    collections =  category if category else CATEGORIES

    mongo_filter = {}
    
    if sections:
        mongo_filter["section"] = {"$in": sections}
        
    if date_start:
        if date_end:
            
            mongo_filter["date_published"] = {"$gt": date_start, "$lt": date_end}
        else:
            mongo_filter["date_published"] = {"$gt": date_start}
    else:
        if date_end:
            mongo_filter["date_published"] = {"$lt": date_end}
    
    results = []
    for c in collections:
        results.extend(map(format_object_id, db[c].find(filter=mongo_filter)))
        
    results = [Article(**r) for r in results]
    
    return results

@api.get(
    "/data/articles/{category}/{object_id}",
    tags=["Data"],
    responses={
        200: {
            "description":"OK",
            "model": Article
        },
        404: {
            "description": "Article or category not found"
        }
    }
)
def get_article(category: str, object_id: str):
    if category not in CATEGORIES:
        raise HTTPException(404, detail=f"Category '{category}' not found.")
    try:
        result = db[category].find_one({"_id": bson.objectid.ObjectId(object_id)})
    except bson.errors.InvalidId:
        raise HTTPException(422, detail=f"Id '{object_id}' is not valid.")
    
    if not result:
        raise HTTPException(404, detail=f"Article with id '{object_id}' not found.")
    return Article(**result)
        
    
    
    