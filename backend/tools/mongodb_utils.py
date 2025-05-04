# backend/tools/mongodb_utils.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import config
from typing import Any, Dict
from bson import ObjectId

def get_mongo_client() -> MongoClient:
    client = MongoClient(
        config.MONGO_URI,
        server_api=ServerApi('1'),
        tls=True,
        tlsCAFile=certifi.where()
    )
    client.admin.command('ping')
    return client

def clean_duplicates(coll):
    pipeline = [
        {"$group": {"_id": "$filename", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]
    for grp in coll.aggregate(pipeline):
        fname = grp["_id"]
        docs = list(coll.find({"filename": fname}, {"_id":1}).sort("_id",-1))
        to_del = [d["_id"] for d in docs[1:]]
        if to_del:
            coll.delete_many({"_id": {"$in": to_del}})

def load_to_mongo(data: Dict[str,Any]) -> None:
    client = get_mongo_client()
    db = client[config.MONGO_DB]
    coll = db[config.MONGO_COLLECTION]

    clean_duplicates(coll)
    coll.create_index("filename", unique=True)

    inserted = updated = 0
    for fname, sections in data.items():
        doc = {"filename": fname, "sections": sections}
        res = coll.replace_one({"filename": fname}, doc, upsert=True)
        if res.upserted_id:
            inserted += 1
        elif res.modified_count:
            updated += 1

    print(f"Inserted {inserted}, Updated {updated}")
    client.close()