import datetime
import json

import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import NLTKWordTokenizer
from pymongo import MongoClient
from tqdm import tqdm

client = MongoClient()
db = client["articles"]

df = pd.read_csv("data/CNN_Articels_clean/CNN_Articels_clean.csv")
df.head()


tokenizer = NLTKWordTokenizer()

stop_words = set(stopwords.words("english"))

stop_words.update([",", ".", ":", "?", "!", ";", "-", "'s", "'"])

keywords = df["Keywords"].str.lower().apply(tokenizer.tokenize)
keywords = keywords.apply(lambda x: [i for i in x if i not in stop_words])

df["new_keywords"] = keywords

df.columns = [c.replace(" ", "_").lower() for c in df.columns]
df.columns

category_counter = {}

remaining = []

records = df[
    [
        "author",
        "date_published",
        "category",
        "section",
        "url",
        "headline",
        "new_keywords",
        "article_text",
    ]
].to_dict(orient="records")


for c in db.list_collection_names():
    db[c].delete_many({})


for r in tqdm(records):
    category = r.pop("category")
    r["source"] = category
    r["keywords"] = r.pop("new_keywords")
    r["raw_text"] = r.pop("article_text")

    if category_counter.get(category, 0) < 10:

        r["date_published"] = datetime.datetime.fromisoformat(r["date_published"])
        r["hash"] = hash(r["raw_text"])
        r["events"] = [
            {
                "type": "insertion",
                "date": datetime.datetime.utcnow(),
                "author": "paul_dechorgnat",
                "mode": "single",
            }
        ]

        db[category].insert_one(r)

    category_counter[category] = category_counter.get(category, 0) + 1


role_collection = client["api_administration"]["roles"]
role_collection.delete_many({})

with open("tests/roles.json", "r") as file:
    roles = json.load(file)

role_collection.insert_many(roles)
