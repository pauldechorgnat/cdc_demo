import datetime
from typing import List

from pydantic import BaseModel


class Text(BaseModel):
    text: str = "The UN is said to meet in New-York according to Donald Trump."


class Alias(BaseModel):
    text: str = "Paul Déchorgnat"
    alias: str = "PER_0"
    alias_type: str = "PER"


class AliasDescription(BaseModel):
    alias: str = "PER"
    description: str = "Person"


class AnonymizedTextWithAliases(BaseModel):
    raw_text: str
    anonymized_text: str
    aliases: List[Alias]


class NewArticle(BaseModel):
    author: str = "Analysis by Stephen Collinson, CNN"
    date_published: datetime.datetime = datetime.datetime(2021, 12, 1, 14, 32, 33)
    section: str = "golf"
    url: str = "https://www.cnn.com/.../index.html"
    headline: str = "Tiger Woods: Is this the end of his era? - CNN"
    keywords: List[str] = ["golf", "tiger", "woods", "end", "era", "cnn"]
    raw_text: str = "..."
    source: str = "sport"


class UpdateArticleData(BaseModel):
    author: str = None
    date_published: datetime.datetime = None
    section: str = None
    url: str = None
    headline: str = None
    keywords: List[str] = None
    raw_text: str = None


class ManualAnonymizedData(BaseModel):
    manual_anonymized_aliases: List[Alias] = []
    manual_anonymized_text: str = []


class Event(BaseModel):
    type: str = "insertion"
    author: str = "paul_dechorgnat"
    date: datetime.datetime = datetime.datetime(2021, 12, 1, 14, 32, 33)
    mode: str = None


class Article(NewArticle):
    object_id: str = "633c6473b9daeb8a90169dcb"
    hash: int = 533794461304174741
    auto_anonymized_text: str = "..."
    manual_anonymized_text: str = "..."
    anonymized_text: str = "..."
    events: List[Event]
    auto_anonymized_aliases: List[Alias] = []
    manual_anonymized_aliases: List[Alias] = []
